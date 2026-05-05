# Future Title Rename Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the `title` field of 52 EN predictions + 156 locale title cells (2026-04-19..2026-05-04, 16 days, 11 dates with 3 preds + 4 dates with 4 preds + 1 date with 3 preds) to comply with the post-2026-05-05 title rules (`design/scheduled/1_daily_update-writer-rules.md §compose-prediction Field-level rules`), then rerender + reingest + reexport so the dashboard reflects the new titles. Locale sub-agent count is still 48 (16 dates × 3 locales) — each (date, locale) sub-agent translates 3-or-4 titles in one call.

**Architecture:** Two-half pattern mirroring `super_backfill`. Python module `app/skills/rename_future_titles.py` is deterministic — extraction, schema validation, atomic writes, rerender orchestration. The parent agent (Claude) is the dispatch half — Task-tool sub-agent fan-out, reply collection, feeding results back to the Python module. Two sub-agent types: EN title rewriter (52× — one per prediction) and locale title translator (48× — one per (date, locale), 3-or-4 titles each depending on the date).

**Tech Stack:** Python 3.12, argparse-based CLI, pytest, existing in-repo schemas (`app.skills.sourcedata_schemas.PredictionsFile`), existing helpers (`app.skills.super_backfill.apply_locale`, `app.src.ingest._hash_id`).

**Spec:** `design/skills/rename-future-titles.md` (gitignored; tracked rationale at `moushiokuri-rename-future-titles.md`).

---

## File structure

**Created (commit 1 — code + tests):**

| Path | Responsibility | Approx LOC |
|---|---|---|
| `app/skills/rename_future_titles.py` | Single orchestrator module: 8 CLI subcommands + 10 helper functions | ~350 |
| `app/tests/test_rename_future_titles.py` | 6 tests covering parsers, idempotency, ID round-trip, body/summary preservation, rerender | ~250 |

**Modified during execution (data, not code):**

| Path | When |
|---|---|
| `app/sourcedata/<date>/predictions.json` × 16 | Phase 2 (EN apply) |
| `app/sourcedata/locales/<date>/<locale>/predictions.json` × 48 | Phase 3 (locale apply) |
| `report/<locale>/news-YYYYMMDD.md` × 64 | Phase 4 (rerender) |
| `docs/data/graph-{tech,business,mix}.json` | Phase 4 (export) |
| `app/data/research.db` (gitignored) | Phase 4 (ingest) |

**Reference (read-only, do NOT modify):**

| Path | Why relevant |
|---|---|
| `app/skills/super_backfill.py:467` | `apply_locale(repo_root, date, locale, "predictions", payload)` for atomic locale writes |
| `app/skills/super_backfill.py:_atomic_write_json` | Pattern for atomic JSON writes |
| `app/skills/sourcedata_schemas.py` | `PredictionsFile.from_dict(payload)` schema validator |
| `app/src/ingest.py:80` | `_hash_id(prefix, *parts)` recipe: SHA-1 over `"||".join(parts)`, first 16 hex |
| `app/src/ingest.py:298` | Reference label uses param name `prediction_summary` but **the field actually passed is `body`** — see `app/skills/migrate_to_sourcedata.py:131` (`_stable_prediction_id(date_iso, body)`) which states the canonical recipe. Verified empirically: 52/52 prediction IDs match `sha1(date \|\| body)[:16]`, none match `summary`. |
| `design/scheduled/1_daily_update-writer-rules.md` (lines 1-50) | Title rules — inlined verbatim into EN sub-agent bundles |
| `design/skills/locale-fanout.md §Translation contract (JSON-side)` | Locale rules — inlined into locale sub-agent bundles |

---

## Phase 1: Build orchestrator + tests

**Goal of this phase:** Ship `app/skills/rename_future_titles.py` and `app/tests/test_rename_future_titles.py` with all tests passing. No data changes. Single commit at the end.

**Test strategy:** TDD. For each function, write the test first, run it (expect failure), implement minimum code, run it again (expect pass), then move to the next. Tests use a `tmp_path` fixture to copy real sourcedata for write-isolation.

### Task 1: Module skeleton + constants

**Files:**
- Create: `app/skills/rename_future_titles.py`

- [ ] **Step 1: Create the file with module docstring, imports, and `_TARGET_DATES`**

```python
"""One-shot backfill: rewrite future prediction titles to comply with
post-2026-05-05 title rules.

Spec: ``design/skills/rename-future-titles.md`` (gitignored; the tracked
rationale is ``moushiokuri-rename-future-titles.md`` at repo root).

Two-half pattern (mirrors ``super_backfill``):
  * Python (this module): extraction, schema validation, atomic writes,
    rerender orchestration.
  * Parent agent (Claude): Task-tool sub-agent dispatch, reply collection,
    feeding replies back to ``apply-en`` / ``apply-locale``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# Fixed scope: 16 days × 3 predictions = 48 EN entries (one-shot backfill).
_TARGET_DATES: list[str] = [
    (date(2026, 4, 19) + timedelta(days=i)).isoformat() for i in range(16)
]
assert _TARGET_DATES[0] == "2026-04-19"
assert _TARGET_DATES[-1] == "2026-05-04"
assert len(_TARGET_DATES) == 16

_LOCALES: tuple[str, ...] = ("ja", "es", "fil")
```

- [ ] **Step 2: Verify module imports cleanly**

Run: `python -c "import app.skills.rename_future_titles as m; print(len(m._TARGET_DATES))"`
Expected: `16`

### Task 2: `parse_en_reply` (TDD)

**Files:**
- Modify: `app/skills/rename_future_titles.py`
- Create: `app/tests/test_rename_future_titles.py`

- [ ] **Step 1: Create test file with first test**

```python
"""Tests for app.skills.rename_future_titles."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from app.skills import rename_future_titles as rft


def test_parse_en_reply_ok():
    out = rft.parse_en_reply("OK prediction.abc123 New subject does X by Q4 2026")
    assert out == {
        "status": "OK",
        "pid": "prediction.abc123",
        "new_title": "New subject does X by Q4 2026",
    }


def test_parse_en_reply_keep():
    out = rft.parse_en_reply("KEEP prediction.abc123")
    assert out == {"status": "KEEP", "pid": "prediction.abc123", "new_title": None}


def test_parse_en_reply_fail():
    out = rft.parse_en_reply("FAIL prediction.abc123 body is empty")
    assert out == {
        "status": "FAIL",
        "pid": "prediction.abc123",
        "reason": "body is empty",
    }


def test_parse_en_reply_strips_trailing_whitespace():
    out = rft.parse_en_reply("OK prediction.abc123 Title  \n")
    assert out["new_title"] == "Title"


def test_parse_en_reply_malformed_raises():
    with pytest.raises(ValueError):
        rft.parse_en_reply("garbage")
    with pytest.raises(ValueError):
        rft.parse_en_reply("OK")
    with pytest.raises(ValueError):
        rft.parse_en_reply("KEEP prediction.abc extra-token")
```

- [ ] **Step 2: Run tests, expect failure**

Run: `python -m pytest app/tests/test_rename_future_titles.py::test_parse_en_reply_ok -v`
Expected: FAIL with `AttributeError: module 'app.skills.rename_future_titles' has no attribute 'parse_en_reply'`

- [ ] **Step 3: Implement `parse_en_reply` in `app/skills/rename_future_titles.py`**

Append to the module:

