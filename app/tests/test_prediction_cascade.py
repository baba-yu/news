"""Regression tests for prediction re-key debris.

``prediction_id`` hashes the prediction body, so editing a body mints a
new id. Ingest is pure upsert with no DELETE, so historically the
pre-edit rows survived in every child table — 32 orphan rows measured
against the live DB on 2026-08-03, silently inflating any statistic
computed off those tables without a join back to ``predictions``.

Covers:

  * :func:`app.src.prediction_cascade.count_orphans` reports a complete,
    enumerable key set (zeros included).
  * :func:`app.src.prediction_cascade.sweep_orphans` clears all four
    prediction-keyed tables **and** the ``needs_tasks`` join-orphan case
    that a prediction_id-keyed sweep misses.
  * The sweep's internal ordering: a task whose parent need is itself
    swept in the same pass is removed in that same pass.
  * :func:`app.src.prediction_cascade.purge_prediction` cascades
    completely and re-points the content-bearing ``validation_rows``.
  * ``_upsert_candidate`` keys on the prediction *slot*, so a body edit
    UPDATES the candidate row instead of minting a duplicate — the bug
    that corrupted the "≥3 pending hits" promotion signal.
  * A candidate's DB-owned ``status`` survives re-ingest.
  * :mod:`app.skills.migrate_candidate_keys` agrees with the ingest hash
    and is a fixed point.
  * The post-update validator fails on orphan debris and passes clean.

Each test uses an isolated in-memory DB seeded from ``app/src/schema.sql``
so the real ``app/data/analytics.sqlite`` is never touched.
"""

from __future__ import annotations

import importlib
import json
import sqlite3
from pathlib import Path

import pytest

from app.skills.ingest_sourcedata import ingest_day
from app.skills.post_update_validation import _check_orphan_rows
from app.src import prediction_cascade
from app.src.ingest import _hash_id

# The migration follows the repo's numbered one-shot convention
# (app/migrations/01_rename_eli14_to_plain_language.py), and a
# digit-leading module name is not a valid import statement target.
_migration = importlib.import_module("app.migrations.02_rekey_theme_candidates")
new_candidate_id = _migration.new_candidate_id
migrate_plan = _migration.plan

REPO_ROOT_REAL = Path(__file__).resolve().parents[2]
SCHEMA_SQL = (REPO_ROOT_REAL / "app" / "src" / "schema.sql").read_text(
    encoding="utf-8"
)

SAMPLE_DATE = "2099-03-14"
LIVE_PID = "prediction.live000000000"
DEAD_PID = "prediction.dead000000000"


@pytest.fixture()
def conn() -> sqlite3.Connection:
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA_SQL)
    yield c
    c.close()


@pytest.fixture()
def fake_repo(tmp_path: Path) -> Path:
    (tmp_path / "app" / "sourcedata").mkdir(parents=True)
    return tmp_path


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _fk_off(conn: sqlite3.Connection) -> None:
    """Allow this test to write the debris the way it was actually written.

    ``schema.sql`` turns foreign keys ON, so orphan rows cannot be
    inserted through it. The historical ``design/_scratch/rekey_*.py``
    scripts opened the DB with a bare ``sqlite3.connect()``, where FK
    enforcement defaults OFF — which is exactly why their
    ``DELETE FROM predictions`` was never refused and left the children
    dangling. Reproducing that here is the point of the fixture.

    ``PRAGMA foreign_keys`` is a no-op inside a transaction, so commit
    whatever the caller has open before flipping it.
    """
    conn.commit()
    conn.execute("PRAGMA foreign_keys = OFF")


def _clear_themes(conn: sqlite3.Connection) -> None:
    """Guarantee the theme matcher misses, so every prediction yields a candidate.

    ``schema.sql`` seeds 18 themes and ``_pick_theme_per_scope`` records a
    ``theme_candidate`` only when no theme matches. Without this, whether a
    test exercises the candidate path at all depends on whether its sample
    prose happens to collide with a seeded theme's keywords — which is not
    something these tests should be asserting on.
    """
    conn.execute("DELETE FROM themes")
    conn.commit()


def _predictions_payload(body: str, *, title: str = "Demo title") -> dict:
    return {
        "date": SAMPLE_DATE,
        "predictions": [
            {
                "id": "prediction.demo01",
                "title": title,
                "body": body,
                "reasoning": {
                    "because": "observed precondition",
                    "given": "structural force",
                    "so_that": "consequence",
                    "landing": "by Q4 2099",
                    "plain_language": "in plain English, the thing happens",
                },
                "summary": "mid-tier summary of the prediction.",
            },
        ],
    }


