# Theme review — 2026-04-26

Source data: `docs/data/graph-{tech,business,mix}.json` (generated 2026-04-27 04:54 UTC) + `theme_candidates` (pending) from `app/data/analytics2.sqlite`.

Total themes: tech=7, business=6, mix=13 (= tech ∪ business).
Total predictions: tech=27, business=27, mix=27 (single shared pool, attached per scope).

> Note (DB path): the spec references `app/data/analytics.sqlite`, but the live database after the latest `update_pages.bat` is `app/data/analytics2.sqlite` (the legacy file is now zero-byte). All `theme_candidates` queries below ran against `analytics2.sqlite`. Worth fixing the path in `update_pages.bat` / spec or aliasing the file — but out of scope for this proposal.

## Empty / underused themes

### tech
- (none) — all 7 themes have ≥ 3 child predictions. Lowest is `tech.model_supply_chain` (3 children: Secret leakage / GGUF supply chain / third-party-vendor security) — clean, on-topic. Leave as-is.

### business
- (none) — all 6 themes have ≥ 5 children. No deprecation candidates this week.

### mix
- (none — rolls up tech + business; nothing additional.)

## Overpopulated themes

**Headline**: 10 of 13 themes (77%) clear the 6-child threshold this week, several heavily. Two distinct root causes drive this:

1. **Physical AI / Robotics pollution (carry-over from 2026-04-19 review).** Three predictions about humanoid robots / RaaS / IROS-GTC league tables (`prediction.e4f30420fe941737`, `prediction.2f5cbbb37e45ead7`, `prediction.d37ac1a85b3993d2`) have **no on-topic theme** and are forced into 3-4 themes each across both scopes. This single fact inflates 8+ themes' child counts. Last week's recommendation #1 (add `tech.physical_ai_robotics`) has not been acted on; renewing it as #1 again.
2. **Multi-attach matcher behaviour.** The spec describes the matcher as "best-1 IDF token overlap", but the live data has 4 predictions attached to **5 themes each in tech alone** (`prediction.13dcd36243d68603` capital markets reset, `prediction.fb0d91658912a8c3` and `prediction.253c0bfdc8132db0` capital coupling — note these two are an ingest duplicate, see end of report — and `prediction.90b4675202d33271` 1M context default). A 5-way attach inflates 5 themes' child counts off one prediction. Worth a separate look at `app/src/score.py` / `parsers/` — likely outside taxonomy edits, but flagging here because tightening descriptions alone won't undo the inflation if the matcher keeps multi-attaching.

### tech

- **`tech.agent_control_plane`** — 17 children (63% of the 27-prediction tech pool). Children list:
  - `prediction.342e299461a540b2` — OAuth trust between AI SaaS *(real fit)*
  - `prediction.20a028f81ea19c5f` — Agent Control Plane as hyperscaler battleground *(real fit)*
  - `prediction.e630d0fac3d53d2c` — MCP protocol attack surface *(real fit — but also belongs in agent_runtime_security)*
  - `prediction.4881c566cb8008ce`, `prediction.f9d235d81b1fe2a2` — consumer-GPU coding agent *(duplicate pair; real fit)*
  - `prediction.6100b04a88af9443` — Headless Everything architecture *(real fit)*
  - `prediction.83e19dc1fff01461` — Secret leakage through CI/agents *(real fit)*
  - `prediction.dee650f8ff1b78d9` — AI agent security standards / vendor boundary *(real fit)*
  - `prediction.e4f30420fe941737` — Physical AI as SaaS / RaaS *(forced fit)*
  - `prediction.d37ac1a85b3993d2` — Physical AI IROS/GTC league tables *(forced fit)*
  - `prediction.2f5cbbb37e45ead7` — Physical AI 8-hour production *(forced fit)*
  - `prediction.b6ed13351a6bad1b` — local-first cloud-overflow inversion *(weak fit — belongs in local_inference_runtime)*
  - `prediction.3b0b1a7d9c98262a` — 27B Dense + 1M context *(weak fit — local LLM topic)*
  - `prediction.90b4675202d33271` — 1M context as default *(weak fit — open-weight / one_bit topic)*
  - `prediction.13dcd36243d68603` — Capital markets reset SaaS valuation *(weak fit — finance/macro)*
  - `prediction.fb0d91658912a8c3`, `prediction.253c0bfdc8132db0` — Hyperscaler-AI-lab capital coupling *(duplicate pair; weak fit — finance/alliance topic)*
  - Suggested: **rewrite description** to anchor on agent identity / OAuth / MCP / coding-agent harness / Headless / Control Plane terminology and drop the broader "agent" / "robot" / "context" / "capital" tokens that pull everything in. Real cluster after pruning: ~9 children — still on the high side but clean. **Do not split** — the residual cluster is one concept.

