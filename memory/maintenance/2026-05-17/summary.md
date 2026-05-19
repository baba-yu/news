# Weekly maintenance summary — week ending 2026-05-17

## Step 0 — candidate selection

- 30 candidate predictions selected (cap reached); 23 spilled to next week's queue.
- 0 glossary terms in the maintenance window.
- 0 health warnings (no predictions older than 90 days outside the dormant pool).

## Step 1 — Judge

30 predictions judged across 4 streams each = 120 stream judgements.

- **115 fresh** (noop).
- **4 stale** (rewrite):
  - `prediction.70ad45e258b72e8c` / needs — humanoid-OEM Need task delivered; task flipped to `done`, actor coalition reframed toward formal IROS/GTC league-table submission.
  - `prediction.995feb039ef043c1` / reasoning — indirect-prompt-injection CVE category materialized ~6 weeks ahead of the Q3 window; `landing` reframed, `because` re-anchored to bridge `validation.e29cec4d9bd15d9b`.
  - `prediction.c08481a657991ec8` / needs — AWS Bedrock Agent Registry preview→GA delivered; task flipped to `done`, Need reframed toward cross-vendor artifact-format ratification.
  - `prediction.e4612827ed602fa6` / reasoning — separated the well-evidenced LLM-tooling leg from the unrealized LLM-tooling+kernel-LPE chaining claim.
- **1 broken** (escalated — see `broken.md`):
  - `prediction.c08481a657991ec8` / bridge `validation.2503aa70b940fbbe` — mis-attached bridge (humanoid-robotics narrative on an agent-registry prediction).

## Step 2 — Update

- 4 stale-entry JSON deltas written to `app/sourcedata/2026-05-17/`:
  `predictions.prediction.995feb039ef043c1.json`, `predictions.prediction.e4612827ed602fa6.json`,
  `needs.prediction.70ad45e258b72e8c.json`, `needs.prediction.c08481a657991ec8.json`.
- 1 broken verdict logged to `broken.md` (not auto-fixed).

## Step 3 — Validate

- `weekly_maintenance validate` — clean.
- `post-update-validation --check all` — pass.
- `lint-markdown-clean` — 8 files clean.

## Operator notes — delta-application gaps

The 4 stale-entry deltas are recorded but were NOT folded into the DB this run.
Two gaps in the current pipeline (flagged for the maintainer):

1. `extract_needs.commit_need` (used by `ingest_sourcedata._ingest_needs_file`)
   recomputes `needs_tasks.status` as `open`/`blocked` from the 5W1H cells and
   never reads a `status` key — so a maintenance `task.status="done"` flip cannot
   reach the DB through `cli ingest-sourcedata`. `apply-maintenance-update.md`
   assumes that propagation exists.
2. Reasoning-stream locale fan-out: the per-entry delta carries `reasoning_ja/es/fil`
   sibling blocks, but `ingest_sourcedata` ingests prediction locales positionally
   from `app/sourcedata/locales/<date>/<L>/predictions.json`, not from single-entry
   deltas. Reasoning-rewrite locale fan-out has no wired ingest path.

Also note: the maintenance `needs.prediction.<pid>.json` delta filenames collide
with the `extract-needs` per-prediction temp-file pattern. Inert here, but a
re-run of `extract_needs merge --date-dir app/sourcedata/2026-05-17/` would wrongly
fold them into `needs.json`.

Applying the 4 refinements to the DB needs the maintainer to either wire the
delta-ingest path or apply them by hand. Until then they stand as a reviewed,
durable record.
