# Theme review — week ending 2026-05-17

Mode: Sunday rotation (5_weekly_theme_review). Bounded read of `docs/data/graph-*.json` + `app/src/schema.sql` + `theme_candidates` table.

## Diagnostic snapshot

Total themes: tech 9, business 7, mix 16. Total predictions: tech 86, business 67, mix 91 unique. Pending `theme_candidates`: 29 rows (24 business-scope, 5 tech-scope), all `candidate_reason='no_keyword_match'`, none carrying a `nearest_theme_id`, and every row a single distinct `suggested_theme_label` with exact-label hit count = 1 — same verbatim-label problem flagged on 5/10 and 5/5 (see Theme candidates and recommendation 4 below).

Two themes proposed on 5/10 were applied to `schema.sql` during the week: `tech.ai_macro_capital_markets` (under `tech.infrastructure`) and `business.inference_server_supply_chain` (under `business.regulation-compliance`). The 5/10 `tech.ai_chip_architecture` description-widening (recommendation 1) was also applied — that theme went from 2 children on 5/10 to 7 this week, and is no longer underused.

### Tech scope — theme attachments + category density

| Theme | Category | child_ids |
|---|---|---|
| AI Macro & Capital Markets (`tech.ai_macro_capital_markets`) | tech.infrastructure | 42 |
| Agent Registry Architecture (`tech.agent_registry_architecture`) | tech.standards | 31 |
| Agent Runtime Security (`tech.agent_runtime_security`) | tech.security | 29 |
| Model Supply Chain (`tech.model_supply_chain`) | tech.security | 18 |
| Agent Control Plane (`tech.agent_control_plane`) | tech.agents | 16 |
| Local Inference Runtime (`tech.local_inference_runtime`) | tech.inference-runtime | 13 |
| 1-bit / Edge LLM (`tech.one_bit_edge_llm`) | tech.models | 12 |
| AI Chip Architecture (`tech.ai_chip_architecture`) | tech.infrastructure | 7 |
| Physical AI / Robotics (`tech.physical_ai_robotics`) | tech.infrastructure | 7 |

Tech category density (primary attach via `theme_id` / `category_id`, 86 distinct predictions): tech.infrastructure 39 / 86 = 45.3 %, tech.security 17 / 86 = 19.8 %, tech.standards 12 / 86 = 14.0 %, tech.inference-runtime 9 / 86 = 10.5 %, tech.agents 6 / 86 = 7.0 %, tech.models 3 / 86 = 3.5 %. No tech category crosses the 50 % dominance threshold (tech.infrastructure at 45.3 % is the closest — see Category-level notes).

### Business scope — theme attachments + category density

| Theme | Category | child_ids |
|---|---|---|
| Inference Server Supply Chain (`business.inference_server_supply_chain`) | business.regulation-compliance | 50 |
| Hyperscaler × Frontier Lab Alliance (`business.hyperscaler_frontier_lab_alliance`) | business.market-structure | 40 |
| Open Weight vs Proprietary AI (`business.open_weight_vs_proprietary`) | business.competition | 28 |
| Developer Toolchain Platformization (`business.developer_platformization`) | business.enterprise-adoption | 23 |
| AI Security Compliance Market (`business.ai_security_compliance_market`) | business.regulation-compliance | 23 |
| Cloud vs Local AI Distribution (`business.cloud_vs_local_distribution`) | business.distribution | 11 |
| Compute Capex Strategy (`business.compute_capex_strategy`) | business.capital-supply-chain | 7 |

Business category density (primary attach, 67 distinct predictions): business.regulation-compliance 35 / 67 = 52.2 %, business.competition 11 / 67 = 16.4 %, business.market-structure 8 / 67 = 11.9 %, business.enterprise-adoption 7 / 67 = 10.4 %, business.capital-supply-chain 5 / 67 = 7.5 %, business.distribution 1 / 67 = 1.5 %. **`business.regulation-compliance` crosses the 50 % dominance threshold** — flagged in Category-level notes and recommendation 2.

### Mix scope

Rolls up tech + business; same theme + category shape as above. Total unique predictions = 91.

### Multi-attach pressure (secondary-attach path in `app/src/export.py`)

Distribution of theme-parents per prediction (counted via theme-node `child_ids` membership):

- Tech (86 predictions): 41 attach to exactly one theme, 21 to two, 13 to three, 6 to four, 1 to five, 4 to six. 45 / 86 = 52.3 % multi-attach.
- Business (67 predictions): 22 attach to exactly one theme, 10 to two, 11 to three, 14 to four, 9 to five, 1 to six. 45 / 67 = 67.2 % multi-attach.

