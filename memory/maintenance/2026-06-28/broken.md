# Weekly maintenance — broken/escalated items (week ending 2026-06-28)

Items flagged `broken` by the Judge (Step 1). Per `6_weekly_maintenance` policy these are NOT auto-fixed — they need human review.

## prediction.af116b6aeee58cde — bridge/broken (confidence 0.90)

- **Prediction:** "DiffusionGemma seeds an open-weight text-diffusion training …" (origin 2026-06-14).
- **Bridge:** `validation_rows.id = validation.009784698efcdc4e` (dated 2026-06-28, `support_dimension=given`).
- **Defect:** the bridge is keyed to this DiffusionGemma text-diffusion prediction, but its `bridge_text` is about an unrelated topic — i.e. today's `2_future_prediction` mis-attributed the bridge narrative to the wrong prediction.
- **Action required (human):** review today's `app/sourcedata/2026-06-28/bridges.json` row whose `prediction_ref` resolves to `prediction.af116b6aeee58cde`; either rewrite the bridge narrative to actually address the DiffusionGemma prediction, or drop the row if today's news bears no real relevance to it. Not auto-fixed to avoid asserting an unsupported link.