```python
def parse_en_reply(line: str) -> dict:
    """Parse a single EN sub-agent reply line.

    Returns one of:
      * ``{"status": "OK", "pid": ..., "new_title": ...}``
      * ``{"status": "KEEP", "pid": ..., "new_title": None}``
      * ``{"status": "FAIL", "pid": ..., "reason": ...}``

    Raises ``ValueError`` for malformed input.
    """
    line = line.rstrip()
    if not line:
        raise ValueError("empty reply")
    if line.startswith("OK "):
        parts = line.split(" ", 2)
        if len(parts) != 3:
            raise ValueError(f"OK reply missing title: {line!r}")
        return {"status": "OK", "pid": parts[1], "new_title": parts[2].rstrip()}
    if line.startswith("KEEP "):
        parts = line.split(" ")
        if len(parts) != 2:
            raise ValueError(f"KEEP reply must be exactly 2 tokens: {line!r}")
        return {"status": "KEEP", "pid": parts[1], "new_title": None}
    if line.startswith("FAIL "):
        parts = line.split(" ", 2)
        if len(parts) != 3:
            raise ValueError(f"FAIL reply missing reason: {line!r}")
        return {"status": "FAIL", "pid": parts[1], "reason": parts[2]}
    raise ValueError(f"unrecognized reply: {line!r}")
```

- [ ] **Step 4: Run tests, expect pass**

Run: `python -m pytest app/tests/test_rename_future_titles.py -v -k parse_en_reply`
Expected: All 5 tests PASS.

### Task 3: `parse_locale_reply` (TDD)

**Files:**
- Modify: `app/tests/test_rename_future_titles.py`
- Modify: `app/skills/rename_future_titles.py`

- [ ] **Step 1: Append tests**

```python
def test_parse_locale_reply_ok():
    text = '```json\n{"prediction.a": "ロケール題", "prediction.b": "別の題", "prediction.c": "三題"}\n```'
    expected_pids = ["prediction.a", "prediction.b", "prediction.c"]
    out = rft.parse_locale_reply(text, expected_pids)
    assert out == {
        "prediction.a": "ロケール題",
        "prediction.b": "別の題",
        "prediction.c": "三題",
    }


def test_parse_locale_reply_no_fence():
    # Bare JSON object without code fence is also accepted.
    text = '{"prediction.a": "x", "prediction.b": "y", "prediction.c": "z"}'
    out = rft.parse_locale_reply(text, ["prediction.a", "prediction.b", "prediction.c"])
    assert out["prediction.a"] == "x"


def test_parse_locale_reply_missing_pid_raises():
    text = '{"prediction.a": "x", "prediction.b": "y"}'
    with pytest.raises(ValueError, match="missing pid"):
        rft.parse_locale_reply(text, ["prediction.a", "prediction.b", "prediction.c"])


def test_parse_locale_reply_extra_pid_raises():
    text = '{"prediction.a": "x", "prediction.b": "y", "prediction.c": "z", "prediction.d": "w"}'
    with pytest.raises(ValueError, match="unexpected pid"):
        rft.parse_locale_reply(text, ["prediction.a", "prediction.b", "prediction.c"])


def test_parse_locale_reply_non_json_raises():
    with pytest.raises(ValueError):
        rft.parse_locale_reply("not json at all", ["prediction.a"])
```

- [ ] **Step 2: Run, expect failure (`parse_locale_reply` undefined)**

Run: `python -m pytest app/tests/test_rename_future_titles.py -v -k parse_locale_reply`
Expected: FAIL with AttributeError.

- [ ] **Step 3: Implement `parse_locale_reply`**

Append to module:

```python
_FENCE_RE_JSON = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def parse_locale_reply(text: str, expected_pids: list[str]) -> dict[str, str]:
    """Parse a locale sub-agent reply.

    Accepts either a fenced ```json``` code block or a bare JSON object.
    Returns ``{pid: locale_title}``. Raises ``ValueError`` if the reply
    fails to parse, has missing pids, or has unexpected extra pids.
    """
    text = text.strip()
    m = _FENCE_RE_JSON.search(text)
    json_str = m.group(1).strip() if m else text
    try:
        obj = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"locale reply is not valid JSON: {e}") from e
    if not isinstance(obj, dict):
        raise ValueError(f"locale reply must be a JSON object, got {type(obj).__name__}")
    expected = set(expected_pids)
    got = set(obj.keys())
    missing = expected - got
    if missing:
        raise ValueError(f"missing pid(s): {sorted(missing)}")
    extra = got - expected
    if extra:
        raise ValueError(f"unexpected pid(s): {sorted(extra)}")
    for pid, title in obj.items():
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"locale title for {pid} must be non-empty string")
    return {pid: obj[pid].strip() for pid in expected_pids}
```

- [ ] **Step 4: Run tests, expect pass**

Run: `python -m pytest app/tests/test_rename_future_titles.py -v -k parse_locale_reply`
Expected: All 5 tests PASS.

### Task 4: `scan()` + smoke test

**Files:**
- Modify: `app/skills/rename_future_titles.py`
- Modify: `app/tests/test_rename_future_titles.py`

- [ ] **Step 1: Append `scan()` to the module**

```python
def scan(repo_root: Path) -> list[dict]:
    """Return ``[{"date", "pid", "old_title"}, ...]`` for all 48 targets."""
    out: list[dict] = []
    for date_iso in _TARGET_DATES:
        path = Path(repo_root) / "app" / "sourcedata" / date_iso / "predictions.json"
        if not path.is_file():
            raise FileNotFoundError(f"missing sourcedata: {path}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        for entry in payload["predictions"]:
            out.append({
                "date": date_iso,
                "pid": entry["id"],
                "old_title": entry["title"],
            })
    return out
```

- [ ] **Step 2: Append a smoke test**

```python
@pytest.fixture
def repo_root() -> Path:
    """Repo root resolved from this test file's location."""
    return Path(__file__).resolve().parents[2]


def test_scan_covers_all_dates(repo_root):
    out = rft.scan(repo_root)
    # 16 dates, but per-date prediction counts vary (3 or 4).
    # Real corpus as of 2026-05-05: 11×3 + 4×4 + 1×3 = 52.
    assert len(out) == 52
    assert {entry["date"] for entry in out} == set(rft._TARGET_DATES)
    # Every entry has the three expected keys.
    assert all({"date", "pid", "old_title"} == set(e.keys()) for e in out)
    # Every pid starts with "prediction."
    assert all(e["pid"].startswith("prediction.") for e in out)
```

- [ ] **Step 3: Run, expect pass**

Run: `python -m pytest app/tests/test_rename_future_titles.py::test_scan_returns_48_targets -v`
Expected: PASS.

### Task 5: `bundle_en()` — context bundles for EN sub-agents

**Files:**
- Modify: `app/skills/rename_future_titles.py`
- Modify: `app/tests/test_rename_future_titles.py`

- [ ] **Step 1: Append the title-rules constant + `bundle_en` function**

