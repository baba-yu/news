# Weekly maintenance — week ending 2026-08-02

## Scope

30 candidate predictions (the Step-0 cap), judged by 5 batched sub-agents at 6
predictions each, all four streams per prediction. **127 judgements** over 30
predictions.

| verdict | count |
|---|---|
| broken | 59 |
| stale | 46 |
| fresh | 22 |
| retire | 0 |

By stream: needs 36, bridge 31, readings 30, reasoning 30. Proposed actions:
79 `noop`, 48 `rewrite` (46 `stale` plus 2 `broken`-with-clear-fix). Confidence
0.55-0.95, mean 0.81.

Selection was thin. All 30 candidates carry only `landed_this_week` (20) and/or
`relevance_drift` (19); **no candidate was selected on a new chain edge, a new
relation edge, or a contradict signal**, because none of those three signals can
fire (see §1 and §6 below). Spillover to next Sunday: 37 predictions
(`memory/maintenance/queue.md`). Two of them — `prediction.a96ff0bdaae351aa` and
`prediction.cb8447f5c6e4c65d` — reached `weeks_starved = 4` and must be
force-promoted next week regardless of cap, per the spec's starvation guarantee.

Minor, in passing: `memory/maintenance/queue.md` carries its intro paragraph
**8 times**, once per week the step has run, because the writer appends its header
block instead of replacing it. Cosmetic, but it will keep growing. Not edited
here — the file is tool-owned output.

## ⚠️ What was actually applied: nothing

The 46 `stale` verdicts produced 46 `maintenance-update.<stream>.<pid>.json`
markers — one per `(prediction, stream)` pair, no collisions, no stale pair left
without a marker. **Those markers are inert.** `_stale_applied`
(`app/skills/weekly_maintenance.py:722`) checks only `.is_file()`, and no ingest
path in `app/` ever reads their contents. The rewrites they describe have **not**
reached `app/data/analytics.sqlite`.

So this section reads: *46 rewrites were identified and none were performed.*
The Step-3 gate passes anyway, because it tests for marker existence rather than
for applied change.

All 46 of this week's markers carry `"applied": false` and the note "NOT APPLIED.
maintenance-update markers are write-only: weekly_maintenance._stale_applied
checks only file existence and no ingest path reads this content." Earlier weeks'
markers asserted the opposite: 2026-07-19 (33 of 33), 2026-07-12 (6 of 6) and
2026-06-28 (2 of 3) all claim `"applied": true`. They are wrong, and it is
checkable — the 07-12 marker for `prediction.0bb5badc89f68769` claims
`"applied": true` and carries a complete `new_reasoning` bundle, while
`predictions.reasoning_because` in the DB today is still the original "Sonnet 5
launched at $2/$10 with claimed Opus-parity on agentic-search and computer-use
benchmarks." Verified directly this run. 2026-07-26's 57 markers already said
`false`.

The consequence shows up in the verdicts: judges repeatedly re-issued the same
finding against unchanged text and said so explicitly.
`prediction.6ba7ca6e01ab313e` needs is stale for the third consecutive week;
`prediction.a31a93089cef22da` needs is a verbatim re-affirmation of the 2026-07-19
escalation; `prediction.0b8bcb868b9c8fa5` needs re-issues the 07-19 `broken`
verdict unchanged. As one judge put it: "last week's marker file was never read by
anything, so re-reporting the identical defect is the correct outcome."

`retire` remains unenforceable and no `retire` verdict was issued this week. The
`predictions` table has **no `status` and no `reviewed_by_human` column** —
confirmed again against the live schema — so the spec's deterministic retire path
cannot execute at all.

## A second false-applied path

Found independently by three judges: `_stale_applied` Form 3
(`weekly_maintenance.py:724-732`) returns `True` when the *merged* stream file for
the week merely **contains the prediction id anywhere in its text**. The
stream-to-file map is `reasoning`/`readings` to `predictions.json`, `bridge` to
`bridges.json`, `needs` to `needs.json`. So any prediction that appears in this
week's merged files is reported "applied" for free, with no update of any kind
having been written for it.

Recorded plainly because it is a real defect and it will bite. The honest
empirical result for **this** week is that it changed nothing: the merged files
carry only the day's own output (3 new predictions, 26 bridge rows), and of the 4
candidate predictions that do appear in `bridges.json` (`16c7b8053e39aa1f`,
`359ad701e052546c`, `6b1c8cb1541ca0a5`, `eca92ec7ee67c161`) all four had `fresh`
bridge verdicts, which need no application. 0 of the 105 `stale`-plus-`broken`
judgements were satisfied by Form 3.

What *did* fire is the same function's granularity. Form 2 is keyed
`(prediction_id, stream)`, not `entry_id`, so a marker written for a `stale`
judgement also satisfies every other judgement on the same pair — including
`broken` ones that are supposed to go to a human. **Six `broken` needs judgements
are reported "applied" this week on the strength of a sibling marker**:
`0bb5badc89f68769`, `42a2372350593ef7`, `6ba7ca6e01ab313e`, `a31a93089cef22da`
(two distinct entry_ids) and `c43f854e46b748b1`. They are in `broken.md`
regardless.

