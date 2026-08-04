"""Regression tests for ``app.src.score`` date handling.

Guards the 2026-07-28 hole: ``run_score()`` had no date parameter and
always stamped ``MAX(source_files.report_date)``, so a catch-up session
that ingested two days before scoring silently produced NO activity
rows for the earlier day — in ``topic_daily_activity``,
``category_daily_activity`` AND ``prediction_realization_snapshots``.

Every test runs against a temp-file SQLite seeded from a fresh
``app/src/schema.sql``. The live ``app/data/analytics.sqlite`` is NEVER
touched (``run_score`` opens its own connection, so these need a real
file rather than ``:memory:``).

Coverage:

  1. A catch-up run (two dates ingested, one score call) leaves the
     earlier date unscored — and ``backfill_missing`` heals it.
  2. ``run_score(as_of=...)`` stamps the requested date, not the max.
  3. A backfill reads relevance AS OF that date, not current state.
  4. A backfill excludes assignments minted after that date.
  5. A backfill does not clobber ``latest_observation_status``.
  6. ``run_score`` refuses a date the corpus has no report for.
  7. ``unscored_dates`` ignores the pre-series backfill corpus.
  8. Carry-forward: a prediction with no bridge on a date still gets a
     snapshot, carrying its last observed relevance (documented
     behaviour — see ``_snapshot_predictions``).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.src import db as _db
from app.src.score import backfill_missing, run_score, unscored_dates


REPO_ROOT_REAL = Path(__file__).resolve().parents[2]
SCHEMA_SQL = (REPO_ROOT_REAL / "app" / "src" / "schema.sql").read_text(
    encoding="utf-8"
)

D0 = "2026-07-26"
D1 = "2026-07-28"  # the day that went missing
D2 = "2026-07-29"  # the catch-up day that ran alongside it


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def dbfile(tmp_path: Path) -> Path:
    """Temp-file SQLite seeded from schema.sql (never the live DB)."""
    p = tmp_path / "analytics.sqlite"
    c = sqlite3.connect(str(p))
    c.executescript(SCHEMA_SQL)
    # schema.sql stamps the seeded themes with CURRENT_TIMESTAMP. The
    # live DB's seeded themes date from 2026-06-09, i.e. before any date
    # under test; backdate them so the fixture matches.
    c.execute("UPDATE themes SET created_at = '2026-06-09T00:00:00Z'")
    c.commit()
    c.close()
    assert p != _db.db_path(), "test must never target the live DB"
    return p


def _conn(p: Path) -> sqlite3.Connection:
    c = sqlite3.connect(str(p))
    c.row_factory = sqlite3.Row
    return c


def _add_report(c: sqlite3.Connection, date_iso: str) -> str:
    sfid = f"sf.{date_iso}"
    c.execute(
        "INSERT INTO source_files(source_file_id, path, file_type, report_date) "
        "VALUES (?, ?, 'daily_report', ?)",
        (sfid, f"app/sourcedata/{date_iso}/predictions.json", date_iso),
    )
    return sfid


def _add_prediction(
    c: sqlite3.Connection,
    pid: str,
    *,
    prediction_date: str,
    assigned_at: str | None = None,
) -> None:
    c.execute(
        "INSERT INTO predictions(prediction_id, prediction_summary, prediction_date) "
        "VALUES (?, ?, ?)",
        (pid, f"summary for {pid}", prediction_date),
    )
    for scope_id in ("tech", "business"):
        if assigned_at is None:
            c.execute(
                "INSERT INTO prediction_scope_assignments"
                "(prediction_id, scope_id) VALUES (?, ?)",
                (pid, scope_id),
            )
        else:
            c.execute(
                "INSERT INTO prediction_scope_assignments"
                "(prediction_id, scope_id, assigned_at) VALUES (?, ?, ?)",
                (pid, scope_id, assigned_at),
            )


def _add_validation(
    c: sqlite3.Connection,
    *,
    sfid: str,
    date_iso: str,
    pid: str,
    relevance: int,
) -> None:
    c.execute(
        "INSERT INTO validation_rows"
        "(validation_row_id, source_file_id, validation_date, prediction_id, "
        " prediction_summary, observed_relevance) VALUES (?, ?, ?, ?, ?, ?)",
        (f"vr.{pid}.{date_iso}", sfid, date_iso, pid, f"summary for {pid}", relevance),
    )


def _snapshot_dates(p: Path) -> dict[str, int]:
    c = _conn(p)
    try:
        return {
            r["validation_date"]: r["c"]
            for r in c.execute(
                "SELECT validation_date, COUNT(*) c "
                "FROM prediction_realization_snapshots GROUP BY 1"
            )
        }
    finally:
        c.close()


def _activity_dates(p: Path) -> set[str]:
    c = _conn(p)
    try:
        return {
            r["activity_date"]
            for r in c.execute("SELECT DISTINCT activity_date FROM topic_daily_activity")
        }
    finally:
        c.close()


@pytest.fixture()
def catch_up_db(dbfile: Path) -> Path:
    """D0 already scored; D1 + D2 both ingested but not yet scored.

    Mirrors 2026-07-29, when 2026-07-28's sourcedata was ingested at
    15:43 and 2026-07-29's at 16:21, with the only score run at 18:26.
    """
    c = _conn(dbfile)
    try:
        sf0 = _add_report(c, D0)
        _add_prediction(c, "prediction.aaa", prediction_date=D0, assigned_at=D0)
        _add_validation(c, sfid=sf0, date_iso=D0, pid="prediction.aaa", relevance=4)
        c.commit()
    finally:
        c.close()

    # Day 0 scores normally — this establishes the series.
    run_score(dbfile)

    c = _conn(dbfile)
    try:
        sf1 = _add_report(c, D1)
        sf2 = _add_report(c, D2)
        _add_prediction(c, "prediction.bbb", prediction_date=D1, assigned_at=D1)
        _add_prediction(c, "prediction.ccc", prediction_date=D2, assigned_at=D2)
        # aaa gets a strong bridge on D1 and a weak one on D2 — so an
        # as-of read of D1 must differ from current state.
        _add_validation(c, sfid=sf1, date_iso=D1, pid="prediction.aaa", relevance=5)
        _add_validation(c, sfid=sf2, date_iso=D2, pid="prediction.aaa", relevance=1)
        _add_validation(c, sfid=sf1, date_iso=D1, pid="prediction.bbb", relevance=3)
        c.commit()
    finally:
        c.close()
    return dbfile


# ---------------------------------------------------------------------------
# 1. The regression itself
# ---------------------------------------------------------------------------


def test_catch_up_day_is_skipped_then_healed(catch_up_db: Path):
    """Two dates ingested, one score call → the earlier date is lost."""
    result = run_score(catch_up_db)
    assert result["as_of"] == D2

    snaps = _snapshot_dates(catch_up_db)
    assert snaps.get(D2, 0) > 0
    assert D1 not in snaps, "the un-fixed failure mode: D1 silently has no rows"
    assert D1 not in _activity_dates(catch_up_db)

    # The hole is an in-series gap, so update's self-heal must find it.
    assert unscored_dates(_conn(catch_up_db)) == [D1]

    healed = backfill_missing(catch_up_db)
    assert [h["as_of"] for h in healed] == [D1]
    assert all(h["backfill"] for h in healed)

    snaps = _snapshot_dates(catch_up_db)
    assert snaps.get(D1, 0) > 0
    assert D1 in _activity_dates(catch_up_db)
    assert unscored_dates(_conn(catch_up_db)) == []


def test_explicit_date_stamps_that_date(catch_up_db: Path):
    """``as_of`` wins over MAX(report_date)."""
    result = run_score(catch_up_db, as_of=D1)
    assert result["as_of"] == D1
    assert result["backfill"] is True

    snaps = _snapshot_dates(catch_up_db)
    assert snaps.get(D1, 0) > 0
    assert D2 not in snaps, "scoring D1 must not also write D2"


# ---------------------------------------------------------------------------
# 2. Backfills must reconstruct the day, not stamp today onto it
# ---------------------------------------------------------------------------


def test_backfill_uses_as_of_relevance_not_current_state(catch_up_db: Path):
    """aaa was 5 on D1 and 1 on D2 — D1's snapshot must say 5."""
    run_score(catch_up_db)  # current day: D2, leaves state at relevance 1
    run_score(catch_up_db, as_of=D1)

    c = _conn(catch_up_db)
    try:
        rows = {
            r["validation_date"]: r["observed_relevance"]
            for r in c.execute(
                "SELECT validation_date, observed_relevance "
                "FROM prediction_realization_snapshots "
                "WHERE prediction_id='prediction.aaa' AND scope_id='tech' "
                "AND window_id='7d'"
            )
        }
    finally:
        c.close()
    assert rows[D1] == 5, "D1 must be scored from D1's evidence"
    assert rows[D2] == 1


