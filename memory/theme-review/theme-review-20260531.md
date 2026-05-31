# Theme review — week ending 2026-05-31

Mode: routine Sunday rotation (5_weekly_theme_review). Diagnostic + advisory pass over the current schema. Inputs: `docs/data/graph-{tech,business,mix}.json` (post-update_pages snapshot), `theme_candidates` table (read-only), `app/src/schema.sql`.

## Diagnostic summary

Total themes: tech 10 (the new `tech.frontier_model_regulatory_board` landed in `app/src/schema.sql` and is now live in the graph snapshots), business 8, mix 18. Total predictions: tech 129, business 146, mix 151 unique. Pending `theme_candidates`: 52 rows (26 business-scope, 26 tech-scope), all `candidate_reason='no_keyword_match'`, none carrying a `nearest_theme_id`. Five labels appear with hit count = 2 (all cross-scope tech+business duplicates of the FMRB executive-order / SEC Corp Fin AI-accelerator / per-counterparty risk-factor cluster); the other 42 are unique, max within-scope hit count = 1. Sixth consecutive week the formal `≥ 3 distinct-day` promotion bar cannot fire on raw labels (5/5, 5/10, 5/17, 5/24, this week).

All three of last week's recommendations landed in `app/src/schema.sql` (commit `e5e0a79`, 5/26): the new `tech.frontier_model_regulatory_board` theme was added under `tech.standards`; `tech.model_supply_chain` description widened to absorb the loader-verification cluster; `business.compute_capex_strategy` description sharpened to reclaim its core from `business.ai_revenue_disclosure`. The new FMRB theme landed with 56 child_ids (27 primary / 29 secondary) — the second-largest tech-side primary core after `tech.ai_macro_capital_markets`. **`tech.infrastructure` category dominance unwound from 50.5 % on 5/24 to 39.5 % this week** (below threshold) because the FMRB theme absorbed ~27 primary attachments into `tech.standards`. The carve-out worked exactly as the 5/24 deferred-items note predicted for tech.

**`business.capital-supply-chain` category dominance did the opposite — went from 68.9 % on 5/24 to 74.0 % this week.** Root cause: `business.ai_revenue_disclosure` grew from 100 → 127 child_ids (79 primary → 105 primary), absorbing more business-scope predictions rather than fewer. A close audit of the 105 primary kids (see "Overpopulated themes" below) shows ~42 are genuinely about AI-revenue disclosure / SEC concept release / IPO cohort / per-token margin reporting; the remaining ~63 are tech-flavored predictions (KV-cache, MoE recipes, agent control plane, frontier policy executive orders, CISA guides, OCC addenda) that have no better business-scope home and end up here because this theme's keyword set is the broadest in the business pool. This is a NEW pain point this week — the 5/24 read "uniform around single thesis arc" no longer holds at primary=105. Recommendation 1 addresses this.

The 5/24 watch on `business.compute_capex_strategy` (4 kids → expected recovery toward 6+) did not materialize: still 4 children, 3 primary, unchanged from last week despite the description sharpening landing 5 days ago. Week 1 of the 2-week watch; will re-examine next Sunday before recommending a merge into `business.ai_revenue_disclosure`.

### Tech scope — theme attachments + category density

| Theme | Category | child_ids | primary |
|---|---|---|---|
| AI Macro & Capital Markets (`tech.ai_macro_capital_markets`) | tech.infrastructure | 65 | 40 |
| Frontier Model Regulatory Board (`tech.frontier_model_regulatory_board`) | tech.standards | 56 | 27 |
| Agent Runtime Security (`tech.agent_runtime_security`) | tech.security | 37 | 14 |
| Agent Registry Architecture (`tech.agent_registry_architecture`) | tech.standards | 35 | 13 |
| Model Supply Chain (`tech.model_supply_chain`) | tech.security | 25 | 5 |
| Agent Control Plane (`tech.agent_control_plane`) | tech.agents | 19 | 7 |
| Local Inference Runtime (`tech.local_inference_runtime`) | tech.inference-runtime | 16 | 9 |
| 1-bit / Edge LLM (`tech.one_bit_edge_llm`) | tech.models | 12 | 3 |
| AI Chip Architecture (`tech.ai_chip_architecture`) | tech.infrastructure | 9 | 3 |
| Physical AI / Robotics (`tech.physical_ai_robotics`) | tech.infrastructure | 9 | 8 |

