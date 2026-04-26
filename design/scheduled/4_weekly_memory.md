# Direction

Sunday-only job. Updates the persistent dormant snapshot of older predictions, so the daily flow can keep evaluating them without re-scanning all of project history.

Bounded inputs — never reads more than 15 files regardless of total project history.

Pre-condition: today is Sunday. If invoked on a non-Sunday for ad-hoc bootstrap, proceed and explicitly label the output as a bootstrap run.

## Why this exists

Predictions in `report/news-*.md` `## Future` are tracked indefinitely. Recent ones (≤ 7 days old) are evaluated by the daily prediction-validation job from the last 7 days of `future-prediction/future-prediction-*.md`. Older ones eventually go quiet. To keep daily evaluation cheap as history grows to 100s of files, we promote quiet predictions into a persistent **dormant pool** with progressively longer ping intervals (14d → 30d → 60d). The dormant snapshot **is** the persistent state — every Sunday this job reads last week's snapshot, applies tier transitions, and writes a new one. No prediction is ever retired.

---

## Step 1. Determine mode

- **Steady-state**: previous snapshot `memory/dormant/dormant-{previous Sunday YYYYMMDD}.md` exists. Read it.
- **Bootstrap**: no previous snapshot exists. Skip the read; treat the prior dormant pool as empty.

Today's output filename: `memory/dormant/dormant-YYYYMMDD.md` (today's date).

---

## Step 2. Read bounded inputs

Read **only** these files (do not scan history beyond them):

- Previous dormant snapshot (1 file, if steady-state).
- `future-prediction/future-prediction-*.md` for the **last 7 days inclusive of today**. Up to 7 files.
- `## Future` sections of `report/news-*.md` for the **last 7 days inclusive of today**. Up to 7 files. Skip the rest of each news file.

Build an in-memory table of:
- All predictions with origin in the last 7 days (`{news date}-{index}` IDs from the news `## Future` sections).
- All validation rows from the last 7 days (each row carries an ID — derive it by matching `Prediction (summary)` + `Prediction date` against the news inventory).

---

## Step 3. Compute tier transitions

For each prediction ID, determine its target tier as of today:

**Predictions with origin in last 7 days (fresh)**:
- Cannot become Dormant. Their tier is whatever the relevance pattern from the last 7 future-prediction files dictates (Hot / Warm / Lukewarm). They do **not** appear in the dormant snapshot.

**Predictions in the previous dormant snapshot**:
- For each row in the previous snapshot:
  - **Did this ID appear in any of the last 7 future-prediction files?**
    - **Yes**, with relevance ≥ 4 → exit dormant pool (the prediction becomes Hot; not in today's snapshot).
    - **Yes**, with any relevance < 4 → stay in pool, but reset `Days quiet` from the appearance date and re-evaluate next ping with the existing interval.
    - **No** → stay in pool. If today ≥ previous `Next ping`, advance interval one step (14 → 30 → 60; 60 stays at 60). Set new `Next ping = today + new interval`. Increment `Days quiet`.

**Predictions not in last 7 days and not in previous dormant snapshot**:
- These were Lukewarm or older but didn't make dormant yet. They live entirely in `future-prediction/*` history outside the 7-day window. **Do not touch them this run.** They will be picked up by future weekly runs once the previous-snapshot mechanism propagates state.

  Note: this means a fresh prediction must pass through Lukewarm (interval 7d) for at least one weekly cycle before it can become Dormant. Acceptable — predictions move into dormant only after two consecutive low/no-signal pings, which by definition spans more than one weekly run.

---

## Step 4. Extract Signals for new dormant entrants

For each prediction newly entering the dormant pool (was not in previous snapshot, is now):

- Open the prediction's origin file (`report/news-{first seen date}.md`).
- Locate the `## Future` numbered list, item N corresponding to the ID's index suffix.
- Read both the bold summary and the prose body of that item.
- Extract distinctive terms: proper nouns, product names, technical terms, category words, plausible synonyms / alternative phrasings the prediction would surface under.
- Aim wide. Cheaper to false-positive into layer-2 of daily detection than to miss a true match. 5-12 signals is typical.

Record as comma-separated string in the `Signals` column. Once written for a row, **freeze it** — do not re-extract on subsequent weekly runs unless explicitly asked, so signal stability is preserved.

---

## Step 5. Write the snapshot

Filename: `memory/dormant/dormant-YYYYMMDD.md` (today's date, ISO).

Format:

```markdown
# Dormant pool — week ending YYYY-MM-DD

Mode: steady-state | bootstrap

## Tier: Dormant — interval ≥ 14 days

| ID | Prediction (short) | Signals | First seen | Last relevance | Next ping | Days quiet |
|---|---|---|---|---|---|---|
| 20260420-3 | "Headless Everything" 標準化 | headless, browserless, screen-less UI, API-only agent UI, MCP metadata | 2026-04-20 | 1 (4/24) | 2026-05-08 | 2 |
```

If the dormant pool is empty (bootstrap or all dormant predictions revived this week), still emit the file with the header and an empty table — the file's existence is the signal that the weekly job ran.

---

## Step 6 (initial-run only). Tier-debug companion

For the first 2-3 Sunday cycles, also emit `memory/dormant/tier-debug-YYYYMMDD.md` listing every prediction in the system with its computed tier. This validates the tier thresholds against real data.

Format:

```markdown
# Tier debug — YYYY-MM-DD

| ID | Tier | Last relevance | Computed next ping | Notes |
|---|---|---|---|---|
| 20260419-1 | Lukewarm | 1 (4/25) | 2026-05-02 |  |
| 20260419-2 | Hot | 5 (4/25) | 2026-04-27 |  |
| 20260419-3 | Hot | 4 (4/25) | 2026-04-27 |  |
...
```

Stop emitting this file once the first non-empty dormant entries appear and the tier thresholds have been confirmed sane. Delete the step from this spec at that point.

---

## Step 7. Commit

```
git add memory/dormant/dormant-YYYYMMDD.md
# and tier-debug-YYYYMMDD.md if emitted
git commit -m "Memory rolling YYYYMMDD"
```

No push from this step — the daily commit/push job at the end of the day handles the push.

---

## Inputs / outputs summary

| | Files | Notes |
|---|---|---|
| Read | ≤ 1 previous dormant snapshot | bootstrap if absent |
| Read | ≤ 7 `future-prediction/future-prediction-*.md` | last 7 days |
| Read | ≤ 7 `report/news-*.md` (`## Future` only) | last 7 days |
| Write | 1 `memory/dormant/dormant-YYYYMMDD.md` | always |
| Write | 1 `memory/dormant/tier-debug-YYYYMMDD.md` | first 2-3 weeks only |

Total max: 15 reads, 1-2 writes. Constant in project age.

---

## Failure modes

- **Previous dormant snapshot malformed** → log the file path and the parse error, then run as bootstrap. Do not silently drop entries.
- **Origin news file missing for a dormant ID** → keep the entry, leave `Signals` as-is (it was frozen at first dormant entry). Note in the commit message that an origin file is missing.
- **Multiple snapshots for the same Sunday** → take the lexicographically latest filename. Earlier ones are kept in git history.