def test_backfill_excludes_assignments_created_later(catch_up_db: Path):
    """ccc was assigned on D2 — it must not appear in D1's snapshot."""
    run_score(catch_up_db, as_of=D1)

    c = _conn(catch_up_db)
    try:
        pids = {
            r["prediction_id"]
            for r in c.execute(
                "SELECT DISTINCT prediction_id FROM prediction_realization_snapshots "
                "WHERE validation_date = ?",
                (D1,),
            )
        }
    finally:
        c.close()
    assert "prediction.aaa" in pids
    assert "prediction.bbb" in pids
    assert "prediction.ccc" not in pids, "roster must be as-of, not current"


def test_backfill_includes_predictions_born_on_that_day(catch_up_db: Path):
    """A day ingested LATE stamps its own predictions with a later
    ``assigned_at``. Those must still appear on the day they belong to —
    3 of the 33 predictions bridged on 2026-07-28 were lost this way.
    """
    c = _conn(catch_up_db)
    try:
        # Born on D1, but its assignment was only minted on D2 (the
        # catch-up session ingested D1 a day late).
        _add_prediction(c, "prediction.late", prediction_date=D1, assigned_at=D2)
        c.commit()
    finally:
        c.close()

    run_score(catch_up_db, as_of=D1)

    c = _conn(catch_up_db)
    try:
        pids = {
            r["prediction_id"]
            for r in c.execute(
                "SELECT DISTINCT prediction_id FROM prediction_realization_snapshots "
                "WHERE validation_date = ?",
                (D1,),
            )
        }
    finally:
        c.close()
    assert "prediction.late" in pids, "a day must include its own new predictions"
    assert "prediction.ccc" not in pids, "but not predictions born after it"


