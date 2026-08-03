# Broken entries — week ending 2026-08-02

Data inconsistencies escalated for human review. NOT auto-fixed, per
`design/scheduled/6_weekly_maintenance.md` Step 2.

**59 `broken` verdicts over 30 predictions — but far fewer than 59 problems.**
Two code defects account for 42 of them. This file is grouped so a reviewer can
act on the root causes once instead of thirty times. **Only the two entries in
§D.3 are genuinely per-row**; everything else is an instance of a group. Read
§D.3 first, then the four root-cause tickets: the extractor (§A), the parser
(§B.1), the `[REVIVED]` stamp (§D.1) and the 2026-07-28 re-score (§D.2).

Note on Step-3 accounting: six of the entries below (§B.1 `prediction.0bb5badc89f68769`,
`prediction.42a2372350593ef7`, `prediction.6ba7ca6e01ab313e` and `prediction.c43f854e46b748b1`; §B.2
`prediction.a31a93089cef22da` ×2) are reported "applied" by
`weekly_maintenance._stale_applied` because a *sibling* `stale` judgement on the
same `(prediction, stream)` pair got a marker file. They are escalations, not
applied fixes. The gate will not tell you that.

---

## §A — Readings: edge-extraction outage (30 entries, ONE defect)

**Do not action these per prediction.** All 30 candidates were judged `broken` on
readings for the same reason, found independently by all five batches.

- `prediction_chain`: 127 rows, `created_at` 2026-06-09T18:25:42Z ..
  2026-06-10T10:34:13Z. `prediction_relations`: 200 rows, all
  2026-06-09T18:25:42Z. Nothing extracted in 53 days.
- 52 of 324 predictions carry any edge (48 chain, 52 relation). Of the 160
  predictions dated after 2026-06-10, **zero** do.
- All 30 candidates have zero edges in either direction; most were minted inside
  the dead window and were never eligible for one.
- Prior runs scored this stream `fresh` at confidence 0.8-0.9 — 93 such verdicts
  after the outage began — which converted a dead pipeline into a health signal.
  That is why the verdict is `broken` and not `fresh`.

**Action:** one ticket on the chain/relation extractor. Per-prediction rewrites
cannot produce edges, and Step 2 cannot apply them if they could.

**Secondary, same ticket:** `prediction_relations.relation_type` is
CHECK-constrained to `parallel|exclusive_variant|negation|entails|equivalent`.
A *contradicting* relation is not expressible even after extraction resumes.
Flagged by four judges independently.

**Named unmade edges** (the reviewer's regression set — each is a `parallel`
candidate the judges verified from shared evidence *inside* a single 6-prediction
batch):

| pair | shared basis |
|---|---|
| `prediction.0b8bcb868b9c8fa5` ↔ `prediction.0bb5badc89f68769` | `evidence.54ee76ae9206d639` (OpenAI GPT-5.6 launch); both are mid-tier repricing claims |
| `prediction.0b8bcb868b9c8fa5` ↔ `prediction.14cd36ae7a6a8633` | `evidence.276435801946ac94` (Kimi K3 repo listing, 1.56 TB / 96 shards), read in opposite directions |
| `prediction.0b8bcb868b9c8fa5` ↔ `prediction.fd7bdbc998adaac2` | 3 shared evidence items (OpenRouter Kimi K3 pricing, DeepSeek V4-Flash-0731 card, Kimi K3 licence) |
| `prediction.14cd36ae7a6a8633` ↔ `prediction.fd7bdbc998adaac2` | `evidence.7372d8cb937a6ab6` (Moonshot Kimi K3 model card) |
| `prediction.359ad701e052546c` ↔ `prediction.eca92ec7ee67c161` | 8 shared evidence items — Unsloth v0.1.51-beta, PRs 7616/7619/7685/7687, tags page. Largest overlap found. |
| `prediction.359ad701e052546c` ↔ `prediction.23b794192e56e85b` | OpenRouter Kimi K3 hosted-pricing page / Kimi K3 licence |
| `prediction.5c41341a6a3b81a6` ↔ `prediction.e997117d0c9d145c` | 3 shared items, 07-27 Open Secure AI Alliance cluster; both turn on the same White House framework and its Aug 1 date |
| `prediction.4dba2dbfb8d2798b` ↔ `prediction.6ba7ca6e01ab313e` | same MemGhost disclosure (07-13) and same YC `qm` launch (08-01), bridged twice each |
| `prediction.6b1c8cb1541ca0a5` ↔ `prediction.a31a93089cef22da` | identical Samsung 07-30 Q2 release, graded rel 5 `so_that` on one and rel 4 `landing` non-event on the other |
| `prediction.6d2fa8b171b201e4` ↔ `prediction.70b4b143e969eb36` | same Kimi K3 weights release, both 07-27 |
| `prediction.70b4b143e969eb36` ↔ `prediction.9cfa3212e98d1f5c` | Kimi-K3-versus-Redis campaign is one's bridge and the other's originating event |
| `prediction.70b4b143e969eb36` ↔ `prediction.b177dc0150808a3d` | identical `because` — the Hugging Face intrusion |
| `prediction.299950dc17b30ddd` ↔ `prediction.2d800e2dfed12361` | shared `source.0c139537e17c33b8`, wolfSSL CVE-2026-5194 / Project Glasswing substrate |
| `prediction.2d800e2dfed12361` ↔ `prediction.9cfa3212e98d1f5c` | Redis non-standardised-disclosure pair; the 07-26 marker already specified this edge |