```python
# Inlined verbatim from design/scheduled/1_daily_update-writer-rules.md
# §compose-prediction Field-level rules → title section.
_EN_TITLE_RULES = """\
TITLE RULES (from design/scheduled/1_daily_update-writer-rules.md):

- The title MUST lead with the predicted SUBJECT and VERB. The title states the
  prediction itself — what subject does what — not the catalyst that motivated it.

- DO NOT open with the triggering event (e.g. "Mag 7 Q1 earnings reset ...",
  "WSJ OpenAI-revenue-miss + Mag 7 print collision triggers ...").
- DO NOT open with the observer / analyst / publication (e.g. "WSJ Apr 28 ...",
  "OpenAI Apr 28 WSJ initiates ...").
- DO NOT open with a date or timing reference. The trigger's date, the publication
  that flagged it, and any analyst commentary belong in the body / reasoning /
  source citations — never in the leading phrase of the title.

- The subject is the actor / system / category whose future state is being predicted
  (e.g. "Local-LLM training stack", "Big-3 hyperscalers", "SEC", "Frontier
  cyber-AI models"). The verb states the predicted action / state change.

- A trailing "by <time>" is fine; a leading time is not.

- Length: ≤ 80 chars.
- No scope prefix: (Tech) / (Business) / (Mix) / (技術) / (Tecnología) / (Teknikal) etc.
- Acronyms: only common-knowledge ones (AI, LLM, GPU, SEC, MCP) or expand on first use.

GOOD examples:
  - "Local-LLM training stack hits 70% VRAM reduction baseline by H2 2026"
  - "SEC publishes AI-revenue disclosure concept release by Q4 2026"
  - "Big-3 hyperscalers ship MCP-server policy enforcement as default by Q4 2026"

BAD examples:
  - "Mag 7 Q1 earnings (Apr 29-30) reset the AI-capex ROI narrative ..." (trigger + date)
  - "WSJ OpenAI-revenue-miss + Mag 7 print collision triggers ..." (collision/observer)
  - "OpenAI Apr 28 WSJ initiates 2026 \\"AI-revenue disclosure rewrite\\" ..." (observer + date)

REPLY CONTRACT (one line, exactly one of):
  OK <pid> <new_title>     -- rewrite delivered
  KEEP <pid>               -- existing title already complies
  FAIL <pid> <reason>      -- rewrite impossible
"""


def bundle_en(repo_root: Path, date_iso: str) -> list[dict]:
    """Return 3 EN sub-agent context bundles for one date.

    Each bundle has: pid, prediction_date, old_title, body, so_that,
    landing, title_rules.
    """
    path = Path(repo_root) / "app" / "sourcedata" / date_iso / "predictions.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    bundles: list[dict] = []
    for entry in payload["predictions"]:
        bundles.append({
            "pid": entry["id"],
            "prediction_date": date_iso,
            "old_title": entry["title"],
            "body": entry["body"],
            "so_that": entry["reasoning"]["so_that"],
            "landing": entry["reasoning"]["landing"],
            "title_rules": _EN_TITLE_RULES,
        })
    return bundles
```

- [ ] **Step 2: Append test**

```python
def test_bundle_en_shape(repo_root):
    bundles = rft.bundle_en(repo_root, "2026-04-19")
    assert len(bundles) == 3
    for b in bundles:
        assert set(b.keys()) == {
            "pid", "prediction_date", "old_title", "body",
            "so_that", "landing", "title_rules"
        }
        assert b["prediction_date"] == "2026-04-19"
        assert b["pid"].startswith("prediction.")
        assert "TITLE RULES" in b["title_rules"]
```

- [ ] **Step 3: Run, expect pass**

Run: `python -m pytest app/tests/test_rename_future_titles.py::test_bundle_en_shape -v`
Expected: PASS.

### Task 6: `bundle_locale()`

**Files:**
- Modify: `app/skills/rename_future_titles.py`
- Modify: `app/tests/test_rename_future_titles.py`

- [ ] **Step 1: Append `bundle_locale`**

```python
# Inlined excerpt from design/skills/locale-fanout.md §Translation contract.
_LOCALE_RULES = """\
LOCALE TRANSLATION RULES (from design/skills/locale-fanout.md):

- Translate the value into the target locale (ja / es / fil).
- Preserve numerics + named entities + ISO dates verbatim:
  $1.5B, Anthropic, OpenAI, 2026-04-26, Q4 2026, H2 2026, GPU, LLM.
- Filipino: modern tech-news style — Tagalog grammar with English borrow words
  for technical terms is fine.
- No scope prefix in any locale ((技術), (Tecnología), (Teknikal) all forbidden).
- Translate ONLY the title strings. Do not modify any other field.

REPLY CONTRACT:
- Success: a single JSON object in a fenced ```json``` block:
    {"<pid_1>": "<title_1>", "<pid_2>": "<title_2>", "<pid_3>": "<title_3>"}
  All 3 input pids must appear exactly. No prose around the block.
- Failure: one line "FAIL <date> <locale> <reason>" (no JSON block).
"""


def bundle_locale(repo_root: Path, date_iso: str, locale: str) -> dict:
    """Return the locale sub-agent context bundle.

    Reads the **already-applied** EN predictions.json (must run after
    apply-en) plus the existing locale predictions.json for terminology
    context. Output bundle has: date, locale, entries (3×
    {pid, en_new_title, locale_old_title}), locale_rules.
    """
    if locale not in _LOCALES:
        raise ValueError(f"unknown locale: {locale!r}; expected one of {_LOCALES}")
    en_path = Path(repo_root) / "app" / "sourcedata" / date_iso / "predictions.json"
    loc_path = (
        Path(repo_root) / "app" / "sourcedata" / "locales" / date_iso
        / locale / "predictions.json"
    )
    en_payload = json.loads(en_path.read_text(encoding="utf-8"))
    loc_payload = json.loads(loc_path.read_text(encoding="utf-8"))
    en_by_id = {e["id"]: e for e in en_payload["predictions"]}
    entries = []
    for loc_entry in loc_payload["predictions"]:
        pid = loc_entry["id"]
        if pid not in en_by_id:
            raise ValueError(f"locale {locale} {date_iso}: pid {pid} not in EN")
        entries.append({
            "pid": pid,
            "en_new_title": en_by_id[pid]["title"],
            "locale_old_title": loc_entry["title"],
        })
    return {
        "date": date_iso,
        "locale": locale,
        "entries": entries,
        "locale_rules": _LOCALE_RULES,
    }
```

- [ ] **Step 2: Append test**

```python
def test_bundle_locale_shape(repo_root):
    bundle = rft.bundle_locale(repo_root, "2026-04-19", "ja")
    assert bundle["date"] == "2026-04-19"
    assert bundle["locale"] == "ja"
    assert len(bundle["entries"]) == 3
    for e in bundle["entries"]:
        assert set(e.keys()) == {"pid", "en_new_title", "locale_old_title"}
    assert "LOCALE TRANSLATION RULES" in bundle["locale_rules"]


def test_bundle_locale_rejects_bad_locale(repo_root):
    with pytest.raises(ValueError, match="unknown locale"):
        rft.bundle_locale(repo_root, "2026-04-19", "zz")
```

- [ ] **Step 3: Run, expect pass**

Run: `python -m pytest app/tests/test_rename_future_titles.py -v -k bundle_locale`
Expected: 2 PASS.

### Task 7: `assemble_dryrun()` + idempotency test

**Files:**
- Modify: `app/skills/rename_future_titles.py`
- Modify: `app/tests/test_rename_future_titles.py`

- [ ] **Step 1: Append `assemble_dryrun`**