def _seed_pair(conn: sqlite3.Connection) -> None:
    """Insert one live prediction and child rows for both a live and a dead id."""
    _fk_off(conn)
    conn.execute(
        "INSERT INTO predictions (prediction_id, prediction_summary, "
        "prediction_date, source_row_index) VALUES (?, ?, ?, ?)",
        (LIVE_PID, "live body", SAMPLE_DATE, 0),
    )
    for tag, pid in (("live", LIVE_PID), ("dead", DEAD_PID)):
        conn.execute(
            "INSERT INTO prediction_scope_assignments "
            "(prediction_id, scope_id, theme_id) VALUES (?, 'tech', 'tech.x')",
            (pid,),
        )
        conn.execute(
            "INSERT INTO prediction_evidence_links (prediction_id, evidence_id, "
            "scope_id, support_direction, evidence_recency_type, validation_date) "
            "VALUES (?, 'evidence.e1', 'tech', 'support', 'new', ?)",
            (pid, SAMPLE_DATE),
        )
        conn.execute(
            "INSERT INTO theme_candidates (candidate_id, scope_id, "
            "suggested_theme_label, origin_prediction_id) VALUES (?, 'tech', ?, ?)",
            (f"candidate.{tag}", f"label for {tag}", pid),
        )
        conn.execute(
            "INSERT INTO prediction_needs (need_id, prediction_id, actor, job) "
            "VALUES (?, ?, 'actor', 'job')",
            (f"need.{tag}", pid),
        )
        conn.execute(
            "INSERT INTO needs_tasks (task_id, need_id, what_text) "
            "VALUES (?, ?, 'do the thing')",
            (f"task.{tag}", f"need.{tag}"),
        )
    conn.commit()


# ---------------------------------------------------------------------------
# count_orphans / sweep_orphans
# ---------------------------------------------------------------------------


def test_count_orphans_reports_every_key_including_zeros(conn):
    """A missing key must be a bug, not an implicit 'no orphans here'."""
    counts = prediction_cascade.count_orphans(conn)
    assert set(counts) == set(prediction_cascade.ORPHAN_KEYS)
    assert all(v == 0 for v in counts.values()), counts


def test_sweep_removes_orphans_and_spares_live_rows(conn):
    _seed_pair(conn)

    before = prediction_cascade.count_orphans(conn)
    # One orphan row per table for DEAD_PID. needs_tasks is 0 *before* the
    # sweep because its parent need still exists at this point — it only
    # becomes an orphan once prediction_needs is swept.
    assert before["prediction_scope_assignments.prediction_id"] == 1
    assert before["prediction_evidence_links.prediction_id"] == 1
    assert before["theme_candidates.origin_prediction_id"] == 1
    assert before["prediction_needs.prediction_id"] == 1
    assert before["needs_tasks.need_id"] == 0

    removed = prediction_cascade.sweep_orphans(conn)
    conn.commit()

    assert removed["prediction_scope_assignments.prediction_id"] == 1
    assert removed["prediction_evidence_links.prediction_id"] == 1
    assert removed["theme_candidates.origin_prediction_id"] == 1
    assert removed["prediction_needs.prediction_id"] == 1
    # The ordering guarantee: prediction_needs is swept before the
    # needs_tasks join sweep, so the task orphaned by this very pass is
    # removed in the same pass rather than surviving until the next run.
    assert removed["needs_tasks.need_id"] == 1

    assert prediction_cascade.count_orphans(conn) == {
        k: 0 for k in prediction_cascade.ORPHAN_KEYS
    }

    # Live rows untouched.
    for table, column in prediction_cascade.PREDICTION_CHILD_TABLES:
        n = conn.execute(
            f"SELECT COUNT(*) FROM {table} WHERE {column} = ?", (LIVE_PID,)
        ).fetchone()[0]
        assert n == 1, f"sweep destroyed the live row in {table}"
    assert (
        conn.execute(
            "SELECT COUNT(*) FROM needs_tasks WHERE need_id = 'need.live'"
        ).fetchone()[0]
        == 1
    )
    assert (
        conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0] == 1
    )


