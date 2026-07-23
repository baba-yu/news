# Weekly maintenance — week ending 2026-07-19

## Scope

30 candidate predictions selected under the ≤30 weekly cap, plus **1 force-promoted**:
`prediction.bcace95fe3e753d1` had sat in `memory/maintenance/queue.md` for 4 consecutive
weeks unjudged, which is the starvation trigger in `6_weekly_maintenance.md` §Failure modes.
6 further candidates spilled to next week's queue.

31 predictions judged across all 4 streams by 6 batched sub-agents → **131 judgements**.

| verdict | count | | stream | fresh | stale | broken |
|---|---|---|---|---|---|---|
| fresh | 73 | | reasoning | 16 | 14 | 1 |
| stale | 34 | | bridge | 27 | — | 5 |
| broken | 24 | | needs | 14 | 10 | 13 |
| retire | 0 | | readings | 16 | 10 | 5 |

Fresh rate 56%, against 93% last week. That is a cohort effect, not over-eager judging:
most of the non-fresh verdicts are objective data defects rather than content drift, and
no prediction tripped the 4-stale-under-0.7-confidence judging-error guard.

## ⚠️ The rewrites in this run did NOT reach the database

33 `maintenance-update.<stream>.<pid>.json` markers were written (reasoning 14, readings 10,
needs 9) and `weekly_maintenance validate` passes clean. **That green is misleading.**

`_stale_applied()` (`app/skills/weekly_maintenance.py:722`) checks only that the marker file
EXISTS. The string `maintenance-update` appears nowhere else in `app/` except that check and
its docstring — no ingest path reads the contents. Verified against last Sunday's five
reasoning markers: **0 of 5 applied**; every one still carries its original
`reasoning_because` in `analytics.sqlite`.

The loop this creates is visible in this run's own data:
- `prediction.02bf6210bbfa3a6e` was judged stale on 2026-07-12, "rewritten", and judged stale
  again today against unchanged text.
- `prediction.4ecb84808c9acc3f`'s needs finding is a verbatim re-run of the 2026-07-12 finding.

These re-fire every week and consume slots under the ≤30 cap, starving new candidates.
**The 33 markers here are correctly authored and should be replayed once an ingest path
exists — they are the intended content, not throwaway.**

## Systemic defects found (all escalated, none auto-fixed)

Full per-prediction detail in `broken.md`. Eight distinct defects, most found independently
by more than one judge and all verified directly against the DB:

1. **Maintenance rewrites are never applied** — the write-only marker defect above.
2. **Time-window parser mis-anchors and drops tokens** (`app/src/timewindow.py`) — a trailing
   quarter/half beats an earlier runway start, so 431 of 809 windowed `needs_tasks` sit exactly
   on their prediction's landing window, which the schema explicitly forbids. Hyphenated
   quarters (`Q3-2026`) and bare modifier+year (`Mid-to-late 2026`) parse to `(None, None)`;
   59 of 114 NULL-window rows carry a readable period token.
3. **Readings edge extraction stopped** — `prediction_chain` last wrote 2026-06-10,
   `prediction_relations` 2026-06-09; 230 of 282 predictions have zero edges. Earlier runs
   recorded this as per-prediction `fresh`, converting an outage into a healthy verdict.
4. **Contradiction cannot be recorded** — all 6,626 `prediction_evidence_links` are
   `support_direction='support'` with `contradiction_score=0.0`. Step 0's `new_contradict`
   signal and the spec's flagship Bridge→Reasoning rule are both unreachable.
5. **`needs_tasks.status` never transitions** — all 923 rows `'open'`; `'done'` never written.
6. **Bridge text attributed to the wrong prediction** — several `validation_rows` carry a
   `bridge_text` about a different prediction while `related_items_text` is correctly on-topic;
   the mismatched text scores as supporting evidence at relevance 3-4.
7. **`entails` double-encoding** — 12 of 14 `entails` relations are recorded both in
   `prediction_relations` and as a `prediction_chain` edge, which the schema comment forbids.
8. **`prediction_summary` generation stub** — terminates in a repeated `"In plain language:"`
   with no body, across 44 predictions.

Two naming traps worth carrying forward: `landed_this_week` is set from `huge_longshot_hit_at`,
which is a **dormant-revival** marker, not a landing — treating it as realization would wrongly
retire live predictions. And pre-2026-07-06 sourcedata is keyed under prediction ids that no
longer exist (185 of 280 keys); because ingest is upsert-only with no DELETE, re-ingesting those
days would mint ~185 orphan predictions.

## Force-promoted prediction

`prediction.bcace95fe3e753d1` deserved promotion. It is the most decayed item in the cohort —
the only one down to `observed_relevance 2 / realization 0.4` while its batch peers hold at
3/0.6, with three consecutive adverse bridges in four days, and its core landing condition
(≥3 vendor 20-30B dense releases) recorded unmet by its own bridges continuously since
2026-04-24 with ~10 weeks left. It is also the batch's most connected node (4 downstream chain
edges), so its decay propagates.

**Root cause of the starvation:** `confidence_drift_score` counts discrete change-signals, so a
prediction that decays *monotonically* never generates a `landed_this_week` or `relevance_drift`
event and is invisible to the ranking. Worth a Step 0 amendment rather than repeated
force-promotion.

## Gates

| gate | result |
|---|---|
| `weekly_maintenance validate --week-ending 2026-07-19` | OK, clean (exit 0) |
| `post_update_validation --check all` | see daily-briefing step |
| `lint_markdown_clean --date 2026-07-19` | OK, 8 files clean |

Glossary: 0 candidate terms this week (all within the 14-day `glossary_audit` TTL).
