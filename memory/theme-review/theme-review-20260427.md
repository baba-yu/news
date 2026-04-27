# Theme review — 2026-04-27

Source data: docs/data/graph-{tech,business,mix}.json (post-origin-age-gate rebuild) + theme_candidates (pending). Run mode: ad-hoc Mon, triggered by today's matcher fix + `predictions.created_at → ingested_at` rename + new export-layer origin-age gate. The first scope-level cluster shape since 2026-04-26's Sunday review.
Total themes: tech=8, business=6, mix=14.

## Empty / underused themes

### tech
- **`Model Supply Chain`** (`tech.model_supply_chain`) — 1 child (`prediction.ef67c8de79361722`, "GGUF supply chains are the new battleground").
  - Suggested: rewrite description with a wider keyword surface — the current text only names *Malicious model files / GGUF / tokenizer templates / Hugging Face / Ollama / ModelScope*. Today's news already covers **model signing**, **provenance attestation**, **SLSA-for-models**, **sigstore**, **Bonsai / Qwen / DeepSeek / Llama distribution channels**, **safetensors integrity** — none of these are tokens in the matcher's bag, so anything mentioning model-distribution risk lands elsewhere.

### business
- **`Compute Capex Strategy`** (`business.compute_capex_strategy`) — 1 child (`prediction.fb0d91658912a8c3`, "Hyperscaler-AI-lab capital coupling grows").
  - Suggested: rewrite description. The current generic *AI chip investments, data center capex, accelerator differentiation, and cloud capacity constraints* fails to attract any of this week's recurrent capex-themed predictions (Mag 7 Q1 earnings, Alphabet $175-185B 2026 capex, Trainium / GB300 / Vera Rubin commitments). Add concrete brand / product names so the IDF matcher catches them.

### mix
- (rolls up tech + business; no mix-specific empties.)

## Overpopulated themes

The current overpopulation pattern is **not** a single-theme split case. Eight themes exceed the 6-children threshold, and inspecting the membership lists reveals a single underlying cause: a small set of "broad-context" predictions (e.g. *Capital markets reset valuation of AI-agent-displaced SaaS*, *Mag 7 Q1 earnings reset*, *Public-opinion blowback against AI*, *Capital coupling between hyperscaler and AI lab*) is multi-attaching across 7-8 themes each via the IDF secondary-attach path in `export.py:extra_theme_parents`. The themes themselves are not the problem; the secondary-attach threshold (`SECONDARY_THEME_THRESHOLD`) is too loose for the current corpus and a handful of generic-vocabulary predictions saturate every theme they share even one rare token with.

### tech
- **`Agent Runtime Security`** (12 children) — boundaries are clean for the on-topic children (Indirect prompt injection, Secret leakage CI, Inference servers as primitive, Attack surface against MCP, AI agent security standards, AI-Infra CVE class). The remaining 6 children (Capital markets, Public-opinion blowback, Hyperscaler-AI-lab coupling, exclusive alliance, frontier-lab Tier-1 capacity, Convergence on Agent Registry) are arriving through secondary attach and don't actually concern runtime security.
  - Suggested: leave the theme schema as-is. The visible "overpopulation" is multi-attach noise; tightening the matcher's secondary threshold (or making secondary attach require a non-generic token in common) would clean it up without any schema edit.
- **`1-bit Edge LLM`** (10 children) — same shape: on-topic children are 1-bit native training, 27B Dense, 1M context default, GGUF supply chains, consumer-GPU coding agent. Off-topic children (Capital markets, Mag 7, Hyperscaler coupling, frontier-lab capacity, Proprietary re-expansion) again secondary-attach.
  - Suggested: leave as-is, same reason.
- **`Local Inference Runtime`** (9 children), **`Agent Control Plane`** (8 children) — same multi-attach pattern. Suggested: leave as-is.

### business
- **`Hyperscaler × Frontier Lab Alliance`** (15 children) — most populated theme in the corpus. On-topic for ~6 children (exclusive alliance, frontier-lab capacity, capital coupling, Mag 7, training-vs-inference SKU, Apr 21 alliance arc); the remaining 9 are multi-attach.
  - Suggested: leave as-is — see matcher-investigation note below.
- **`AI Security Compliance Market`** (14), **`Cloud vs Local AI Distribution`** (9), **`Developer Toolchain Platformization`** (8) — same multi-attach shape.

## Theme candidates (≥ 3 pending hits)

| scope | suggested label | hits | avg novelty | proposed category | sample evidence |
|---|---|---|---|---|---|
| (none) | — | — | — | — | — |

The `theme_candidates` table holds zero pending rows with ≥ 3 hits. This is consistent with the current corpus age (predictions only began on 2026-04-19); the matcher has not had enough time to surface stable "no-keyword-match" themes.

## Category-level notes

(none — no category exceeds 50%-attention or sat dormant for ≥ 2 consecutive reviews.)

## Recommended actions

1. **Tighten description on `tech.model_supply_chain`.** Replace the current narrow text with a wider keyword surface: anchor on **model signing / provenance attestation / SLSA / sigstore / safetensors integrity / Bonsai / Qwen / Llama / DeepSeek distribution / model marketplace governance** terminology. Drop the generic tokens that aren't doing matcher work. Goal: pull at least 2-3 model-distribution-risk predictions in next week's run that currently land elsewhere.

2. **Tighten description on `business.compute_capex_strategy`.** Anchor on concrete brand / product names: **Mag 7 capex / Alphabet 2026 capex / Microsoft Azure capex / Trainium / GB300 / Vera Rubin / MAIA / 5GW commitments / 10-year compute deals / data center power footprint**. Drop the generic four-word taxonomy that's failing to attract anything.

3. **Carry-over: investigate matcher secondary-attach behaviour.** The 8 themes flagged "overpopulated" are dominated by 5-6 broad-context predictions multi-attaching via `export.py:extra_theme_parents` IDF threshold. Out of scope for this week's schema edit; surface for next week's review. Candidate fixes: raise `SECONDARY_THEME_THRESHOLD`, or require the shared tokens to include at least one with `df < N` so generic vocabulary alone (`agent`, `ai`, `cloud`, `capital`) cannot sustain a secondary attachment.

4. **Carry-over: theme_candidates pipeline empty.** Zero pending rows with ≥ 3 hits is expected at this corpus age; revisit at the 2026-05-03 weekly run after another full cycle of news ingest.