def test_needs_tasks_join_orphan_is_swept_without_any_prediction_id(conn):
    """needs_tasks has no prediction_id column — it orphans via need_id only.

    A sweep keyed on prediction_id misses this case entirely, which is why
    the join condition is a separate step.
    """
    _fk_off(conn)
    conn.execute(
        "INSERT INTO needs_tasks (task_id, need_id, what_text) "
        "VALUES ('task.solo', 'need.gone', 'orphaned task')"
    )
    conn.commit()
    assert "prediction_id" not in {
        r["name"]
        for r in conn.execute("PRAGMA table_info(needs_tasks)").fetchall()
    }

    assert prediction_cascade.count_orphans(conn)["needs_tasks.need_id"] == 1
    removed = prediction_cascade.sweep_orphans(conn)
    assert removed["needs_tasks.need_id"] == 1
    assert conn.execute("SELECT COUNT(*) FROM needs_tasks").fetchone()[0] == 0


def test_sweep_is_idempotent(conn):
    _seed_pair(conn)
    prediction_cascade.sweep_orphans(conn)
    second = prediction_cascade.sweep_orphans(conn)
    assert all(v == 0 for v in second.values()), second


# ---------------------------------------------------------------------------
# purge_prediction
# ---------------------------------------------------------------------------


def test_purge_prediction_cascades_to_every_child_table(conn):
    """The helper a re-key script should call instead of a hand-rolled list."""
    _seed_pair(conn)
    conn.execute(
        "INSERT INTO predictions (prediction_id, prediction_summary, "
        "prediction_date, source_row_index) VALUES (?, ?, ?, ?)",
        (DEAD_PID, "dead body", SAMPLE_DATE, 0),
    )
    conn.commit()

    removed = prediction_cascade.purge_prediction(conn, DEAD_PID)
    conn.commit()

    assert removed["predictions"] == 1
    for table, column in prediction_cascade.PREDICTION_CHILD_TABLES:
        assert removed[f"{table}.{column}"] == 1, (table, removed)
        assert (
            conn.execute(
                f"SELECT COUNT(*) FROM {table} WHERE {column} = ?", (DEAD_PID,)
            ).fetchone()[0]
            == 0
        )
    assert removed["needs_tasks.need_id"] == 1
    # And it leaves no debris behind — the whole point.
    assert prediction_cascade.count_orphans(conn) == {
        k: 0 for k in prediction_cascade.ORPHAN_KEYS
    }


def test_purge_prediction_repoints_validation_rows(conn):
    """validation_rows carries published bridge text — re-point, never delete."""
    _seed_pair(conn)
    conn.execute(
        "INSERT INTO predictions (prediction_id, prediction_summary, "
        "prediction_date, source_row_index) VALUES (?, ?, ?, ?)",
        (DEAD_PID, "dead body", SAMPLE_DATE, 0),
    )
    conn.execute(
        "INSERT INTO validation_rows (validation_row_id, source_file_id, "
        "validation_date, prediction_id, prediction_summary, bridge_text) "
        "VALUES ('validation.v1', 'source.s1', ?, ?, 'summary', "
        "'the bridge narrative')",
        (SAMPLE_DATE, DEAD_PID),
    )
    conn.commit()

    prediction_cascade.purge_prediction(conn, DEAD_PID, replacement_id=LIVE_PID)
    conn.commit()

    row = conn.execute(
        "SELECT prediction_id, bridge_text FROM validation_rows "
        "WHERE validation_row_id = 'validation.v1'"
    ).fetchone()
    assert row is not None, "purge deleted published bridge content"
    assert row["prediction_id"] == LIVE_PID
    assert row["bridge_text"] == "the bridge narrative"


def test_purge_prediction_detaches_validation_rows_without_replacement(conn):
    _fk_off(conn)
    conn.execute(
        "INSERT INTO predictions (prediction_id, prediction_summary, "
        "prediction_date, source_row_index) VALUES (?, ?, ?, ?)",
        (DEAD_PID, "dead body", SAMPLE_DATE, 0),
    )
    conn.execute(
        "INSERT INTO validation_rows (validation_row_id, source_file_id, "
        "validation_date, prediction_id, prediction_summary) "
        "VALUES ('validation.v1', 'source.s1', ?, ?, 'summary')",
        (SAMPLE_DATE, DEAD_PID),
    )
    conn.commit()

    prediction_cascade.purge_prediction(conn, DEAD_PID)
    conn.commit()

    row = conn.execute(
        "SELECT prediction_id FROM validation_rows "
        "WHERE validation_row_id = 'validation.v1'"
    ).fetchone()
    assert row is not None
    assert row["prediction_id"] is None
    assert prediction_cascade.count_orphans(conn) == {
        k: 0 for k in prediction_cascade.ORPHAN_KEYS
    }


# ---------------------------------------------------------------------------
# theme_candidates re-key stability
# ---------------------------------------------------------------------------


