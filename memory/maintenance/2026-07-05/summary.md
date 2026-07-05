# Weekly maintenance — week ending 2026-07-05

- **Candidates (Step 0):** 21 predictions (change signals: `relevance_drift` ×20, `landed_this_week` ×1); 0 glossary terms; 0 spillover; 0 health warnings.
- **Judged (Step 1):** 3 batched sub-agents (7 + 7 + 7). 81 judgements across streams (reasoning + bridge×N + needs; `readings` only where `prediction_chain`/`prediction_relations` edges exist).
- **Verdicts:** fresh 79 · stale 0 · broken 2 · retire 0.
- **Updates (Step 2):** 0 stale rewrites (nothing to apply); 2 broken bridge rows escalated to `broken.md` (not auto-fixed); 0 retires.
- **Validation (Step 3):** `weekly_maintenance validate` passes with `broken.md` present; the day's `post-update-validation` / `lint-markdown-clean` / `daily-flow-check` gates are green in the daily-briefing run.

This week's news cycle (Ollama multi-token prediction local speedup, Together AI $800M open-model inference neocloud, Tenstorrent's Qualcomm-buyout denial, Stathera timing-silicon Series B, the Geneva-anchored AI-events slate) was orthogonal to or only mildly reinforcing for every candidate prediction — no stream required rewriting. The two `broken` rows are pre-existing mis-attached `bridge_text`, not this-week staleness; see `broken.md`.
