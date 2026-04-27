# Theme review — 2026-04-26

Source data: docs/data/graph-{tech,business,mix}.json (generated 2026-04-26 14:08 UTC) + theme_candidates (pending).
Total themes: tech=7, business=6, mix=13.
Total predictions: tech=23, business=17, mix=24.

## Empty / underused themes

### tech
- **`tech.local_inference_runtime`** — 1 child (`prediction.86ef7aadd10c9ea3` — *プロプライエタリ再膨張とオープンウェイトの地政学分断*). The single match is a forced fit; the prediction is about hosted-API gating, not local runtime stacks.
  - Real local-runtime signal exists this week (`prediction.eca68dc3b55aaba9` 1-bit native, `prediction.c78dc80a3ef32b02` 27B Dense + 1M context on RTX 4090, `prediction.27359f38a3635387` GGUF supply chain) but is being absorbed by `tech.one_bit_edge_llm` and `tech.model_supply_chain` — keyword overlap loses to those themes.
  - Suggested: **rewrite description** to add concrete keywords the matcher will hit — `Qwen3.6-27B`, `27B Dense`, `RTX 4090`, `1M context local`, `ローカル LLM`, `Bonsai`, `量子化` — alongside the existing tool names. Alternative: **merge** into `tech.one_bit_edge_llm` and rename the survivor to `Local / Edge LLM Runtime` if the boundary between "1-bit / Edge LLM" and "Local Inference Runtime" is intentionally blurred.

### business
- (none)

### mix
- (mix-specific finding: same `tech.local_inference_runtime` issue propagates — no separate notes needed)

## Overpopulated themes

A consistent pattern dominates this week: three **Physical AI / Robotics** predictions (`prediction.2a3fdae5b2a53dd0`, `prediction.f557408cd7493f7c`, `prediction.0dfad84ba446e403` — Robot-as-a-Service, 8-hour production runs, IROS/GTC league tables) are matching into **8 different themes** (`tech.agent_control_plane`, `tech.ai_chip_architecture`, `tech.agent_runtime_security`, `business.compute_capex_strategy`, `business.open_weight_vs_proprietary`, `business.cloud_vs_local_distribution`, `business.developer_platformization`, `business.ai_security_compliance_market`). They are inflating child counts everywhere without a natural home. This is the single largest source of overpopulation this week. See **Recommended actions** for the suggested resolution.

### tech

- **`tech.agent_control_plane`** — 12 children. Children list:
  - `prediction.fd5ec69ffd4e80e1` — CI / エージェントへの Secret 流出
  - `prediction.9b65b90cbb86218c` — Headless Everything アーキテクチャ
  - `prediction.2a3fdae5b2a53dd0` — Physical AI の SaaS 化 / RaaS *(forced fit)*
  - `prediction.930f44e1636b2cfb` — AI SaaS 間の OAuth 横断信任
  - `prediction.3eada9420515674b` — Agent Control Plane がハイパースケーラ競争の新主戦場
  - `prediction.f557408cd7493f7c` — Physical AI 8 時間本番稼働 *(forced fit)*
  - `prediction.0dfad84ba446e403` — Physical AI 本番ライン稼働実績 IROS/GTC *(forced fit)*
  - `prediction.50591988b3c5c84e` — MCP プロトコル攻撃面
  - `prediction.2317c1a05cf93f96` — フロンティアコーディングエージェント retract サイクル
  - `prediction.275700a6438b1089` — サプライチェーン経由 AI ツール侵害
  - `prediction.3d945cf6630dd017` — 1M context が既定 *(weak fit)*
  - `prediction.beaca8dbf3c448e3` — AI エージェントが SaaS を displace
  - Suggested: **rewrite description** to tighten on identity / registry / harness / OAuth / coding-agent permissions, and drop the broader "agent" / "Robot" terms that pull Physical AI in. Real cluster after pruning: agent identity (Secret leakage, OAuth, MCP attack, supply chain compromise) + agent platform competition (Control Plane, Headless, coding-agent retract cycle, SaaS displacement). No clean split — leave shape, fix description.