Tech category density (primary attach via `theme_id` / `category_id`, 129 distinct predictions): tech.infrastructure 51 / 129 = 39.5 % (down from 50.5 % on 5/24 — below the 50 % threshold), tech.standards 40 / 129 = 31.0 % (up from 15.6 % — the new FMRB theme drove this), tech.security 19 / 129 = 14.7 %, tech.inference-runtime 9 / 129 = 7.0 %, tech.agents 7 / 129 = 5.4 %, tech.models 3 / 129 = 2.3 %. No category over 50 %.

### Business scope — theme attachments + category density

| Theme | Category | child_ids | primary |
|---|---|---|---|
| AI-Revenue Disclosure Rewrite (`business.ai_revenue_disclosure`) | business.capital-supply-chain | 127 | 105 |
| Inference Server Supply Chain (`business.inference_server_supply_chain`) | business.regulation-compliance | 77 | 23 |
| Developer Toolchain Platformization (`business.developer_platformization`) | business.enterprise-adoption | 35 | 6 |
| Hyperscaler × Frontier Lab Alliance (`business.hyperscaler_frontier_lab_alliance`) | business.market-structure | 31 | 3 |
| Open Weight vs Proprietary AI (`business.open_weight_vs_proprietary`) | business.competition | 28 | 3 |
| AI Security Compliance Market (`business.ai_security_compliance_market`) | business.regulation-compliance | 22 | 2 |
| Cloud vs Local AI Distribution (`business.cloud_vs_local_distribution`) | business.distribution | 9 | 1 |
| Compute Capex Strategy (`business.compute_capex_strategy`) | business.capital-supply-chain | 4 | 3 |

Business category density (primary attach, 146 distinct predictions): **business.capital-supply-chain 108 / 146 = 74.0 %** (up from 68.9 % — worse, not better), business.regulation-compliance 25 / 146 = 17.1 %, business.enterprise-adoption 6 / 146 = 4.1 %, business.market-structure 3 / 146 = 2.1 %, business.competition 3 / 146 = 2.1 %, business.distribution 1 / 146 = 0.7 %. The single-category-dominance pattern on business is now structural and deepening — recommendation 1 attempts a description-level mitigation; the proper category carve-out remains a §2.3 milestone-level item.

### Mix scope

Rolls up tech + business; same theme + category shape as above. Total unique predictions = 151.

### Multi-attach pressure (secondary-attach path in `app/src/export.py`)

Distribution of theme-parents per prediction (counted via theme-node `child_ids` membership):

- Tech (129 predictions): 56 attach to exactly one theme, 31 to two, 20 to three, 11 to four, 7 to five, 2 to six, 2 to seven. 73 / 129 = 56.6 % multi-attach.
- Business (146 predictions): 59 attach to exactly one theme, 33 to two, 26 to three, 17 to four, 6 to five, 3 to six, 2 to seven. 87 / 146 = 59.6 % multi-attach.
- Mix (151 predictions): 15 attach to exactly one theme, 37 to two, 25 to three, 19 to four, 15 to five, 13 to six, 12 to seven, 5 to eight, 3 to nine, 5 to ten, 2 to eleven. 136 / 151 = **90.1 % multi-attach**.

The same broad-context-prediction pattern flagged on 4/27, 5/3, 5/5, 5/10, 5/17, and 5/24 — seventh consecutive week. Primary-vs-secondary on the most populated themes: `business.ai_revenue_disclosure` 105 primary / 22 secondary (NB: primary > secondary because this theme is winning the IDF tournament on most business-scope predictions — see Pain points), `business.inference_server_supply_chain` 23 / 54 (multi-attach exceeds primary), `tech.ai_macro_capital_markets` 40 / 25, `tech.frontier_model_regulatory_board` 27 / 29, `business.hyperscaler_frontier_lab_alliance` 3 / 28, `business.open_weight_vs_proprietary` 3 / 25, `business.ai_security_compliance_market` 2 / 20. See recommendation 4.

## Empty / underused themes

None. Lowest is `business.compute_capex_strategy` at 4 children (3 primary) — same as 5/24, the description sharpening did not move the count. Week 1 of the 2-week watch (will flip to merge recommendation next Sunday if still flat).

## Overpopulated themes

Every theme except `business.compute_capex_strategy` exceeds the threshold. The four largest with structural issues:

- **`business.ai_revenue_disclosure` 127 children, 105 primary — NEW PAIN POINT THIS WEEK.** Manual audit of the 105 primary kids: ~42 are genuinely about AI-revenue disclosure (SEC concept release, audited monthly revenue + WAU cadence, 10-Q footnote breakouts, AMD AI-accelerator 10-Q segment, AI-accelerator S-1 cohort, Cerebras IPO, per-token-margin reporting, Powell / FOMC institutional-volatility regime, AI-accelerator IPO pricing). The remaining ~63 are not — they include KV-cache-compression deployment knobs, MoE LoRA recipes, MCP registry RFCs, Linux-kernel CVE chains, CISA agentic-AI deployment guides, OCC Model Risk Management addenda, sandboxed-skill verification harnesses, edge-LLM recipes, physical-AI procurement cuts, Headless Everything via MCP. These off-topic primary attachments happen because the theme's keyword set ("frontier", "hyperscaler", "AI-accelerator", "AI-services", "Big-3", "audited") is the broadest among the 8 business themes; the IDF tournament defaults to this theme whenever a prediction has no closer match in the business pool. The 5/24 read "uniform around single thesis arc" no longer holds at primary=105. Recommendation 1 addresses this with a description sharpening that drops the broadest anchor-name tokens and concentrates on disclosure-mechanic vocabulary.
- `business.inference_server_supply_chain` (77 kids, 23 primary, 54 secondary) — primary core remains coherent (inference-server CVE class, CISA AI-Infra KEV sub-catalog, signed-checkpoint loading defaults, NIST non-human-identity profile, FMRB tie-ins, agent-skills threat sub-matrix); the multi-attach inflation is `export.py`-driven, not a schema fault. Leave as-is.
- `tech.ai_macro_capital_markets` (65 kids, 40 primary) — primary core uniform around macro / capital-markets dynamics. Healthy size growth. Leave as-is.
- `tech.frontier_model_regulatory_board` (56 kids, 27 primary) — new theme, first-week landing. Primary core coherent (FMRB executive order, AISI reciprocity ladder, allied procurement mirror clauses, cyber-eval attestation, agent-registry GA cyber-eval default). Strong placement; leave as-is. Watch next week for any drift.

## Theme candidates

No candidates above the ≥3-hit raw-label bar. Manual topical clustering surfaces the following pending clusters, all already covered by existing themes:

- AI Revenue Disclosure cluster — 22 rows (15 business + 7 tech). All stale candidates: created 5/26 (same day the schema landed); existing `business.ai_revenue_disclosure` covers; will clear on next re-ingest.
- FMRB / Cyber-Eval Reciprocity — 6 rows (3 tech + 3 business). All stale: created 5/26 same day `tech.frontier_model_regulatory_board` landed; covered by the new theme; will clear on next re-ingest.
- Loader-Verification Default — 4 rows (all tech). All stale: created 5/26 same day `tech.model_supply_chain` was widened to include loader-verification keywords; will clear on next re-ingest.
- Hyperscaler Capital Coupling — 3 rows (all tech): AGI-clause unwind, three-cloud training oligopoly, hyperscaler-AI-lab capital coupling. Covered by existing `business.hyperscaler_frontier_lab_alliance`.
- Physical AI Industrial Procurement — 3 rows (all business). Covered by existing `tech.physical_ai_robotics` description (8-hour production runs, RaaS, league tables).
- Sub-threshold clusters (≤ 2 rows): Edge / Local LLM (2), Agent Registry / MCP (2), Frontier-Lab Governance (2), Multi-cloud SLA / cloud-overflow (2), Open Weight Cohort / MoE (2), AI Search Regulatory (1), Cyber-Insurance Agentic (1).

**No new-theme proposal warranted this week.** Every cluster at or above the 3-row bar is already covered by an existing theme.

## Category-level notes

Category dominance (≥ 50 %): one — `business.capital-supply-chain` at 74.0 % (up from 68.9 %; structural, driven by `business.ai_revenue_disclosure` over-fitting). `tech.infrastructure` 39.5 % (reverted below threshold this week, the FMRB carve-out worked). `business.regulation-compliance` 17.1 % (down from 20.2 %). `tech.standards` 31.0 % (up from 15.6 %, the new FMRB theme; below threshold but worth monitoring).

## Recommended actions

### Action 1: Sharpen `business.ai_revenue_disclosure` description