```python
def assemble_dryrun(
    repo_root: Path,
    replies_text: str,
    *,
    generated_at: str | None = None,
) -> dict:
    """Parse 48 EN reply lines + cross-reference scan() to build dry-run JSON.

    ``replies_text``: a string with one reply per line.
    ``generated_at``: ISO timestamp; if None, uses the current UTC time
    (parameter exists so tests can pin it for byte-identical comparison).

    Returns the dict shape suitable for writing to
    ``.tmp/rename-titles-dryrun.json``.
    """
    if generated_at is None:
        generated_at = datetime.now(timezone.utc).isoformat()
    targets = scan(repo_root)
    by_pid: dict[str, dict] = {t["pid"]: t for t in targets}
    entries: list[dict] = []
    seen: set[str] = set()
    for raw in replies_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        parsed = parse_en_reply(line)
        pid = parsed["pid"]
        if pid in seen:
            raise ValueError(f"duplicate pid in replies: {pid}")
        seen.add(pid)
        if pid not in by_pid:
            raise ValueError(f"reply for unknown pid: {pid}")
        target = by_pid[pid]
        if parsed["status"] == "OK":
            entry = {
                "date": target["date"], "pid": pid,
                "old": target["old_title"], "new": parsed["new_title"],
                "status": "OK",
            }
        elif parsed["status"] == "KEEP":
            entry = {
                "date": target["date"], "pid": pid,
                "old": target["old_title"], "new": target["old_title"],
                "status": "KEEP",
            }
        else:  # FAIL
            entry = {
                "date": target["date"], "pid": pid,
                "old": target["old_title"], "new": None,
                "status": "FAIL", "reason": parsed["reason"],
            }
        entries.append(entry)
    missing = set(by_pid) - seen
    if missing:
        raise ValueError(f"missing replies for pids: {sorted(missing)}")
    # Sort by date then pid for deterministic output.
    entries.sort(key=lambda e: (e["date"], e["pid"]))
    return {
        "generated_at": generated_at,
        "scope": f"{_TARGET_DATES[0]}..{_TARGET_DATES[-1]}",
        "entries": entries,
    }
```

- [ ] **Step 2: Append idempotency test**

```python
def _make_mock_replies(repo_root):
    """Build 48 OK reply lines from real corpus, prefixing each old title with 'NEW: '."""
    targets = rft.scan(repo_root)
    return "\n".join(
        f"OK {t['pid']} NEW: {t['old_title']}" for t in targets
    )


def test_dry_run_idempotent(repo_root):
    replies = _make_mock_replies(repo_root)
    pinned = "2026-05-05T00:00:00+00:00"
    a = rft.assemble_dryrun(repo_root, replies, generated_at=pinned)
    b = rft.assemble_dryrun(repo_root, replies, generated_at=pinned)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert len(a["entries"]) == len(rft.scan(repo_root))


def test_dry_run_missing_reply_raises(repo_root):
    replies = _make_mock_replies(repo_root)
    truncated = "\n".join(replies.splitlines()[:-1])  # drop last reply
    with pytest.raises(ValueError, match="missing replies"):
        rft.assemble_dryrun(repo_root, truncated, generated_at="2026-05-05T00:00:00+00:00")


def test_dry_run_unknown_pid_raises(repo_root):
    bogus = "OK prediction.deadbeefdeadbeef New title"
    with pytest.raises(ValueError, match="unknown pid"):
        rft.assemble_dryrun(
            repo_root, bogus + "\n" + _make_mock_replies(repo_root),
            generated_at="2026-05-05T00:00:00+00:00",
        )
```

- [ ] **Step 3: Run, expect pass**

Run: `python -m pytest app/tests/test_rename_future_titles.py -v -k dry_run`
Expected: 3 PASS.

### Task 8: `apply_en()` + ID round-trip + summary/body preservation

**Files:**
- Modify: `app/skills/rename_future_titles.py`
- Modify: `app/tests/test_rename_future_titles.py`

- [ ] **Step 1: Append helpers + `apply_en`**

```python
def _hash_id_check(pid: str, prediction_date: str, body: str) -> bool:
    """Recompute prediction_id from (date, body) and compare to pid.

    Mirrors ``app.skills.migrate_to_sourcedata._stable_prediction_id(date_iso, body)``.
    Note: ``app.src.ingest._hash_id`` shadows this with a parameter named
    ``prediction_summary`` but actually receives ``body`` at call time —
    the field-vs-param-name divergence is a known terminology drift in this
    codebase, called out in migrate_to_sourcedata's docstring.
    """
    h = hashlib.sha1("||".join([prediction_date, body]).encode("utf-8")).hexdigest()[:16]
    return pid == f"prediction.{h}"


def _atomic_write_json(path: Path, payload: dict) -> None:
    """Write JSON atomically via mkstemp + os.replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, path)
    except Exception:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


def apply_en(repo_root: Path, dryrun_payload: dict) -> dict:
    """Apply EN title changes from a dry-run payload.

    Mutates ``app/sourcedata/<date>/predictions.json`` × 16 in place.
    Validates schema + ID round-trip after writing.

    Returns ``{"updated": <int>, "kept": <int>, "failed": <int>}``.
    """
    from app.skills.sourcedata_schemas import PredictionsFile

    by_date: dict[str, list[dict]] = {}
    for entry in dryrun_payload["entries"]:
        if entry["status"] == "FAIL":
            continue
        by_date.setdefault(entry["date"], []).append(entry)

    counts = {"updated": 0, "kept": 0, "failed": 0}
    for entry in dryrun_payload["entries"]:
        if entry["status"] == "FAIL":
            counts["failed"] += 1
        elif entry["status"] == "KEEP":
            counts["kept"] += 1
        else:
            counts["updated"] += 1

    for date_iso, entries in by_date.items():
        path = (
            Path(repo_root) / "app" / "sourcedata" / date_iso / "predictions.json"
        )
        payload = json.loads(path.read_text(encoding="utf-8"))
        new_by_pid = {e["pid"]: e["new"] for e in entries if e["status"] in ("OK", "KEEP")}
        for pred in payload["predictions"]:
            if pred["id"] in new_by_pid:
                pred["title"] = new_by_pid[pred["id"]]
        # Validate schema BEFORE writing.
        PredictionsFile.from_dict(payload)
        # Validate ID round-trip BEFORE writing.
        for pred in payload["predictions"]:
            if not _hash_id_check(pred["id"], date_iso, pred["body"]):
                raise ValueError(
                    f"ID round-trip failed for {pred['id']} on {date_iso}: "
                    f"body may have been mutated"
                )
        _atomic_write_json(path, payload)
    return counts
```

- [ ] **Step 2: Append tests**

