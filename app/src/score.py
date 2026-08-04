"""Compute daily activity rows for themes, subthemes, categories, and
prediction realization snapshots across 7d / 30d / 90d windows.

This is deliberately simple: for each ``(scope, theme, window)`` we
compute a single aggregate metric bundle based on the prediction
assignments in that scope/theme plus their evidence links inside the
window. We store only one activity row per theme — the one dated at
``as_of``.

Dating
------
``run_score(as_of=...)`` scores exactly ONE date. When ``as_of`` is
omitted it defaults to ``MAX(source_files.report_date)``.

That default is why a catch-up session silently loses a day: a single
run can only ever stamp one date, so if two days' sourcedata are
ingested before ``score`` runs, the earlier day never gets an activity
row at all. That is what happened to 2026-07-28 (ingested 2026-07-29
15:43, one hour before 2026-07-29's own ingest; the only score run that
day came after both). Pass ``--date`` to score a specific day, or let
``cli update`` call :func:`backfill_missing`, which re-scores any
in-series date that has no activity rows.

Carry-forward semantics
-----------------------
A prediction gets a realization snapshot on EVERY scored date, not only
on dates where it actually had a bridge. On a date with no new
validation row for that prediction, the snapshot carries forward its
most recent observed relevance (see :func:`_snapshot_predictions`).
The series is therefore step-wise, not sparse: a flat run of identical
``realization_score`` values means "no new evidence since <date>", NOT
"re-confirmed daily". Nothing decays it.
"""

from __future__ import annotations

import hashlib
import sqlite3
from datetime import date
from pathlib import Path

from .analytics.scoring import (
    attention_score,
    continuing_signal_from_sum,
    grass_level,
    new_signal_from_sum,
    normalize_relevance,
    prediction_status,
    realization_score,
    theme_status,
)
from .analytics.windows import WINDOWS, parse_iso_date, window_range
from .db import connect


def _now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _hid(prefix: str, *parts: str) -> str:
    h = hashlib.sha1("||".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}.{h}"


def _latest_report_date(conn: sqlite3.Connection) -> date | None:
    cur = conn.execute(
        "SELECT MAX(report_date) AS d FROM source_files WHERE file_type = 'daily_report'"
    )
    row = cur.fetchone()
    if not row or not row["d"]:
        return None
    return parse_iso_date(row["d"])


def _earliest_report_date(conn: sqlite3.Connection) -> date | None:
    cur = conn.execute(
        "SELECT MIN(report_date) AS d FROM source_files WHERE file_type = 'daily_report'"
    )
    row = cur.fetchone()
    if not row or not row["d"]:
        return None
    return parse_iso_date(row["d"])


def _report_dates(conn: sqlite3.Connection) -> list[str]:
    cur = conn.execute(
        "SELECT DISTINCT report_date FROM source_files "
        "WHERE file_type = 'daily_report' AND report_date IS NOT NULL "
        "ORDER BY report_date"
    )
    return [r["report_date"] for r in cur.fetchall()]


def unscored_dates(conn: sqlite3.Connection) -> list[str]:
    """Report dates inside the scored era that have no activity rows.

    Bounded below by the earliest date that HAS activity rows. The
    corpus contains ~50 daily reports from 2026-04-19..2026-06-08 that
    predate daily scoring entirely (they were backfilled as markdown
    long after the fact); re-scoring those would invent a history the
    series never had. Only gaps that opened up *after* the series
    started are real gaps.
    """
    cur = conn.execute("SELECT MIN(activity_date) AS d FROM topic_daily_activity")
    row = cur.fetchone()
    first_scored = row["d"] if row else None
    if not first_scored:
        return []
    cur = conn.execute("SELECT DISTINCT activity_date FROM topic_daily_activity")
    scored = {r["activity_date"] for r in cur.fetchall()}
    return [
        d for d in _report_dates(conn) if d >= first_scored and d not in scored
    ]