- **`tech.agent_runtime_security`** — 12 children. Real cluster ≈ 6 (prompt injection CVE, secret leakage, MCP attack surface, inference-server CVE Q3 + Q2 dup, vendor-boundary standards). Forced fits: 3 Physical AI preds + 3 finance/capital preds. Suggested: **rewrite description** to anchor on CVE / CVSS / OWASP / sandbox / RCE / prompt-injection vocabulary; drop generic "agent" wording so the matcher stops absorbing Physical AI and capital-markets stories.

- **`tech.agent_registry_architecture`** — 9 children. Real cluster ≈ 4 (Agent Registry model, Headless Everything, MCP attack surface, vendor-boundary standards if read as "registry hygiene"). Forced fits: 3 Physical AI + 27B Dense + 1M context default + Capital markets. Suggested: **rewrite description** to anchor on registry / skill-permission / audit-log / MCP-metadata terms; drop generic "architecture" / "standards" tokens.

- **`tech.one_bit_edge_llm`** — 8 children. Real cluster ≈ 3 (1-bit native training, 1M context default, 27B Dense + 1M context). Forced fits: Physical AI RaaS, local-first inversion (belongs in `local_inference_runtime`), Capital markets reset, Capital coupling pair. Suggested: **rewrite description** to anchor on "1-bit" / "BitNet" / "Bonsai" / "quantization" / "Qwen3" / "DeepSeek V4" / "open-weight"; drop generic "edge" / "LLM" / "context" wording.

- **`tech.local_inference_runtime`** — 7 children. Real cluster ≈ 3 (local-first inversion, Proprietary re-expansion vs open-weight, 27B Dense + 1M context). Forced fits: Physical AI 8-hour, Capital markets reset, Capital coupling pair. Suggested: **rewrite description** to add concrete Qwen / DeepSeek / GGUF / RTX-4090 / Foundry-Local / Bonsai keywords (carry-over from last week's #3 — schema description still says only "llama.cpp, Ollama, MLX, WebGPU, OpenVINO" which the matcher isn't reaching the new releases through). Also drop generic "deployment" wording so finance/Physical AI stops absorbing in.

### business

- **`business.developer_platformization`** — 11 children. Real cluster ≈ 7 (Secret leakage, MCP attack surface, local-first inversion, Headless Everything, 27B Dense local enterprise, consumer-GPU coding agent dup pair, Agent Registry model, Agent Control Plane). Forced fits: Physical AI 8-hour, Capital markets reset. Suggested: **rewrite description** to anchor on developer-workflow / IDE / coding-agent / CI/CD / tool-registry vocabulary; drop generic "AI" / "enterprise" wording. Real cluster after pruning is genuinely about dev-platform consolidation — keep shape, fix description.

- **`business.hyperscaler_frontier_lab_alliance`** — 11 children. Real cluster ≈ 6 (Headless Everything, Agent Registry, exclusive HSC×lab alliance, SKU split, Agent Control Plane as battleground, frontier-lab × Tier-1 capacity capture, Capital coupling dup pair). Forced fits: 3 Physical AI preds. Suggested: **rewrite description** to anchor on "exclusive alliance" / "compute commitment" / "Tier-1 capacity" / "capital coupling" terms; drop "AI" / "deployment" tokens. After pruning it remains 8 children — leave as-is shape, just tighten.

- **`business.ai_security_compliance_market`** — 11 children. Real cluster ≈ 7 (prompt injection CVE, Secret leakage, OAuth trust, MCP attack surface, inference-server CVE Q3+Q2 dup, GGUF supply chain, vendor-boundary standards). Forced fits: Physical AI 8-hour, Capital markets reset, Agent Control Plane (which is a competitive-dynamics story, not a compliance one). Suggested: **rewrite description** to anchor on CVE / CVSS / OWASP / compliance / security-tooling-spend / risk-budget vocabulary; drop "agent" / "platform" tokens. Real cluster after pruning = 7 children, clean.

- **`business.open_weight_vs_proprietary`** — 7 children. Real cluster ≈ 5 (GGUF supply chain, consumer-GPU coding agent dup pair, Agent Registry model, Proprietary re-expansion / geopolitical split, 1M context as default). Forced fits: vendor-boundary standards (security/compliance topic). Suggested: **leave shape — minor description tightening** to anchor on "open-weight" / "proprietary" / "geopolitical" / "Hugging Face" / "DeepSeek" / "Qwen" terminology.

- **`business.cloud_vs_local_distribution`** — 6 children. Real cluster ≈ 4 (1-bit native training, local-first inversion, GGUF supply chain, Capital markets reset). Forced fits: Physical AI RaaS, Physical AI IROS/GTC. Suggested: **rewrite description** to anchor on "local" / "edge" / "on-device" / "cloud-overflow" / "distribution model" terms; drop "AI" / "deployment" / "Robot" tokens.