```python
@pytest.fixture
def fixture_root(tmp_path, repo_root) -> Path:
    """Copy real sourcedata into an isolated tmp tree for write-tests."""
    src_app = repo_root / "app" / "sourcedata"
    dst_app = tmp_path / "app" / "sourcedata"
    shutil.copytree(src_app, dst_app)
    return tmp_path


def _build_dryrun_with_new_titles(repo_root: Path) -> dict:
    """Build a dry-run payload that prefixes every title with 'NEW: '."""
    replies = _make_mock_replies(repo_root)
    return rft.assemble_dryrun(repo_root, replies, generated_at="2026-05-05T00:00:00+00:00")


def test_apply_en_preserves_id(fixture_root):
    dryrun = _build_dryrun_with_new_titles(fixture_root)
    rft.apply_en(fixture_root, dryrun)
    # For every modified date, every prediction's ID must round-trip.
    for date_iso in rft._TARGET_DATES:
        path = fixture_root / "app" / "sourcedata" / date_iso / "predictions.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        for pred in payload["predictions"]:
            assert rft._hash_id_check(pred["id"], date_iso, pred["body"]), (
                f"ID round-trip failed: {pred['id']} on {date_iso}"
            )


def test_apply_en_preserves_summary_and_body(fixture_root, repo_root):
    """Title is mutated, but summary + body + reasoning + scope_hint are byte-identical."""
    pre = {}
    for date_iso in rft._TARGET_DATES:
        path = fixture_root / "app" / "sourcedata" / date_iso / "predictions.json"
        pre_payload = json.loads(path.read_text(encoding="utf-8"))
        for pred in pre_payload["predictions"]:
            pre[(date_iso, pred["id"])] = {
                "summary": pred["summary"], "body": pred["body"],
                "reasoning": pred["reasoning"], "scope_hint": pred["scope_hint"],
            }
    dryrun = _build_dryrun_with_new_titles(fixture_root)
    rft.apply_en(fixture_root, dryrun)
    for date_iso in rft._TARGET_DATES:
        path = fixture_root / "app" / "sourcedata" / date_iso / "predictions.json"
        post_payload = json.loads(path.read_text(encoding="utf-8"))
        for pred in post_payload["predictions"]:
            key = (date_iso, pred["id"])
            assert pred["summary"] == pre[key]["summary"]
            assert pred["body"] == pre[key]["body"]
            assert pred["reasoning"] == pre[key]["reasoning"]
            assert pred["scope_hint"] == pre[key]["scope_hint"]
            # And title HAS changed (sanity).
            assert pred["title"].startswith("NEW: ")
```

- [ ] **Step 3: Run, expect pass**

Run: `python -m pytest app/tests/test_rename_future_titles.py -v -k apply_en`
Expected: 2 PASS.

### Task 9: `apply_locale_one()`

**Files:**
- Modify: `app/skills/rename_future_titles.py`
- Modify: `app/tests/test_rename_future_titles.py`

- [ ] **Step 1: Append `apply_locale_one`**

```python
def apply_locale_one(
    repo_root: Path,
    date_iso: str,
    locale: str,
    new_titles_by_pid: dict[str, str],
) -> Path:
    """Apply 3 locale title updates for one (date, locale) cell.

    Reads ``app/sourcedata/locales/<date>/<locale>/predictions.json``,
    swaps the title in each of the 3 predictions, validates schema,
    atomic-writes via ``super_backfill.apply_locale``.
    """
    from app.skills.super_backfill import apply_locale

    path = (
        Path(repo_root) / "app" / "sourcedata" / "locales" / date_iso
        / locale / "predictions.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    expected_pids = {p["id"] for p in payload["predictions"]}
    if set(new_titles_by_pid.keys()) != expected_pids:
        raise ValueError(
            f"locale {locale} {date_iso}: pid mismatch — "
            f"expected {sorted(expected_pids)}, got {sorted(new_titles_by_pid)}"
        )
    for pred in payload["predictions"]:
        pred["title"] = new_titles_by_pid[pred["id"]]
    return apply_locale(Path(repo_root), date_iso, locale, "predictions", payload)
```

- [ ] **Step 2: Append test**

```python
def test_apply_locale_one_preserves_other_fields(fixture_root):
    date_iso = "2026-04-19"
    locale = "ja"
    path = (
        fixture_root / "app" / "sourcedata" / "locales" / date_iso / locale
        / "predictions.json"
    )
    pre = json.loads(path.read_text(encoding="utf-8"))
    pre_by_pid = {p["id"]: p for p in pre["predictions"]}
    new_titles = {pid: f"新題: {pre_by_pid[pid]['title']}" for pid in pre_by_pid}
    rft.apply_locale_one(fixture_root, date_iso, locale, new_titles)
    post = json.loads(path.read_text(encoding="utf-8"))
    for p in post["predictions"]:
        assert p["title"] == new_titles[p["id"]]
        # body / reasoning / summary unchanged.
        assert p["body"] == pre_by_pid[p["id"]]["body"]
        assert p["reasoning"] == pre_by_pid[p["id"]]["reasoning"]
        assert p["summary"] == pre_by_pid[p["id"]]["summary"]
```

- [ ] **Step 3: Run, expect pass**

Run: `python -m pytest app/tests/test_rename_future_titles.py -v -k apply_locale_one`
Expected: 1 PASS.

### Task 10: `rerender()` orchestrator wrapper + `verify()` wrapper

**Files:**
- Modify: `app/skills/rename_future_titles.py`

- [ ] **Step 1: Append wrappers**

(Note: `subprocess` is already imported at the top of the module per Task 1.)

```python
def rerender(repo_root: Path, *, only_date: str | None = None) -> int:
    """Re-render markdown for one date (or all 16) + reingest + reexport.

    Subprocess-based so each step gets a fresh interpreter and the renderer's
    template caches don't carry stale state.
    """
    dates = [only_date] if only_date else list(_TARGET_DATES)
    for date_iso in dates:
        for locale in ("en",) + _LOCALES:
            cmd = [
                sys.executable, "-m", "app.skills.render_news_md",
                "--date", date_iso, "--locale", locale, "--write",
                "--repo-root", str(repo_root),
            ]
            rc = subprocess.run(cmd, check=False).returncode
            if rc != 0:
                return rc
        cmd = [
            sys.executable, "-m", "app.src.cli", "ingest-sourcedata",
            "--date", date_iso,
        ]
        rc = subprocess.run(cmd, check=False, cwd=str(repo_root)).returncode
        if rc != 0:
            return rc
    if not only_date:
        rc = subprocess.run(
            [sys.executable, "-m", "app.src.cli", "export"],
            check=False, cwd=str(repo_root),
        ).returncode
        if rc != 0:
            return rc
    return 0


def verify(repo_root: Path) -> int:
    """Run all validation gates without making changes.

    Gates:
      1. PredictionsFile.from_dict() per EN file (16) and per locale file (48).
      2. ID round-trip across all 48 EN entries.
      3. lint_markdown_clean per date (16 dates).
      4. post_write_integrity per news markdown (64 files).
      5. daily_flow_check --date 2026-05-04 --strict.
    """
    from app.skills.sourcedata_schemas import PredictionsFile

    # Gates 1 + 2: schema + ID round-trip.
    for date_iso in _TARGET_DATES:
        en_path = Path(repo_root) / "app" / "sourcedata" / date_iso / "predictions.json"
        en_payload = json.loads(en_path.read_text(encoding="utf-8"))
        PredictionsFile.from_dict(en_payload)
        for pred in en_payload["predictions"]:
            if not _hash_id_check(pred["id"], date_iso, pred["body"]):
                print(f"FAIL ID round-trip: {pred['id']} on {date_iso}")
                return 1
        for locale in _LOCALES:
            loc_path = (
                Path(repo_root) / "app" / "sourcedata" / "locales" / date_iso
                / locale / "predictions.json"
            )
            loc_payload = json.loads(loc_path.read_text(encoding="utf-8"))
            PredictionsFile.from_dict(loc_payload)
    print(f"OK schema + ID round-trip ({len(_TARGET_DATES)} dates × 4 locales)")

    # Gate 3: lint per date.
    for date_iso in _TARGET_DATES:
        rc = subprocess.run(
            [sys.executable, "-m", "app.skills.lint_markdown_clean",
             "--date", date_iso, "--repo-root", str(repo_root)],
            check=False,
        ).returncode
        if rc != 0:
            print(f"FAIL lint_markdown_clean for {date_iso}")
            return 1
    print(f"OK lint_markdown_clean ({len(_TARGET_DATES)} dates)")

    # Gate 4: post_write_integrity per news markdown file.
    paths: list[str] = []
    for date_iso in _TARGET_DATES:
        ymd = date_iso.replace("-", "")
        for locale in ("en",) + _LOCALES:
            paths.append(str(
                Path(repo_root) / "report" / locale / f"news-{ymd}.md"
            ))
    cmd = [
        sys.executable, "-m", "app.skills.post_write_integrity",
        "--kind", "news",
    ]
    for p in paths:
        cmd.extend(["--path", p])
    rc = subprocess.run(cmd, check=False).returncode
    if rc != 0:
        print(f"FAIL post_write_integrity")
        return 1
    print(f"OK post_write_integrity ({len(paths)} files)")

    # Gate 5: daily_flow_check.
    rc = subprocess.run(
        [sys.executable, "-m", "app.skills.daily_flow_check",
         "--date", _TARGET_DATES[-1], "--strict",
         "--repo-root", str(repo_root)],
        check=False,
    ).returncode
    if rc != 0:
        print("FAIL daily_flow_check")
        return 1
    print("OK daily_flow_check")
    return 0
```

