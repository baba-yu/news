"""Cascade + orphan-sweep helpers for the prediction-keyed child tables.

``prediction_id`` is content-derived — ``_hash_id("prediction",
prediction_date, prediction_summary)`` in :mod:`app.src.ingest`, i.e.
``sha1(f"{prediction_date}||{body}")[:16]`` behind a ``prediction.``
prefix — so **editing a prediction's body mints a new id**. The ingest
layer is pure upsert (there is no ``DELETE`` anywhere under ``app/``),
so a re-key leaves every pre-edit child row behind unless something
removes it explicitly.

Historically that "something" was a hand-written one-off script under
the untracked ``design/_scratch/`` (``fix_0719_idcascade.py``,
``fix_predB_rekey_0731.py``, ``rekey_0801.py``, ``rekey_0802.py``, …).
Each carried its own hardcoded table list, each list was different, and
every one of them was incomplete in the same way: they all swept
``predictions`` / ``prediction_needs`` / ``validation_rows`` /
``needs_tasks`` and every one of them forgot
``prediction_scope_assignments``, ``prediction_evidence_links`` and
``theme_candidates``. Those scripts also opened the DB with a bare
``sqlite3.connect()``, where ``PRAGMA foreign_keys`` defaults to OFF —
so the ``DELETE FROM predictions`` that orphaned the children was never
refused, even though :func:`app.src.db.connect` turns FKs on for every
connection the application itself makes.

Measured against ``app/data/analytics.sqlite`` on 2026-08-03 (324
predictions) that left 17 + 12 + 3 = 32 orphan rows, accruing on
2026-07-19, 07-30, 08-01 and 08-02. The debris silently inflates any
statistic computed from these tables without a join back to
``predictions``: category dominance read 69.8% / 73.0% instead of
69.4%, and ``business.ai_revenue_disclosure`` read 161 instead of 156.

This module is the single owner of the child-table map, so that list
can only ever be wrong in one place:

  * :data:`PREDICTION_CHILD_TABLES` — every table keyed on a
    ``prediction_id``, with the column that holds it.
  * :func:`count_orphans` — read-only; what the post-update validator
    gates on.
  * :func:`sweep_orphans` — remove the debris. Wired into the ingest /
    update CLI path so a re-key cleans up after itself.
  * :func:`purge_prediction` — the complete cascade for a single id.
    Future re-key scripts should call **this** rather than re-deriving
    a table list by hand; that is the failure this module exists to
    stop repeating.

Deliberately **not** swept
--------------------------

``validation_rows`` is keyed on ``(validation_date, prediction_date,
prediction_summary)``, not on ``prediction_id``, so a prediction re-key
does not re-key the bridge row — it only leaves ``prediction_id``
pointing at the old value. The row also carries reader-visible content
(the bridge narrative), so the correct repair is to *re-point* it, not
to delete it; :func:`purge_prediction` does that via its
``replacement_id`` argument. A blanket DELETE here would silently drop
published bridge text, so ``validation_rows`` is excluded from both the
sweep and the validator gate. ``prediction_chain`` and
``prediction_relations`` are likewise excluded: both are derived,
advisory streams rebuilt from ``readings.json`` on every ingest.
"""

from __future__ import annotations

import sqlite3


# (table, column-holding-a-prediction_id). The sweep runs in this order
# and ``prediction_needs`` must stay ahead of the ``needs_tasks`` join
# sweep below — a task is only orphaned once its parent need is gone.
PREDICTION_CHILD_TABLES: tuple[tuple[str, str], ...] = (
    ("prediction_scope_assignments", "prediction_id"),
    ("prediction_evidence_links", "prediction_id"),
    ("theme_candidates", "origin_prediction_id"),
    ("prediction_needs", "prediction_id"),
)

# ``needs_tasks`` has no ``prediction_id`` column — it reaches a
# prediction only through ``prediction_needs.need_id``. A sweep keyed on
# prediction_id therefore misses it entirely and it needs its own join
# condition.
NEEDS_TASKS_ORPHAN_SQL = (
    "needs_tasks WHERE need_id NOT IN (SELECT need_id FROM prediction_needs)"
)

# Stable key for every count/sweep report, so callers can enumerate the
# full set rather than guessing which keys a dict happens to carry.
ORPHAN_KEYS: tuple[str, ...] = tuple(
    f"{table}.{column}" for table, column in PREDICTION_CHILD_TABLES
) + ("needs_tasks.need_id",)