## Theme candidates (≥ 3 pending hits)

`theme_candidates` table (in `analytics2.sqlite`) is **empty** — 0 pending rows total. Either the candidate-generation step did not run on this rebuild, or `update_pages.bat` cleared `theme_candidates` and the next ingest hasn't repopulated it. Worth verifying separately from the schema review.

| scope | suggested label | hits | avg novelty | proposed category | sample evidence |
|---|---|---|---|---|---|
| _(none — 0 candidates ≥ 3 hits this week)_ | | | | | |

## Category-level notes

- **`tech.agents`** — holds 17 / 27 = **63%** of all unique tech predictions, via its sole child theme `tech.agent_control_plane`. Crosses the 50% spec threshold for "category absorbs ≥ 50% of scope's predictions." Caveat: the dominance is largely driven by the multi-attach matcher behaviour and Physical AI pollution flagged above, not by the scope being too coarse. A new sibling category is **not** recommended yet — re-check after the description tightening + (if applicable) the matcher fix.
- All other tech categories are between 18-48% of scope. Business categories all sit at 19-41% (closest is `enterprise-adoption`, `market-structure`, `regulation-compliance` tied at 41%). Below threshold; nothing to do.

## Adjacent issues (not taxonomy, but worth raising)

These showed up while auditing the graph and are not in the spec's scope, but they materially distort the numbers above. Surfacing here so the human can decide whether to track them as separate work items.

1. **Three duplicate prediction pairs** in the active set:
   - `prediction.4881c566cb8008ce` ≡ `prediction.f9d235d81b1fe2a2` — identical "consumer-GPU coding agent" labels.
   - `prediction.82cd3e6c1b184467` (Q3 2026) ≈ `prediction.c3c573011deb90ec` (Q2 2026) — same "Inference servers ... primitive supply chain" headline differing only in the timing target.
   - `prediction.fb0d91658912a8c3` ≡ `prediction.253c0bfdc8132db0` — identical "Hyperscaler-AI-lab capital coupling" labels.
   These six rows inflate every theme they touch, and the dups attach near-identically — fixing dedup at ingest would deflate ~5 themes' child counts by 1 each.

2. **Matcher behaviour vs spec.** Spec says "best-1 IDF token overlap"; observed behaviour is multi-attach (one prediction → up to 5 themes). If best-1 is the desired matcher, this is a code bug worth tracking separately. If multi-attach is the new desired behaviour, the overpopulation thresholds in this spec (≥ 6 → "candidate for split") need recalibration upward (≥ 10? ≥ 12?), otherwise nearly every theme triggers the heuristic forever.

3. **`update_pages.bat` writes `analytics2.sqlite`, spec reads `analytics.sqlite`.** The legacy file at `app/data/analytics.sqlite` is zero-byte; queries blindly following the spec would have returned "no candidates" for the wrong reason. This proposal queried `analytics2.sqlite` directly — but the spec / `.bat` should be reconciled.

## Recommended actions

1. **Add `tech.physical_ai_robotics` theme** under `tech.infrastructure` (e.g. *"Humanoid robots, Robot-as-a-Service, production-line robotics, Siemens HMND, NVIDIA Isaac GR00T / Cosmos, Neura × AWS, DEEPX × Hyundai, IROS / GTC robotics benchmarks"*). Three predictions are currently polluting 4-8 themes each; a dedicated home will absorb them and deflate overpopulation across the board. **Renewed from last week — highest-leverage change still pending.**
2. **Tighten descriptions** on the 5 most-polluted tech themes (`tech.agent_control_plane`, `tech.agent_runtime_security`, `tech.agent_registry_architecture`, `tech.one_bit_edge_llm`, `tech.local_inference_runtime`) and 4 business themes (`business.developer_platformization`, `business.hyperscaler_frontier_lab_alliance`, `business.ai_security_compliance_market`, `business.cloud_vs_local_distribution`). Specific keyword guidance is per-theme above. Drop generic "AI" / "agent" / "deployment" / "context" tokens; anchor on each theme's distinguishing concrete terms.
3. **Investigate matcher behaviour separately.** Best-1 vs multi-attach is the underlying cause of most overpopulation; description tightening alone is a partial fix. Out of scope for `schema.sql` edits — track as a separate code task.
4. **Investigate `theme_candidates` pipeline.** Empty table after a successful rebuild is suspicious. Check that the candidate-generation step ran during `update_pages.bat`; if not, last week's "8 pending candidates" should still be present. Out of scope for this proposal but blocking §2.3 of the weekly review.
5. **No splits this week.** Despite the high overpopulation count, none of the themes show 2-3 cleanly separable sub-clusters — the inflation is mostly forced fits + duplicates + multi-attach, not genuinely-split topics. Revisit after #1 and #2 land.
