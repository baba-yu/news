# Weekly maintenance — week ending 2026-06-21

Sunday slot 5.5 (`6_weekly_maintenance`). Run shape: Step 0 candidates → Step 1 judge (3 batched sub-agents) → merge → Step 2 update (3 sub-agents) → Step 3 validate.

## Step 0 — candidates
- 20 predictions selected, 0 glossary terms, spillover 0, health_warnings 0 (no >90-day non-dormant leak).
- Signal mix: 14 `landed_this_week`, 7 `relevance_drift` (some overlap). Cross-stream state pre-extracted to `app/sourcedata/2026-06-21/maintenance-state.json` (reasoning + recent bridges + needs + chain/relation edges per candidate).

## Step 1 — judge (20 predictions × 4 streams, 3 batched sub-agents)
- Judged reasoning / bridge / needs / readings with cross-stream awareness. 31 judgements total.
- **6 stale (prediction, stream) pairs across 3 predictions**; the remaining 25 fresh/noop (conservative — `landed_this_week` signals were mostly confirmatory, not resolving).

## Step 2 — update (forward-reframe; EN reasoning authoritative, applied to origin-date sourcedata)
| Prediction | Streams | Reframe |
|---|---|---|
| `prediction.386fc2ca894276ee` — Governed agent-ontology layer hardens into the enterprise-agent moat (orig 2026-06-03) | reasoning, needs | Databricks Data+AI Summit (Jun 15-18) catalyst has now passed; dropped it as the trigger and pointed `landing` forward to whether a *second* platform ships a comparable governed ontology layer at GA by Q4 2026. |
| `prediction.8ae347c6052558e0` — AMD Helios + MI450 commitment book clears 15GW by H2 2026 (orig 2026-05-20) | reasoning, needs | `because`/`given` were pinned to a late-May weekday snapshot; reframed to the settled ~11.1GW landmark + the slower trajectory, with AMD Advancing AI (Jul 22-23) as the next signing catalyst. 15GW/H2-2026 outcome NOT contradicted. |
| `prediction.d7abb993513f7449` — Tenstorrent S-1 anchors three-name AI-chip IPO set by early August 2026 (orig 2026-05-24) | reasoning, needs | Dropped the "doubly-weekend-aged fifteen-business-day" lifecycle vocab frozen at May 24; reflected the mid/late-June cohort state (SpaceX June 12 listing opened the IPO window) and kept the early-August-2026 landing; needs re-anchored on the next observable filing/pricing milestone. |

Notes:
- Reframed reasoning (`because`/`given`/`so_that`/`landing`) applied **in place to the origin-date EN sourcedata** (`app/sourcedata/{2026-06-03,2026-05-20,2026-05-24}/predictions.json`); `id`/`title`/`body`/`summary`/`plain_language` preserved verbatim so the hash id reproduces and `cli update` (run in `3_daily_briefing`) folds the fresh reasoning into the DB + dashboard.
- Per-judgement update markers written under `app/sourcedata/2026-06-21/` (`maintenance-update.reasoning.<pid>.json`, `maintenance-update.needs.<pid>.json`) to satisfy the Step 3 validate gate.
- Locale fan-out intentionally NOT rewritten for maintenance deltas (EN reasoning is authoritative; `ingest_day_locales` pairs locale rows by `source_row_index` within the file's date, so a back-dated delta would mis-key). Locale reasoning keeps its prior translation; the dashboard falls back to EN where they diverge.
- `needs` reframes are recorded as editorial markers (the next-phase actor/outcome); `needs_tasks.status` is recomputed from 5W1H completeness at ingest, so no DB status flip is forced.

## Step 3 — validate
- `weekly_maintenance validate --week-ending 2026-06-21`: clean — every stale judgement has an applied update marker; no broken/retire verdicts.
