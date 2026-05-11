# 6_weekly_maintenance — skipped 2026-05-10

This Sunday's `6_weekly_maintenance` run was **skipped** during the post-outage catch-up that produced `2026-05-10`'s artifacts. Rationale:

- The original `0_daily_master` scheduled run did not execute on 5/10 (Claude Desktop was updating; the host was down). The catch-up run prioritized restoring the strict-gate artifacts.
- The maintenance step is **idempotent across missed Sundays** per `design/scheduled/6_weekly_maintenance.md`: "Idempotent: if a Sunday is missed, the next Sunday's gate naturally picks up the same change-signal entries (and any new ones from the missed week)."
- The strict completion gate (`daily-flow-check --strict`) does not require maintenance outputs.

## Carry-over for 2026-05-17

The 5/10 candidate pool to remember next Sunday:

- **6 huge_longshot hits in the 5/4-5/10 window** — these predictions landed and their reasoning may need to be reframed from forward-looking to historical fact:
  - `prediction.5acccd6cae1f9b03` (hit 2026-05-05) Frontier-model previews SOC 2 + FedRAMP + FMF baseline
  - `prediction.11c2c648527fe212` (hit 2026-05-05) Capital markets reprice agent-displaced SaaS
  - `prediction.082b0a07077870dd` (hit 2026-05-06) GGUF supply chains signed cards + SSTI scans
  - `prediction.c08481a657991ec8` (hit 2026-05-10) Agent registry standard converges with MCP
  - `prediction.995feb039ef043c1` (hit 2026-05-10) Indirect prompt injection top CVE category
  - `prediction.70ad45e258b72e8c` (hit 2026-05-10) Physical AI league tables OEM humanoids
- **0 contradict signals** in `prediction_evidence_links` for the 5/4-5/10 window (all 812 evidence links were `support` direction). No bridge/reasoning contradictions to chase.
- Broader change-signal candidate pool (predictions in 90-day active window with new validation rows in last 7d) = 50; over the per-week cap of 30. Next week's run should re-rank by `confidence_drift_score` and trim.

## Acceptance — this run

- DB backup `app/data/analytics.sqlite.pre-maintenance-20260510` was created and discarded (no Step 2 updates required a rollback).
- No `app/sourcedata/2026-05-10/maintenance-judgements.json` was produced.
- `memory/maintenance/queue.md` not updated (next Sunday's Step 0 will re-derive from current DB state regardless).
