# Maintenance — broken entries (week ending 2026-07-05)

Two bridge rows were flagged `broken` by the Step-1 Judge as **pre-existing data-quality issues** (mis-attached `bridge_text` from a different prediction). Per `design/scheduled/6_weekly_maintenance.md` §Step 2, `broken` verdicts are logged for human review and **not auto-fixed**.

| Prediction | Bridge row (`validation_rows.id`) | Issue |
|---|---|---|
| `prediction.a96ff0bdaae351aa` — open-weight coding model tops Terminal-Bench | `validation.43bd5c4d3f8748ab` | `bridge_text` describes OpenAI's US-government-stake / public-listing story — unrelated to the Terminal-Bench coding-model prediction it is attached to. |
| `prediction.af116b6aeee58cde` — DiffusionGemma open-weight text-diffusion | `validation.009784698efcdc4e` | `bridge_text` describes AMD/Qualcomm confidential-inference hardware — unrelated to the DiffusionGemma prediction it is attached to. |

Both carry `proposed_action: noop` (escalate, do not auto-fix). Likely cause: a prior day's fuzzy validation-row→prediction match resolved to the wrong `prediction_id`, so the bridge prose landed on the wrong row.

**Suggested human action:** inspect the origin `future-prediction/en/future-prediction-*.md` validation tables for these two prediction summaries, correct the `validation_rows.bridge_text` attachment (or re-run `ingest-sourcedata` for the affected origin date once the fuzzy-match mis-resolution is fixed).
