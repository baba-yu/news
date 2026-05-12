# 6_weekly_maintenance — skipped 2026-05-10

This Sunday's `6_weekly_maintenance` run was **skipped** during the post-outage catch-up that produced `2026-05-10`'s artifacts.

## Why this run was skipped

Scope-based deferral, not a signal-availability problem:

- The original `0_daily_master` scheduled run did not execute on 5/10 (Claude Desktop was updating; the host was down). The catch-up run prioritized restoring the strict-gate artifacts (news + future-prediction × 4 locales + dormant + theme review + READMEs + dashboard exports). Running the full 30-prediction Judge fan-out on top of that would have meaningfully extended an already-long catch-up turn.
- The maintenance step is **idempotent across missed Sundays** per `design/scheduled/6_weekly_maintenance.md`: "Idempotent: if a Sunday is missed, the next Sunday's gate naturally picks up the same change-signal entries (and any new ones from the missed week)."
- The strict completion gate (`daily-flow-check --strict`) does not require maintenance outputs.

## Gate signals — what was firing this week

Step 0 SQL's change-signal UNION had ample fires:

- **Relevance W/W swing** (`ABS(observed_relevance - prev_week) >= 2`): the broader candidate pool (predictions in 90d active window with new validation rows in last 7d) reached **50 predictions** — well above the per-week cap of 30. Next Sunday's run should re-rank by `confidence_drift_score` (count of distinct change-signals × magnitude) and trim.
- **`huge_longshot_hit_at` last 7 days = 6 hits** — these predictions landed and their `reasoning` likely needs reframing from forward-looking to historical fact:
  - `prediction.5acccd6cae1f9b03` (hit 2026-05-05) Frontier-model previews SOC 2 + FedRAMP + FMF baseline
  - `prediction.11c2c648527fe212` (hit 2026-05-05) Capital markets reprice agent-displaced SaaS
  - `prediction.082b0a07077870dd` (hit 2026-05-06) GGUF supply chains signed cards + SSTI scans
  - `prediction.c08481a657991ec8` (hit 2026-05-10) Agent registry standard converges with MCP
  - `prediction.995feb039ef043c1` (hit 2026-05-10) Indirect prompt injection top CVE category
  - `prediction.70ad45e258b72e8c` (hit 2026-05-10) Physical AI league tables OEM humanoids
- **Chain / relation edge changes**: not enumerated this run, but the trigger is live.

## Note on `support_direction='contradict'` (the dead clause in Step 0 SQL)

The Step 0 SQL still contains a vestigial `SELECT prediction_id FROM prediction_evidence_links WHERE support_direction = 'contradict'` clause. It will never fire — not because of a bug, but because the **contradiction axis was retired by design in the 2026 scoring redesign**. Per `app/src/analytics/scoring.py` module docstring:

> "Contradiction as a separate signal is gone. Real counter-evidence is rare; 'a prediction didn't play out' is already captured by a low `realization_score`, so we don't need a second axis."

The relevance W/W swing trigger (item ② above) is the post-redesign equivalent — a downward swing from `rel=5→2` is exactly what the old `support_direction='contradict'` was meant to catch. The clause should be removed from the spec; see `design/decisions/ADR-001-contradiction-axis-retirement.md` (when written).

## Acceptance — this run

- DB backup `app/data/analytics.sqlite.pre-maintenance-20260510` was created and discarded (no Step 2 updates ran; nothing to roll back).
- No `app/sourcedata/2026-05-10/maintenance-judgements.json` was produced.
- `memory/maintenance/queue.md` not updated (next Sunday's Step 0 will re-derive candidates from current DB state regardless).