def run_score(db_path: Path | None = None, *, as_of: date | str | None = None) -> dict:
    """Compute and upsert daily activity rows for a single date.

    ``as_of`` defaults to the latest ``daily_report`` report date. Pass
    an explicit date to score a day that was skipped (see the module
    docstring). Scoring a PAST date switches on three guards, so a
    backfill reconstructs that day rather than stamping today onto it:

    * the assignment roster is restricted to assignments that already
      existed on that date (``prediction_scope_assignments.assigned_at``,
      which the ingest upsert leaves untouched on conflict);
    * the theme roster is restricted the same way via ``themes.created_at``;
    * ``latest_observation_status`` on the assignment row is left alone,
      since a past day's status must not overwrite the current one.

    Raises ``ValueError`` if the corpus has no daily report for
    ``as_of`` — a typo must not mint a phantom date.
    """
    conn = connect(db_path) if db_path else connect()
    try:
        latest = _latest_report_date(conn)
        if latest is None:
            return {"status": "no-data"}

        if as_of is None:
            target = latest
        else:
            target = parse_iso_date(as_of) if isinstance(as_of, str) else as_of
            if target.isoformat() not in set(_report_dates(conn)):
                raise ValueError(
                    f"no daily_report source file for {target.isoformat()} — "
                    "refusing to score a date the corpus has no report for"
                )
        backfill = target < latest

        # 1. theme daily activity per window/scope
        theme_rows = 0
        for scope_id in ("tech", "business"):
            theme_rows += _score_themes(
                conn, scope_id=scope_id, as_of=target, backfill=backfill
            )

        # 2. category daily activity per window/scope (aggregated from themes)
        category_rows = 0
        for scope_id in ("tech", "business"):
            category_rows += _score_categories(
                conn, scope_id=scope_id, as_of=target
            )

        # 3. prediction realization snapshots per window/scope
        pred_rows = _snapshot_predictions(conn, as_of=target, backfill=backfill)

        conn.commit()
        return {
            "latest": target.isoformat(),
            "as_of": target.isoformat(),
            "backfill": backfill,
            "theme_activity_rows": theme_rows,
            "category_activity_rows": category_rows,
            "prediction_snapshots": pred_rows,
        }
    finally:
        conn.close()


def backfill_missing(db_path: Path | None = None) -> list[dict]:
    """Score every in-series date that has no activity rows.

    Called by ``cli update`` so a catch-up session self-heals instead of
    leaving a permanent hole. Returns one :func:`run_score` result per
    date healed (empty list when there is nothing to do).
    """
    conn = connect(db_path) if db_path else connect()
    try:
        pending = unscored_dates(conn)
    finally:
        conn.close()
    return [run_score(db_path, as_of=d) for d in pending]


# ---------------------------------------------------------------------------
# Theme scoring
# ---------------------------------------------------------------------------


def _themes_predate(conn: sqlite3.Connection, as_of: date) -> bool:
    """True when the themes table was populated on or before ``as_of``.

    Distinguishes "this theme is newer than the day I'm scoring" from
    "the whole DB was rebuilt after that day, so created_at tells me
    nothing".
    """
    row = conn.execute("SELECT MIN(created_at) AS d FROM themes").fetchone()
    if not row or not row["d"]:
        return False
    return str(row["d"])[:10] <= as_of.isoformat()


def _score_themes(
    conn: sqlite3.Connection, *, scope_id: str, as_of: date, backfill: bool = False
) -> int:
    # `first_seen_date` is NULL on every seeded theme, so `created_at` is
    # the only usable "existed by" signal when backfilling. Without it a
    # backfill hands the old day themes the weekly review promoted since
    # (e.g. tech.ai_infra_private_capital, created 2026-08-03).
    #
    # Guard: the whole table gets a fresh `created_at` whenever the DB is
    # rebuilt from schema.sql (the documented recovery path in db.py). In
    # that state every theme postdates every past date, so the filter
    # would silently score an old day with ZERO themes. Only apply it
    # when the table demonstrably predates `as_of`.
    theme_clause = ""
    params: tuple = (scope_id,)
    if backfill and _themes_predate(conn, as_of):
        theme_clause = " AND substr(created_at, 1, 10) <= ?"
        params = (scope_id, as_of.isoformat())
    cur = conn.execute(
        f"""
        SELECT theme_id, category_id, first_seen_date
        FROM themes
        WHERE scope_id = ? AND status IN ('active', 'candidate')
        {theme_clause}
        """,
        params,
    )
    themes = cur.fetchall()
    inserted = 0
    for theme in themes:
        for window_id, days in WINDOWS:
            start, end = window_range(as_of, days)
            metrics = _theme_window_metrics(
                conn,
                scope_id=scope_id,
                theme_id=theme["theme_id"],
                window_start=start,
                window_end=end,
            )
            _upsert_topic_activity(
                conn,
                activity_date=as_of.isoformat(),
                window_id=window_id,
                scope_id=scope_id,
                category_id=theme["category_id"],
                theme_id=theme["theme_id"],
                subtheme_id=None,
                activity_level="theme",
                metrics=metrics,
                first_seen=theme["first_seen_date"],
            )
            inserted += 1
    return inserted