## Systemic defects found

Each was found independently by multiple batches, which is why it is recorded here
rather than as a per-prediction finding.

1. **The readings stream is an outage, not per-prediction health.**
   `prediction_chain` holds 127 rows whose `created_at` spans
   2026-06-09T18:25:42Z..2026-06-10T10:34:13Z; `prediction_relations` holds 200
   rows all stamped 2026-06-09T18:25:42Z. Nothing has been extracted in 53 days.
   Of 324 predictions, **52 carry any edge** (48 chain, 52 relation) — and of the
   **160 predictions dated after 2026-06-10, exactly zero** do. All 30 of this
   week's candidates have zero edges. 30 of 30 were judged `broken` on readings.

   The reason this is the week it changed is not that the data changed. **Prior
   runs recorded this same stream as `fresh` at high confidence and thereby
   laundered a pipeline outage into per-prediction health.** Readings was scored
   100% `fresh` every week from 2026-05-05 through 2026-07-12 at mean confidence
   0.80-0.88, including five full weeks *after* the extractor died; **93 `fresh`
   readings verdicts were issued post-outage** before 2026-07-19 began to break
   the pattern. Judges quoted the exact laundering language they were overturning:
   "no chain or relation edges exist for this prediction; nothing to assess"
   (07-12, confidence 0.9). Fourteen concrete unmade edges were named from
   shared-evidence overlap *inside* the judges' own 6-prediction batches; see
   `broken.md`.

   Also worth a ticket: `prediction_relations.relation_type` is CHECK-constrained
   to `parallel|exclusive_variant|negation|entails|equivalent`, so a
   *contradicting* relation has no representable value even once extraction
   resumes.

2. **`landed_this_week` is a misnomer and fired on non-events.** The signal
   derives from `predictions.huge_longshot_hit_at`
   (`weekly_maintenance.py:190-199`), which `app/src/ingest.py:504` stamps whenever
   the literal string `[REVIVED]` appears in a validation row's
   `related_items_text` — a dormant-pool revival, not a prediction resolving.
   **All 20 of this week's `landed_this_week` candidates were stamped by a
   `[REVIVED]` row; none by a resolution.** Judges found the triggering bridge
   recorded an explicit non-event or a wrong-mechanism event in the large majority
   of cases — batch 4 reported 4 of its 5 — and quoted the rows: "No customer
   appears as an investor" (`04ff49878f99c77f`, 07-28); "The rate did not move, and
   that is most of what happened" (`0b8bcb868b9c8fa5`, 08-01); "No vendor repriced
   a mid-tier model today, in either direction" (same prediction, 07-27). Both
   quotes verified against the DB.

   A judge reading the signal name literally would misapply the
   Readings-to-Reasoning "upstream landed" rule. Separately the `[REVIVED]` marker
   is never stripped: it ships to readers verbatim in
   `future-prediction/en/future-prediction-20260802.md`. 407 validation rows carry
   it all-time; 53 predictions were stamped in the last 7 days.

3. **A one-day scoring blackout on 2026-07-28.**
   `prediction_realization_snapshots` has **zero rows for
   `validation_date='2026-07-28'`**, while 2026-07-27 has 1,644 and 2026-07-29 has
   1,677 (every date 07-20..08-02 falls in the 1,527-1,902 band). That date has
   **33 `validation_rows`** and 147 `prediction_evidence_links`. Verified
   independently this run: 2026-07-28 is the only date after 2026-06-08 that has
   validation rows and no snapshots at all. So one day's evidence never reached
   `realization_score`, `observation_status`, or the `confidence_drift_score` that
   drives candidate selection. Five `broken` bridge verdicts (batch 3) are this
   single defect. A separate ticket is filed; recorded here so the week's scores
   are read with it in mind.

   Adjacent finding from the same batch: snapshots **forward-fill**.
   `prediction.91ae7c2c7675fd1c` has no bridge after 2026-07-28 yet carries
   `observed_relevance=3 / realization 0.6` on 07-29, 07-30, 07-31, 08-01 and 08-02
   — five days of scored relevance with no evidence behind it. Same shape on
   `prediction.23b794192e56e85b`. That is a design decision to make, not just a
   fix.

