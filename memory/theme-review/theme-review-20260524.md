# Theme review — week ending 2026-05-24

Mode: Sunday rotation (5_weekly_theme_review). Bounded read of `docs/data/graph-*.json` + `app/src/schema.sql` + `theme_candidates` table.

## Diagnostic snapshot

Total themes: tech 9, business 8, mix 17. Total predictions: tech 109, business 119, mix 124 unique. Pending `theme_candidates`: 40 rows (23 business-scope, 17 tech-scope), all `candidate_reason='no_keyword_match'`, none carrying a `nearest_theme_id`. Three labels now appear with hit count = 2 (the AMD AI-accelerator 10-Q footnote, the SEC Corp Fin AI-accelerator IPO Staff Legal Bulletin, and the AI-accelerator S-1 per-counterparty risk-factor table — each duplicated across tech + business scopes); the other 37 are unique, max non-cross-scope hit count = 1. Same verbatim-label problem flagged on 5/17, 5/10, and 5/5 (see Theme candidates and recommendation 5 below).

One theme proposed on 5/17 was applied to `schema.sql` during the week: `business.ai_revenue_disclosure` (under `business.capital-supply-chain`). The new theme landed at the top of the corpus with 100 child_ids (79 primary / 21 secondary) — the largest theme ever observed in this project. This single placement drove `business.capital-supply-chain` from 7.5 % category density on 5/17 to **68.9 % this week**, the highest category dominance since the 5/5 spike (and structurally not a spike — see Category-level notes and recommendation 4).

The 5/17-flagged structural concentration on `business.regulation-compliance` (52.2 %) unwound to 20.2 % this week — the revenue-disclosure cluster that was over-attaching to compliance themes now primary-attaches to the new disclosure theme.

### Tech scope — theme attachments + category density

| Theme | Category | child_ids |
|---|---|---|
| AI Macro & Capital Markets (`tech.ai_macro_capital_markets`) | tech.infrastructure | 61 |
| Agent Runtime Security (`tech.agent_runtime_security`) | tech.security | 35 |
| Agent Registry Architecture (`tech.agent_registry_architecture`) | tech.standards | 35 |
| Model Supply Chain (`tech.model_supply_chain`) | tech.security | 24 |
| Agent Control Plane (`tech.agent_control_plane`) | tech.agents | 19 |
| Local Inference Runtime (`tech.local_inference_runtime`) | tech.inference-runtime | 13 |
| 1-bit / Edge LLM (`tech.one_bit_edge_llm`) | tech.models | 13 |
| Physical AI / Robotics (`tech.physical_ai_robotics`) | tech.infrastructure | 10 |
| AI Chip Architecture (`tech.ai_chip_architecture`) | tech.infrastructure | 9 |

Tech category density (primary attach via `theme_id` / `category_id`, 109 distinct predictions): **tech.infrastructure 55 / 109 = 50.5 %** (just crossed the 50 % dominance threshold — see Category-level notes), tech.security 18 / 109 = 16.5 %, tech.standards 17 / 109 = 15.6 %, tech.inference-runtime 10 / 109 = 9.2 %, tech.agents 6 / 109 = 5.5 %, tech.models 3 / 109 = 2.8 %. The 5/17 view at 45.3 % stepped over the threshold this week as `tech.ai_macro_capital_markets` grew from 42 → 61 children (44 primary).

### Business scope — theme attachments + category density

| Theme | Category | child_ids |
|---|---|---|
| AI-Revenue Disclosure Rewrite (`business.ai_revenue_disclosure`) | business.capital-supply-chain | 100 |
| Inference Server Supply Chain (`business.inference_server_supply_chain`) | business.regulation-compliance | 60 |
| Developer Toolchain Platformization (`business.developer_platformization`) | business.enterprise-adoption | 26 |
| Hyperscaler × Frontier Lab Alliance (`business.hyperscaler_frontier_lab_alliance`) | business.market-structure | 24 |
| Open Weight vs Proprietary AI (`business.open_weight_vs_proprietary`) | business.competition | 21 |
| AI Security Compliance Market (`business.ai_security_compliance_market`) | business.regulation-compliance | 16 |
| Cloud vs Local AI Distribution (`business.cloud_vs_local_distribution`) | business.distribution | 8 |
| Compute Capex Strategy (`business.compute_capex_strategy`) | business.capital-supply-chain | 4 |