def test_body_edit_updates_candidate_instead_of_duplicating(fake_repo, conn):
    """The promotion-signal bug: one prediction must yield one candidate row.

    The 2026-08-02 theme review found the only cluster that appeared to
    clear the "≥3 pending hits" threshold was 3 sha1 variants of a single
    prediction. Keying the candidate on the prediction *slot* rather than
    on the body-derived prediction_id is what prevents that.
    """
    _clear_themes(conn)
    pred_path = fake_repo / "app" / "sourcedata" / SAMPLE_DATE / "predictions.json"

    _write_json(pred_path, _predictions_payload("original body text"))
    ingest_day(conn, fake_repo, SAMPLE_DATE)

    first = conn.execute(
        "SELECT candidate_id, origin_prediction_id FROM theme_candidates "
        "WHERE scope_id = 'tech'"
    ).fetchall()
    assert len(first) == 1, f"expected 1 tech candidate, got {len(first)}"
    original_pid = first[0]["origin_prediction_id"]

    # Edit the body — this re-keys the prediction.
    _write_json(pred_path, _predictions_payload("edited body text — re-keyed"))
    ingest_day(conn, fake_repo, SAMPLE_DATE)

    pids = [
        r["prediction_id"]
        for r in conn.execute(
            "SELECT prediction_id FROM predictions WHERE prediction_date = ?",
            (SAMPLE_DATE,),
        ).fetchall()
    ]
    assert len(pids) == 2, "body edit should have minted a new prediction id"

    after = conn.execute(
        "SELECT candidate_id, origin_prediction_id FROM theme_candidates "
        "WHERE scope_id = 'tech'"
    ).fetchall()
    assert len(after) == 1, (
        f"body edit duplicated the theme candidate: {len(after)} rows — "
        "this is the bug that corrupted the promotion signal"
    )
    assert after[0]["candidate_id"] == first[0]["candidate_id"], (
        "candidate_id must be stable across a body edit"
    )
    assert after[0]["origin_prediction_id"] != original_pid, (
        "candidate should now point at the surviving prediction"
    )
    assert after[0]["origin_prediction_id"] in pids


def test_candidate_status_survives_reingest(fake_repo, conn):
    """`status` is DB-owned lifecycle state; a re-ingest must not reset it."""
    _clear_themes(conn)
    pred_path = fake_repo / "app" / "sourcedata" / SAMPLE_DATE / "predictions.json"
    _write_json(pred_path, _predictions_payload("original body text"))
    ingest_day(conn, fake_repo, SAMPLE_DATE)

    conn.execute(
        "UPDATE theme_candidates SET status = 'rejected' WHERE scope_id = 'tech'"
    )
    conn.commit()

    _write_json(pred_path, _predictions_payload("edited body text"))
    ingest_day(conn, fake_repo, SAMPLE_DATE)

    statuses = [
        r["status"]
        for r in conn.execute(
            "SELECT status FROM theme_candidates WHERE scope_id = 'tech'"
        ).fetchall()
    ]
    assert statuses == ["rejected"], (
        f"re-ingest resurrected a rejected candidate: {statuses}"
    )


def test_candidate_refreshes_wording_on_reingest(fake_repo, conn):
    """The upsert should still carry an edited title/body through."""
    _clear_themes(conn)
    pred_path = fake_repo / "app" / "sourcedata" / SAMPLE_DATE / "predictions.json"
    _write_json(pred_path, _predictions_payload("body one", title="First title"))
    ingest_day(conn, fake_repo, SAMPLE_DATE)

    _write_json(pred_path, _predictions_payload("body two", title="Second title"))
    ingest_day(conn, fake_repo, SAMPLE_DATE)

    row = conn.execute(
        "SELECT suggested_theme_label, suggested_description FROM theme_candidates "
        "WHERE scope_id = 'tech'"
    ).fetchone()
    assert row["suggested_theme_label"] == "Second title"
    assert row["suggested_description"].startswith("body two")