The theme is over-fitting on broad anchor-name tokens ("frontier", "hyperscaler", "AI-accelerator", "AI-services", "Big-3", "audited", "foundation labs (OpenAI, Anthropic, xAI)", "Microsoft Azure", "Alphabet", "AMD", "Cerebras") that match too many business-scope predictions and let it win the IDF tournament on ~63 of its 105 primary kids that are not actually about AI-revenue disclosure (KV-cache deployment knobs, MoE LoRA recipes, MCP RFCs, Linux-kernel CVE chains, agentic-AI deployment guides, OCC Model Risk Management, sandboxed-skill verification harnesses, edge-LLM recipes, etc.).

The rewrite below tightens the keyword set to disclosure mechanics only — SEC concept releases, Corporation Finance staff guidance and Staff Legal Bulletins, audited monthly-revenue cadence, WAU disclosure, 10-Q segment footnote breakouts, AI-services 10-Q breakout mechanics, AI-accelerator IPO / S-1 disclosure mechanics, per-counterparty risk-factor tables, hyperscaler-anchor warrant-equity disclosure, per-token-margin reporting, AI-revenue concept release commentary — and explicitly drops the bare company-name and bare-category anchor tokens that were pulling unrelated predictions in. Expected effect: a fraction of the off-topic primary kids re-route to other themes (or to `theme_candidates` if no other theme matches well), restoring this theme's primary core to the ~42-prediction genuine disclosure cluster. Off-topic predictions that fall out are diagnostic — they are the proper signal for the longer-term `business.governance` / `business.regulatory` carve-out conversation per §2.3.

This is a sharpening, not a widening; total token count goes down by intent.

