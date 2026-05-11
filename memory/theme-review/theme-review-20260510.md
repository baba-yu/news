# Theme review — week ending 2026-05-10

Mode: Sunday rotation (5_weekly_theme_review). Bounded read of `docs/data/graph-*.json` + `app/src/schema.sql` + `theme_candidates` table.

## Diagnostic snapshot

Total themes: tech 8, business 6, mix 14. Total predictions: tech 47, business 48, mix 67 unique. Pending theme_candidates: 39 rows, all `no_keyword_match`, every row a single distinct label (max hit count = 1, none crosses the ≥ 3 promotion threshold).

### Tech scope — theme attachments + category density

| Theme | Category | child_ids |
|---|---|---|
| Agent Runtime Security (`tech.agent_runtime_security`) | tech.security | 25 |
| Agent Registry Architecture (`tech.agent_registry_architecture`) | tech.standards | 21 |
| 1-bit / Edge LLM (`tech.one_bit_edge_llm`) | tech.models | 12 |
| Model Supply Chain (`tech.model_supply_chain`) | tech.security | 12 |
| Agent Control Plane (`tech.agent_control_plane`) | tech.agents | 11 |
| Physical AI / Robotics (`tech.physical_ai_robotics`) | tech.infrastructure | 9 |
| Local Inference Runtime (`tech.local_inference_runtime`) | tech.inference-runtime | 8 |
| AI Chip Architecture (`tech.ai_chip_architecture`) | tech.infrastructure | 2 |

Tech category density (primary attach only, 47 distinct predictions): tech.security 18 / 47 = 38.3 %, tech.standards 8 / 47 = 17.0 %, tech.agents 6 / 47 = 12.8 %, tech.infrastructure 6 / 47 = 12.8 %, tech.inference-runtime 5 / 47 = 10.6 %, tech.models 4 / 47 = 8.5 %. No category crosses the 50 % dominance threshold this week (was 76.9 % on 5/5; the unusual security-heavy concentration has unwound).

### Business scope — theme attachments + category density

| Theme | Category | child_ids |
|---|---|---|
| Hyperscaler × Frontier Lab Alliance (`business.hyperscaler_frontier_lab_alliance`) | business.market-structure | 38 |
| AI Security Compliance Market (`business.ai_security_compliance_market`) | business.regulation-compliance | 27 |
| Open Weight vs Proprietary AI (`business.open_weight_vs_proprietary`) | business.competition | 21 |
| Developer Toolchain Platformization (`business.developer_platformization`) | business.enterprise-adoption | 19 |
| Compute Capex Strategy (`business.compute_capex_strategy`) | business.capital-supply-chain | 15 |
| Cloud vs Local AI Distribution (`business.cloud_vs_local_distribution`) | business.distribution | 13 |

Business category density (primary attach only, 48 distinct predictions): business.market-structure 16 / 48 = 33.3 %, business.regulation-compliance 10 / 48 = 20.8 %, business.capital-supply-chain 10 / 48 = 20.8 %, business.enterprise-adoption 6 / 48 = 12.5 %, business.competition 5 / 48 = 10.4 %, business.distribution 1 / 48 = 2.1 %. No category crosses the 50 % dominance threshold this week (was 78.4 % on 5/5; same unwind as tech.security).

### Mix scope

Rolls up tech + business; same theme + category shape as above. Total unique predictions = 67.

### Multi-attach pressure (secondary-attach path in `app/src/export.py`)

Distribution of theme-parents per prediction:

- Tech (47 predictions): 18 attach to exactly one theme, 13 to two, 10 to three, 4 to four, 2 to five. 29 / 47 = 61.7 % multi-attach.
- Business (48 predictions): 9 attach to exactly one theme, 12 to two, 12 to three, 12 to four, 2 to five, 1 to six. 39 / 48 = 81.2 % multi-attach.

Both numbers are wider than 5/5. This is the same broad-context-prediction pattern flagged on 4/27, 5/3, and 5/5 — broad-token predictions saturate every theme they share even one rare token with.

## Empty / underused themes

### tech
- **`AI Chip Architecture`** (`tech.ai_chip_architecture`) — 2 children (`Hyperscaler training-vs-inference SKU split`, `AMD breaks out AI-accelerator revenue as 10-Q segment footnote`). Third consecutive week the theme is the sole underused theme in the schema, and the 5/5 description-widening recommendation was not applied during the week. The chip-architecture signal in the 5/10 corpus is high (Cerebras IPO mid-May print, AMD AI-accelerator revenue cluster, training-vs-inference SKU split), but those predictions are absorbed by `business.hyperscaler_frontier_lab_alliance` and `business.compute_capex_strategy` via the multi-attach path.
  - Suggested: re-apply the 5/5 widening — add **Cerebras IPO, WSE-3, AMD MI355X, AMD AI-accelerator revenue, training-vs-inference SKU split, accelerator-revenue 10-Q segment footnote, GB300 vs Trainium positioning, per-accelerator margin disclosure, hyperscaler custom silicon** terminology to the description.

