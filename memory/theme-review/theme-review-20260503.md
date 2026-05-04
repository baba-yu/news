# Theme review — 2026-05-03

Source data: docs/data/graph-{tech,business,mix}.json (post-Phase-4b live rebuild) + theme_candidates (pending). Run mode: routine Sunday weekly per `5_weekly_theme_review.md`. Cluster shape since 2026-04-27's review with 22 new predictions and the new locale-fan-out + post-update-validation infrastructure landed in between.
Total themes: tech=8, business=6, mix=14. Total predictions: tech 49 + business 49 = 49 unique (mix is the union).

## Empty / underused themes

### tech
- **`Agent Registry Architecture`** (`tech.agent_registry_architecture`) — 1 child despite the May 1 Microsoft Agent 365 Registry Sync GA preview being the largest single agent-identity primitive of the cycle and today's Pred #1 (cross-cloud agent-identity + MCP registry RFC draft by Q3 2026) being directly on-theme.
  - Suggested: rewrite description to widen the keyword surface. Add **Agent Registry, MCP server inventory, agent identity sync, cross-cloud agent ID, Entra ID for agents, Defender per-agent relationship-map, registry-sync, Agent Discovery, Agent Gateway, Glasswing partner registry, agent attestation, Project Glasswing 50-org partner list**. Goal: pull in next week's Agent 365 + Glasswing + Mythos-related predictions that currently scatter across `agent_runtime_security` + `agent_control_plane`.
- **`Model Supply Chain`** (`tech.model_supply_chain`) — still 2 children one week after the 4/27 review's "tighten description" recommendation. The recommendation was not applied (the schema edit step deferred). Today's news adds **Anthropic Project Glasswing model-distribution program (Apr 7) + AWS Bedrock Mythos Gated Research Preview SKU + Anthropic Mythos $100M usage credits + ~50-launch-partner roster** as concrete model-distribution governance signal. Re-applying the same recommendation: **add gated-distribution / partner-list / usage-credit / Glasswing / Mythos / SLSA-for-models / sigstore / model marketplace governance / safetensors integrity / Bonsai / Qwen / DeepSeek / Llama** terminology.

### business
- **`Open Weight vs Proprietary AI`** (`business.open_weight_vs_proprietary`) — 1 child. The Chinese open-weight wave (DeepSeek V4 / Qwen 3.6 / Kimi K2.6 / GLM-5.1 MIT) + Google Gemini 3.1 Flash-Lite at $0.25/M input is the structural backdrop. Description appears to miss **MIT license, Apache-2.0 license, BenchLM Chinese leaderboard, Hugging Face open-weight downloads, gpt-oss, open-weight pricing floor** — extending this would pull in next week's open-weight cohort predictions that currently land in `cloud_vs_local_distribution`.
  - Suggested: rewrite description with the open-weight licensing + leaderboard vocabulary above.
- **`Developer Toolchain Platformization`** (`business.developer_platformization`) — 2 children. Microsoft Build June 2-3 anchor + GitHub Copilot CLI + Codex CLI 0.128.0 + AWS AgentCore CLI + Microsoft Foundry Toolkit GA represent the dev-toolchain platformization arc explicitly, but predictions about this consistently land in `agent_control_plane`. Description should add **dev tooling consolidation, IDE integration, CLI standardization, GitHub-as-platform, Microsoft Build, Foundry Toolkit, AgentCore CLI, dev-experience SLA**.

### mix
- (rolls up tech + business; no mix-specific empties.)

## Overpopulated themes

The 4/27 review's diagnosis still holds: a small set of "broad-context" predictions multi-attaches across many themes via the IDF secondary-attach path in `export.py`. Today the most-attached predictions are: *Hyperscaler-AI-lab capital coupling*, *Mag 7 prints + FOMC force per-token-margin gating*, *Public-opinion blowback against AI*, *Mag 7 super-week + capex + AAPL buyback*, *AGI-clause unwind*. None of these are theme-specific and they saturate every theme they share even one rare token with.

