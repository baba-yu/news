# Weekly maintenance — week ending 2026-07-26

## Scope

30 candidate predictions (the Step-0 cap), judged by 5 batched sub-agents at 6
predictions each, all four streams per prediction. **123 judgements** over 30
predictions.

| verdict | count |
|---|---|
| stale | 58 |
| fresh | 54 |
| broken | 10 |
| retire | 1 |

By stream: bridge 32, needs 31, readings 30, reasoning 30.

Spillover to next Sunday: 13 predictions (`memory/maintenance/queue.md`).

## ⚠️ What was actually applied: nothing

The 58 `stale` verdicts produced 57 `maintenance-update.<stream>.<pid>.json`
markers (one collision on a repeated stream+prediction pair). **Those markers are
inert.** `_stale_applied` (`app/skills/weekly_maintenance.py:722`) checks only
`.is_file()`; nothing in `app/` ever reads their contents. Verified on 2026-07-19
that 0 of 5 of the 2026-07-12 reasoning markers reached the DB.

So this section should be read as: *58 rewrites were identified and none were
performed.* The Step-3 gate will pass regardless, because it tests for marker
existence rather than for applied change.

The single `retire` verdict (`prediction.5e0beac647793331`, resolved at the AMD
Advancing AI keynote on 07-23) is likewise unenforceable: the `predictions` table
has **no `status` or `reviewed_by_human` column** — both exist only on
`glossary_terms` — so the spec's deterministic retire path cannot execute.

A consequence worth naming: verdicts recur weekly against unchanged text. Judges
were briefed on this and labelled repeats explicitly. Batch A reported 4 of its 12
stale and 3 of its 4 broken as unapplied prior work; batch C reported 4; batch D
reported 3; batch E reported 2 with a changed basis. Batch B's 15 stale were all
first-time calls.

## Systemic defects found

Several were found independently by multiple agents, which is why they are
recorded here rather than as per-prediction findings.

1. **The readings stream is frozen project-wide.** `prediction_chain` max
   `created_at` = 2026-06-10, `prediction_relations` max = 2026-06-09 — zero edges
   in 46 days, from a single backfill. Only 48/303 and 52/303 predictions have any
   edge. **All 30 `readings` verdicts share this one root cause.** Found by A, B,
   C, D and E independently.
2. **The contradict channel is dead.** `prediction_evidence_links.support_direction`
   is `support` on **7295/7295** rows all-time. Step 0's `new_contradict` gate can
   never fire, and the spec's flagship Bridge→Reasoning correlation is unreachable
   from data. Bridges that argue *against* their prediction are stored as support.
3. **`landed_this_week` is a misnomer.** It is derived from
   `predictions.huge_longshot_hit_at`, which ingest stamps on any `[REVIVED]`
   dormant-pool bridge — not on a prediction resolving. Most candidates this week
   carried only this signal, and in at least two cases the triggering bridge
   records an explicit *non-event*. A judge reading the name literally would
   misapply the Readings→Reasoning "upstream landed" rule.
4. **The quarter-trap contaminates historical needs windows.** `parse_time_window`
   discards the stated runway start: `"Runway from June 2026 through Q2 2027"` →
   `('2027-04-01','2027-06-30')`. **431 of 899** non-null `needs_tasks` windows are
   identical to their prediction's landing window, which the schema says they must
   not be. Also produces degenerate single-day windows
   (`2026-07-08..2026-07-08`) from a date mentioned inside a range. Not fixable by
   per-prediction rewrites.
5. **`_is_complete_5w1h` omits `how`.** `app/skills/extract_needs.py:57` checks
   only who/what/where/when/why while the `cells` tuple below it includes `how`.
   17 tasks project-wide have `how_text` NULL yet `status='open'` instead of the
   schema-documented `'blocked'`.
6. **`created_at` is worthless as a vintage signal.** `prediction_needs` and
   `validation_rows` are truncate-and-rebuild on every ingest, so both carry
   today's date on essentially every row.

## Data defects escalated (see `broken.md`)

10 entries. Notable:

- `prediction.41589b1968c4543f.prediction_summary` is corrupted — "In plain
  language:" appears 3×, the body ends with two empty repetitions, and the first
  two-thirds is wrapped in a stray `**…**` span. Four prior weekly reviews
  returned `fresh` and missed it.
- `validation.48fb619b7e9f55c0` (05-13) is a 98.3% duplicate of
  `validation.8d7f80058cbad309` (05-12) — `bridge_text` byte-identical after a
  Tuesday→Wednesday substitution, re-dating a Tuesday event to Wednesday while
  citing Tuesday's articles.
- `future-prediction/en/future-prediction-20260704.md` has shuffled bridge
  paragraphs — `bridge_text` attached to the wrong prediction while the same row's
  `related_items_text` is correct. Confirmed on ≥5 validation rows. Source-level,
  not an ingest fault.
- `validation.5b732ffe3f54c82f` (07-26) carries bridge text that is an explicit
  counter-example, yet is scored `observed_relevance=5` with
  `realization_score=1.0` and `observation_status='supported'`.
- `prediction.6095c8445805dcf4` rests on a retracted premise: its body asserts
  "reported $8-10B Tenstorrent talks", publicly denied 2026-06-30 and reiterated
  07-03. It was judged all-fresh on 07-12, *after* the denial.

## Health check

Step 0's assertion (predictions older than 90 days AND not dormant) returned **24
rows**, all origin 2026-04-19 → 04-26 — logged to `health.md`. This corroborates
the dormant-pool leak quantified during Step 4 the same day: of 280 predictions
with origin ≤ 07-19, only 118 were in the previous snapshot; this week's rotation
recovered 36, leaving roughly 126 unreachable.

## Outside-batch finding

`prediction.9bc46d8a918d51a2` ("MI400 launches with a named ship, memory, or rack
spec by Q3 2026", landing text naming the AMD Advancing AI July 22-23 keynote) had
its landing condition satisfied on 2026-07-23 — Helios in full production, MI455X,
named gigawatt customers — yet its newest bridge is 2026-07-05,
`huge_longshot_hit_at` is NULL, and it was not selected as a candidate. Its
resolution is the precondition for `prediction.cc109942df2a6460` and no edge
records it.
