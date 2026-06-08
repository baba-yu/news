# Weekly maintenance — week ending 2026-06-07

Sunday slot 5.5 (`6_weekly_maintenance`). Run shape: Step 0 candidates → Step 1 judge (3 batched sub-agents) → merge → Step 2 update (4 sub-agents) → Step 3 validate.

## Step 0 — candidates
- 20 predictions selected, 0 glossary terms, spillover 0, health_warnings 0 (no >90-day non-dormant leak).

## Step 1 — judge (20 predictions × 4 streams)
- Judged across reasoning / bridge / needs / readings with cross-stream awareness.
- **7 stale (prediction, stream) pairs** across 4 predictions; everything else fresh/noop (conservative — landed-this-week signals were mostly confirmatory, not resolving).

## Step 2 — update (forward-reframe; EN deltas authoritative)
| Prediction | Streams | Reframe |
|---|---|---|
| `prediction.27edd133aaf6687a` — Federal AI procurement mandates frontier-model cyber attestations | reasoning, needs | June-2 cyber EO signed → precondition satisfied; point forward to the unresolved OECD 16-jurisdiction recognition leg. OSTP signing-coordinator Need → done. |
| `prediction.3ac3816759e9ba15` — Anthropic files confidential S-1 by Q2 2027 | reasoning, needs | Filed ~10 months early → `landing` outdated; reframe to post-filing SEC-comment / audit / banker bake-off → public S-1 by H2 2027. GC-office Need → done. |
| `prediction.8ae347c6052558e0` — AMD Helios + MI450 commitment book clears 15GW by H2 2026 | reasoning, needs | Sovereign-cloud signing cadence went dormant after 5/22; reframe to the settled ~11.1GW landmark + slower, July-Advancing-AI-catalyzed trajectory (15GW/Dec-31 outcome NOT contradicted). |
| `prediction.eadbcf808bc0c2e7` — FMRB / US frontier-AI oversight | reasoning, needs | June-2 signing + Great American AI Act draft acknowledged as realized coupled instrument; open leg = 60-day covered-frontier-model benchmarking + committee gate. OSTP interagency-review Need → done. |

Notes:
- Deltas written as per-pid files under `app/sourcedata/2026-06-07/` (`predictions.<pid>.json`, `needs.<pid>.json`); `id`/`title`/`body`/`summary` preserved verbatim so the hash id reproduces (in-place update on fold).
- Locale fan-out intentionally NOT written for maintenance deltas: `ingest_day_locales` pairs locale rows by `source_row_index` within the file's date, so a back-dated prediction's maintenance delta dated 2026-06-07 would mis-key. EN deltas are authoritative; there is no maintenance locale-merge path today.
- `needs_tasks.status` is recomputed from 5W1H completeness at ingest (no JSON `task.status` read path), so the `done` flips are editorial markers in the Need prose, not a DB status flip.

## Step 3 — validate
- `weekly_maintenance validate --week-ending 2026-06-07`: **OK clean** (all stale judgements have applied JSON; no broken/retire).