```action
{
  "kind": "rewrite-description",
  "theme_id": "business.ai_revenue_disclosure",
  "new_description_en": "The 2026 rewrite of how AI revenue is reported to capital markets, focused on disclosure-mechanic vocabulary: SEC AI-revenue concept release; Corporation Finance staff guidance and Staff Legal Bulletins on AI-accelerator IPO disclosure; audited monthly-revenue and WAU disclosure cadence as a recurring reporting primitive; per-token-margin disclosure as a recurring reporting primitive; 10-Q segment footnote breakouts as a disclosure mechanic (AI-services run-rate, AI-accelerator segment footnote, AI-business KPI footnote); AI-accelerator IPO and S-1 disclosure cohort mechanics; per-counterparty risk-factor tables in S-1 filings; hyperscaler-anchor warrant-equity disclosure language; AGI-clause / capability-attestation disclosure language in lab-hyperscaler contracts; AI-accelerator vendor forward-supply 8-K cadence as disclosure primitive; Cerebras / Tenstorrent / Anthropic IPO pricing and post-IPO disclosure mechanics specifically as filings. (Macro and capital-markets regime dynamics around these disclosures are covered by tech.ai_macro_capital_markets, not here. Compute-capex commitments are covered by business.compute_capex_strategy. Hyperscaler-lab partnership structure is covered by business.hyperscaler_frontier_lab_alliance.)",
  "new_description_ja": "2026年のAI売上の資本市場開示再構築、開示メカニクスの語彙に焦点: SEC AI-revenue concept release; AI-accelerator IPO 開示に関する Corporation Finance スタッフガイダンスおよび Staff Legal Bulletins; 反復報告プリミティブとしての監査済み月次売上 + WAU 開示ケイデンス; 反復報告プリミティブとしての per-token margin 開示; 開示メカニクスとしての 10-Q セグメント脚注ブレイクアウト (AI-services ランレート、AI-accelerator セグメント脚注、AI-business KPI 脚注); AI-accelerator IPO/S-1 開示コホートメカニクス; S-1 提出書類のカウンターパーティ別リスク要因表; ハイパースケーラー・アンカー新株予約権-持分開示文言; ラボ-ハイパースケーラー契約の AGI 条項 / 能力アテステーション開示文言; 開示プリミティブとしての AI-accelerator ベンダー先渡し供給 8-K ケイデンス; Cerebras / Tenstorrent / Anthropic の IPO 値付けおよび IPO 後開示メカニクス (具体的に提出書類として)。(これらの開示を取り巻くマクロおよび資本市場レジームのダイナミクスは tech.ai_macro_capital_markets 側でカバー。計算 capex コミットメントは business.compute_capex_strategy 側。ハイパースケーラー-ラボ パートナーシップ構造は business.hyperscaler_frontier_lab_alliance 側。)",
  "new_description_es": "La reescritura de 2026 sobre cómo se reporta el ingreso de IA a los mercados de capital, enfocada en vocabulario de mecánicas de divulgación: SEC AI-revenue concept release; staff guidance de Corporation Finance y Staff Legal Bulletins sobre la divulgación en IPOs de AI-accelerator; cadencia de divulgación de ingresos auditados mensuales + WAU como primitiva de reporte recurrente; divulgación de per-token margin como primitiva de reporte recurrente; breakouts de notas a pie en segmentos 10-Q como mecánica de divulgación (run-rate de AI-services, nota a pie de segmento de AI-accelerator, nota a pie de KPI de AI-business); mecánicas de la cohorte de divulgación de IPO y S-1 de AI-accelerator; tablas de factores de riesgo por contraparte en presentaciones S-1; lenguaje de divulgación de warrants-equity de anclaje de hyperscaler; lenguaje de divulgación de cláusulas AGI / atestación de capacidad en contratos lab-hyperscaler; cadencia de oferta forward 8-K de proveedores de AI-accelerator como primitiva de divulgación; mecánicas de pricing de IPO y divulgación post-IPO específicamente como presentaciones de Cerebras / Tenstorrent / Anthropic. (Dinámicas de régimen macro y de mercados de capital alrededor de estas divulgaciones las cubre tech.ai_macro_capital_markets, no este tema. Los compromisos de capex de cómputo los cubre business.compute_capex_strategy. La estructura de partnerships hyperscaler-lab la cubre business.hyperscaler_frontier_lab_alliance.)",
  "new_description_fil": "Ang 2026 rewrite kung paano iniuulat ang kita ng AI sa capital markets, nakatuon sa vocabulary ng disclosure mechanics: SEC AI-revenue concept release; staff guidance ng Corporation Finance at mga Staff Legal Bulletin tungkol sa AI-accelerator IPO disclosure; cadence ng audited monthly-revenue at WAU disclosure bilang recurring reporting primitive; per-token-margin disclosure bilang recurring reporting primitive; 10-Q segment footnote breakouts bilang disclosure mechanic (run-rate ng AI-services, AI-accelerator segment footnote, AI-business KPI footnote); mga mechanic ng AI-accelerator IPO at S-1 disclosure cohort; mga per-counterparty risk-factor table sa S-1 filings; hyperscaler-anchor warrant-equity disclosure language; AGI-clause / capability-attestation disclosure language sa mga lab-hyperscaler contract; AI-accelerator vendor forward-supply 8-K cadence bilang disclosure primitive; mechanic ng IPO pricing at post-IPO disclosure ng Cerebras / Tenstorrent / Anthropic partikular bilang mga filing. (Ang macro at capital-markets regime dynamics sa paligid ng mga disclosure na ito ay sakop ng tech.ai_macro_capital_markets, hindi nito. Ang compute-capex commitments ay sakop ng business.compute_capex_strategy. Ang hyperscaler-lab partnership structure ay sakop ng business.hyperscaler_frontier_lab_alliance.)"
}
```

### Action 2: Observation (no schema edit) — `business.compute_capex_strategy` 2-week watch, week 1 of 2

Last week's review proposed a description sharpening to reclaim the theme's core from `business.ai_revenue_disclosure`. The schema edit landed in commit `e5e0a79` (5/26). Five days later: still 4 children, 3 primary — **no movement at all**. The sharpening did not pull predictions back. If this remains flat through next Sunday (week 2), recommendation will flip to **merge `business.compute_capex_strategy` into `business.ai_revenue_disclosure`** as the cleaner option — maintaining a parallel theme with a primary count of 3 for two weeks running is no longer defensible. (Note that recommendation 1 above also drops capex-related anchor tokens from `business.ai_revenue_disclosure`, which may help capex-strategy reclaim its core — re-examine next Sunday with that interaction in mind.)

```action
{"kind": "log-only"}
```

### Action 3: Observation (no schema edit) — category-level carve-out for business scope is now overdue