- **`tech.ai_chip_architecture`** — 7 children:
  - `prediction.2a3fdae5b2a53dd0` — Physical AI RaaS *(forced fit)*
  - `prediction.f557408cd7493f7c` — Physical AI 8 時間 *(forced fit)*
  - `prediction.0dfad84ba446e403` — Physical AI IROS/GTC *(forced fit)*
  - `prediction.99122278b821a7b6` — ハイパースケーラ × フロンティアラボ排他同盟
  - `prediction.000fad2f54c5cd01` — 訓練 / 推論 SKU 分離
  - `prediction.130b56d4ef6d6f70` — エージェントセキュリティ標準 *(forced fit)*
  - `prediction.4e3fa8ad03d6817d` — フロンティア × Tier-1 容量囲い込み
  - Suggested: **rewrite description** to anchor on chip-specific terms (TPU, Trainium, MAIA, MI300X, SKU, accelerator) and explicitly exclude robotics / agent-security signal. After pruning, real cluster is 3 children (SKU separation, Hyperscaler alliance, frontier × Tier-1 capacity) — borderline underused once Physical AI is removed. Worth revisiting next week.

- **`tech.one_bit_edge_llm`** — 6 children:
  - `prediction.eca68dc3b55aaba9` — 1-bit ネイティブ学習
  - `prediction.86ef7aadd10c9ea3` — プロプライエタリ再膨張 *(weak fit)*
  - `prediction.c78dc80a3ef32b02` — 27B Dense + 1M context
  - `prediction.3d945cf6630dd017` — 1M context が既定
  - `prediction.beaca8dbf3c448e3` — AI エージェントが SaaS を displace *(forced fit)*
  - `prediction.d939d1001add1919` — Day-0 推論 + RL + 即時値下げ
  - Suggested: **leave as-is** — children genuinely cluster around model architecture / context length / quantization. Two outliers (`prediction.86ef7aadd10c9ea3`, `prediction.beaca8dbf3c448e3`) are noise from broader keyword matches; tightening description is optional.

- **`tech.agent_runtime_security`** — 8 children:
  - `prediction.fd5ec69ffd4e80e1` — Secret 流出
  - `prediction.9b65b90cbb86218c` — Headless Everything *(weak fit)*
  - `prediction.2a3fdae5b2a53dd0` — Physical AI RaaS *(forced fit)*
  - `prediction.f557408cd7493f7c` — Physical AI 8 時間 *(forced fit)*
  - `prediction.0dfad84ba446e403` — Physical AI IROS/GTC *(forced fit)*
  - `prediction.50591988b3c5c84e` — MCP プロトコル攻撃面
  - `prediction.f41f0510dc8724db` — 間接プロンプトインジェクション CVE
  - `prediction.beaca8dbf3c448e3` — SaaS displace *(forced fit)*
  - Suggested: **rewrite description** to drop generic "agent" terms and anchor on prompt injection / RCE / sandbox escape / MCP attack surface / Secret leakage. After pruning, real cluster is 3-4 children — clean.

### business

- **`business.compute_capex_strategy`** — 6 children:
  - `prediction.000fad2f54c5cd01` — 訓練 / 推論 SKU 分離
  - `prediction.2a3fdae5b2a53dd0` — Physical AI RaaS *(forced fit)*
  - `prediction.930f44e1636b2cfb` — OAuth 横断信任 *(forced fit)*
  - `prediction.f557408cd7493f7c` — Physical AI 8 時間 *(forced fit)*
  - `prediction.0dfad84ba446e403` — Physical AI IROS/GTC *(forced fit)*
  - `prediction.4e3fa8ad03d6817d` — フロンティア × Tier-1 容量
  - Suggested: **rewrite description** to anchor on capex / chip investment / capacity / data center / accelerator commitment terms; drop generic "AI" / "deployment" wording that pulls Physical AI and OAuth in. Real cluster after pruning: 2 children (SKU separation, Tier-1 capacity).

