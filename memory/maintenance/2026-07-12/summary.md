# Weekly maintenance summary — week ending 2026-07-12

- **Candidates selected (Step 0):** 22 predictions, 0 glossary terms, 0 spillover, 0 health warnings.
  - 5 `relevance_drift` (0bb5badc, 0c569408, 908f6597, 9eb6e988, a879b036); 17 `landed_this_week`.
- **Judgements (Step 1):** 88 total (22 predictions × 4 streams) — 82 fresh, 6 stale, 0 broken, 0 retire. Judged in 5 batched sub-agents with per-prediction cross-stream awareness.
- **Updates applied (Step 2)** — reframe deltas emitted as `maintenance-update.<stream>.<pid>.json` markers (origin-sourcedata + locale propagation deferred for these conf 0.6–0.72 items; markers document the recommended reframe):
  - `prediction.02bf6210bbfa3a6e` reasoning/stale (0.7) → OpenAI's new flagship listed $5/$30, half the predicted $10/$50 band — this-week bridge (07-10) contradicts the re-anchor thesis. Reasoning reframed to acknowledge the counter-datapoint; Q3-2026 landing still needs a rival at/above the band.
  - `prediction.0bb5badc89f68769` reasoning/stale (0.6) → landing bridge (07-10, rel5): predicted agent-tuned mid-tier model shipped ~5 months early; reasoning reframed forward (precondition satisfied → durability / second-lab adoption).
  - `prediction.4ecb84808c9acc3f` needs/stale (0.72) → CIS/OWASP editorial-maintainer Need delivered (task shipped); next-phase ranking/adoption Need named. (Same prediction reframed 2026-06-28; class advanced again this week.)
  - `prediction.4ecb84808c9acc3f` reasoning/stale (0.7) → reframed forward: risk moved from codified-in-standard (OWASP v2.01) to demonstrated; next precondition = discrete named CIS/OWASP top-list entry by Q3 2026.
  - `prediction.a2d6a1d80d9edd87` reasoning/stale (0.7) → origin `because` superseded as the mechanism went mainstream this week; forward precondition restated.
  - `prediction.b4ec0c53d816fdb4` reasoning/stale (0.6) → Copilot's same-day adoption of all three GPT-5.6 tiers is a third-party-default counter-signal to the first-party-MAI-default thesis; reasoning reframed to note it.
- **Broken / escalated (Step 3):** none this week (see `broken.md`).
- **Validation (Step 3):** `weekly_maintenance validate` clean; `post_update_validation --check all`, `lint_markdown_clean`, `daily_flow_check --strict` green.

Note: schema is `apply-schema-edit`-managed; the two long-pending theme rewrites (`business.ai_revenue_disclosure` sharpen, `business.cloud_vs_local_distribution` widen) landed in `app/src/schema.sql` this Sunday.
