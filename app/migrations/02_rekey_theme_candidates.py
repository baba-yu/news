"""One-shot migration: re-key ``theme_candidates.candidate_id`` onto the prediction slot.

Idempotent: re-running on an already-migrated DB is a no-op.

Usage:
    python -m app.migrations.02_rekey_theme_candidates --db app/data/analytics.sqlite
    python -m app.migrations.02_rekey_theme_candidates --db app/data/analytics.sqlite --apply

``app.src.ingest._upsert_candidate`` used to derive the candidate id from
``(scope_id, prediction_id)``. ``prediction_id`` hashes the prediction
body, so editing a body re-keyed the prediction and minted a *second*
candidate row for the same prediction. That corrupted the promotion
signal itself: the 2026-08-02 theme review found the only cluster that
appeared to clear the "≥3 pending hits" threshold was in fact 3 sha1
variants of one prediction. The id is now derived from the prediction's
**slot** — ``(scope_id, prediction_date, source_row_index)`` — which
survives a body edit while still separating genuinely different
predictions.

Changing the derivation strands every pre-existing row under the old
scheme. ``app/data/analytics.sqlite`` must not be rebuilt
(design/memory-policy.md §6: the glossary lifecycle and the candidate
``pending → promoted / merged / rejected / ignored`` flow are DB-owned
and not reconstructible from files), and ``python -m app.src.cli update``
re-ingests *every* date under ``app/sourcedata/`` — so without this
migration the next update would insert a full second set of candidate
rows alongside the old ones, strictly worse than the bug being fixed.
Run this once, alongside the ingest change.

Rows whose ``origin_prediction_id`` is absent from ``predictions`` have
no knowable slot and are skipped; they belong to
``app.src.prediction_cascade.sweep_orphans``, which should run first.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path


# Which status wins when two old rows collapse onto one new id. A human
# or reviewer decision outranks the machine default, so `pending` is the
# only status that ever loses. (No collisions existed in the 2026-08-03
# corpus — this is here so the merge is defined rather than arbitrary.)
_STATUS_PRIORITY = {
    "promoted": 4,
    "merged": 3,
    "rejected": 2,
    "ignored": 1,
    "pending": 0,
}


def new_candidate_id(
    scope_id: str, prediction_date: str, source_row_index: int
) -> str:
    """Mirror of ``_hash_id("candidate", scope, date, str(index))``.

    Spelled out here rather than imported so this one-shot keeps
    reproducing the scheme that was current when it was written, even if
    the ingest helper is later refactored. ``app/tests/
    test_prediction_cascade.py`` asserts the two agree today.
    """
    parts = (scope_id, prediction_date, str(source_row_index))
    h = hashlib.sha1("||".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"candidate.{h}"


def plan(conn: sqlite3.Connection) -> dict:
    """Compute the re-key plan without writing anything.

    Returns ``{"rekey": [(old_id, new_id)], "merge": [(loser_id, new_id)],
    "skipped_orphan": [ids], "already_new": n, "total": n}``.
    """
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT c.candidate_id, c.scope_id, c.status, c.origin_prediction_id,
               p.prediction_date, p.source_row_index
        FROM theme_candidates c
        LEFT JOIN predictions p
               ON p.prediction_id = c.origin_prediction_id
        ORDER BY c.candidate_id
        """
    ).fetchall()

    rekey: list[tuple[str, str]] = []
    merge: list[tuple[str, str]] = []
    skipped_orphan: list[str] = []
    already_new = 0
    claimed: dict[str, tuple[str, str]] = {}  # new_id -> (candidate_id, status)

    for r in rows:
        if r["origin_prediction_id"] is None:
            # Candidate originated from evidence, not a prediction: it has
            # no slot, and the old scheme never applied to it either.
            continue
        if r["prediction_date"] is None:
            # LEFT JOIN missed => the origin prediction is gone.
            skipped_orphan.append(r["candidate_id"])
            continue
        nid = new_candidate_id(
            r["scope_id"], r["prediction_date"], r["source_row_index"]
        )
        if nid == r["candidate_id"]:
            already_new += 1
            claimed[nid] = (r["candidate_id"], r["status"])
            continue
        prior = claimed.get(nid)
        if prior is None:
            claimed[nid] = (r["candidate_id"], r["status"])
            rekey.append((r["candidate_id"], nid))
        else:
            # Two old rows map onto one slot — they were duplicates of a
            # single prediction all along. Keep the higher-priority status.
            prior_id, prior_status = prior
            if _STATUS_PRIORITY.get(r["status"], 0) > _STATUS_PRIORITY.get(
                prior_status, 0
            ):
                rekey[:] = [pair for pair in rekey if pair[0] != prior_id]
                merge.append((prior_id, nid))
                claimed[nid] = (r["candidate_id"], r["status"])
                rekey.append((r["candidate_id"], nid))
            else:
                merge.append((r["candidate_id"], nid))

    return {
        "rekey": rekey,
        "merge": merge,
        "skipped_orphan": skipped_orphan,
        "already_new": already_new,
        "total": len(rows),
    }


def apply_plan(conn: sqlite3.Connection, p: dict) -> dict:
    """Apply a plan from :func:`plan`. Does not commit."""
    for loser, _winner in p["merge"]:
        conn.execute(
            "DELETE FROM theme_candidates WHERE candidate_id = ?", (loser,)
        )
    for old, new in p["rekey"]:
        conn.execute(
            "UPDATE theme_candidates SET candidate_id = ? WHERE candidate_id = ?",
            (new, old),
        )
    return {"rekeyed": len(p["rekey"]), "merged": len(p["merge"])}


def migrate(db_path: Path, *, apply: bool = False) -> dict:
    if not Path(db_path).is_file():
        raise FileNotFoundError(f"DB not found: {db_path}")
    conn = sqlite3.connect(str(db_path))
    try:
        p = plan(conn)
        result = {
            "db": str(db_path),
            "total": p["total"],
            "already_new_scheme": p["already_new"],
            "to_rekey": len(p["rekey"]),
            "to_merge": len(p["merge"]),
            "skipped_orphan": len(p["skipped_orphan"]),
            "applied": False,
        }
        if not apply:
            return result
        res = apply_plan(conn, p)
        conn.commit()
        result["applied"] = True
        result["rekeyed"] = res["rekeyed"]
        result["merged"] = res["merged"]
        # A correct migration is a fixed point: re-plan on the committed
        # state and refuse to report success if anything is still pending.
        after = plan(conn)
        if after["rekey"] or after["merge"]:
            raise RuntimeError(
                f"not idempotent: {len(after['rekey'])} re-key / "
                f"{len(after['merge'])} merge still pending after apply"
            )
        result["verified_already_new_scheme"] = after["already_new"]
        return result
    finally:
        conn.close()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--db", required=True, type=Path)
    p.add_argument(
        "--apply", action="store_true",
        help="write the changes (default is a dry run)",
    )
    args = p.parse_args(argv)
    try:
        result = migrate(args.db, apply=args.apply)
    except (FileNotFoundError, RuntimeError) as e:
        print(f"FAIL {e}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    if result["skipped_orphan"]:
        print(
            "NOTE orphan candidates cannot be re-keyed (their origin "
            "prediction is gone). Sweep them first: python -m app.src.cli update",
            file=sys.stderr,
        )
    if not result["applied"]:
        print("dry run — pass --apply to write", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