- **`business.open_weight_vs_proprietary`** — 7 children:
  - `prediction.000fad2f54c5cd01` — SKU 分離 *(forced fit)*
  - `prediction.2a3fdae5b2a53dd0` — Physical AI RaaS *(forced fit)*
  - `prediction.930f44e1636b2cfb` — OAuth 横断信任 *(forced fit)*
  - `prediction.f557408cd7493f7c` — Physical AI 8 時間 *(forced fit)*
  - `prediction.beaca8dbf3c448e3` — SaaS displace *(weak fit)*
  - `prediction.0dfad84ba446e403` — Physical AI IROS/GTC *(forced fit)*
  - `prediction.130b56d4ef6d6f70` — エージェントセキュリティ標準 *(forced fit)*
  - Suggested: **rewrite description** with stronger keywords — `Qwen`, `Llama`, `Apache 2.0`, `open weight`, `proprietary`, `hosted-API only`, `gating`, `geopolitical`. Most current matches are forced fits. Real signal (e.g. `prediction.86ef7aadd10c9ea3` proprietary re-expansion, `prediction.eca68dc3b55aaba9` 1-bit native) is being absorbed by `tech.local_inference_runtime` / `tech.one_bit_edge_llm` instead.

- **`business.cloud_vs_local_distribution`** — 10 children:
  - `prediction.27359f38a3635387` — GGUF 供給経路
  - `prediction.3518e31b15b2bb53` — ローカル > クラウド逆転
  - `prediction.000fad2f54c5cd01` — SKU 分離 *(weak fit)*
  - `prediction.2a3fdae5b2a53dd0` — Physical AI RaaS *(forced fit)*
  - `prediction.930f44e1636b2cfb` — OAuth 横断信任 *(forced fit)*
  - `prediction.f557408cd7493f7c` — Physical AI 8 時間 *(forced fit)*
  - `prediction.beaca8dbf3c448e3` — SaaS displace
  - `prediction.0dfad84ba446e403` — Physical AI IROS/GTC *(forced fit)*
  - `prediction.2317c1a05cf93f96` — frontier coding retract サイクル *(weak fit)*
  - `prediction.4e3fa8ad03d6817d` — Tier-1 容量 *(weak fit)*
  - Suggested: **rewrite description** to focus on cloud-vs-local deployment economics (`Local>Cloud reversal`, `GGUF distribution`, `SMB on-prem`, `cost per token`, `privacy`); drop Physical AI and OAuth. Real cluster after pruning: 2-3 children — borderline underused without those.

- **`business.developer_platformization`** — 6 children:
  - `prediction.000fad2f54c5cd01` — SKU 分離 *(forced fit)*
  - `prediction.2a3fdae5b2a53dd0` — Physical AI RaaS *(forced fit)*
  - `prediction.930f44e1636b2cfb` — OAuth 横断信任
  - `prediction.f557408cd7493f7c` — Physical AI 8 時間 *(forced fit)*
  - `prediction.0dfad84ba446e403` — Physical AI IROS/GTC *(forced fit)*
  - `prediction.3eada9420515674b` — Agent Control Plane 競争
  - Suggested: **rewrite description** with concrete dev-tool terms (`Claude Code`, `Codex`, `Cursor`, `Kiro`, `CI/CD`, `tool registry`, `developer workflow`). Most current matches are forced fits. Real signal (`prediction.2317c1a05cf93f96` retract cycle) was absorbed by `tech.agent_control_plane`.