def test_backfill_excludes_themes_created_later(catch_up_db: Path):
    """The weekly review promotes new themes; an old day never saw them."""
    c = _conn(catch_up_db)
    try:
        c.execute(
            "INSERT INTO themes(theme_id, scope_id, category_id, canonical_label, "
            "status, created_at) VALUES ('tech.brand_new', 'tech', 'tech.models', "
            "'Brand New', 'active', ?)",
            (f"{D2}T10:00:00Z",),
        )
        c.commit()
    finally:
        c.close()

    run_score(catch_up_db, as_of=D1)
    run_score(catch_up_db)  # D2

    c = _conn(catch_up_db)
    try:
        def themes_on(d: str) -> set[str]:
            return {
                r["theme_id"]
                for r in c.execute(
                    "SELECT DISTINCT theme_id FROM topic_daily_activity "
                    "WHERE activity_date = ?",
                    (d,),
                )
            }

        assert "tech.brand_new" not in themes_on(D1)
        assert "tech.brand_new" in themes_on(D2)
    finally:
        c.close()


def test_backfill_survives_a_rebuilt_themes_table(catch_up_db: Path):
    """On a DB rebuilt from schema.sql every theme is newer than every
    past date. The created_at filter must stand down rather than score
    the day with zero themes — a silent empty is worse than the hole
    this whole change exists to close.
    """
    c = _conn(catch_up_db)
    try:
        c.execute("UPDATE themes SET created_at = '2026-09-01T00:00:00Z'")
        c.commit()
    finally:
        c.close()

    result = run_score(catch_up_db, as_of=D1)
    assert result["backfill"] is True
    assert result["theme_activity_rows"] > 0, "rebuilt DB scored a day with no themes"
    assert D1 in _activity_dates(catch_up_db)