def test_distinct_slots_still_produce_distinct_candidates(fake_repo, conn):
    """Slot keying must not collapse genuinely different predictions.

    If it did, no real cluster could ever reach the promotion threshold.
    """
    _clear_themes(conn)
    payload = _predictions_payload("first body")
    payload["predictions"].append(
        {
            "id": "prediction.demo02",
            "title": "Second demo title",
            "body": "an entirely different prediction body",
            "reasoning": {
                "because": "b",
                "given": "g",
                "so_that": "s",
                "landing": "by Q4 2099",
                "plain_language": "p",
            },
            "summary": "second summary.",
        }
    )
    _write_json(
        fake_repo / "app" / "sourcedata" / SAMPLE_DATE / "predictions.json",
        payload,
    )
    ingest_day(conn, fake_repo, SAMPLE_DATE)

    rows = conn.execute(
        "SELECT candidate_id, origin_prediction_id FROM theme_candidates "
        "WHERE scope_id = 'tech'"
    ).fetchall()
    assert len(rows) == 2, (
        f"two distinct predictions should yield two candidates, got {len(rows)}"
    )
    assert len({r["candidate_id"] for r in rows}) == 2
    assert len({r["origin_prediction_id"] for r in rows}) == 2
    # Explicitly: slot 0 and slot 1 on the same date/scope are distinct keys.
    assert {r["candidate_id"] for r in rows} == {
        new_candidate_id("tech", SAMPLE_DATE, 0),
        new_candidate_id("tech", SAMPLE_DATE, 1),
    }


# ---------------------------------------------------------------------------
# migration
# ---------------------------------------------------------------------------


def test_migration_hash_matches_ingest_hash():
    """The migration duplicates the hash; the two must not drift apart."""
    assert new_candidate_id("tech", SAMPLE_DATE, 3) == _hash_id(
        "candidate", "tech", SAMPLE_DATE, "3"
    )


def test_migration_rekeys_old_scheme_rows_and_is_a_fixed_point(conn):
    conn.execute(
        "INSERT INTO predictions (prediction_id, prediction_summary, "
        "prediction_date, source_row_index) VALUES (?, ?, ?, ?)",
        (LIVE_PID, "live body", SAMPLE_DATE, 7),
    )
    old_id = _hash_id("candidate", "tech", LIVE_PID)
    conn.execute(
        "INSERT INTO theme_candidates (candidate_id, scope_id, "
        "suggested_theme_label, origin_prediction_id, status) "
        "VALUES (?, 'tech', 'label', ?, 'promoted')",
        (old_id, LIVE_PID),
    )
    conn.commit()

    p = migrate_plan(conn)
    assert p["rekey"] == [(old_id, new_candidate_id("tech", SAMPLE_DATE, 7))]
    assert p["already_new"] == 0

    _migration.apply_plan(conn, p)
    conn.commit()

    row = conn.execute("SELECT candidate_id, status FROM theme_candidates").fetchone()
    assert row["candidate_id"] == new_candidate_id("tech", SAMPLE_DATE, 7)
    assert row["status"] == "promoted", "migration must preserve DB-owned status"

    after = migrate_plan(conn)
    assert after["rekey"] == [] and after["merge"] == []
    assert after["already_new"] == 1


def test_migration_skips_orphan_candidates(conn):
    """An orphan candidate has no knowable slot — the sweep owns it, not this."""
    _fk_off(conn)
    conn.execute(
        "INSERT INTO theme_candidates (candidate_id, scope_id, "
        "suggested_theme_label, origin_prediction_id) "
        "VALUES ('candidate.orphan', 'tech', 'label', ?)",
        (DEAD_PID,),
    )
    conn.commit()
    p = migrate_plan(conn)
    assert p["skipped_orphan"] == ["candidate.orphan"]
    assert p["rekey"] == []


# ---------------------------------------------------------------------------
# validator
# ---------------------------------------------------------------------------


def test_validator_passes_on_clean_db(conn):
    _seed_pair(conn)
    prediction_cascade.sweep_orphans(conn)
    conn.commit()
    assert _check_orphan_rows(conn) == []


def test_validator_fails_and_names_every_offending_table(conn):
    _seed_pair(conn)
    errs = _check_orphan_rows(conn)
    assert errs, "validator passed on a DB with known orphan rows"
    joined = "\n".join(errs)
    for table in (
        "prediction_scope_assignments",
        "prediction_evidence_links",
        "theme_candidates",
        "prediction_needs",
    ):
        assert table in joined, f"validator did not report {table}"
    # The message has to be actionable — it names the offending id and the
    # remedy, not just a count.
    assert DEAD_PID in joined
    assert "sweep" in joined.lower()


def test_validator_catches_needs_tasks_join_orphan(conn):
    _fk_off(conn)
    conn.execute(
        "INSERT INTO needs_tasks (task_id, need_id, what_text) "
        "VALUES ('task.solo', 'need.gone', 'orphaned task')"
    )
    conn.commit()
    errs = _check_orphan_rows(conn)
    assert len(errs) == 1
    assert "needs_tasks" in errs[0]
    assert "task.solo" in errs[0]