**Three of these edges were already specified in prior weeks' markers and never
written**, which is the outage and the write-only Step 2 compounding:
`app/sourcedata/2026-07-19/maintenance-update.readings.prediction.25bbb1fc4e3ce653.json`
(three verified edges enumerated), and the 2026-07-26 equivalents for
`prediction.2d800e2dfed12361` and `prediction.3049b69e910c2279`. The DB still
shows zero rows for all of them.

Full list of the 30: `prediction.04ff49878f99c77f`, `prediction.0b8bcb868b9c8fa5`, `prediction.0bb5badc89f68769`,
`prediction.14cd36ae7a6a8633`, `prediction.1401756144573103`, `prediction.16c7b8053e39aa1f`, `prediction.1ce328e19c9e6685`,
`prediction.23b794192e56e85b`, `prediction.25bbb1fc4e3ce653`, `prediction.299950dc17b30ddd`, `prediction.2d800e2dfed12361`,
`prediction.3049b69e910c2279`, `prediction.359ad701e052546c`, `prediction.42a2372350593ef7`, `prediction.4dba2dbfb8d2798b`,
`prediction.5c41341a6a3b81a6`, `prediction.6b1c8cb1541ca0a5`, `prediction.6ba7ca6e01ab313e`, `prediction.6d2fa8b171b201e4`,
`prediction.70b4b143e969eb36`, `prediction.91ae7c2c7675fd1c`, `prediction.96b1b2cb6ad4924f`, `prediction.9cfa3212e98d1f5c`,
`prediction.a31a93089cef22da`, `prediction.b177dc0150808a3d`, `prediction.c43f854e46b748b1`, `prediction.e4dd413b5cb0ee24`,
`prediction.e997117d0c9d145c`, `prediction.eca92ec7ee67c161`, `prediction.fd7bdbc998adaac2`.

---

## §B — Needs: window defects (17 entries, mostly ONE defect)

### §B.1 — `parse_time_window` span loss (12 entries, one code defect)

`parse_time_window` binds one period token and discards the rest of a spanning
`when_text`. Reproduced live by three judges against `app/src/timewindow.py` and
re-verified this run. Project-wide: 162 tasks carry the exact string
`'H2 2026 through H1 2027'`; 431 tasks hold a window identical to their
prediction's own; **544 tasks have a runway ending before their prediction's
landing window opens**.

**Fix the parser, not the twelve predictions.** A Step-2 content rewrite would be
overwritten on the next `extract-needs` run.