4. **`parse_time_window` drops one end of a spanning `when_text`.** Reproduced
   against live code: `parse_time_window('H2 2026 through H1 2027')` returns
   `('2026-07-01','2026-12-31')`, silently discarding the second half. The
   precedence is "the first (or the landing-quarter) token wins":
   `'Now through Q4 2026'` gives `2026-10-01..2026-12-31`;
   `'Runway from June 2026 through Q2 2027'` gives `2027-04-01..2027-06-30`;
   `'Runway Jul-Sep 2026 (Q3 buildout quarter)'` gives September only.

   In one batch the judge found it corrupts **20 of 21** `needs_tasks` — the one
   survivor, `'H2 2026, during the preview-to-GA transition window.'`, is the
   single-token control. Re-derived directly this run. Project-wide: 162 tasks
   carry the exact string `'H2 2026 through H1 2027'`, 54 hold single-day windows,
   114 hold NULL windows, 431 hold a window identical to their prediction's own,
   and **544 have a runway that ends before their prediction's landing window
   opens** — actors recorded as finishing before the outcome they enable can occur.

   **This week's own 25 new Needs are unaffected.** Every one was written with a
   single-token window (`Q3 2026`, `October 2026`, `H2 2026`, `Q1 2027`, and so
   on), so the stored window equals the rendered text in all 25 cases. The defect
   is historical and per-batch; it is not being added to this week.

5. **The Bridge-to-Needs rule has no data path, and neither does delivery.**
   `validation_rows.contributes_to_task_id` is NULL on **all 1808 rows**, and
   `needs_tasks.status` is `open` on **all 1167 rows** — `done` and `blocked` have
   never been written by any code path. So the spec's flagship Bridge-to-Needs
   correlation cannot be recorded even when a judge identifies it precisely, and an
   elapsed Need window can be read as neither delivery nor failure. Judges hit this
   on substance repeatedly: `prediction.96b1b2cb6ad4924f` has SK hynix's own
   results describing the exact actors doing the exact job and declining the
   deliverable, with nowhere to record it. Related and unfixed since 2026-07-26:
   `extract_needs._is_complete_5w1h` omits `how`, so 17 tasks project-wide have
   `how_text` NULL yet `status='open'` instead of the schema-documented
   `'blocked'`.

6. **The contradict channel is still dead.**
   `prediction_evidence_links.support_direction` is `support` on **8867 of 8867**
   rows (7295 of 7295 last week — the ratio has not moved), with
   `contradiction_score` 0.0 throughout. Step 0's `new_contradict` gate can never
   fire, and the spec's Bridge-to-Reasoning correlation is unreachable from data.
   Every contradiction the judges found this week had to be read out of prose, and
   several said so in as many words.

## What the judges found on substance

Setting the defects aside, the 46 `stale` verdicts are the week's real analytic
output, and none of them landed.

- **Bridge-to-Reasoning was the dominant correlation** — 26 of the 46 `stale` are
  reasoning. The sharpest: `prediction.359ad701e052546c`, whose `because` asserts
  "a 1.4TB 4-bit checkpoint" from pre-release arithmetic while the published
  repository listing is 1.56 TB across 96 safetensors shards, about 11% above.
  `prediction.9cfa3212e98d1f5c`, whose `given` claims identifier assignment stays
  human-paced while both of 07-28's vulnerabilities arrived fully labelled, one at
  CVSS 10.0. `prediction.b177dc0150808a3d`, whose `given` says refusal filters key
  on content and not identity, against a Unit 42 reconstruction showing the
  opposite. `prediction.a31a93089cef22da`, whose entire framing premise (Samsung as
  the one large memory maker absent from the capital surge) broke on 07-30.
- **Needs-to-Reasoning "already historical"** recurs:
  `prediction.1ce328e19c9e6685`'s buyout Need is written prospectively but
  describes the prediction's own `because`; `prediction.42a2372350593ef7`'s
  two-quarter outcome is half-delivered at +257% YoY.
- **Missing actors rather than wrong ones**: `prediction.9cfa3212e98d1f5c`'s six
  Needs cover the whole supply side of the flaw and omit the CNA that the entire
  claim turns on; `prediction.91ae7c2c7675fd1c` omits the actor who actually
  determines whether the financing structure is copyable.
- One judge flagged a **stale future tense in shipped text**:
  `prediction.e997117d0c9d145c`'s bridge reads "due to be finalized by Saturday,
  August 1", August 1 has now passed inside the maintenance window, and no
  confirming item appears in `headlines.json`, `change_log.json` or
  `news_section.json`.

## Data defects escalated (see `broken.md`)

59 entries over 30 predictions, but **not 59 distinct problems**. Grouped there as:
the readings outage (30 entries, one root cause); the needs-window family (17, of
which 12 are `parse_time_window`, 2 are NULL windows, 2 are broken-with-clear-fix
date errors and 1 is the Bridge-to-Needs plumbing); and bridge (12, of which 5 are
the `[REVIVED]` landing-stamp leak, 5 are the 2026-07-28 blackout, and 2 are
genuinely per-row). The two genuinely per-row bridge defects are the ones to read
first.

## Health check

Step 0's assertion (predictions older than 90 days AND not in the dormant
snapshot) returned **49 rows**, all a single class — origin 2026-04-19 through
2026-05-03, dormant-detection leak — logged to `health.md`. Up from 24 rows on
2026-07-26 with the window sliding forward one week, which is consistent with the
leak growing rather than being drained by rotation.