def _theme_window_metrics(
    conn: sqlite3.Connection,
    *,
    scope_id: str,
    theme_id: str,
    window_start: date,
    window_end: date,
) -> dict:
    """Aggregate the prediction/validation signals for a theme in a window."""
    # Pull all prediction-evidence links whose validation_date falls in the window
    # for predictions assigned to this theme in this scope.
    cur = conn.execute(
        """
        SELECT pel.relatedness_score, pel.evidence_strength,
               pel.contradiction_score, pel.evidence_recency_type
        FROM prediction_evidence_links pel
        JOIN prediction_scope_assignments psa
          ON pel.prediction_id = psa.prediction_id
         AND pel.scope_id = psa.scope_id
        WHERE psa.scope_id = ?
          AND psa.theme_id = ?
          AND pel.validation_date BETWEEN ? AND ?
        """,
        (scope_id, theme_id, window_start.isoformat(), window_end.isoformat()),
    )
    rows = cur.fetchall()

    new_relevance: list[float] = []
    cont_relevance: list[float] = []

    for r in rows:
        strength = r["evidence_strength"] or 0.0
        if r["evidence_recency_type"] == "new":
            new_relevance.append(strength)
        else:
            cont_relevance.append(strength)

    # Also pull prediction count for the theme (in-scope, regardless of window).
    cur = conn.execute(
        """
        SELECT COUNT(*) AS cnt
        FROM prediction_scope_assignments
        WHERE scope_id = ? AND theme_id = ?
        """,
        (scope_id, theme_id),
    )
    prediction_count = cur.fetchone()["cnt"] or 0

    # Frequency × relevance: saturate the summed normalized relevances
    # rather than collapsing to max(). One relevance-5 hit now reads
    # different from five relevance-5 hits.
    new_sum = sum(new_relevance)
    cont_sum = sum(cont_relevance)
    new_signal = new_signal_from_sum(new_sum)
    continuing_signal = continuing_signal_from_sum(cont_sum)
    contradiction_signal = 0.0  # retired — kept in schema for compat, always 0.
    atten = attention_score(new_signal, continuing_signal)
    mean_new = (sum(new_relevance) / len(new_relevance)) if new_relevance else 0.0
    mean_cont = (sum(cont_relevance) / len(cont_relevance)) if cont_relevance else 0.0
    realization = realization_score(mean_new, mean_cont)
    gl = grass_level(atten)
    status = theme_status(atten, realization)

    # Streak: count consecutive dates ending at window_end with any evidence.
    streak_days = _streak(
        conn,
        scope_id=scope_id,
        theme_id=theme_id,
        window_end=window_end,
    )

    return {
        "new_signal": new_signal,
        "continuing_signal": continuing_signal,
        "contradiction_signal": contradiction_signal,
        "attention_score": atten,
        "realization_score": realization,
        "grass_level": gl,
        "status": status,
        "new_evidence_count": len(new_relevance),
        "active_prior_evidence_count": len(cont_relevance),
        "prediction_count": prediction_count,
        "streak_days": streak_days,
    }


def _streak(
    conn: sqlite3.Connection,
    *,
    scope_id: str,
    theme_id: str,
    window_end: date,
) -> int:
    cur = conn.execute(
        """
        SELECT DISTINCT pel.validation_date
        FROM prediction_evidence_links pel
        JOIN prediction_scope_assignments psa
          ON pel.prediction_id = psa.prediction_id
         AND pel.scope_id = psa.scope_id
        WHERE psa.scope_id = ? AND psa.theme_id = ?
        """,
        (scope_id, theme_id),
    )
    dates = {parse_iso_date(r["validation_date"]) for r in cur.fetchall() if r["validation_date"]}
    streak = 0
    cursor = window_end
    while cursor in dates:
        streak += 1
        from datetime import timedelta

        cursor = cursor - timedelta(days=1)
    return streak