| prediction | when_text | stored | why it is wrong |
|---|---|---|---|
| `prediction.04ff49878f99c77f` | `H2 2026 through H1 2027` (all 4 tasks) | 2026-07-01..2026-12-31 | second half of the stated runway gone. The 2026-07-26 judge saw this and wrote "noted but not escalated" |
| `prediction.0b8bcb868b9c8fa5` | `Late 2026 through Q2 2027…` / `Continuously through the runway to Q2 2027.` | 2027-04-01..2027-06-30 | landing quarter outranks the runway phrase. Re-affirming the 2026-07-19 `broken`; control task `prediction.fc8d99e71c99fd37` parses correctly |
| `prediction.0bb5badc89f68769` | `Now through Q4 2026` / `Model-training runway through Q4 2026 launch` | 2026-10-01..2026-12-31 | work starts July; the stored runway does not open until October, missing the quarter the 07-09 Terra launch fell in |
| `prediction.1401756144573103` | `H2 2026 through early 2027` (all 3) | 2026-07-01..2026-12-31 | prediction window is 2027-01-01..2027-03-31, so every Need closes before the landing opens |
| `prediction.14cd36ae7a6a8633` | `Now through H1 2027 release cycles` / `After upstream engines ship, through H1 2027` | 2027-01-01..2027-06-30 | vLLM shipped 07-27 and Ollama 07-05 — both inside the writer's "Now", both outside the stored window |
| `prediction.42a2372350593ef7` | `Runway Jul-Sep 2026 (Q3 buildout quarter)` | 2026-09-01..2026-09-30 | only the trailing month kept. The other two Needs on the same prediction parsed the same quarter correctly, which isolates it as a parse defect |
| `prediction.4dba2dbfb8d2798b` | `July 2026 through H1 2027` (all 3) | 2027-01-01..2027-06-30 | collapsed exactly onto the prediction window; eighteen months of runway gone |
| `prediction.6b1c8cb1541ca0a5` | `today through Q2 2027 runway` (both) | 2027-04-01..2027-06-30 | both Needs read as beginning nine months after the work must start |
| `prediction.6ba7ca6e01ab313e` | `H2 2026 through Q1 2027` / `ongoing through 2026 into Q1 2027` | 2027-01-01..2027-03-31 | **third week unfixed** — escalated 2026-07-19, re-affirmed 07-26 and again now |
| `prediction.6d2fa8b171b201e4` | `H2 2026 through H1 2027` (all 3) | 2026-07-01..2026-12-31 | runway closes six months before the 2027-01-01 landing opens. Also carries the `how_text` NULL defect (§C) |
| `prediction.c43f854e46b748b1` | `refereeing push from July 2026 into early 2027` | 2026-07-01..2026-07-31 | **the only expired window in the set** — lapsed 2026-07-31, two days before week end, on a Need that is manifestly still live. Highest priority instance |
| `prediction.fd7bdbc998adaac2` | `H2 2026 through H1 2027` (all 7) | 2026-07-01..2026-12-31 | `app/src/schema.sql` documents `needs_tasks.target_*` as the runway, so this is a wrong value and not a modelling choice |

Batch 4 (`prediction.04ff49878f99c77f`, `prediction.0b8bcb868b9c8fa5`, `prediction.0bb5badc89f68769`,
`prediction.1401756144573103`, `prediction.14cd36ae7a6a8633`, `prediction.fd7bdbc998adaac2`) is the clean measure:
**20 of its 21 `needs_tasks` are corrupted.** The single survivor is
`'H2 2026, during the preview-to-GA transition window.'` — the only single-token
`when_text` in the batch.

### §B.2 — NULL windows (2 entries, same prediction, distinct Needs)

Both re-affirm the 2026-07-19 escalation, verified unchanged today. Distinct from
§B.1: a NULL window makes the Need invisible to *any* expiry or liveness check,
which is worse than a lossy one.

- **`prediction.a31a93089cef22da`** — entry_id `Large memory-maker's HBM/advanced-DRAM fab and process-engineering team`.
  `need.33cbcc782a0de2d1` / `need_task.9b7e0a61ff769577`: both `target_start_date`
  and `target_end_date` NULL against `when_text` "Mid-to-late 2026
  capacity-planning cycle". The third Need on the same prediction
  (`need.ebf3e53f7f2a2f2f`) parsed "H2 2026, ahead of Q4-2026 earnings" correctly,
  which proves the parser can succeed here.
- **`prediction.a31a93089cef22da`** — entry_id `Large memory-maker's investor-relations and earnings-communications team`.
  `need.5d9a923bd537d65f` / `need_task.a84adf6acf942e1c`: both NULL against an
  unambiguous parseable runway, "Q3-2026 and Q4-2026 earnings-prep cycles". It
  matters this week because `validation.5c1dc15555584996` (07-30) shows the Q3
  half is now the only remaining venue before the Q1 2027 deadline.

Kept as two entries deliberately, so they do not collapse under the merge's
`(prediction_id, stream, entry_id)` dedupe and lose the 07-19 granularity.

### §B.3 — Broken with a clear fix: dates that predate their own prediction (2 entries)

The only two `broken` judgements carrying `proposed_action: rewrite`. Both are
lead Needs — the Need the whole prediction hangs on — and both have an unambiguous
correction available from the task's own text.

