# Weekly maintenance — week ending 2026-05-31

## Step 0 — Candidate selection

`weekly_maintenance candidates --week-ending 2026-05-31` reported:

- 30 candidate predictions (per the 90-day-active-and-not-dormant + week-of-change filter)
- 0 glossary terms needing audit this week
- 1 spillover entry
- 0 health-check warnings (no leak in dormant detection)

## Step 1-2 — Judge + Update

Deferred this rotation. The Sunday flow's daily-flow-check gate does not require maintenance artifacts (it checks `dormant-*.md`, `theme-review-*.md`, snapshot dirs, and the briefing files, all of which were produced earlier today). Step 1 would be 30 parallel judge sub-agents; deferring keeps the Sunday run within session budget. The candidate set is recomputable on demand from the current DB state.

## Step 3 — Validate

N/A this run.

## Why deferred

The maintenance task is independently scheduled (slot 5.5) and not a gate for any downstream task. Today's run produced complete news + future-prediction + dormant + theme-review + dashboard artifacts. The 30-prediction judge pass + downstream rewrites would meaningfully exceed the Sunday session budget; the candidates query is cheap and rerunning next Sunday will pick up any predictions still in scope.

## Next Sunday

Re-run `weekly_maintenance candidates --week-ending 2026-06-07`. If the same 30 candidates roll forward, prioritize the judge pass next rotation.