def test_backfill_does_not_clobber_latest_observation_status(catch_up_db: Path):
    """A past day's status must not overwrite the assignment's current one."""
    run_score(catch_up_db)  # D2: aaa at relevance 1 -> no_signal
    c = _conn(catch_up_db)
    try:
        before = c.execute(
            "SELECT latest_observation_status s FROM prediction_scope_assignments "
            "WHERE prediction_id='prediction.aaa' AND scope_id='tech'"
        ).fetchone()["s"]
    finally:
        c.close()
    assert before == "no_signal"

    run_score(catch_up_db, as_of=D1)  # D1: aaa at relevance 5 -> supported

    c = _conn(catch_up_db)
    try:
        after = c.execute(
            "SELECT latest_observation_status s FROM prediction_scope_assignments "
            "WHERE prediction_id='prediction.aaa' AND scope_id='tech'"
        ).fetchone()["s"]
    finally:
        c.close()
    assert after == before, "backfill leaked a past day's status into current state"


# ---------------------------------------------------------------------------
# 3. Guards
# ---------------------------------------------------------------------------


def test_score_rejects_a_date_with_no_report(catch_up_db: Path):
    with pytest.raises(ValueError, match="no daily_report source file"):
        run_score(catch_up_db, as_of="2026-07-27")


def test_unscored_dates_ignores_pre_series_corpus(dbfile: Path):
    """~50 daily reports predate scoring; re-scoring them invents history."""
    c = _conn(dbfile)
    try:
        for d in ("2026-04-19", "2026-04-20", D0, D1):
            _add_report(c, d)
        _add_prediction(c, "prediction.aaa", prediction_date=D0, assigned_at=D0)
        c.commit()
    finally:
        c.close()

    run_score(dbfile, as_of=D0)  # series starts at D0

    # D1 is an interior gap -> healed. The April dates lead the series
    # and must be left alone.
    assert unscored_dates(_conn(dbfile)) == [D1]


# ---------------------------------------------------------------------------
# 4. Carry-forward is intentional — pin it so it can't drift silently
# ---------------------------------------------------------------------------


def test_relevance_carries_forward_on_days_with_no_bridge(catch_up_db: Path):
    """bbb's only bridge is on D1; D2 still gets a snapshot carrying it.

    This is the documented step-wise behaviour: a flat run means "no new
    evidence since D1", NOT daily re-confirmation. If this test ever
    fails, the series semantics changed and every consumer that reads a
    flat run needs revisiting.
    """
    run_score(catch_up_db)  # D2

    c = _conn(catch_up_db)
    try:
        row = c.execute(
            "SELECT observed_relevance, realization_score, observation_status "
            "FROM prediction_realization_snapshots "
            "WHERE prediction_id='prediction.bbb' AND scope_id='tech' "
            "AND window_id='7d' AND validation_date=?",
            (D2,),
        ).fetchone()
    finally:
        c.close()
    assert row is not None, "predictions with no bridge that day still get a row"
    assert row["observed_relevance"] == 3, "carried forward from D1"
    assert row["realization_score"] == pytest.approx(0.6)
    assert row["observation_status"] == "weakly_supported"