def _orphan_predicate(column: str) -> str:
    """SQL predicate matching rows whose ``column`` has no parent prediction.

    ``IS NOT NULL`` matters: ``origin_prediction_id`` is nullable (a
    candidate may originate from evidence rather than a prediction), and
    ``x NOT IN (…)`` is never true for NULL anyway — being explicit keeps
    the intent readable next to the DELETE.
    """
    return (
        f"{column} IS NOT NULL "
        f"AND {column} NOT IN (SELECT prediction_id FROM predictions)"
    )


def count_orphans(conn: sqlite3.Connection) -> dict[str, int]:
    """Return ``{"<table>.<column>": orphan_row_count}`` for every checked table.

    Read-only. Every key in :data:`ORPHAN_KEYS` is always present, zero
    included, so a caller can print a complete report and a missing key
    is a bug rather than "no orphans here".
    """
    counts: dict[str, int] = {}
    for table, column in PREDICTION_CHILD_TABLES:
        counts[f"{table}.{column}"] = conn.execute(
            f"SELECT COUNT(*) FROM {table} WHERE {_orphan_predicate(column)}"
        ).fetchone()[0]
    counts["needs_tasks.need_id"] = conn.execute(
        f"SELECT COUNT(*) FROM {NEEDS_TASKS_ORPHAN_SQL}"
    ).fetchone()[0]
    return counts


def sweep_orphans(conn: sqlite3.Connection) -> dict[str, int]:
    """Delete every child row whose parent prediction (or need) is gone.

    Returns ``{"<table>.<column>": rows_deleted}`` with the same complete
    key set as :func:`count_orphans`. Does **not** commit — the caller
    owns the transaction.

    Safe to run unconditionally: a row here is unreachable by definition
    (nothing can join to a prediction that does not exist), so removing
    it cannot change any correctly-written query's result — only the
    ones that read these tables without joining back to ``predictions``,
    which is precisely the inflation this fixes.
    """
    removed: dict[str, int] = {}
    for table, column in PREDICTION_CHILD_TABLES:
        cur = conn.execute(
            f"DELETE FROM {table} WHERE {_orphan_predicate(column)}"
        )
        removed[f"{table}.{column}"] = cur.rowcount
    # Runs last, after prediction_needs above may have just removed the
    # parent rows that orphan these tasks.
    cur = conn.execute(f"DELETE FROM {NEEDS_TASKS_ORPHAN_SQL}")
    removed["needs_tasks.need_id"] = cur.rowcount
    return removed


def purge_prediction(
    conn: sqlite3.Connection,
    prediction_id: str,
    *,
    replacement_id: str | None = None,
) -> dict[str, int]:
    """Delete ``prediction_id`` and every row that hangs off it.

    This is the helper a re-key script should call for the *old* id once
    the re-ingest has created the new row. Pass ``replacement_id`` (the
    new id) so the content-bearing ``validation_rows`` are re-pointed at
    the surviving prediction instead of being left dangling; omit it to
    detach them (``prediction_id`` set to NULL), which is what the
    schema already uses for an unmatched bridge row.

    Returns per-table removal counts, plus ``validation_rows.repointed``
    and ``predictions``. Does not commit.
    """
    removed: dict[str, int] = {}
    if replacement_id is not None:
        cur = conn.execute(
            "UPDATE validation_rows SET prediction_id = ? WHERE prediction_id = ?",
            (replacement_id, prediction_id),
        )
    else:
        cur = conn.execute(
            "UPDATE validation_rows SET prediction_id = NULL WHERE prediction_id = ?",
            (prediction_id,),
        )
    removed["validation_rows.repointed"] = cur.rowcount

    for table, column in PREDICTION_CHILD_TABLES:
        cur = conn.execute(
            f"DELETE FROM {table} WHERE {column} = ?", (prediction_id,)
        )
        removed[f"{table}.{column}"] = cur.rowcount
    cur = conn.execute(f"DELETE FROM {NEEDS_TASKS_ORPHAN_SQL}")
    removed["needs_tasks.need_id"] = cur.rowcount

    cur = conn.execute(
        "DELETE FROM predictions WHERE prediction_id = ?", (prediction_id,)
    )
    removed["predictions"] = cur.rowcount
    return removed


def format_counts(counts: dict[str, int]) -> str:
    """One-line ``a=1 b=2`` rendering of a count/removal dict.

    Only non-zero entries are shown; ``"none"`` when everything is zero,
    so the daily log line stays readable but never silently empty.
    """
    parts = [f"{k}={v}" for k, v in counts.items() if v]
    return " ".join(parts) if parts else "none"