- **`prediction.299950dc17b30ddd`** — entry_id `CISA inter-agency coordination lead inside the Joint Cyber Defense Collaborative`.
  `need.155ec97511478170` carries 2026-04-01..2026-06-30. That window **opens
  before the prediction was made** (`prediction_date` 2026-05-30), closed five
  weeks ago, sits a full year before the prediction's 2027-07-01..2027-09-30
  target, and contradicts its own task `need_task.6d536473951543c0`, whose
  `when_text` reads "Q2 2026 through Q2 2027 MoU drafting and inter-agency
  clearance window". Nothing has been delivered against it —
  `validation.4d1ed88cbce397cd` (07-28) records no cross-sector advisory for
  either of that day's AI-found flaws. **Correction: extend to 2027-06-30.**
- **`prediction.3049b69e910c2279`** — entry_id `Threat-intelligence research analyst at a major security vendor`.
  `need.42b1cd2555aa159b` carries `target_start_date = target_end_date =
  2026-07-08` — a single day that **predates the prediction** (`prediction_date`
  2026-07-09) and closed 26 days before this review — while its task
  `need_task.49540afe078f1d85` reads "H2 2026, ramping investigation after the
  July 8 2026 JADEPUFFER disclosure." The window was populated from the source
  article's date. One of 54 single-day need windows project-wide. **Correction:
  extend to 2026-07-08..2027-06-30 per the task text.** Escalated in identical
  form on 2026-07-26 and unfixed.

### §B.4 — Bridge-to-Needs has no data path (1 entry)

- **`prediction.96b1b2cb6ad4924f`** — the Need content is the strongest in its
  batch (six Needs covering both sides of the deal: Etched sourcing lead, SK hynix
  strategic-accounts BD lead, memory-system architect, HBM capacity planner, rack
  buyer, comms lead) and needs **no rewrite**. What is broken is the plumbing. The
  07-29 bridge (`validation.4271c9094f3b9fe6`) should attach to
  `need.508b15d1e3735d48` and `need.616e2e843b048aeb` — SK hynix's own results
  describe roughly 10 long-term supply agreements and 2027 allocation visibility,
  the exact actors doing the exact job and declining the deliverable. That link
  cannot be recorded: `contributes_to_task_id` is NULL on **1808 of 1808**
  `validation_rows` and `needs_tasks.status` is `open` on **1167 of 1167** rows.
  All six tasks additionally carry the §B.1 mis-parse.

---

## §C — Standing schema blockers (no per-prediction action possible)

Named repeatedly across §A and §B; listed once so they are not re-litigated.

1. `needs_tasks.status` is `open` on 1167/1167 rows. `done` and `blocked` have
   never been written. Delivery is not representable.
2. `validation_rows.contributes_to_task_id` is NULL on 1808/1808 rows. The
   Bridge-to-Needs edge has no storage.
3. `extract_needs._is_complete_5w1h` (`app/skills/extract_needs.py:57`) omits
   `how`. 17 tasks project-wide have `how_text` NULL yet `status='open'` instead
   of the schema-documented `'blocked'`. Flagged 2026-07-26, unfixed. Instance
   this week: `need_task.b531f05014db14a6` on `prediction.6d2fa8b171b201e4`.
4. `predictions` has no `status` and no `reviewed_by_human` column, so `retire`
   cannot execute. No `retire` verdict was issued this week; the blocker stands.
5. `prediction_evidence_links.support_direction` is `support` on 8867/8867 rows,
   `contradiction_score` 0.0 throughout. No automated contradiction check is
   possible; every counter-signal below had to be read out of prose.

---

## §D — Genuinely per-prediction (the ones to read)

### §D.1 — `[REVIVED]` landing-stamp leak (5 entries, one code defect + a rendering leak)

`app/src/ingest.py:504` stamps `predictions.huge_longshot_hit_at` whenever the
literal `[REVIVED]` appears in `related_items_text`. That column is the sole
source of the `landed_this_week` change-signal. **All 20 of this week's
`landed_this_week` candidates were stamped this way; none by a resolution.** The
marker string is also never stripped and ships to readers verbatim in
`future-prediction/en/future-prediction-20260802.md`.

Five bridge rows were escalated individually because their own text records the
opposite of a landing:

| prediction | row / date | what the row actually says |
|---|---|---|
| `prediction.04ff49878f99c77f` | `validation.fedfba549f5e1e4d`, 07-28 | "No customer appears as an investor" — no operator led, the money came from Churchill Capital Corp XI |
| `prediction.0b8bcb868b9c8fa5` | `validation.c5afdf03c01a74a3`, 08-01 | "The rate did not move, and that is most of what happened." Sibling `validation.e8a86f3501a41320` (07-27): "No vendor repriced a mid-tier model today, in either direction." |
| `prediction.0bb5badc89f68769` | `validation.273e8dd9209add75`, 07-31 | "the premise is a price and a benchmark, and Google published neither" |
| `prediction.1401756144573103` | `validation.b3ac1960e4966959`, 07-31 | "What left the machine was a package the model wrote, not a user's files" — neither a harness upload nor an outside-interceptor finding |
| `prediction.14cd36ae7a6a8633` | `validation.5fb27e4950a9e4d5`, 07-27 | records a precondition hardening; the prediction's window is H1 2027, so nothing could have landed |