### tech
- **`Agent Runtime Security`** (16 children, +4 from 4/27's 12) — on-topic for ~10 children (Indirect prompt injection, Secret leakage CI, Inference servers as primitive, Attack surface against MCP, AI-Infra CVE class, Agent-skills attack surface, Inference-server SSTI, Agentic-AI CVE class CNA-issued, LLM-tooling + Linux-kernel CVE chain, Frontier cyber-AI export-control). The remaining 6 are multi-attach.
  - Suggested: leave as-is. Tighten `SECONDARY_THEME_THRESHOLD` rather than split the theme. The on-topic cluster is coherent — it's the AI-security-substrate thesis arc.
- **`Agent Control Plane`** (11 children, +3 from 4/27's 8) — on-topic for ~6 (Agent Control Plane, Big-3 hyperscalers MCP-server policy enforcement, Cross-cloud agent-identity RFC, MCP-Gateway/Firewall product wave, Microsoft Agent 365 Registry Sync, OpenAI-on-Bedrock SLA standardization). Remaining 5 are multi-attach.
  - Suggested: leave as-is. The cluster is on-topic.
- **`Physical AI / Robotics`** (7 children) — new overpopulation since 4/27. On-topic: Tesla Optimus Q2 production prep, Apptronik + Jabil + Figure 03, IROS/GTC league tables, Physical AI 8h production runs, Robot-as-a-Service, Mag-7 physical-AI capex 10-Q footnote. All children plausibly on-theme.
  - Suggested: leave as-is. This is a real cluster, not multi-attach noise.

### business
- **`Hyperscaler × Frontier Lab Alliance`** (21 children, +6 from 4/27's 15) — most populated theme in the corpus. On-topic for ~8 children (exclusive alliance, frontier-lab capacity, capital coupling, Mag 7, training-vs-inference SKU split, AGI-clause unwind, OpenAI-on-Bedrock SLA, Pentagon 8-vendor + Mythos paradox). Remaining 13 are multi-attach.
  - Suggested: leave as-is.
- **`AI Security Compliance Market`** (13 children) — same multi-attach shape. On-topic for ~6 (AI agent security standards, AI-Infra CVE regulatory primitive, Agentic-AI CVE class CNA-issued, Statutory Identity for Autonomous Agents, frontier cyber-AI export-control, Public-opinion blowback). Remaining 7 are multi-attach.
  - Suggested: leave as-is.

## Theme candidates (≥ 3 pending hits)

| scope | suggested label | hits | avg novelty | proposed category | sample evidence |
|---|---|---|---|---|---|
| (none) | — | — | — | — | — |

The `theme_candidates` table holds zero pending rows. Same shape as 4/27. The matcher hasn't surfaced stable "no-keyword-match" themes — likely because the broad-context predictions absorb anything that lacks a distinctive keyword. Tightening the secondary-attach threshold would also help here by leaving more "orphan" predictions for the candidate-extraction pass to notice.

## Category-level notes

- `business.market-structure` carries 21/49 predictions = 43% of the business scope. Below the 50% threshold but worth watching — if next week's daily flow keeps adding predictions about hyperscaler / frontier-lab dynamics into this category, it will tip into dominance.
- `tech.security` carries 18/49 predictions = 37% of the tech scope. Same shape as last week (was 16/45 = 36%). Stable, not a pain point yet.
- (No category exceeds 50%-attention or sat dormant for ≥ 2 consecutive reviews.)

## Recommended actions

1. **Tighten description on `tech.agent_registry_architecture`**. Add Agent Registry / MCP server inventory / agent identity sync / cross-cloud agent ID / Entra ID for agents / registry-sync / Glasswing partner registry / Mythos partner list keywords. The May 1 Agent 365 Registry Sync makes this the highest-signal-to-noise underused theme.
2. **Tighten description on `tech.model_supply_chain`** (carry-forward from 4/27). Add Glasswing / Mythos / gated distribution / partner-list / usage-credit / SLSA-for-models / sigstore / Bonsai / Qwen / DeepSeek model-distribution governance terminology.
3. **Tighten description on `business.open_weight_vs_proprietary`**. Add MIT license / Apache-2.0 / BenchLM Chinese leaderboard / Hugging Face downloads / gpt-oss / open-weight pricing floor / Gemini 3.1 Flash-Lite $0.25/M tier vocabulary.
4. **Tighten description on `business.developer_platformization`**. Add dev-toolchain consolidation / Microsoft Build / Foundry Toolkit / AgentCore CLI / GitHub-as-platform / Codex CLI dev-experience SLA terminology.
5. **Investigation (no schema edit): `SECONDARY_THEME_THRESHOLD` in `app/src/export.py`** — the same multi-attach pattern flagged 4/27 (themes saturating from broad-context predictions sharing one rare token) is now wider at 21/16/13/11. Tightening the threshold (or requiring a non-generic token in the secondary-attach overlap) would clean the overpopulation appearance without any schema edit. Defer to a separate engineering session — out of scope for this Sunday's `apply-schema-edit` run.