The same broad-context-prediction pattern flagged on 4/27, 5/3, 5/5, and 5/10 — broad-token predictions saturate every theme they share even one rare token with. The headline number on the two new 5/10 themes confirms it directly: `business.inference_server_supply_chain` shows 50 children (29 primary / 21 secondary) and `tech.ai_macro_capital_markets` shows 42 children (32 primary / 10 secondary). Both new themes immediately landed at the top of their scope's overpopulation band — but their *primary* cores (29 and 32) are coherent on inspection, so this is multi-attach inflation on top of a healthy core, not a schema fault. See recommendation 4.

## Empty / underused themes

### tech
- (no underused themes — the lowest tech theme is `tech.ai_chip_architecture` at 7 children. Last week's description widening lifted it out of the underused band; `tech.physical_ai_robotics` also sits at 7. Both are well clear of the `child_ids ∈ {0, 1}` underused threshold.)

### business
- (no underused themes — the lowest is `business.compute_capex_strategy` at 7 children.)

### mix
- (rolls up tech + business; no mix-specific empties.)

For the third review running there is no theme at `child_ids ∈ {0, 1}`. The schema currently has no dead weight to deprecate or merge.

## Overpopulated themes

Every theme in the schema carries `child_ids ≥ 6` this week — 9 / 9 tech and 7 / 7 business. The `app/src/export.py` multi-attach saturation flagged on 5/3, 5/5, and 5/10 is the dominant cause; the on-topic *primary* cores are far smaller than the `child_ids` totals. Cluster inspection of the four most populated themes:

### business
- **`Inference Server Supply Chain`** (50 children — most populated theme in the corpus) — 29 primary children, a coherent AI-security-substrate cluster (inference-server CVE class, CISA AI-Infra KEV sub-catalog, agent-skills threat sub-matrix, NIST non-human-identity profile, FMRB executive order, signed-checkpoint loading defaults). Remaining 21 are secondary multi-attach.
  - Suggested: leave as-is. The 29-child primary core is uniform around the AI-Infra-CVE-becomes-regulation thesis; the theme is one week old and was created precisely to absorb this cluster. Splitting a coherent 29-child core to thin 21 multi-attach rows is the wrong tradeoff. Revisit only if the *primary* core fragments into distinct sub-clusters.
- **`Hyperscaler × Frontier Lab Alliance`** (40 children) — only 8 primary children (5-pole hyperscaler-lab regime, three-cloud training oligopoly, capital-coupling compute lock-in, AGI-clause unwind, autonomous-weapons carve-outs). The other 32 are multi-attach noise — this theme is the single clearest illustration of the export.py pattern: an 8-child real theme wearing a 40-child coat.
  - Suggested: leave as-is. The schema theme is correctly sized at 8 primary children; the inflation is entirely an export.py threshold artefact (recommendation 4), not a schema problem.
- **`Open Weight vs Proprietary AI`** (28 children) — 11 primary children, coherent (closed-weight frontier crystallization, open-weight 1M-context floor, Unsloth managed fine-tuning, disaggregated prefill serving defaults). Remaining 17 multi-attach.
  - Suggested: leave as-is.
- **`AI Security Compliance Market`** (23 children) — 6 primary children (SOC2/FedRAMP/FMF baseline, MCP-redesign enterprise bottleneck, OCC agentic-AI MRM addendum, LLM-tooling + Linux-kernel CVE chain). Remaining 17 multi-attach. This theme now shares `business.regulation-compliance` with the new `business.inference_server_supply_chain`, which is the direct cause of that category crossing 50 % dominance — see recommendation 2.
  - Suggested: leave as-is at the theme level; the category-level concentration is the issue, not this theme's size.

### tech
- **`AI Macro & Capital Markets`** (42 children) — 32 primary children, the largest primary core in the corpus. The cluster is internally coherent (AI-revenue-disclosure rewrite, SEC concept release, audited monthly revenue cadence, AMD/Microsoft/Alphabet 10-Q footnote breakouts, Cerebras IPO, AI-accelerator S-1 cohort, Powell-Fed institutional-volatility regime). Remaining 10 multi-attach.
  - Suggested: leave the *tech* theme as-is — its primary core is uniform. But note the cross-scope gap surfaced in recommendation 1: this theme is `scope=tech`, yet the bulk of the matching `theme_candidates` rows are `scope=business`, so business-scope revenue-disclosure predictions have no home theme.
- **`Agent Registry Architecture`** (31 children) — primary core ~12 (cross-cloud agent-identity + MCP registry, NIST non-human-identity control profile, Microsoft Agent 365 registry sync, agent-skills threat sub-matrix, agent-as-first-class-identity statute). Remaining ~19 multi-attach.
  - Suggested: leave as-is.
- **`Agent Runtime Security`** (29 children) — primary core ~13 (indirect prompt injection, MCP attack surface, inference-server CVEs, agentic-AI CVE class, agent-skills attack surface, LLM-tooling + Linux-kernel CVE chain). Remaining ~16 multi-attach.
  - Suggested: leave as-is.

## Theme candidates

`theme_candidates` holds 29 pending rows (was 39 on 5/10). All 29 are `no_keyword_match` with no `nearest_theme_id`, and every single `suggested_theme_label` is distinct with exact-label hit count = 1 — the candidate-extraction pass still writes one row per prediction summary verbatim, so the `≥ 3 distinct-day` promotion rule from `design/memory-policy.md` §2.1 still cannot fire as written. The drop from 39 to 29 reflects the two themes added during the week (predictions that previously had no keyword match now match the new `tech.ai_macro_capital_markets` / `business.inference_server_supply_chain` keyword sets).

Manual clustering by topic surface (same exercise as 5/10):

| scope | suggested label | rough hits in pending | candidate home | sample evidence |
|---|---|---|---|---|
| business | AI-Revenue Disclosure Rewrite | ~13 | **no business-scope theme exists** | OpenAI audited monthly revenue + WAU cadence; Foundation labs audited monthly revenue + per-token margin; Microsoft audited monthly AI-business KPIs as 10-Q footnote; AMD AI-accelerator revenue 10-Q segment footnote (×2 rows); Big-3 hyperscalers AI-services 10-Q revenue footnote; Alphabet AI Services 10-Q footnote breakout; SEC drafts AI-revenue concept release; SEC Corp Fin AI-accelerator S-1 staff guidance / IPO Staff Legal Bulletin; AI-accelerator S-1s per-counterparty risk-factor table; Cerebras IPO pricing; Cerebras post-IPO valuation comparable |
| business | Physical AI Industrial Procurement | ~4 | `tech.physical_ai_robotics` (after small widening) | Robot-control training consolidates in cloud as per-robot SaaS; Physical AI 8-hour production runs become enterprise RFP cuts; Physical AI league tables rank top-five OEM humanoids; Tesla Optimus capex forces Mag-7 physical-AI 10-Q segment disclosure |
| business / tech | Agent Registry / Loader Verification | ~5 | `tech.agent_registry_architecture` / `tech.model_supply_chain` | Agent registry standard converges with MCP for agent artifacts; Headless Everything standardizes via MCP/Agent Registry; GGUF supply chains gate uploads via signed cards + SSTI scans; Unified loader-verification model ships as framework default; Multi-cloud frontier-model SLA standardization |
| tech / business | Edge / Local-LLM Recipe | ~3 | `tech.one_bit_edge_llm` / `business.cloud_vs_local_distribution` | Bonsai 8B anchors 1-bit native training as default edge-LLM recipe; Local-first coding agents standardize cloud-overflow as default; 27B Dense + 1M context becomes default enterprise local-LLM recipe |
| tech / business | Hyperscaler Capital Coupling | ~2 | `business.hyperscaler_frontier_lab_alliance` | Frontier-AI cloud capacity locks into three-cloud training oligopoly; Hyperscaler-AI-lab capital coupling hardens into compute lock-in |

The strongest signal-to-noise candidate cluster — and the only one without an existing home theme — is the **AI-revenue-disclosure** cluster (~13 rows). It is the single largest cluster in the pending table. The 5/10 review added `tech.ai_macro_capital_markets` to absorb exactly this material, but that theme is `scope=tech`, while ~12 of the ~13 revenue-disclosure candidates are `scope=business`; the matcher cannot primary-attach a business-scope prediction to a tech-scope theme, so these rows keep landing in `theme_candidates`. The fix is a business-scope counterpart theme — recommendation 1. Every other cluster is below the `≥ 3` threshold or already has an adequate home after a description tweak (the Physical AI procurement cluster fits `tech.physical_ai_robotics`, which already lists Tesla Optimus / RaaS / 8-hour production runs).

## Category-level notes

- **`business.regulation-compliance` carries 35 / 67 = 52.2 % of business-scope predictions** — over the 50 % dominance threshold. Root cause is structural, not a one-week spike: the category now holds *two* large themes (`business.inference_server_supply_chain`, added 5/10, and `business.ai_security_compliance_market`). When the 5/10 review proposed `business.inference_server_supply_chain` it noted the new theme would "thin the multi-attach saturation on `business.ai_security_compliance_market`" — at the theme level it did, but it also concentrated two security/compliance themes under one category. See recommendation 2 (advisory; no schema edit this week).
- `tech.infrastructure` carries 39 / 86 = 45.3 % of tech-scope predictions — below the 50 % threshold but the highest tech category, because it hosts three themes including the 42-child `tech.ai_macro_capital_markets`. No action; monitor.
- No tech category and only the one business category exceed 50 % attention this week.

## Recommended actions

1. **Add new theme `business.ai_revenue_disclosure`** under `business.capital-supply-chain`. The largest pending `theme_candidates` cluster (~13 rows: SEC AI-revenue concept release, OpenAI / foundation-lab audited monthly revenue cadence, Microsoft / AMD / Alphabet 10-Q AI-services footnote breakouts, AI-accelerator S-1 / IPO disclosure cohort, Cerebras IPO pricing) is business-scope and has no business-scope home theme. The 5/10-added `tech.ai_macro_capital_markets` covers this material but is `scope=tech`, so business-scope predictions cannot primary-attach to it and keep accumulating in `theme_candidates`. `business.capital-supply-chain` is the closest existing category (compute capex, chip supply, capital strategy) and currently holds only one theme (`business.compute_capex_strategy`, 7 children) — adding the disclosure theme there also relieves that category's thinness without touching the over-50 % `business.regulation-compliance` category.

   ```action
   {
     "kind": "add",
     "theme_id": "business.ai_revenue_disclosure",
     "category_id": "business.capital-supply-chain",
     "label_en": "AI-Revenue Disclosure Rewrite",
     "short_label_en": "AI-Revenue Disclosure",
     "tooltip_en": "AI-Revenue Disclosure Rewrite",
     "description_en": "The 2026 rewrite of how AI revenue is reported to capital markets: SEC AI-revenue concept release and Corporation Finance staff guidance, audited monthly-revenue and WAU disclosure cadence from foundation labs (OpenAI, Anthropic, xAI), Big-3 hyperscaler AI-services 10-Q footnote breakouts (Microsoft Azure AI Services run-rate, Alphabet AI Services segment), AMD AI-accelerator revenue 10-Q segment footnote, AI-accelerator IPO and S-1 disclosure cohort (Cerebras, Tenstorrent, per-counterparty risk-factor tables, hyperscaler-anchor warrant-equity disclosure), per-token-margin reporting.",
     "label_ja": "AI売上開示リライト",
     "short_label_ja": "AI売上開示",
     "description_ja": "AI売上が資本市場にどう報告されるかの2026年リライト: SECのAI売上コンセプトリリースとCorporation Financeスタッフガイダンス、ファウンデーションラボ (OpenAI、Anthropic、xAI) による監査済み月次売上・WAU開示の定期化、Big-3ハイパースケーラのAIサービス10-Q脚注開示 (Microsoft Azure AIサービス・ランレート、Alphabet AIサービス・セグメント)、AMDのAIアクセラレータ売上10-Qセグメント脚注、AIアクセラレータIPO・S-1開示コホート (Cerebras、Tenstorrent、相手先別リスクファクター表、ハイパースケーラ・アンカーのワラント持分開示)、トークン単位マージン報告。",
     "label_es": "Reescritura de divulgación de ingresos de IA",
     "short_label_es": "Divulgación ingresos IA",
     "description_es": "La reescritura de 2026 sobre cómo se reportan los ingresos de IA a los mercados de capitales: concept release de ingresos de IA de la SEC y guía del personal de Corporation Finance, cadencia de divulgación de ingresos mensuales auditados y WAU de los laboratorios fundacionales (OpenAI, Anthropic, xAI), desgloses en notas 10-Q de servicios de IA de los Big-3 hyperscalers (run-rate de Azure AI Services de Microsoft, segmento AI Services de Alphabet), nota de segmento 10-Q de ingresos por aceleradores AI de AMD, cohorte de divulgación de IPO y S-1 de aceleradores AI (Cerebras, Tenstorrent, tablas de factores de riesgo por contraparte, divulgación de warrant-equity de anclas hyperscaler), reporte de margen por token.",
     "label_fil": "AI-Revenue Disclosure Rewrite",
     "short_label_fil": "AI-Revenue Disclosure",
     "description_fil": "Ang 2026 rewrite kung paano iniuulat ang kita ng AI sa capital markets: SEC AI-revenue concept release at staff guidance ng Corporation Finance, cadence ng audited monthly-revenue at WAU disclosure mula sa mga foundation lab (OpenAI, Anthropic, xAI), mga 10-Q footnote breakout ng AI-services ng Big-3 hyperscaler (run-rate ng Microsoft Azure AI Services, segment ng Alphabet AI Services), 10-Q segment footnote ng AI-accelerator revenue ng AMD, cohort ng IPO at S-1 disclosure ng AI-accelerator (Cerebras, Tenstorrent, per-counterparty risk-factor tables, warrant-equity disclosure ng hyperscaler-anchor), pag-uulat ng per-token margin."
   }
   ```
2. **Observation (no schema edit): `business.regulation-compliance` category dominance at 52.2 %.** First time a category has crossed the 50 % threshold since the 5/5 spike unwound. Unlike 5/5 this is structural, not a transient concentration: the category holds two large themes (`business.inference_server_supply_chain` added 5/10, plus `business.ai_security_compliance_market`). A category-level carve-out — splitting AI-security/compliance into a regulatory-CVE bucket vs an enterprise-compliance-market bucket — is the candidate fix, but per `design/memory-policy.md` §2.3 a new category requires its own design discussion and is out of scope for this Sunday's `apply-schema-edit` flow. Logged for the next milestone-level taxonomy discussion; recommendation 1 deliberately routes the new theme to `business.capital-supply-chain` rather than adding a third theme here.

   ```action
   {"kind": "log-only"}
   ```
3. **Observation (no schema edit): no underused themes for the third review running.** Every theme carries `child_ids ≥ 7`. The 5/10 `tech.ai_chip_architecture` description-widening worked — that theme went 2 → 7 children. No deprecate / merge / rewrite-description action is warranted this week; the underused-theme pain class is currently empty.
4. **Investigation (no schema edit): `SECONDARY_THEME_THRESHOLD` in `app/src/export.py`.** Fifth consecutive review flagging the same multi-attach pattern. The two themes added on 5/10 immediately became the #1 and #2 most-populated themes in the corpus (`business.inference_server_supply_chain` 50, `tech.ai_macro_capital_markets` 42), yet their primary cores are 29 and 32 — the gap is pure multi-attach inflation. `business.hyperscaler_frontier_lab_alliance` is the starkest case: 8 primary children, 40 total. Business multi-attach is 67.2 %, tech 52.3 %. Adding themes does not relieve this — it gives broad-token predictions more themes to saturate. Tightening the threshold, or requiring a non-generic token in the secondary-attach overlap, is the only structural fix. Defer to a separate engineering session; out of scope for this Sunday's `apply-schema-edit` flow.
5. **Investigation (no schema edit): `theme_candidates` label normalisation pass.** Carried forward from 5/10 and 5/5, still unaddressed. The candidate-extraction pass writes one row per prediction summary verbatim — 29 rows, every `suggested_theme_label` distinct, max exact-label hit count = 1. The `≥ 3 distinct-day` promotion rule in `design/memory-policy.md` §2.1 can never fire as written; recommendation 1's ~13-row cluster was only found by manual topic clustering. The candidate flow needs label normalisation (lowercase + stopword strip + token-set comparison, or LLM-driven clustering) before automated promotion is possible. Defer to a separate engineering session; out of scope for this Sunday's `apply-schema-edit` flow.

## Deferred for next week

- Category-level carve-out for `business.regulation-compliance` (now at 52.2 %, holds two large themes). Per §2.3 this needs its own design discussion — a new category is not an `apply-schema-edit` operation. Parked for the next milestone-level taxonomy review; revisit urgency if a future week pushes the category higher.
- `tech.infrastructure` density (45.3 %, three themes including the 42-child `tech.ai_macro_capital_markets`). Below the 50 % threshold; monitor only — re-examine if it crosses 50 %.
- Whether `business.cloud_vs_local_distribution` (11 children) and `tech.physical_ai_robotics` / `tech.ai_chip_architecture` (7 each) merit subtheme carve-outs. All in or near the overpopulated band but with uniform primary cores; re-examine if children pass 15 / 12 next week.
- The Physical AI Industrial Procurement candidate cluster (~4 pending rows). Below a confident `≥ 3` distinct-cluster promotion bar after dedup, and `tech.physical_ai_robotics` already covers Tesla Optimus / RaaS / 8-hour production runs — a description widening (not a new theme) would suffice if the cluster grows. Parked.
- A dedicated `tech.macro` / `business.capital-markets` category for the macro and revenue-disclosure themes — both currently parked under `tech.infrastructure` and `business.capital-supply-chain` respectively. Categories are more stable than themes (§2.3) and a new category needs its own design discussion.

---