Business category density (primary attach, 119 distinct predictions): **business.capital-supply-chain 82 / 119 = 68.9 %** (massively over the 50 % threshold, driven entirely by the new `business.ai_revenue_disclosure` theme placement), business.regulation-compliance 24 / 119 = 20.2 % (down from 52.2 % on 5/17), business.enterprise-adoption 6 / 119 = 5.0 %, business.market-structure 3 / 119 = 2.5 %, business.competition 3 / 119 = 2.5 %, business.distribution 1 / 119 = 0.8 %. The cross-week swing is a placement artefact — the underlying disclosure cluster did not change size, it just acquired a primary home theme. See Category-level notes and recommendation 4.

### Mix scope

Rolls up tech + business; same theme + category shape as above. Total unique predictions = 124.

### Multi-attach pressure (secondary-attach path in `app/src/export.py`)

Distribution of theme-parents per prediction (counted via theme-node `child_ids` membership):

- Tech (109 predictions): 52 attach to exactly one theme, 29 to two, 14 to three, 7 to four, 3 to five, 4 to six. 57 / 109 = 52.3 % multi-attach.
- Business (119 predictions): 53 attach to exactly one theme, 27 to two, 18 to three, 13 to four, 4 to five, 2 to six, 2 to seven. 66 / 119 = 55.5 % multi-attach.
- Mix (124 predictions): 12 attach to exactly one theme, 36 to two, 20 to three, 14 to four, 13 to five, 9 to six, 11 to seven, 3 to eight, 3 to nine, 2 to ten, 1 to eleven. 112 / 124 = **90.3 % multi-attach** — a new high for the mix scope.

The same broad-context-prediction pattern flagged on 4/27, 5/3, 5/5, 5/10, and 5/17. Primary-vs-secondary split on the most populated themes confirms the pattern: `business.ai_revenue_disclosure` 79 primary / 21 secondary (the rare case where the primary core is *larger* than the multi-attach inflation), `business.inference_server_supply_chain` 22 / 38 (multi-attach now bigger than primary), `tech.ai_macro_capital_markets` 44 / 17, `business.hyperscaler_frontier_lab_alliance` 3 primary / 21 secondary (8 → 3 primary as the disclosure theme captured former primaries), `business.ai_security_compliance_market` 2 primary / 14 secondary. See recommendation 5.

## Empty / underused themes

### tech
- (no underused themes — the lowest tech theme is `tech.ai_chip_architecture` at 9 children. The 5/10 description-widening has held; `tech.physical_ai_robotics` sits at 10. Both clear of the `child_ids ∈ {0, 1}` underused threshold.)

### business
- **`Compute Capex Strategy`** (`business.compute_capex_strategy`) — **4 children, primary core 3** (down from 7 on 5/17, 15 on 5/10). New underused finding this week. Not under the `child_ids ∈ {0, 1}` strict threshold but it stepped from "healthy" (15 children three weeks ago) through "lowest in scope" (7 two weeks ago) to "borderline underused" this week, and the cause is identifiable: the newly-added `business.ai_revenue_disclosure` (same `business.capital-supply-chain` category) is winning the matcher tournament on every prediction that mentions AMD, Cerebras, 10-Q footnote, or hyperscaler capex disclosure — exactly the vocabulary the existing `business.compute_capex_strategy` description was built on. Predictions about *capex commitments* (5GW Trainium capacity, 10-year compute deals, $175-185B Alphabet capex, hyperscaler buildout footprint) are still flowing in but are now multi-attach-only to this theme, not primary.
  - Suggested: sharpen `business.compute_capex_strategy` to vocabulary the revenue-disclosure theme does *not* cover — multi-year forward-supply commitments, GW capacity, accelerator-vendor backlog allocation, data-center power footprint, multi-cloud capacity warrants — and drop the 10-Q footnote / AMD-revenue / Cerebras-IPO tokens that now belong to `business.ai_revenue_disclosure`. The rewrite below is a sharpening, not a widening; total token count goes down by intent.

### mix
- (rolls up tech + business; the business.compute_capex_strategy underuse is the only one visible.)

## Overpopulated themes

Every theme in the schema carries `child_ids ≥ 4` this week — 9 / 9 tech and 7 / 8 business above 6. The `app/src/export.py` multi-attach saturation flagged on 5/3, 5/5, 5/10, and 5/17 is the dominant cause for the larger themes; the on-topic primary cores are far smaller than the `child_ids` totals. Cluster inspection of the four most populated themes:

### business
- **`AI-Revenue Disclosure Rewrite`** (100 children — new record high for any theme observed in this corpus) — **79 primary children**, the largest primary core ever observed. The cluster is internally coherent on a glance through the primary children (SEC AI-revenue concept release, OpenAI / Anthropic / xAI audited monthly revenue + WAU cadence, Microsoft 10-Q AI-business KPIs, Alphabet AI Services 10-Q footnote, AMD AI-accelerator 10-Q segment, Cerebras IPO pricing, AI-accelerator S-1 per-counterparty risk-factor tables, Tenstorrent IPO disclosure cohort, hyperscaler-anchor warrant-equity disclosure, per-token-margin reporting, AI-capex ROI repricing, agent-displaced-SaaS revenue repricing). Remaining 21 are secondary multi-attach.
  - Suggested: leave as-is. A 79-child primary core that is uniform around a single thesis arc (the 2026 rewrite of how AI revenue is reported to capital markets) is not "overpopulated" in the pathological sense — it is a sectoral theme catching its sector. The size is unusual but the cluster is coherent. Watch over the next 2-3 weeks: if the primary core fragments into distinct sub-clusters (e.g. SEC-vs-corporate-issuer-vs-IPO-cohort), a split is warranted; for now there is no clear cleavage.
- **`Inference Server Supply Chain`** (60 children) — 22 primary children, a coherent AI-security-substrate cluster (inference-server CVE class, CISA AI-Infra KEV sub-catalog, signed-checkpoint loading defaults, NIST non-human-identity profile, FMRB executive order, agent-skills threat sub-matrix). Remaining 38 are secondary multi-attach — a higher ratio than 5/17 (50 children, 29 primary, 21 secondary), because the new disclosure theme pulled away some primary attachments.
  - Suggested: leave as-is. The 22-child primary core is uniform around the inference-server-CVE-becomes-regulation thesis; the multi-attach inflation is `export.py`-driven, not a schema fault.