def _upsert_topic_activity(
    conn: sqlite3.Connection,
    *,
    activity_date: str,
    window_id: str,
    scope_id: str,
    category_id: str | None,
    theme_id: str,
    subtheme_id: str | None,
    activity_level: str,
    metrics: dict,
    first_seen: str | None,
) -> None:
    activity_id = _hid(
        "activity",
        scope_id,
        theme_id,
        subtheme_id or "",
        window_id,
        activity_date,
        activity_level,
    )
    conn.execute(
        """
        INSERT OR REPLACE INTO topic_daily_activity (
          activity_id, activity_date, window_id, scope_id,
          category_id, theme_id, subtheme_id, activity_level,
          new_signal, continuing_signal, contradiction_signal,
          attention_score, realization_score, grass_level,
          new_evidence_count, active_prior_evidence_count, prediction_count,
          status, streak_days, last_active_date, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?,
                  ?, ?, ?,
                  ?, ?, ?,
                  ?, ?, ?,
                  ?, ?, ?, ?)
        """,
        (
            activity_id,
            activity_date,
            window_id,
            scope_id,
            category_id,
            theme_id,
            subtheme_id,
            activity_level,
            metrics["new_signal"],
            metrics["continuing_signal"],
            metrics["contradiction_signal"],
            metrics["attention_score"],
            metrics["realization_score"],
            metrics["grass_level"],
            metrics["new_evidence_count"],
            metrics["active_prior_evidence_count"],
            metrics["prediction_count"],
            metrics["status"],
            metrics["streak_days"],
            activity_date,
            _now(),
        ),
    )


# ---------------------------------------------------------------------------
# Category scoring
# ---------------------------------------------------------------------------


def _score_categories(
    conn: sqlite3.Connection, *, scope_id: str, as_of: date
) -> int:
    cur = conn.execute(
        "SELECT category_id FROM categories WHERE scope_id = ? AND active = 1",
        (scope_id,),
    )
    categories = [r["category_id"] for r in cur.fetchall()]
    inserted = 0
    priority = ["new", "active", "continuing", "dormant"]
    for category_id in categories:
        for window_id, _days in WINDOWS:
            cur = conn.execute(
                """
                SELECT attention_score, realization_score, contradiction_signal,
                       grass_level, status, prediction_count
                FROM topic_daily_activity
                WHERE scope_id = ? AND category_id = ? AND window_id = ?
                  AND activity_level = 'theme' AND activity_date = ?
                """,
                (scope_id, category_id, window_id, as_of.isoformat()),
            )
            rows = cur.fetchall()
            if not rows:
                metrics = {
                    "attention_score": 0.0,
                    "realization_score": 0.0,
                    "contradiction_signal": 0.0,
                    "grass_level": 0,
                    "theme_count": 0,
                    "active_theme_count": 0,
                    "prediction_count": 0,
                    "status": "dormant",
                }
            else:
                atts = [r["attention_score"] or 0.0 for r in rows]
                rels = [r["realization_score"] or 0.0 for r in rows]
                pred_counts = [r["prediction_count"] or 0 for r in rows]
                pred_total = sum(pred_counts)
                # Weighted avg realization by prediction_count, fallback plain avg.
                if pred_total > 0:
                    realization = sum(
                        (r["realization_score"] or 0.0) * (r["prediction_count"] or 0)
                        for r in rows
                    ) / pred_total
                else:
                    realization = sum(rels) / len(rels)
                atten = max(atts)
                # Choose strongest status by priority.
                status = "dormant"
                for p in priority:
                    if any(r["status"] == p for r in rows):
                        status = p
                        break
                metrics = {
                    "attention_score": atten,
                    "realization_score": realization,
                    "contradiction_signal": 0.0,
                    "grass_level": grass_level(atten),
                    "theme_count": len(rows),
                    "active_theme_count": sum(
                        1 for r in rows if r["status"] in ("active", "continuing", "new")
                    ),
                    "prediction_count": pred_total,
                    "status": status,
                }
            _upsert_category_activity(
                conn,
                activity_date=as_of.isoformat(),
                window_id=window_id,
                scope_id=scope_id,
                category_id=category_id,
                metrics=metrics,
            )
            inserted += 1
    return inserted