### business
- (no underused themes — all 6 carry ≥ 13 children.)

### mix
- (rolls up tech + business; no mix-specific empties.)

## Overpopulated themes

The 5/3 and 5/5 diagnosis holds and worsens: the broad-context multi-attach pattern in `app/src/export.py` continues to saturate every theme any broad-token prediction shares a single rare token with. 11 of 14 themes carry ≥ 6 children, the top four crest the overpopulation band. Cluster inspection from 5/5 carries over — the on-topic cores are ~ 6 – 10 children per theme, the remainder is multi-attach noise.

### tech
- **`Agent Runtime Security`** (25 children, +4 from 5/5's 21) — on-topic core still ~ 10 (Indirect prompt injection, MCP attack surface, Inference-server SSTI / CVE, Agentic-AI CVE class, Agent-skills attack surface, CISA AI-Infra KEV, LLM-tooling + Linux-kernel CVE chain, Frontier cyber-AI export-control). Remaining 15 are multi-attach.
  - Suggested: leave as-is. The on-topic cluster is coherent (AI-security-substrate thesis arc). The multi-attach noise is an `export.py` threshold issue, not a schema issue.
- **`Agent Registry Architecture`** (21 children, +4 from 5/5's 17) — on-topic core ~ 7 (Cross-cloud agent-identity + MCP registry RFC, NIST non-human-identity control profile, Agent registry standard converges with MCP, Microsoft Agent 365 MCP policy enforcement, Agent-skills threat sub-matrix, Agent-as-first-class-identity statute, Headless Everything via MCP). Remaining 14 multi-attach.
  - Suggested: leave as-is. Same export.py multi-attach pattern.

### business
- **`Hyperscaler × Frontier Lab Alliance`** (38 children, +9 from 5/5's 29) — still the most populated theme in the corpus. On-topic core ~ 10 (Anthropic-AWS 5-pole regime, Three-cloud training oligopoly, Hyperscaler-AI-lab capital coupling, Big-3 per-token-margin floor, Frontier-model SOC2/FedRAMP/FMF baseline, Multi-cloud SLA standardization, AGI-clause unwind, Foundation labs audited monthly revenue, Hyperscaler custom silicon training/inference SKU split, Tier-1 cloud capacity capture). Remaining 28 multi-attach.
  - Suggested: leave as-is. The on-topic cluster is uniform — splitting a healthy 10-child cluster to clean up 28 multi-attach rows is the wrong tradeoff.
- **`AI Security Compliance Market`** (27 children, +9 from 5/5's 18) — on-topic core ~ 7 (Frontier-model SOC2 baseline, MCP protocol redesign as enterprise bottleneck, Agentic-AI CVE class CNA, OCC agentic-AI MRM addendum, Agent-in-the-Loop Secret Exfiltration, Frontier cyber-AI export-control, OpenAI audited monthly revenue cadence). Remaining 20 multi-attach.
  - Suggested: leave as-is.
- **`Open Weight vs Proprietary AI`** (21 children, +7 from 5/5's 14) — on-topic core ~ 6 (Closed-weight frontier crystallizes / open-weights cap at 35B-A3B, Open-weight 1M-context era arrives as new floor, Consumer-GPU coding agents displace cloud-only APIs, Local-LLM stacks expose unified compressed-KV-cache flag, Unsloth 2026 stack as managed fine-tuning service, Per-token pricing floor competition). Remaining 15 multi-attach.
  - Suggested: leave as-is.
- **`Developer Toolchain Platformization`** (19 children, +5 from 5/5's 14) — on-topic core ~ 5 (Agent Control Plane as hyperscaler battleground, Capital markets reprice agent-displaced SaaS by API share, Consumer-GPU coding agents displace cloud-only APIs, Multi-cloud SLA standardization wave, Unsloth 2026 stack as managed fine-tuning service). Remaining 14 multi-attach.
  - Suggested: leave as-is.
- **`Compute Capex Strategy`** (15 children, +3 from 5/5's 12) — on-topic core ~ 6 (Hyperscaler training/inference SKU split, Big-3 per-token-margin floor, Hyperscaler per-token-margin-gated GPU capex, AMD AI-accelerator revenue 10-Q footnote, Microsoft audited monthly KPIs as 10-Q footnote, KV-cache-compression dtype as inference-stack knob). Remaining 9 multi-attach.
  - Suggested: leave as-is.
- **`Cloud vs Local AI Distribution`** (13 children) — first appearance over the 6-threshold this review. On-topic core ~ 6 (Local-first cloud-overflow inversion, SMB local-first adoption, 27B Dense + 1M context becomes default enterprise local-LLM recipe, Consumer-GPU coding agents, On-device inference for privacy/cost/latency, Headless Everything standardization). Remaining 7 multi-attach.
  - Suggested: leave as-is. The on-topic core is uniform; no clear sub-cluster for carve-out.

## Theme candidates

`theme_candidates` holds 39 pending rows (was 34 on 5/5). All 39 are `no_keyword_match` with no `nearest_theme_id` proposed, and every single row is a distinct `suggested_theme_label` with hit count = 1. The label-deduplication problem flagged on 5/5 has not been addressed during the week — the candidate-extraction pass writes one row per prediction summary verbatim, so the `≥ 3 distinct-day` promotion rule from `design/memory-policy.md` §2.1 can never fire as currently written.

Manual clustering by topic surface (same exercise as 5/5):

| scope | suggested label | rough hits in pending | proposed category | sample evidence |
|---|---|---|---|---|
| tech | AI Macro & Capital-Markets Reset | ~10 | tech.infrastructure (or new tech.macro) | Cerebras IPO mid-May ≥ $22-25B; Powell stays on Fed Board / Fed-investigation swing vote; FOMC dissent norm reverts; Microsoft audited monthly AI-business KPIs as 10-Q footnote; OpenAI audited monthly revenue + WAU cadence; Foundation labs audited monthly revenue + per-token margin; SEC drafts AI-revenue concept release; Big-3 hyperscalers AI-services 10-Q footnote; Hyperscaler per-token-margin-gated GPU capex floor; AI-accelerator vendors lock mid-quarter forward-supply 8-K cadence |
| business | Inference-Server Supply-Chain Risk | ~7 | business.regulation-compliance | Inference servers form supply chain triggering AI-Infra CVE class; Indirect prompt injection becomes top CVE category; GGUF supply chains gate uploads via signed cards + SSTI scans; CISA + NIST publish inference-server + agentic-tool CVE sub-catalog; CISA ships AI-Infra KEV sub-catalog with inference-server SBOM; Agent-skills attack surface lands MITRE-style threat sub-matrix; NIST publishes non-human-identity control profile |
| business | Physical AI Industrial Procurement | ~3 | business.enterprise-adoption | Physical AI 8-hour production runs become enterprise RFP cuts; Physical AI league tables rank top-five OEM-adopted humanoids; Tesla Optimus capex forces Mag-7 physical-AI 10-Q segment disclosure |
| business | Agent Skills Marketplace Governance | ~3 | business.regulation-compliance | Agent-skills threat sub-matrix lands as MITRE/NIST extension; Agent registry standard converges with MCP for agent artifacts; Per-tenant capability-attestation logs ship as MCP framework default |

The strongest signal-to-noise candidates for new themes (same as 5/5) are the macro / capital-markets cluster and the inference-server / supply-chain cluster. Both are repeated as recommended actions below. The other clusters either fit existing themes after a description tweak (Physical AI Industrial Procurement → `tech.physical_ai_robotics` already covers it after a small widening; Agent Skills Marketplace Governance → `tech.agent_registry_architecture` already covers it) or are below the conservative ≥ 3 distinct-day threshold for promoting a new theme on first appearance.

## Category-level notes

- `tech.security` carries 18 / 47 = 38.3 % of tech-scope predictions (was 30 / 39 = 76.9 % on 5/5). Back below the 50 % dominance threshold — the 5/5 spike has unwound. No action.
- `business.market-structure` carries 16 / 48 = 33.3 % of business-scope predictions (was 29 / 37 = 78.4 % on 5/5). Same shape — dominance unwound. No action.
- `business.regulation-compliance` carries 10 / 48 = 20.8 % (was 18 / 37 = 48.6 % on 5/5). Also unwound.
- (No category exceeded 50 %-attention this week.)

## Recommended actions

1. **Tighten description on `tech.ai_chip_architecture`** (`type: rename` / `apply_mode: manual`). Carry-forward from 5/5 and 4/27 — the recommendation has now been deferred for three Sundays running. Add **Cerebras IPO, WSE-3, AMD MI355X, AMD AI-accelerator revenue, training-vs-inference SKU split, accelerator-revenue 10-Q segment footnote, GB300 vs Trainium positioning, per-accelerator margin disclosure, hyperscaler custom silicon** terminology. Still the only underused theme in the schema and the 5/10 cycle continues to add Cerebras-IPO / Mag-7-training-vs-inference-SKU / AMD-10-Q-footnote signals that should be primary-attaching here. Test-mode proposal — do not auto-apply.
2. **Add new theme `tech.ai_macro_capital_markets`** (`type: new` / `apply_mode: manual`). Carry-forward from 5/5. Category: `tech.infrastructure` (closest existing bucket; a dedicated `tech.macro` category remains a separate design discussion per §2.3). Description draft: "Macro and capital-markets dynamics shaping AI: Mag 7 super-week earnings, AI-capex ROI repricing, AI-revenue disclosure rewrite (SEC concept release, OpenAI audited revenue cadence, AMD AI-accelerator 10-Q segment, Microsoft audited monthly AI-business KPIs), Powell-Fed Board institutional-volatility regime, FOMC dissent norm, Cerebras IPO, Apple-buyback collision with $700B AI-capex print, AI-accelerator vendor forward-supply 8-K cadence." Justification: the 5/5 manually-clustered ~ 10-hit cluster is now ~ 10 in this week's pending rows as well; no existing theme cleanly absorbs it. Test-mode proposal — do not auto-apply.
3. **Add new theme `business.inference_server_supply_chain`** (`type: new` / `apply_mode: manual`). Carry-forward from 5/5. Category: `business.regulation-compliance`. Description draft: "Inference-server supply-chain governance: AI-Infra CVE class as regulatory primitive, indirect prompt injection as top CVE category, GGUF supply-chain integrity gates (signed cards, SSTI scans), OAuth trust between AI SaaS, inference-server SSTI to OWASP LLM Top-10 v2026, agent-skills attack-surface threat sub-matrix, CISA AI-Infra KEV sub-catalog with inference-server SBOM, NIST non-human-identity control profile." Justification: 7 of the pending business-scope rows describe inference-server / supply-chain risk in market / compliance terms; the only existing security theme is tech-scope (`tech.agent_runtime_security`). Adds a business-scope counterpart so the multi-attach saturation on `business.ai_security_compliance_market` (27 children) thins. Test-mode proposal — do not auto-apply.
4. **Investigation (no schema edit): `SECONDARY_THEME_THRESHOLD` in `app/src/export.py`**. Fourth consecutive review flagging the same multi-attach pattern. Tech multi-attach 61.7 %, business multi-attach 81.2 %, both wider than 5/5. The overpopulation appearance on the top four themes (38 / 27 / 25 / 21) and the `theme_candidates` label-deduplication problem (39 single-hit rows, no clusters firing) both have the same root cause. Tightening the threshold — or requiring a non-generic token in the secondary-attach overlap — would clean both. Defer to a separate engineering session; out of scope for this Sunday's `apply-schema-edit` flow.
5. **Investigation (no schema edit): `theme_candidates` label normalisation pass**. New this week. The candidate-extraction pass writes one row per prediction summary verbatim — 39 rows, every label distinct, max hit count = 1. The `≥ 3 distinct-day` promotion rule from `design/memory-policy.md` §2.1 needs label normalisation (lowercase, stopword strip, token-set comparison, or LLM-driven clustering) before it can fire. Without this the candidate flow effectively produces zero promotion candidates regardless of how many real clusters land in the table. Defer to a separate engineering session; out of scope for this Sunday's `apply-schema-edit` flow.

## Deferred for next week

- Category-level carve-out for `tech.security` (e.g. splitting runtime-CVE vs agent-governance buckets). Below the 50 % dominance threshold this week (38.3 %), so the 5/5 carry-forward is parked — revisit only if a future week pushes it back above 50 %.
- Category-level carve-out for `business.market-structure` (single-theme concentration). Same shape; 33.3 % this week, parked.
- Reviewing whether `business.cloud_vs_local_distribution` (13 children, first time crossing the overpopulation threshold) and `tech.physical_ai_robotics` (9 children) merit subtheme carve-outs. Both fall in the overpopulated band but the on-topic core is uniform — re-examine if children pass 15 / 12 next week.
- A `tech.macro` category for the proposed `tech.ai_macro_capital_markets` theme — currently parked under `tech.infrastructure` per recommendation 2. Categories are more stable than themes (§2.3) and a new category needs its own design discussion.

---