- **`Developer Toolchain Platformization`** (26 children, +3 from 5/17's 23) — primary core 6 (Agent Control Plane as hyperscaler battleground, Capital markets reprice agent-displaced SaaS by API share, local-first coding agents standardize cloud-overflow, Codex CLI 0.128.0 model-provider-owned discovery, Microsoft Foundry Toolkit, GitHub-as-platform consolidation). Remaining 20 multi-attach.
  - Suggested: leave as-is. Same export.py multi-attach pattern.
- **`Hyperscaler × Frontier Lab Alliance`** (24 children, down from 40 on 5/17) — only 3 primary children now (down from 8 last week). Multi-attach is 21 — the same export.py inflation pattern. The primary-children drop is again a placement artefact: predictions about Anthropic-AWS or Microsoft-OpenAI revenue dynamics now primary-attach to `business.ai_revenue_disclosure` instead of `business.hyperscaler_frontier_lab_alliance`.
  - Suggested: leave as-is. The schema theme is correctly sized at 3 primary children for the *partnership-structure* cluster proper; the 21 multi-attach rows are mostly broad-token predictions about cloud-lab alliances that touch any of the secondary tokens.

### tech
- **`AI Macro & Capital Markets`** (61 children, +19 from 5/17) — 44 primary children, still the largest tech-side primary core. Cluster internally coherent (AI-revenue-disclosure rewrite, SEC concept release, audited monthly revenue cadence, AMD/Microsoft/Alphabet 10-Q footnote breakouts, Cerebras IPO, AI-accelerator S-1 cohort, Powell-Fed institutional-volatility regime, FOMC dissent norm, AI-capex ROI repricing, Apple-buyback collision with $700B AI-capex print). Remaining 17 multi-attach.
  - Suggested: leave as-is. Tech-scope counterpart to `business.ai_revenue_disclosure`; the two themes are deliberately scope-paired and share no theme_id. The 5/24 widening of vocabulary on the business theme transferred well — the matcher routed business-scope predictions there as intended.
- **`Agent Runtime Security`** (35 children, +6 from 5/17) — primary core 12 (indirect prompt injection, MCP attack surface, inference-server CVEs, agentic-AI CVE class, agent-skills attack surface, LLM-tooling + Linux-kernel CVE chain). Remaining 23 multi-attach.
  - Suggested: leave as-is.
- **`Agent Registry Architecture`** (35 children, +4 from 5/17) — primary core 17 (cross-cloud agent-identity + MCP registry, NIST non-human-identity control profile, Microsoft Agent 365 registry sync, agent-skills threat sub-matrix, agent-as-first-class-identity statute, Headless Everything via MCP). Remaining 18 multi-attach.
  - Suggested: leave as-is.

## Theme candidates

`theme_candidates` holds 40 pending rows (was 29 on 5/17, 39 on 5/10). All 40 are `no_keyword_match` with no `nearest_theme_id`. 37 of 40 labels are unique with exact-label hit count = 1; the remaining 3 labels each appear twice (one tech-scope row + one business-scope row) — three predictions describing AMD AI-accelerator 10-Q footnote, SEC Corp Fin AI-accelerator IPO Staff Legal Bulletin, and AI-accelerator S-1 per-counterparty risk-factor tables show up in both scopes' candidate rows. Max within-scope hit count remains 1; the `≥ 3 distinct-day` promotion rule from `design/memory-policy.md` §2.1 still cannot fire as written. The five-week label-normalisation gap (5/5, 5/10, 5/17, this week) is still unaddressed (recommendation 5).

Manual clustering by topic surface (same exercise as 5/17):

| scope | suggested label | rough hits in pending | candidate home | sample evidence |
|---|---|---|---|---|
| business | AI-Revenue Disclosure Rewrite | ~14 | **exists** (`business.ai_revenue_disclosure`) — keyword expansion needed | OpenAI audited monthly revenue + WAU cadence; Foundation labs audited monthly revenue + per-token margin; Microsoft audited monthly AI-business KPIs as 10-Q footnote; AMD AI-accelerator revenue 10-Q segment footnote (×2 rows); Big-3 hyperscalers AI-services 10-Q revenue footnote; Alphabet AI Services 10-Q footnote breakout; SEC drafts AI-revenue concept release; SEC Corp Fin AI-accelerator S-1 staff guidance / IPO Staff Legal Bulletin; AI-accelerator S-1s per-counterparty risk-factor table; Cerebras IPO pricing; Powell stays on Fed Board; FOMC dissent norm reverts |
| tech | AI Cyber-Eval Reciprocity / FMRB | **~3** | **no home** — new theme candidate | AISI cyber-eval reciprocity locks in as allied procurement gate by Q3 2026; FMRB executive order adopts allied cyber-eval reciprocity ladder by Q3 2026; FMRB executive order signs by July 2026 with allied procurement mirror clause |
| tech | Loader-Verification Default | ~4 (tech) + 1 (business) | `tech.model_supply_chain` (after small widening) | Loader-verification chain ships training-to-tenant signed default by H2 2026; Loader-verification eight-document reference set settles as the mid-June default-shipment anchor; Loader-verification nine-document reference set anchors mid-June default shipment across five frameworks; Unified loader-verification model ships as framework default by mid-June 2026; GGUF supply chains gate uploads via signed cards + SSTI scans |
| tech | Hyperscaler Capital Coupling | ~3 | `business.hyperscaler_frontier_lab_alliance` (existing) | AGI-clause unwind spreads to peer hyperscaler-lab contracts; Frontier-AI cloud capacity locks into three-cloud training oligopoly; Hyperscaler-AI-lab capital coupling hardens into compute lock-in |
| business | Physical AI Industrial Procurement | ~3 | `tech.physical_ai_robotics` (already covers Tesla Optimus / RaaS / 8-hour production runs) | Robot-control training consolidates in cloud as per-robot SaaS; Physical AI 8-hour production runs become enterprise RFP cuts; Physical AI league tables rank top-five OEM humanoids |
| business | Agent Registry / MCP Convergence | ~2 | `tech.agent_registry_architecture` (existing) | Agent registry standard converges with MCP for agent artifacts; Headless Everything standardizes via MCP/Agent Registry |
| business | Edge / Local-LLM Recipe | ~2 | `tech.one_bit_edge_llm` / `business.cloud_vs_local_distribution` | Bonsai 8B anchors 1-bit native training as default edge-LLM recipe; 27B Dense + 1M context becomes default enterprise local-LLM recipe |
| tech | Multi-Cloud SLA Wave | ~1 | none yet — sub-threshold | Multi-cloud frontier-model SLA standardization wave breaks by H2 2026 |

Two clusters cross the actionable bar this week:

1. **AI Cyber-Eval Reciprocity / FMRB** (3 tech-scope rows, no home). New cluster, distinct from the existing security-compliance themes — focuses on cross-jurisdictional regulatory reciprocity (US AISI ↔ allied AI safety institutes ↔ FMRB executive-order procurement mirror clause), not CVE substrate. Recommendation 1.
2. **Loader-Verification Default** (5 rows total, 4 tech + 1 business). Closely related to but not currently covered by `tech.model_supply_chain` — the existing description emphasises signing / provenance / GGUF-supply-chain risk, but the new candidate vocabulary is "loader-verification chain", "training-to-tenant signed default", "mid-June 2026 reference set", "five-framework default shipment". A description widening absorbs this cluster cleanly without a new theme. Recommendation 2.

The AI-revenue-disclosure cluster (~14 business + 4 tech in pending) is striking because `business.ai_revenue_disclosure` already exists with 100 children — meaning the matcher *can* attach this material, but the candidate-extraction pass apparently produces rows *before* the matcher runs against the new theme's keywords. Since these candidates are leftovers from the pre-5/17 schema state, they should clear on the next ingest run that touches them. No action needed.

The physical AI industrial procurement cluster (~3 rows) and the agent-registry / MCP cluster (~2 rows) fit existing themes adequately; the edge-LLM cluster (~2 rows) is below the conservative `≥ 3` distinct-day bar on its own. All parked.

## Category-level notes

- **`business.capital-supply-chain` carries 82 / 119 = 68.9 % of business-scope predictions** — by a large margin the highest category dominance ever observed in this project (previous peak: 78.4 % on 5/5 was a different scope). Root cause is structural and self-inflicted by last week's recommendation 1: when the 5/17 review proposed `business.ai_revenue_disclosure`, the only existing business-scope category that fit the disclosure subject was `business.capital-supply-chain`, and the proposal explicitly noted the placement would "relieve that category's thinness". The relief was over-effective: a 100-child theme is now ~80 % of the category's total weight. A proper fix is a dedicated `business.capital-markets` category — but per `design/memory-policy.md` §2.3 a new category needs its own design discussion and is out of scope for this Sunday's `apply-schema-edit` flow. See recommendation 4.
- **`tech.infrastructure` carries 55 / 109 = 50.5 % of tech-scope predictions** — just crossed the 50 % threshold (was 45.3 % on 5/17). Same root cause shape as `business.capital-supply-chain` but milder: it hosts three themes including the 61-child `tech.ai_macro_capital_markets`. The cross-week step was 5.2 percentage points driven by `tech.ai_macro_capital_markets` growing from 42 → 61 children. Logged in recommendation 4 alongside the business category; both point to the same `tech.macro` / `business.capital-markets` carve-out conversation.
- `business.regulation-compliance` carries 24 / 119 = 20.2 % — back below the 50 % threshold (was 52.2 % on 5/17). Unwound exactly as the 5/17 narrative predicted once revenue-disclosure predictions found a primary home outside the compliance category. No action.
- (Two categories cross 50 %-attention this week; both flagged for the same category-level discussion.)

## Recommended actions

1. **Add new theme `tech.frontier_model_regulatory_board`** under `tech.standards`. The AI-cyber-eval-reciprocity / FMRB cluster has 3 pending tech-scope rows (AISI cyber-eval reciprocity as allied procurement gate; FMRB executive order with allied cyber-eval reciprocity ladder; FMRB executive order with allied procurement mirror clause). Distinct from existing security themes — covers cross-jurisdictional regulatory mirror clauses, allied AI-safety-institute reciprocity, frontier-model regulatory board executive-order vocabulary. `tech.standards` is the closest existing category (it already houses `tech.agent_registry_architecture` and is broadly the "governance protocols, schemas, interoperability" bucket). Hits the `≥ 3` distinct-cluster promotion bar on first appearance.

   ```action
   {
     "kind": "add",
     "theme_id": "tech.frontier_model_regulatory_board",
     "category_id": "tech.standards",
     "label_en": "Frontier Model Regulatory Board",
     "short_label_en": "FMRB",
     "tooltip_en": "Frontier Model Regulatory Board",
     "description_en": "Cross-jurisdictional regulatory architecture for frontier AI: Frontier Model Regulatory Board (FMRB) executive order, AISI cyber-eval reciprocity ladder, allied AI-safety-institute mutual recognition, allied procurement mirror clauses, cross-border cyber-evaluation reciprocity gates, allied procurement gating, frontier-model evaluation regime as procurement primitive, executive-order signing windows, mid-2026 regulatory-board buildout cadence.",
     "label_ja": "フロンティアモデル規制ボード",
     "short_label_ja": "FMRB",
     "description_ja": "フロンティアAIの跨管轄規制アーキテクチャ: Frontier Model Regulatory Board (FMRB) 大統領令、AISI サイバー評価相互承認はしご、同盟国 AI 安全機関の相互認証、同盟国調達ミラー条項、国境横断サイバー評価相互承認ゲート、同盟国調達ゲーティング、調達プリミティブとしてのフロンティアモデル評価レジーム、大統領令署名ウィンドウ、2026 年中盤の規制ボード構築ケイデンス。",
     "label_es": "Junta Reguladora de Modelos Frontier",
     "short_label_es": "FMRB",
     "description_es": "Arquitectura regulatoria transjurisdiccional para IA frontera: orden ejecutiva de la Frontier Model Regulatory Board (FMRB), escalera de reciprocidad de cyber-eval del AISI, reconocimiento mutuo entre AI safety institutes aliados, cláusulas espejo de aprovisionamiento aliado, gates de reciprocidad de cyber-evaluación transfronteriza, gating de aprovisionamiento aliado, régimen de evaluación de modelos frontera como primitiva de aprovisionamiento, ventanas de firma de orden ejecutiva, cadencia de construcción de la junta regulatoria a mediados de 2026.",
     "label_fil": "Frontier Model Regulatory Board",
     "short_label_fil": "FMRB",
     "description_fil": "Cross-jurisdictional regulatory architecture para sa frontier AI: executive order ng Frontier Model Regulatory Board (FMRB), AISI cyber-eval reciprocity ladder, mutual recognition ng mga kaalyadong AI safety institute, allied procurement mirror clauses, cross-border cyber-evaluation reciprocity gates, gating ng allied procurement, frontier-model evaluation regime bilang procurement primitive, mga executive-order signing window, cadence ng pagtatayo ng regulatory board sa kalagitnaan ng 2026."
   }
   ```
2. **Rewrite description on `tech.model_supply_chain`** to absorb the 5-row loader-verification-default cluster. The existing description leads on "model signing, provenance attestation, SLSA-for-models, sigstore, safetensors integrity, GGUF supply-chain risk" — close to but not actually containing the candidate vocabulary "loader-verification chain", "training-to-tenant signed default", "framework-default shipment", "five-framework default", "mid-June 2026 reference set". The widening keeps the existing keyword set intact and appends the new loader-verification vocabulary; the theme already sits in `tech.security` and the cluster fits naturally — a new theme would be over-fitting.

   ```action
   {
     "kind": "rewrite-description",
     "theme_id": "tech.model_supply_chain",
     "new_description_en": "Model signing, provenance attestation, SLSA-for-models, sigstore, safetensors integrity, GGUF supply-chain risk, malicious model files, tokenizer templates, gated distribution programs, Anthropic Project Glasswing, Mythos Preview, partner-list distribution, usage-credit tier gates, AWS Bedrock Gated Research Preview, Bonsai / Qwen / Llama / DeepSeek / Kimi / GLM-5.1 distribution channels, Hugging Face / Ollama / ModelScope marketplace governance, model artifact attestation, loader-verification chain, training-to-tenant signed default loader, unified loader-verification model, framework-default loader shipment, five-framework signed-loader default, mid-2026 loader-reference-set anchor, GGUF signed-card upload gate, SSTI scan on model upload.",
     "new_description_ja": "モデル署名、出所証明、SLSA-for-models、sigstore、safetensors 完全性、GGUF サプライチェーン・リスク、悪意あるモデルファイル、tokenizer テンプレート、ゲート付き配布プログラム、Anthropic Project Glasswing、Mythos Preview、パートナーリスト配布、利用クレジット階層ゲート、AWS Bedrock Gated Research Preview、Bonsai / Qwen / Llama / DeepSeek / Kimi / GLM-5.1 配布チャネル、Hugging Face / Ollama / ModelScope マーケットプレイス統治、モデル成果物アテステーション、ローダー検証チェーン、training-to-tenant 署名済みデフォルトローダー、統一ローダー検証モデル、フレームワークデフォルトのローダー出荷、5フレームワーク横断の署名済みローダーデフォルト、2026 年中盤のローダー参照セットアンカー、GGUF 署名済みカードによるアップロードゲート、モデルアップロード時の SSTI スキャン。",
     "new_description_es": "Firma de modelos, atestación de procedencia, SLSA-for-models, sigstore, integridad de safetensors, riesgo de cadena de suministro GGUF, archivos de modelo maliciosos, plantillas de tokenizer, programas de distribución gated, Anthropic Project Glasswing, Mythos Preview, distribución por lista de socios, gates de tier de créditos de uso, AWS Bedrock Gated Research Preview, canales de distribución Bonsai / Qwen / Llama / DeepSeek / Kimi / GLM-5.1, gobernanza de marketplace Hugging Face / Ollama / ModelScope, atestación de artefactos de modelo, cadena de loader-verification, loader firmado por defecto training-to-tenant, modelo unificado de loader-verification, envío de loader por defecto de framework, default firmado de loader a través de cinco frameworks, anclaje del conjunto de referencia de loader a mediados de 2026, gate de subida con tarjeta firmada GGUF, escaneo SSTI en subida de modelo.",
     "new_description_fil": "Model signing, provenance attestation, SLSA-for-models, sigstore, safetensors integrity, GGUF supply-chain risk, mga maling model file, tokenizer templates, gated distribution programs, Anthropic Project Glasswing, Mythos Preview, partner-list distribution, usage-credit tier gates, AWS Bedrock Gated Research Preview, mga channel ng distribution ng Bonsai / Qwen / Llama / DeepSeek / Kimi / GLM-5.1, governance ng Hugging Face / Ollama / ModelScope marketplace, model artifact attestation, loader-verification chain, training-to-tenant signed default loader, unified loader-verification model, framework-default loader shipment, five-framework signed-loader default, mid-2026 loader-reference-set anchor, GGUF signed-card upload gate, SSTI scan sa pag-upload ng modelo."
   }
   ```
3. **Rewrite description on `business.compute_capex_strategy`** to reclaim its core from `business.ai_revenue_disclosure`. New underused finding (4 children, primary core 3 — down from 7 on 5/17 and 15 on 5/10). The existing description leads on tokens (`AMD AI-accelerator`, `Cerebras`, `10-Q footnote`, `Microsoft Azure capex`) that the matcher now routes to `business.ai_revenue_disclosure` instead, leaving the capex-strategy theme without primary signal. The rewrite below sharpens to vocabulary the disclosure theme does *not* cover (forward-supply commitments, GW capacity, data-center power footprint, vendor backlog allocation, multi-year compute deals, capacity warrants) and explicitly drops the revenue-shaped tokens that now belong to `business.ai_revenue_disclosure`. Total token count is intentionally lower than the prior description.

   ```action
   {
     "kind": "rewrite-description",
     "theme_id": "business.compute_capex_strategy",
     "new_description_en": "Multi-year compute capex commitments and capacity strategy: 10-year hyperscaler compute deals, 5GW Trainium capacity commitments, GW-scale data-center power footprint, accelerator-vendor multi-quarter backlog allocation, hyperscaler buildout cadence, forward-supply 8-K commitments, hyperscaler capacity warrants, Vera Rubin / MAIA accelerator commitments, Tesla compute capex, capex-as-strategic-asset positioning, capacity-coupling between cloud providers and accelerator vendors. (Revenue disclosure of capex is covered by business.ai_revenue_disclosure, not here.)",
     "new_description_ja": "複数年にわたる計算 capex コミットメントとキャパシティ戦略: ハイパースケーラの10年計算契約、5GW Trainium キャパシティ・コミットメント、GW 規模のデータセンター電力フットプリント、アクセラレータ・ベンダーの複数四半期バックログ配分、ハイパースケーラ建設ケイデンス、先渡し供給 8-K コミットメント、ハイパースケーラ・キャパシティ・ワラント、Vera Rubin / MAIA アクセラレータ・コミットメント、Tesla の計算 capex、戦略資産としての capex ポジショニング、クラウド事業者とアクセラレータ・ベンダー間のキャパシティ・カップリング。(capex の売上開示は business.ai_revenue_disclosure 側でカバー)",
     "new_description_es": "Compromisos de capex de cómputo plurianuales y estrategia de capacidad: contratos de cómputo de hyperscaler a 10 años, compromisos de capacidad Trainium de 5GW, huella de energía de centros de datos a escala GW, asignación de backlog plurimensual de proveedores de aceleradores, cadencia de buildout de hyperscaler, compromisos de oferta forward 8-K, warrants de capacidad de hyperscaler, compromisos de aceleradores Vera Rubin / MAIA, capex de cómputo de Tesla, posicionamiento de capex como activo estratégico, acoplamiento de capacidad entre proveedores de nube y proveedores de aceleradores. (La divulgación de ingresos asociada al capex la cubre business.ai_revenue_disclosure, no este tema.)",
     "new_description_fil": "Multi-year na compute capex commitments at capacity strategy: 10-taong compute deals ng hyperscaler, 5GW Trainium capacity commitments, GW-scale data-center power footprint, multi-quarter backlog allocation ng mga accelerator vendor, cadence ng buildout ng hyperscaler, forward-supply 8-K commitments, mga hyperscaler capacity warrant, mga commitment para sa Vera Rubin / MAIA accelerators, Tesla compute capex, positioning ng capex bilang strategic asset, capacity-coupling sa pagitan ng mga cloud provider at accelerator vendor. (Ang revenue disclosure ng capex ay sakop ng business.ai_revenue_disclosure, hindi nito.)"
   }
   ```
4. **Observation (no schema edit): two categories now cross 50 % attention — `business.capital-supply-chain` at 68.9 % and `tech.infrastructure` at 50.5 %.** Both are driven by the same root cause: a single sectoral theme (`business.ai_revenue_disclosure` with 100 kids, `tech.ai_macro_capital_markets` with 61 kids) now dominates its category. The proper fix is two new categories — `business.capital-markets` / `tech.macro` — to carve the macro / capital-markets themes out from the infrastructure / supply-chain buckets where they were placed for lack of a better home. Per `design/memory-policy.md` §2.3 a new category needs its own design discussion and is out of scope for this Sunday's `apply-schema-edit` flow. Logged for the next milestone-level taxonomy discussion; this is now the third week running that one of these themes' placement has generated a category-level dominance flag (5/17 was `business.regulation-compliance` at 52.2 % when the inference-server-supply-chain theme landed there; this week the placement-induced dominance is wider and on two categories simultaneously). The category-level structural mismatch should be treated as a milestone-priority discussion item, not a "park and revisit" task.

   ```action
   {"kind": "log-only"}
   ```
5. **Investigation (no schema edit): `SECONDARY_THEME_THRESHOLD` in `app/src/export.py` + `theme_candidates` label normalisation pass.** Sixth consecutive review flagging the multi-attach pattern; fifth consecutive review flagging the candidate-label-uniqueness problem; they share a root cause (broad-token tolerance) and stay paired here. Tech multi-attach 52.3 %, business 55.5 %, **mix 90.3 %** — the mix-scope number is a new high. Primary-vs-secondary on the most populated themes: `business.inference_server_supply_chain` 22 primary / 38 secondary (multi-attach now exceeds primary), `business.hyperscaler_frontier_lab_alliance` 3 primary / 21 secondary, `business.ai_security_compliance_market` 2 primary / 14 secondary. On the candidate side: 40 pending rows, 37 unique labels, only 3 labels at hit count 2 (and those duplicates are cross-scope artefacts, not genuine clusters). The `≥ 3 distinct-day` promotion rule still cannot fire as written; recommendation 1's 3-row FMRB cluster was only surfaced by manual topic clustering during this review. Both problems remain out of scope for `apply-schema-edit` — they need engineering work on `app/src/export.py` (secondary-attach threshold) and on the candidate-extraction pass (label normalisation). Deferred again.

   ```action
   {"kind": "log-only"}
   ```

## Deferred for next week

- Category-level carve-out of `business.capital-markets` and `tech.macro`. Both `business.capital-supply-chain` (68.9 %) and `tech.infrastructure` (50.5 %) now cross the 50 % threshold, driven by the sectoral macro / capital-markets themes (100 + 61 children combined). Per §2.3 this is a new-category discussion, not an `apply-schema-edit` operation. The cross-week trend — 5/17 flagged the matching structural issue under a different category — pushes this from "park and revisit" to "milestone-priority".
- Whether `business.ai_revenue_disclosure` (100 children, 79 primary) eventually fragments into sub-clusters worth splitting (e.g. SEC-side vs corporate-issuer-side vs IPO-cohort-side). The primary core is currently uniform; re-examine in 2-3 weeks if a clear sub-cleavage emerges. The dashboard renders fine at 100 children, but a 79-primary cluster is large enough that some users may benefit from a sub-pivot.
- Whether `business.cloud_vs_local_distribution` (8 children, 1 primary) and `tech.physical_ai_robotics` / `tech.ai_chip_architecture` (10 / 9 each) need work. All sit in the lower band but their primary cores are coherent — `business.cloud_vs_local_distribution` is the most exposed at primary=1, and could be a future merge candidate with `tech.local_inference_runtime` if it continues to lose primary attachments. Monitor.
- The Physical AI Industrial Procurement candidate cluster (~3 pending rows). At the `≥ 3` bar for the second week running but `tech.physical_ai_robotics` already covers Tesla Optimus / RaaS / 8-hour production runs. If next week shows ≥ 4 pending rows for procurement-specific vocabulary, a description widening (not a new theme) becomes warranted.
- `business.compute_capex_strategy` follow-through after this week's description sharpening (recommendation 3). If primary count does not recover from 3 back toward 6+ over 2 weeks, the theme is competing for a niche that the revenue-disclosure theme has structurally absorbed — at which point a merge into `business.ai_revenue_disclosure` (rather than maintaining a parallel theme) becomes the cleaner option.

---