def _upsert_category_activity(
    conn: sqlite3.Connection,
    *,
    activity_date: str,
    window_id: str,
    scope_id: str,
    category_id: str,
    metrics: dict,
) -> None:
    activity_id = _hid(
        "catactivity", scope_id, category_id, window_id, activity_date
    )
    conn.execute(
        """
        INSERT OR REPLACE INTO category_daily_activity (
          category_activity_id, activity_date, window_id, scope_id, category_id,
          attention_score, realization_score, contradiction_signal, grass_level,
          theme_count, active_theme_count, prediction_count, status, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            activity_id,
            activity_date,
            window_id,
            scope_id,
            category_id,
            metrics["attention_score"],
            metrics["realization_score"],
            metrics["contradiction_signal"],
            metrics["grass_level"],
            metrics["theme_count"],
            metrics["active_theme_count"],
            metrics["prediction_count"],
            metrics["status"],
            _now(),
        ),
    )


# ---------------------------------------------------------------------------
# Prediction snapshot
# ---------------------------------------------------------------------------


def _snapshot_predictions(
    conn: sqlite3.Connection, *, as_of: date, backfill: bool = False
) -> int:
    """Snapshot every assignment's realization state as of ``as_of``.

    CARRY-FORWARD IS INTENTIONAL AND LOSSLESS-BY-DESIGN, BUT UNDECAYED.
    Every ``(prediction, scope)`` pair gets a row on every scored date,
    whether or not it had a bridge that day. The relevance written is
    the prediction's most recent ``validation_rows.observed_relevance``
    *at or before* ``as_of`` — so a prediction whose last bridge was on
    2026-07-28 keeps reporting that relevance on every later date until
    a new bridge replaces it. Consumers must read a flat run as "no new
    evidence since <first date of the run>", not as daily
    re-confirmation. There is no decay and no staleness flag; the only
    way to tell a fresh 3 from a six-week-old 3 is to join back to
    ``validation_rows`` on ``validation_date``.

    This reads the historized ``validation_rows`` rather than the
    denormalized ``prediction_scope_assignments.latest_*`` columns.
    Those columns are last-writer-wins with no date attached, so they
    only describe *today*; using them made every date impossible to
    score except the newest one.
    """
    roster_clause = ""
    params: tuple = (as_of.isoformat(),)
    if backfill:
        # Assignments minted after `as_of` did not exist on that date.
        # `assigned_at` is INSERT-stable: _upsert_assignment's ON
        # CONFLICT branch updates `updated_at` only.
        #
        # The `prediction_date = ?` arm is load-bearing for exactly the
        # catch-up case this function exists to repair: when day D is
        # ingested on D+1, the assignments for D's OWN new predictions
        # get `assigned_at` = D+1. Without that arm, the three
        # predictions introduced on 2026-07-28 were excluded from their
        # own day. It must stay `=` and not `<=`: an older prediction
        # re-assigned later (what the weekly theme review does) really
        # did not have that assignment on `as_of`.
        roster_clause = (
            " WHERE psa.assigned_at IS NULL"
            " OR substr(psa.assigned_at, 1, 10) <= ?"
            " OR p.prediction_date = ?"
        )
        params = (as_of.isoformat(), as_of.isoformat(), as_of.isoformat())

    cur = conn.execute(
        f"""
        SELECT p.prediction_id, psa.scope_id,
               (SELECT v.observed_relevance
                  FROM validation_rows v
                 WHERE v.prediction_id = p.prediction_id
                   AND v.validation_date <= ?
                   AND v.observed_relevance IS NOT NULL
                 ORDER BY v.validation_date DESC, v.validation_row_id DESC
                 LIMIT 1) AS observed_relevance
        FROM predictions p
        JOIN prediction_scope_assignments psa ON p.prediction_id = psa.prediction_id
        {roster_clause}
        """,
        params,
    )
    rows = cur.fetchall()
    n = 0
    for row in rows:
        contradiction = 0.0  # retired; column kept for schema compat.
        # ingest sets latest_realization_score = normalize_relevance(
        # observed_relevance), so realization and new_evidence_relevance
        # are the same number by construction.
        realization = normalize_relevance(row["observed_relevance"])
        status = prediction_status(realization)
        for window_id, _days in WINDOWS:
            conn.execute(
                """
                INSERT OR REPLACE INTO prediction_realization_snapshots (
                  prediction_id, scope_id, validation_date, window_id,
                  new_evidence_relevance, continuing_evidence_relevance,
                  observed_relevance, realization_score, contradiction_score,
                  observation_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["prediction_id"],
                    row["scope_id"],
                    as_of.isoformat(),
                    window_id,
                    realization,
                    0.0,
                    row["observed_relevance"],
                    realization,
                    contradiction,
                    status,
                ),
            )
            n += 1
        if not backfill:
            # Update latest_observation_status on assignment for convenience.
            # Skipped when backfilling: a past day's status must not
            # overwrite the current one.
            conn.execute(
                """
                UPDATE prediction_scope_assignments
                SET latest_observation_status = ?
                WHERE prediction_id = ? AND scope_id = ?
                """,
                (status, row["prediction_id"], row["scope_id"]),
            )
    return n