`business.capital-supply-chain` at **74.0 %** primary-attach density (up from 68.9 % on 5/24, up from 7.5 % on 5/17). This is now the highest single-category dominance ever recorded in the project; the tech-side carve-out via the new FMRB theme already showed that adding a well-placed theme outside the dominant category mechanically relieves the imbalance. The business side has no equivalent escape valve because every business theme except `business.compute_capex_strategy` and `business.ai_revenue_disclosure` sits in a different category, and those other categories cap out at small populations (regulation-compliance 17.1 %, enterprise-adoption 4.1 %, market-structure 2.1 %, competition 2.1 %, distribution 0.7 %). The structural fix is a new `business.capital-markets` category (or equivalent) that pulls `business.ai_revenue_disclosure` out of `business.capital-supply-chain` and gives the macro / IPO / disclosure cluster its own home. Per `design/memory-policy.md` §2.3 a new category needs its own design discussion and is out of scope for this Sunday's `apply-schema-edit` flow. Third week running this category-level discussion has been flagged — first as `business.regulation-compliance` 52.2 % (5/17), then as `business.capital-supply-chain` 68.9 % + `tech.infrastructure` 50.5 % (5/24), now as `business.capital-supply-chain` 74.0 % alone (this week). Promote to milestone-priority.

```action
{"kind": "log-only"}
```

### Action 4: Investigation (no schema edit) — `SECONDARY_THEME_THRESHOLD` in `app/src/export.py` + `theme_candidates` label normalisation pass

Seventh consecutive review flagging the multi-attach pattern; sixth consecutive review flagging the candidate-label-uniqueness problem. Tech multi-attach 56.6 %, business 59.6 %, mix 90.1 % — mix still over 90 %. On the candidate side: 52 pending rows, 47 unique labels, 5 labels at hit count 2 (all cross-scope duplicates). Three large cluster groups (AI Revenue Disclosure 22 rows, FMRB 6 rows, Loader-Verification 4 rows) all consist of stale candidates created the same day their target theme's schema edit landed — the candidate-extraction pass apparently runs against the keyword set in effect at ingest time and does not re-evaluate when the schema is updated later in the day. These should clear on the next ingest run that touches those source predictions; in the meantime they inflate the pending candidate count without representing real new clusters. Both problems remain out of scope for `apply-schema-edit` — they need engineering work on `app/src/export.py` (secondary-attach threshold) and on the candidate-extraction pass (label normalisation + post-schema-edit re-evaluation). Deferred again.

```action
{"kind": "log-only"}
```

## Why this rotation

The new FMRB theme + the model_supply_chain widening + the compute_capex_strategy sharpening from 5/24 all landed in `app/src/schema.sql` (commit e5e0a79). The FMRB carve-out worked: tech.infrastructure dominance unwound from 50.5 % to 39.5 %. The capex_strategy sharpening did NOT work: still 4 kids / 3 primary, unchanged. The business-side dominance got worse: business.capital-supply-chain went from 68.9 % to 74.0 % because `business.ai_revenue_disclosure` is over-fitting on broad anchor-name tokens and absorbing ~63 unrelated predictions as primary kids. This week's single recommended action sharpens that theme's description to redirect the off-topic kids elsewhere; the structural fix (new `business.capital-markets` category) needs its own §2.3 discussion outside this rotation.

## Deferred for next week

- **`business.compute_capex_strategy` 2-week watch — week 2 of 2.** If primary count is still 3 next Sunday (with the additional effect of recommendation 1 from this week potentially helping it reclaim some predictions), recommendation flips to merge into `business.ai_revenue_disclosure`.
- **`business.ai_revenue_disclosure` post-sharpen state.** If recommendation 1 lands, next Sunday should show: primary kids drop from 105 toward 40-50 range; off-topic predictions either re-route to other themes or land in `theme_candidates`; business.capital-supply-chain category density drops from 74.0 % toward 50-55 % range. If the primary count barely moves, the matcher is more keyword-promiscuous than expected and the proper fix moves to a category-level intervention.
- **Business-scope category carve-out** (`business.capital-markets` or equivalent). Per §2.3, requires its own design discussion. Now flagged for three weeks running; should be promoted to milestone-priority and not deferred further.
- **`business.cloud_vs_local_distribution` and `business.compute_capex_strategy` as merge candidates.** Both have primary < 5 for two weeks running. If next week's primary counts are still flat, both become candidates for description merging or theme consolidation.
- **Pipeline-level fixes** (export.py secondary-attach threshold, candidate-extraction label normalisation + post-schema-edit re-evaluation). Carry forward — these remain engineering work outside `apply-schema-edit` scope.

---