(No new tests for these wrappers — they're integration glue tested by Phase 4 execution.)

### Task 11: `dry_run_format_table()` + console rendering

**Files:**
- Modify: `app/skills/rename_future_titles.py`

- [ ] **Step 1: Append the table renderer**

```python
def format_dryrun_table(payload: dict) -> str:
    """Return a markdown table of OLD → NEW for human review."""
    rows = ["| date | pid | status | OLD | NEW |", "|---|---|---|---|---|"]
    for e in payload["entries"]:
        old = (e["old"] or "").replace("|", "\\|")
        new = (e["new"] or "").replace("|", "\\|") if e.get("new") else (e.get("reason") or "")
        rows.append(
            f"| {e['date']} | {e['pid'][:30]} | {e['status']} | {old} | {new} |"
        )
    return "\n".join(rows)
```

(No test — pure formatting.)

### Task 12: CLI plumbing — `main()`

**Files:**
- Modify: `app/skills/rename_future_titles.py`

- [ ] **Step 1: Append `main()` at the bottom of the module**

```python
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m app.skills.rename_future_titles")
    parser.add_argument("--repo-root", default=".", help="Repo root (default: cwd)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("scan", help="Print 48 (date, pid, old_title) targets")

    bp = sub.add_parser("bundle", help="Print sub-agent context bundle(s)")
    bp.add_argument("--kind", required=True, choices=["en", "locale"])
    bp.add_argument("--date", required=True)
    bp.add_argument("--locale", default=None, help="Required if --kind locale")

    dp = sub.add_parser("dry-run", help="Assemble dry-run JSON from a replies file")
    dp.add_argument("--replies-file", required=True, type=Path)
    dp.add_argument(
        "--out", default=Path(".tmp/rename-titles-dryrun.json"), type=Path,
        help="Output dry-run JSON path (default: .tmp/rename-titles-dryrun.json)"
    )

    aep = sub.add_parser("apply-en", help="Apply EN titles from dry-run JSON")
    aep.add_argument("--from-file", required=True, type=Path)

    alp = sub.add_parser("apply-locale", help="Apply locale titles for one (date, locale)")
    alp.add_argument("--date", required=True)
    alp.add_argument("--locale", required=True, choices=list(_LOCALES))
    alp.add_argument(
        "--json-file", required=True, type=Path,
        help="JSON file with {pid: locale_title}"
    )

    rp = sub.add_parser("rerender", help="Re-render markdown + reingest + reexport")
    rp.add_argument("--date", default=None, help="Single date (default: all 16)")

    sub.add_parser("verify", help="Run all validation gates without changes")

    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()

    if args.cmd == "scan":
        print(json.dumps(scan(repo_root), ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "bundle":
        if args.kind == "en":
            print(json.dumps(
                bundle_en(repo_root, args.date), ensure_ascii=False, indent=2
            ))
        else:
            if not args.locale:
                print("--locale required for --kind locale", file=sys.stderr)
                return 2
            print(json.dumps(
                bundle_locale(repo_root, args.date, args.locale),
                ensure_ascii=False, indent=2,
            ))
        return 0
    if args.cmd == "dry-run":
        replies_text = args.replies_file.read_text(encoding="utf-8")
        payload = assemble_dryrun(repo_root, replies_text)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(format_dryrun_table(payload))
        print(f"\nWrote {args.out}", file=sys.stderr)
        return 0
    if args.cmd == "apply-en":
        payload = json.loads(args.from_file.read_text(encoding="utf-8"))
        counts = apply_en(repo_root, payload)
        print(json.dumps(counts, indent=2))
        return 0
    if args.cmd == "apply-locale":
        new_titles = json.loads(args.json_file.read_text(encoding="utf-8"))
        path = apply_locale_one(repo_root, args.date, args.locale, new_titles)
        print(f"OK {path}")
        return 0
    if args.cmd == "rerender":
        return rerender(repo_root, only_date=args.date)
    if args.cmd == "verify":
        return verify(repo_root)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Smoke-test the CLI**

Run: `python -m app.skills.rename_future_titles scan | python -c "import json,sys; d=json.load(sys.stdin); print(len(d), d[0])"`
Expected: First number `48`, then a sample dict like `{'date': '2026-04-19', 'pid': 'prediction....', 'old_title': '...'}`.

Run: `python -m app.skills.rename_future_titles bundle --kind en --date 2026-04-19 | python -c "import json,sys; d=json.load(sys.stdin); print(len(d), list(d[0].keys()))"`
Expected: First number `3`, then keys `['pid', 'prediction_date', 'old_title', 'body', 'so_that', 'landing', 'title_rules']`.

### Task 13: `test_rerender_uses_new_title` — end-to-end render check

**Files:**
- Modify: `app/tests/test_rename_future_titles.py`

- [ ] **Step 1: Append the test**

```python
def test_rerender_uses_new_title(fixture_root):
    """Apply a new title, run render_news_md, assert it appears in the output."""
    from app.skills import render_news_md

    date_iso = "2026-04-19"
    new_title_marker = "TESTSENTINEL Subject does X by Q4 2026"
    # Build a 1-prediction dry-run that touches just the first prediction.
    targets = rft.scan(fixture_root)
    first = next(t for t in targets if t["date"] == date_iso)
    # Build replies for ALL 48 (KEEP for everything except our one OK).
    lines = []
    for t in targets:
        if t["pid"] == first["pid"]:
            lines.append(f"OK {t['pid']} {new_title_marker}")
        else:
            lines.append(f"KEEP {t['pid']}")
    payload = rft.assemble_dryrun(
        fixture_root, "\n".join(lines),
        generated_at="2026-05-05T00:00:00+00:00",
    )
    rft.apply_en(fixture_root, payload)
    # Render the EN news markdown.
    md = render_news_md.render_day(str(fixture_root), date_iso, "en")
    # The new title must appear in the ## Future numbered list.
    assert new_title_marker in md, (
        f"new title not in rendered news markdown for {date_iso}"
    )
```

- [ ] **Step 2: Run, expect pass**

Run: `python -m pytest app/tests/test_rename_future_titles.py::test_rerender_uses_new_title -v`
Expected: PASS.

### Task 14: Final test run + commit 1

**Files:**
- All of `app/skills/rename_future_titles.py` and `app/tests/test_rename_future_titles.py`

- [ ] **Step 1: Run the full test suite for the new module**

Run: `python -m pytest app/tests/test_rename_future_titles.py -v`
Expected: All tests PASS. Aim for ≥ 13 tests (5 EN parser + 5 locale parser + 1 scan + 1 bundle_en + 2 bundle_locale + 3 dry_run + 2 apply_en + 1 apply_locale + 1 rerender = 21 if all granular tests are kept).

- [ ] **Step 2: Run the full project test suite to confirm no regressions**

Run: `python -m pytest app/tests/ -x`
Expected: All previously passing tests still PASS; no new failures.

- [ ] **Step 3: Commit 1**

```bash
git add app/skills/rename_future_titles.py app/tests/test_rename_future_titles.py
git commit -m "rename-future-titles: orchestrator + tests"
```

Verify: `git log --oneline -1` shows the new commit.

---

## Phase 2: EN dispatch + apply (commit 2)

**Goal:** Run the 48 EN sub-agents, dry-run review, apply.

This phase is procedural. Each "task" is a parent-driven action.

### Task 15: Generate all 16 EN bundles

- [ ] **Step 1: For each of the 16 dates, generate bundles to a temp file**

```bash
mkdir -p .tmp/rft-bundles
for d in 2026-04-19 2026-04-20 2026-04-21 2026-04-22 2026-04-23 2026-04-24 2026-04-25 2026-04-26 2026-04-27 2026-04-28 2026-04-29 2026-04-30 2026-05-01 2026-05-02 2026-05-03 2026-05-04; do
  python -m app.skills.rename_future_titles bundle --kind en --date "$d" \
    > ".tmp/rft-bundles/en-${d}.json"
done
ls .tmp/rft-bundles/en-*.json | wc -l
```

Expected: `16`.

### Task 16: Dispatch 48 EN sub-agents in parallel batches

- [ ] **Step 1: Read each bundle file and dispatch 3 sub-agents per date in parallel**

Strategy: harness limit ~16 parallel sub-agents. 52 predictions total (some dates have 4 predictions, not 3). Group as 5-6 dates per round (15-18 agents); 4 rounds covers everything.

Sub-agent prompt template (replace `<BUNDLE_JSON>` with the per-pid bundle JSON object — extracted from the `bundle --kind en --date <D>` output, which is a 3-element array; pass each element separately):

```
You are rewriting one prediction's title to comply with new rules.

Input (one prediction):

<BUNDLE_JSON>

Use `title_rules` (inlined above) as the authoritative spec. Read `body`, `so_that`, and `landing` to identify the predicted SUBJECT and VERB. Replace the title with one that leads with subject + verb, ≤ 80 chars, no scope prefix, no leading date / observer / trigger.

Output: exactly ONE line, in the reply contract format from `title_rules`. No prose, no explanation, no code fence — just the single line. Examples:

  OK <pid> <new_title>
  KEEP <pid>
  FAIL <pid> <reason>
```

The Task tool's `subagent_type` is `general-purpose`. The sub-agent returns a single line which the parent saves to a per-pid result file.

Suggested batching (per-date counts: 11×3 + 4×4 + 1×3 = 52):
- Round 1: 2026-04-19..2026-04-23 (5 dates × 3 = 15 agents)
- Round 2: 2026-04-24..2026-04-28 (5 dates × 3 = 15 agents)
- Round 3: 2026-04-29..2026-04-30 (3 + 4 = 7 agents) + 2026-05-01..2026-05-02 (4 + 4 = 8 agents) = 15 agents
- Round 4: 2026-05-03..2026-05-04 (4 + 3 = 7 agents)

Collect all 52 reply lines into `.tmp/rft-replies.txt` (one per line).

- [ ] **Step 2: Verify reply count**

```bash
wc -l .tmp/rft-replies.txt
```

Expected: `52`.

- [ ] **Step 3: Sanity-check all pids match scan**

```bash
python -m app.skills.rename_future_titles scan | python -c "
import json, sys
targets = {t['pid'] for t in json.load(sys.stdin)}
got = set()
for line in open('.tmp/rft-replies.txt'):
    parts = line.strip().split(' ', 2)
    if len(parts) >= 2:
        got.add(parts[1])
print('missing:', sorted(targets - got))
print('extra:', sorted(got - targets))
"
```

Expected: both lists empty.

### Task 17: Dry-run + user review gate

- [ ] **Step 1: Generate dry-run JSON + table**

```bash
python -m app.skills.rename_future_titles dry-run \
  --replies-file .tmp/rft-replies.txt \
  --out .tmp/rename-titles-dryrun.json
```

Expected: A markdown table printed to stdout, dry-run JSON written.

- [ ] **Step 2: Present the table to the user. Wait for explicit go/no-go.**

If the user requests changes for specific pids, return to Task 16 with corrected sub-agent inputs (or re-prompt the failing sub-agent only).

### Task 18: Apply EN titles + commit 2

- [ ] **Step 1: Apply**

```bash
python -m app.skills.rename_future_titles apply-en \
  --from-file .tmp/rename-titles-dryrun.json
```

Expected output: `{"updated": 52, "kept": 0, "failed": 0}` (or similar — actual counts depend on KEEP decisions; total = 52).

- [ ] **Step 2: Quick schema + ID round-trip check**

```bash
python -c "
from pathlib import Path
from app.skills import rename_future_titles as rft
from app.skills.sourcedata_schemas import PredictionsFile
import json

repo = Path('.').resolve()
for d in rft._TARGET_DATES:
    p = repo / 'app' / 'sourcedata' / d / 'predictions.json'
    payload = json.loads(p.read_text(encoding='utf-8'))
    PredictionsFile.from_dict(payload)
    for pred in payload['predictions']:
        assert rft._hash_id_check(pred['id'], d, pred['body']), f'{pred[\"id\"]} {d}'
print('OK 52 entries pass schema + ID round-trip')
"
```

Expected: `OK 52 entries pass schema + ID round-trip`.

- [ ] **Step 3: Commit 2**

```bash
git add app/sourcedata/2026-04-{19,20,21,22,23,24,25,26,27,28,29,30}/predictions.json \
        app/sourcedata/2026-05-{01,02,03,04}/predictions.json
git commit -m "rename-future-titles: en titles applied (52 entries)"
```

Verify: `git diff HEAD~1 --stat | tail -3` shows ~16 files modified.

---

## Phase 3: Locale dispatch + apply (commit 3)

**Goal:** Translate the new EN titles into ja/es/fil for all 16 dates (48 sub-agents, 144 title cells).

### Task 19: Generate 48 locale bundles

- [ ] **Step 1: For each (date, locale), generate a bundle file**

```bash
for d in 2026-04-19 2026-04-20 2026-04-21 2026-04-22 2026-04-23 2026-04-24 2026-04-25 2026-04-26 2026-04-27 2026-04-28 2026-04-29 2026-04-30 2026-05-01 2026-05-02 2026-05-03 2026-05-04; do
  for loc in ja es fil; do
    python -m app.skills.rename_future_titles bundle --kind locale \
      --date "$d" --locale "$loc" \
      > ".tmp/rft-bundles/locale-${d}-${loc}.json"
  done
done
ls .tmp/rft-bundles/locale-*.json | wc -l
```

Expected: `48`.

### Task 20: Dispatch 48 locale sub-agents

- [ ] **Step 1: Run sub-agents in parallel batches of 16**

Sub-agent prompt template (replace `<BUNDLE_JSON>` with the contents of `.tmp/rft-bundles/locale-<date>-<locale>.json`):

```
You are translating 3 prediction titles into one locale.

Input bundle:

<BUNDLE_JSON>

For each `entries[i]`, translate `en_new_title` into the locale `<bundle.locale>`. Use `locale_old_title` only as terminology context — do NOT reuse it if the new EN title differs in meaning. Follow `locale_rules` (inlined above): preserve named entities, ISO dates, and numerics verbatim; no scope prefix; JSON keys stay literal English.

Output: a fenced ```json``` code block containing exactly 3 pid → translated-title pairs, in the same order as `entries[]`. No prose around the block. Example shape:

  ```json
  {
    "prediction.aaaa...": "<locale title 1>",
    "prediction.bbbb...": "<locale title 2>",
    "prediction.cccc...": "<locale title 3>"
  }
  ```

On unrecoverable failure, output a single line `FAIL <date> <locale> <reason>` instead of the JSON block.
```

For each successful sub-agent reply, extract the JSON object via `parse_locale_reply` (or just save the raw JSON if the sub-agent emitted only the fenced block) and save to `.tmp/rft-locale-replies/<date>-<locale>.json`.

- [ ] **Step 2: Verify all 48 reply files exist and parse**

```bash
ls .tmp/rft-locale-replies/*.json | wc -l
python -c "
import json
from pathlib import Path
n = 0
for p in Path('.tmp/rft-locale-replies').glob('*.json'):
    obj = json.loads(p.read_text(encoding='utf-8'))
    assert isinstance(obj, dict) and len(obj) == 3, p
    n += 1
print(f'OK {n} locale reply files')
"
```

Expected: `48`, then `OK 48 locale reply files`.

### Task 21: Apply locale titles + commit 3

- [ ] **Step 1: Apply each locale cell**

```bash
for d in 2026-04-19 2026-04-20 2026-04-21 2026-04-22 2026-04-23 2026-04-24 2026-04-25 2026-04-26 2026-04-27 2026-04-28 2026-04-29 2026-04-30 2026-05-01 2026-05-02 2026-05-03 2026-05-04; do
  for loc in ja es fil; do
    python -m app.skills.rename_future_titles apply-locale \
      --date "$d" --locale "$loc" \
      --json-file ".tmp/rft-locale-replies/${d}-${loc}.json"
  done
done
```

Expected: 48 lines of `OK <path>` output.

- [ ] **Step 2: Schema validation across all 48 locale files**

```bash
python -c "
from pathlib import Path
from app.skills import rename_future_titles as rft
from app.skills.sourcedata_schemas import PredictionsFile
import json

repo = Path('.').resolve()
n = 0
for d in rft._TARGET_DATES:
    for loc in rft._LOCALES:
        p = repo / 'app' / 'sourcedata' / 'locales' / d / loc / 'predictions.json'
        payload = json.loads(p.read_text(encoding='utf-8'))
        PredictionsFile.from_dict(payload)
        n += 1
print(f'OK {n} locale predictions.json pass schema')
"
```

Expected: `OK 48 locale predictions.json pass schema`.

- [ ] **Step 3: Commit 3**

```bash
git add app/sourcedata/locales/
git commit -m "rename-future-titles: locale titles applied (156 entries)"
```

Verify: `git diff HEAD~1 --stat | tail -3` shows 48 files modified.

---

## Phase 4: Rerender + reingest + reexport + verify (commit 4)

**Goal:** Propagate the new titles to all derived artifacts (markdown, DB, graph), then run all validation gates.

### Task 22: Rerender all 16 dates × 4 locales

- [ ] **Step 1: Run the orchestrator's rerender command**

```bash
python -m app.skills.rename_future_titles rerender
```

Expected: exit 0. Each date logs `OK wrote report/<L>/news-YYYYMMDD.md` × 4 locales, then ingest output, repeated 16 times, then `cli export` runs once.

- [ ] **Step 2: Verify the rendered markdown contains new titles for a spot-check**

```bash
grep -A 2 "^## Future" report/en/news-20260419.md | head -10
```

Expected: 3 numbered list entries (1., 2., 3.) with the new titles.

### Task 23: Run all validation gates

- [ ] **Step 1: Verify**

```bash
python -m app.skills.rename_future_titles verify
```

Expected output:
- `OK schema + ID round-trip (16 dates × 4 locales)`
- `OK lint_markdown_clean (16 dates)`
- `OK post_write_integrity (64 files)`
- `OK daily_flow_check`

If any gate fails, investigate immediately. The most common failure modes:
- `lint_markdown_clean` flagging a forbidden token (e.g., a leftover scope prefix in a translated title) — fix the failing locale title and re-apply that one cell.
- `daily_flow_check` complaining about missing artifacts — usually means rerender skipped a date; re-run `rerender --date <d>` for the offending date.

### Task 24: Commit 4 + cleanup

- [ ] **Step 1: Commit rerender outputs + DB + graph**

```bash
git status
```

Expected files modified:
- `report/{en,ja,es,fil}/news-2026{0419..0504}.md` × 64
- `docs/data/graph-{tech,business,mix}.json`

```bash
git add report/ docs/data/graph-*.json
git commit -m "rename-future-titles: rerender + db reingest + graph export"
```

Verify: `git log --oneline -4` shows the 4 commits in order.

- [ ] **Step 2: Visual dashboard check (manual)**

Start a local server:

```bash
python -m http.server 8000 --directory docs &
```

Open `http://localhost:8000/` in a browser. Navigate the BIZ / TECH / MIX views. Confirm:
- Past 16 days of prediction cards now show the new titles (subject + verb leading).
- 7d / 30d / 90d window switches don't break.

Stop the server when done.

- [ ] **Step 3: Mark moushiokuri complete**

Per the moushiokuri's "完了条件" section, either:

Option A: Append a `## 進捗ログ` section to `moushiokuri-rename-future-titles.md` listing the 4 commits and any deviations, then commit:

```bash
git add moushiokuri-rename-future-titles.md
git commit -m "rename-future-titles: progress log + done"
```

Option B: Move the moushiokuri to a `done/` directory:

```bash
mkdir -p done
git mv moushiokuri-rename-future-titles.md done/
git commit -m "rename-future-titles: archive moushiokuri (done)"
```

User's choice — default to Option A unless the user has previously moved old moushiokuri to a `done/` archive.

---

## Out of scope (do not do during execution)

- Do not modify `summary` / `body` / `reasoning` / `short_label` / `scope_hint` (would break IDs / bridges / scope assignment).
- Do not regenerate `app/sourcedata/<date>/bridges.json` or `needs.json` (they reference predictions by `id` / `short_label`, both unchanged).
- Do not update `docs/data/snapshots/<date>/graph-*.json` (point-in-time history, intentionally frozen).
- Do not build `app/skills/translate_sourcedata.py` (separate moushiokuri; this is a one-shot backfill).
- Do not run the matcher / scope-assignment changes hinted at in the moushiokuri's "並列タスク" section — that is a separate task.