- **`business.ai_security_compliance_market`** — 10 children:
  - `prediction.f41f0510dc8724db` — 間接プロンプトインジェクション CVE
  - `prediction.fd5ec69ffd4e80e1` — Secret 流出
  - `prediction.27359f38a3635387` — GGUF 供給経路
  - `prediction.50591988b3c5c84e` — MCP プロトコル攻撃面
  - `prediction.275700a6438b1089` — サプライチェーン AI ツール侵害
  - `prediction.000fad2f54c5cd01` — SKU 分離 *(forced fit)*
  - `prediction.2a3fdae5b2a53dd0` — Physical AI RaaS *(forced fit)*
  - `prediction.930f44e1636b2cfb` — OAuth 横断信任
  - `prediction.f557408cd7493f7c` — Physical AI 8 時間 *(forced fit)*
  - `prediction.0dfad84ba446e403` — Physical AI IROS/GTC *(forced fit)*
  - Suggested: **rewrite description** to anchor on CVE / CVSS / OWASP / compliance / security tooling spend; drop Physical AI and SKU. Real cluster after pruning is 5-6 children — clean and the right shape.

## Theme candidates (≥ 3 pending hits)

`theme_candidates` has 8 pending rows; all are unique single-mention `no_keyword_match` entries (one row per candidate label, distinct labels). Query returned **0 rows ≥ 3 hits** — nothing to promote this week.

For reference, the 8 pending labels (one hit each):
- business: `1-bit ネイティブ学習が主流の量子化代替に`, `1M context が既定」のオープン重み時代に 2026 Q3 以降完全移行`, `27B Dense + 1M context」が 2026 後半のエンタープラ…`, `Agent Registry」方式への収斂`, `Day-0 推論 + RL 訓練 + 即時 API 値下げ」の三位一体ローンチ…`, `ハイパースケーラ × フロンティアラボの排他同盟」時代`, `プロプライエタリ再膨張とオープンウェイトの地政学分断`
- tech: `ローカル>クラウド」逆転の加速`

These look like prediction titles that didn't keyword-match any active theme — useful as evidence that the active themes' descriptions need broader / more specific keywords (see Empty/Underused and Overpopulated sections), not as theme proposals.

## Category-level notes

Three categories absorb ≥ 50% of their scope's predictions:
- **`tech.agents`** — 12 / 23 = 52% (single child theme `tech.agent_control_plane`).
- **`business.distribution`** — 10 / 17 = 59% (single child theme `business.cloud_vs_local_distribution`).
- **`business.regulation-compliance`** — 10 / 17 = 59% (single child theme `business.ai_security_compliance_market`).

In all three cases the dominance is driven by the same Physical-AI-pollution issue plus other forced fits in those themes. The category structure itself is fine; the dominance will likely fall once theme descriptions are tightened. **Do not** add sibling categories yet — re-check after one schema refresh.

## Recommended actions

1. **Add a Physical AI / Robotics theme** under `tech.infrastructure` (e.g. `tech.physical_ai_robotics` — "Humanoid robots, Robot-as-a-Service, production-line robotics, Siemens HMND, NVIDIA Isaac GR00T / Cosmos, Neura × AWS, DEEPX × Hyundai, IROS / GTC robotics benchmarks"). Three predictions are currently polluting 8 themes; a dedicated home will absorb them and deflate the overpopulation across the board. Strongly recommended — this is the highest-leverage change this week.
2. **Tighten descriptions** on the 5 themes most affected by Physical-AI pollution: `tech.agent_runtime_security`, `tech.ai_chip_architecture`, `business.compute_capex_strategy`, `business.developer_platformization`, `business.open_weight_vs_proprietary`. Drop generic "deployment" / "AI" / "agent" wording; anchor on each theme's distinctive keywords as listed in the per-theme suggestions above.
3. **Fix `tech.local_inference_runtime` description** to actually catch the local-LLM signal that exists this week (Qwen3.6-27B / RTX 4090 / 1-bit native / GGUF). Or merge into `tech.one_bit_edge_llm` if the boundary is intentionally blurred.
4. **Tighten `business.cloud_vs_local_distribution` and `business.ai_security_compliance_market`** descriptions to drop Physical-AI / OAuth / SKU keywords. Both have a clean real cluster underneath the noise.
5. **Leave `tech.agent_control_plane` and `tech.one_bit_edge_llm` shape alone**, only edit description on `tech.agent_