In every one of the five, **the bridge prose is accurate and needs no rewrite**.
The defects are the marker handling and the derived signal. Judges were explicit
about this to avoid a reviewer "fixing" good text.

### §D.2 — 2026-07-28 scoring blackout (5 entries, one pipeline defect)

`prediction_realization_snapshots` holds **zero rows for
`validation_date='2026-07-28'`** while 07-27 has 1,644 and 07-29 has 1,677, and
that date carries 33 `validation_rows` and 147 `prediction_evidence_links`. It is
the only date after 2026-06-08 with validation rows and no snapshots. Verified
independently this run. Each row below exists and was never scored:

- `prediction.6d2fa8b171b201e4` / `validation.51a5d1c91b207ab3`, rel 4
- `prediction.70b4b143e969eb36` / `validation.c63521c1afad2738`, rel 4 — the 8-bridge run
  07-24..07-31 is the strongest in its batch and argues against its own prediction
  twice
- `prediction.91ae7c2c7675fd1c` / `validation.64f9ea8fe72ab143`, rel 3 — **and this is the
  prediction's last bridge**; a keyword sweep of 07-29..08-02 finds essentially no
  power/utility/interconnection coverage, so the topic left the feed
- `prediction.9cfa3212e98d1f5c` / `validation.4c45723536f64ffc`, rel 3 — **worst case**: the
  prediction has only three bridges and this one is the strongest counter-case
  against its own `given`
- `prediction.b177dc0150808a3d` / `validation.db8532b688105663`, rel 4 — three of its seven
  bridges argue against the prediction

**Action: re-score 2026-07-28.** Do not rewrite any bridge text.

**Related, needs a decision rather than a fix — snapshot forward-fill.**
`prediction.91ae7c2c7675fd1c` has no bridge after 07-28 yet carries
`observed_relevance=3 / realization 0.6` on 07-29, 07-30, 07-31, 08-01 and 08-02:
five days of scored relevance with no evidence behind them. Same shape on
`prediction.23b794192e56e85b` (last bridge 07-27, rel 2 / 0.4 emitted daily
through 08-02). The dashboard therefore shows a current reading that no current
evidence supports.

### §D.3 — Two genuinely per-row bridge defects

These are the only two entries in this file that are not an instance of a group.

- **`prediction.1401756144573103` — `validation.6cdaf9caf30058af`** (confidence
  0.75). *Internal contradiction between the row's own two fields, plus a
  dimension tag its body refuses.* The row is tagged
  `support_dimension='landing'` and its `bridge_text` asserts flatly "This reads
  as the second instance arriving", while its own `related_items_text` says the
  opposite: "whether it is genuinely distinct from the prior Grok finding or the
  same behavior resurfacing is not established today", and "a cleanly documented,
  discrete second instance is the piece still loose". The subject is xAI's Grok
  Build — the *same* harness as the origin finding (the 07-15 mitmproxy capture of
  Grok build CLI 0.2.93, open-sourced as `xai-org/grok-build` on 07-16).
  `need.cca583b7e5f96b5b`'s outcome requires "a coding agent other than Grok CLI"
  and `reasoning.so_that` requires "another coding agent", so a landing-tagged row
  on the origin harness cannot be the landing. **The rendered summary drops the
  hedge the source row carries, and that is the part readers see.**
- **`prediction.e4dd413b5cb0ee24` — `validation.7f522bf61f371525`** (confidence
  0.7). *Scoring contradicts the row's own text.* The 2026-07-28 row carries
  `support_dimension='given'` and `observed_relevance=4`, and it is the row that
  stamped `huge_longshot_hit_at=2026-07-28`. But its `related_items_text` opens
  with `[REVIVED]` and its `bridge_text` argues the premise is being *relieved*,
  not confirmed. The effect on derived columns is measurable:
  `prediction_realization_snapshots` ran `no_signal / 0.2` through 2026-07-27 and
  flipped to `supported / 0.8` from 2026-07-29 through 2026-08-02 on the strength
  of a row that reads against the thesis. A counter-signal is being scored as
  strong support *and* is driving queue selection. Human review of the
  dimension/relevance assignment required.
