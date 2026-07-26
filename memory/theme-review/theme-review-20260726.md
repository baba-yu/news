# Theme review — week ending 2026-07-26

Mode: routine Sunday rotation (5_weekly_theme_review). Diagnostic + advisory pass over the current schema. Inputs: `app/data/analytics.sqlite` (read-only — `themes`, `prediction_scope_assignments`, `theme_candidates`, `glossary_audit`), `app/src/schema.sql`, `docs/data/graph-{tech,business,mix}.json` (aggregated programmatically, not read into context), `memory/theme-review/theme-review-20260719.md`.

## Diagnostic summary

Total themes: **18** (tech 10, business 8) — unchanged, and that is itself the week's headline. Total predictions: tech 255, business 289, mix 303 (+18 / +22 / +21 week over week). Pending `theme_candidates`: **64** rows (up from 60), all `status='pending'`, all `candidate_reason='no_keyword_match'`, all with `nearest_theme_id` NULL. Zero candidates have ever been promoted or rejected in the table's history.

**Neither of last week's two schema actions reached the database, and one of them did not reach `schema.sql` either.** This was verified directly rather than inferred.

**Action 1 (`add tech.ai_infra_private_capital`) did not land at all.** The `themes` table still holds exactly 18 rows and `schema.sql` contains no seed row for that `theme_id`. The string `tech.ai_infra_private_capital` does appear four times in `schema.sql` — at lines 1207, 1482, 1592, 1596 — but every one of those is inside the *cross-reference text of the `tech.ai_chip_architecture` description written by Action 2*. The theme was never inserted. Root cause confirmed empirically: `_insert_before_themes_seed_terminator` in `app/skills/apply_schema_edit.py:310-323` uses

    (INSERT\s+OR\s+IGNORE\s+INTO\s+themes\s*\([^)]*\)\s*VALUES\s*(?:\([^;]*\)\s*,?\s*)*)(\([^;]*\))(\s*;\s*\n)

and its `[^;]*` row groups cannot cross a semicolon. Running that exact regex against the current `app/src/schema.sql` returns **no match**, so the operation raised `could not locate themes seed block to append into` and was skipped.

**Action 2 (`rewrite-description` on `tech.ai_chip_architecture`) landed in `schema.sql` but not in the matcher**, exactly as last week predicted it would. The seed row at line 1207 now carries the new 996-character description while the `themes.description` column in `app/data/analytics.sqlite` still holds the old 296-character text. The Spanish and Filipino columns, by contrast, carry the new text at 1128 and 1073 characters. **The EN-drift set has therefore grown from two themes to three.** A full sweep of all 18 themes comparing the `schema.sql` seed description against the DB column:

| Theme | schema.sql EN | DB EN | Verdict |
|---|---|---|---|
| `business.ai_revenue_disclosure` | 1251 | 590 | drift (since 7/12) |
| `business.cloud_vs_local_distribution` | 936 | 217 | drift (since 7/12) |
| `tech.ai_chip_architecture` | 996 | 296 | **drift (new, since 7/19)** |
| other 15 themes | — | — | OK |

The emitter census confirms the mechanism is unchanged: `schema.sql` contains **1** `INSERT OR IGNORE INTO themes(`, **24** `UPDATE themes SET` blocks carrying 23 `description_ja`, 25 `description_es` and 25 `description_fil` assignments, and **0** occurrences of `UPDATE themes SET description =`. `apply_schema_edit.py` contains zero occurrences of `SET description =`. English is the column the IDF matcher reads and it is the one column no statement can ever update on a populated database.

**The two defects have now compounded into a user-visible artifact.** Because Action 2's locale halves *did* reach the DB while Action 1 never created the theme they reference, the live `description_ja`, `description_es` and `description_fil` for `tech.ai_chip_architecture` all tell readers that private-market silicon financing "is covered by `tech.ai_infra_private_capital`" — a theme that does not exist in the taxonomy. Three of the four dashboard locales are currently rendering a dangling cross-reference.

**What this means for every number below**: the matcher that produced this week's table ran against the same English descriptions as the last three weeks. Movements in the three drifting themes are re-measurements, not trends.

### Tech scope — theme attachments + category density

255 distinct predictions. `primary` is the count of `prediction_scope_assignments` rows in tech scope, `children` is the `child_ids` length on the mix-scope graph node.

| Theme | Category | children | primary | vs 7/19 |
|---|---|---|---|---|
| Model Supply Chain (`tech.model_supply_chain`) | tech.security | 183 | 83 | +8 |
| AI Macro & Capital Markets (`tech.ai_macro_capital_markets`) | tech.infrastructure | 104 | 42 | +3 |
| Agent Runtime Security (`tech.agent_runtime_security`) | tech.security | 90 | 26 | +1 |
| Agent Control Plane (`tech.agent_control_plane`) | tech.agents | 46 | 23 | +1 |
| Local Inference Runtime (`tech.local_inference_runtime`) | tech.inference-runtime | 33 | 21 | +1 |
| Frontier Model Regulatory Board (`tech.frontier_model_regulatory_board`) | tech.standards | 37 | 17 | +1 |
| Physical AI / Robotics (`tech.physical_ai_robotics`) | tech.infrastructure | 20 | 16 | +2 |
| Agent Registry Architecture (`tech.agent_registry_architecture`) | tech.standards | 41 | 10 | 0 |
| 1-bit / Edge LLM (`tech.one_bit_edge_llm`) | tech.models | 39 | 10 | +1 |
| AI Chip Architecture (`tech.ai_chip_architecture`) | tech.infrastructure | 25 | 7 | **0** |

Tech category density: tech.security 109/255 = 42.7%, tech.infrastructure 65/255 = 25.5%, tech.standards 27/255 = 10.6%, tech.agents 23/255 = 9.0%, tech.inference-runtime 21/255 = 8.2%, tech.models 10/255 = 3.9%. No category over 50%. `tech.ai_chip_architecture` is the only tech theme that took **zero** new primaries this week and is now flat at 7 for a fourth consecutive week — the predicted consequence of its rewrite never reaching the matcher.

### Business scope — theme attachments + category density

289 distinct predictions.

| Theme | Category | children | primary | vs 7/19 |
|---|---|---|---|---|
| AI-Revenue Disclosure Rewrite (`business.ai_revenue_disclosure`) | business.capital-supply-chain | 253 | 142 | +9 |
| Compute Capex Strategy (`business.compute_capex_strategy`) | business.capital-supply-chain | 160 | 64 | +11 |
| Inference Server Supply Chain (`business.inference_server_supply_chain`) | business.regulation-compliance | 143 | 33 | 0 |
| Open Weight vs Proprietary AI (`business.open_weight_vs_proprietary`) | business.competition | 75 | 24 | +1 |
| Developer Toolchain Platformization (`business.developer_platformization`) | business.enterprise-adoption | 69 | 17 | +1 |
| Hyperscaler x Frontier Lab Alliance (`business.hyperscaler_frontier_lab_alliance`) | business.market-structure | 80 | 5 | 0 |
| AI Security Compliance Market (`business.ai_security_compliance_market`) | business.regulation-compliance | 41 | 3 | 0 |
| Cloud vs Local AI Distribution (`business.cloud_vs_local_distribution`) | business.distribution | 47 | 1 | 0 |

Business category density: **business.capital-supply-chain 206/289 = 71.3%**, business.regulation-compliance 36/289 = 12.5%, business.competition 24/289 = 8.3%, business.enterprise-adoption 17/289 = 5.9%, business.market-structure 5/289 = 1.7%, business.distribution 1/289 = 0.3%.

The shape is stark and clean this week: **all 20 new business primaries went to the two `business.capital-supply-chain` themes**, and every one of the six themes outside that category took 0 or +1. Dominance rose 69.7% → 71.3%, its largest single-week move since May. Per last week's Action 4 this is held without a business-scope content edit, and that hold is reaffirmed — the corrective disclosure description still has not entered the matcher, so widening any starved theme now would still confound the only clean before-and-after available.

### Mix scope

303 predictions, 18 themes, 12 categories. Primary re-tournamented across the combined pool: `tech.model_supply_chain` 82 (27.1%), `tech.ai_macro_capital_markets` 42 (13.9%), `tech.agent_runtime_security` 26, `tech.agent_control_plane` 23, `business.compute_capex_strategy` 21, `tech.local_inference_runtime` 21, `business.ai_revenue_disclosure` **19**, down the tail to `business.cloud_vs_local_distribution` 1 and `business.inference_server_supply_chain` 1. Mix category density: tech.security 108/303 = 35.6%, tech.infrastructure 65/303 = 21.5%, business.capital-supply-chain 40/303 = 13.2%, everything else below 9%. **No category is over 50% in mix scope.**

The long-standing mix pattern holds and sharpened: business themes shed almost their entire primary core once tech themes are allowed to compete (`business.ai_revenue_disclosure` 142 → 19, `business.inference_server_supply_chain` 33 → 1). That remains the strongest evidence that a large share of the business pool is tech-flavoured content parked there only because no tech theme contests it in business-only mode.

### Glossary audit stagnation (§6.1 hook)

`glossary_terms`: 112 active, 874 candidate, 201 retired. `glossary_audit` across 61 distinct check dates: `dedupe/pass` 6983 rows / 263 terms, `form/pass` 3804 / 66, **`form/warn` 3027 rows across only 47 distinct terms**, `form/fail` 154 rows / 154 terms, `semantic/pass` 6, `dedupe/fail` 1, `dedupe/warn` 1. The `form/fail` empty-`quick_def` count rose 140 → 154. Because `warn` does not flip status, the same 47 over-length terms are re-logged every run and never self-clear. Unchanged diagnosis from last week: the writer prompt systematically overshoots the 25-word cap. Carried in Action 5.

## Empty / underused themes

By the literal §2.1 rule (`child_ids` in {0, 1}) **no theme qualifies** — the smallest child count in the project is 20 (`tech.physical_ai_robotics`). The rule has been non-firing for months. See Action 5.

Reading underuse by primary core instead, the discriminating signal at this pool size is high linkage with near-zero primary assignment:

- **`business.cloud_vs_local_distribution` — 47 children, 1 primary. Seventh consecutive week at 1.** Its widened description has been correct in `schema.sql` since 7/12 and has never reached the matcher. Not a merge candidate on this evidence.
- **`business.ai_security_compliance_market` — 41 children, 3 primary.** Flat. Competes with `business.inference_server_supply_chain` inside `business.regulation-compliance`. Log-only watch, unchanged.
- **`business.hyperscaler_frontier_lab_alliance` — 80 children, 5 primary.** Worst children-to-primary ratio in the project and now worse than last week at 16.0:1 (was 14.4:1) because children grew 72 → 80 while primary stayed at 5. First in the queue for keyword sharpening once the business-scope measurement is clean.
- **`tech.ai_chip_architecture` — 25 children, 7 primary.** Fourth week flat, and the only tech theme with zero growth. Not confounded by matcher competition: its corrective rewrite exists in `schema.sql` and is simply unreachable.

Two more worth naming at this scale because they are high-linkage and low-primary in a way the §2.1 text does not capture: `business.developer_platformization` (69 children, 17 primary) and `business.open_weight_vs_proprietary` (75 children, 24 primary). Both look like description or matcher problems rather than dead themes.

## Overpopulated themes

By the literal §2.1 rule (`child_ids` >= 6) **all 18 themes qualify**, since the smallest is 20. The rule carries zero information at current pool size. See Action 5.

Reading the §2.1 intent instead — high population *plus* separable sub-topics:

- **`business.ai_revenue_disclosure` — 253 children, 142 primary.** Still the largest theme in any scope. Assessment unchanged: roughly a third is genuine disclosure content and the rest defaults to it because its live description is the broadest in the business scope. **No content change proposed.** The corrective sharpening is already correct in `schema.sql`. Action 3 touches only its punctuation, for tooling reasons, and preserves its words exactly.
- `tech.model_supply_chain` (183 children, 83 primary) — largest tech theme, strongest growth again. Primary core stays coherent around signing, provenance and loader verification and does not separate into a clean second cluster. Leave as-is.
- `business.compute_capex_strategy` (160 children, 64 primary) — fastest-growing theme this week at +11. Coherent around multi-year commitments and GW-scale buildouts. Leave as-is.
- `business.inference_server_supply_chain` (143 children, 33 primary) — primary core coherent, high child count is `export.py` secondary-attach inflation. Leave as-is.
- `tech.ai_macro_capital_markets` (104 children, 42 primary) — coherent around public-market macro. It is now also the only sensible home for the private-capital cluster that Action 1 of last week failed to carve out. See Action 5.

Multi-attach pressure via the `export.py` secondary-attach path persists for a fifteenth consecutive week — mix scope carries 1570 links across 333 nodes versus 643 links across 270 nodes in tech scope. This is an `export.py` threshold property, not a schema fault. Carried in Action 5.

## Theme candidates

64 pending rows, up from 60. **All 64 are `status='pending'`. None has ever been promoted or rejected — the `promoted_theme_id` column is NULL for every row in the table's entire history.** Combined with the fact that the one `add` attempted in that history silently failed, the honest reading is that the promotion path has never successfully executed end to end.

`created_at` distribution is unchanged in shape: 37 of 64 rows are a single 2026-06-09 bulk backfill, and 27 arrived as a 1-3 per day trickle since. Clusters should be judged on the post-6/09 organic rows. All 15 business-scope candidates remain 6/09 backfill rows, and all of them are tech-flavoured content — no genuinely business-flavoured candidate has been recorded in 47 days.

Clustering:

- **AI-infrastructure private capital — now 12 organic rows and still completely unhomed.** Last week counted 8 between 6/17 and 7/18. Four more arrived: AMD converting MI450 co-design into a firm rack-scale commitment (7/20), self-financed multi-decade power deals reaching a second frontier lab (7/24), Etched converting SK hynix equity into a disclosed HBM agreement (7/26), plus OpenAI locking equity-coupled HBM allocation with a memory maker (6/24). Together with the sovereign-AI unicorn crossing (6/29), OpenAI's public-listing step with a US-government stake (7/04), standalone infrastructure funding for non-GPU datacenter silicon (7/05), the inference-ASIC challenger anchoring a raise on a $1B-plus order book (7/06), SK Hynix converting ADR proceeds into booked EUV orders (7/12), the European defense-AI institutional mega-round (7/14), the Together or Baseten $5B-plus raise (7/18) and the Corsair-class hyperscaler deployment (6/17), this is the strongest and fastest-accumulating cluster in the table. It clears the §2.1 bar several times over. **It cannot be promoted this week because the `add` operation is broken.** Treated in Action 5 as log-only with the tooling dependency named.
- **Autonomous offensive-security agents — a genuine second cluster, sub-threshold on organic rows but worth naming.** Three organic rows: an autonomous-pentest vendor landing a named enterprise or government deal (6/22), autonomous pentest agents shipping as a named managed tier (6/25), and autonomous-AI-agent intrusions becoming a named detection category (7/09), with policy-flavoured backfill rows behind them (AI-assisted vuln triage federal baseline, US export-control defensive-cyber carve-out, OECD cyber-eval reciprocity). `tech.agent_runtime_security` covers defending agents at runtime and `business.ai_security_compliance_market` covers the compliance market. Offensive and autonomous-pentest *tooling* sits between them. If this reaches 5-6 organic rows, prefer widening `tech.agent_runtime_security` over adding a theme. No action now.
- **Securities-disclosure for AI hardware — an extraction artifact, not an unhomed cluster.** Seven rows look like a cluster (AI-accelerator S-1 per-counterparty risk-factor tables, SEC Corp Fin S-1 staff guidance, SEC AI-accelerator IPO Staff Legal Bulletin, SEC AI compute prebuy concept release, frontier-lab chip-supply warrant deals in S-1 disclosure, Anthropic confidential S-1, AI-accelerator IPO cohort second deal above $10B) but **all seven are 6/09 backfill rows and every one of them is already named almost verbatim in the `business.ai_revenue_disclosure` description in `schema.sql`** — which explicitly lists Corporation Finance staff guidance and Staff Legal Bulletins on AI-accelerator IPO disclosure, per-counterparty risk-factor tables in S-1 filings, and hyperscaler-anchor warrant-equity disclosure language. They are unmatched because candidate extraction never re-evaluates rows after a schema edit, not because the content is unhomed. Promoting a theme here would duplicate an existing one.
- **Frontier-lab voluntary governance / safety-framework convergence** — still exactly 2 tightly-worded 6/09 rows, unchanged since 6/14. Below the bar. If it reaches 3-4, widen `tech.frontier_model_regulatory_board`.
- **Stale clusters already covered by live themes** — the FMRB/allied-reciprocity group, loader-verification group, local and edge-LLM recipe group, hyperscaler compute-coupling group and open-weight/coding-benchmark group are all 6/09 backfill and all map onto existing themes whose descriptions already carry the tokens.
- **Sub-threshold scattered rows** — DeepMind retention packages, DOJ Apple-Siri search remedies, OpenSharing cross-org protocol, x402 settlement metrics, Inkling managed fine-tuning, OpenRouter priced spend-control tier, coding-agent unrequested-upload findings, frontier mid-tier API pricing below $1 per million input tokens. One row each.

## Category-level notes

One scope-category pair is over the 50% dominance threshold: **`business.capital-supply-chain` at 71.3%** (206/289), up from 69.7%. It is the only one, in any scope. `tech.security` at 42.7% is the top tech category with room to spare, and mix-scope's top category is `tech.security` at 35.6%. The structural half of the business finding is unchanged and does not depend on any pending fix: only two of eight business themes live in `business.capital-supply-chain`, and those two now carry 206 of 289 primaries, so any capital-, funding-, supply- or filing-flavoured business prediction has nowhere else to land. Per §2.3 the `business.capital-markets` carve-out remains a design-discussion item, now flagged eleven weeks running. No new category is proposed here.

## Recommended actions

The three schema actions below are a **single indivisible program with one purpose: repair the `add` operation** by removing every semicolon from the themes seed block. They are not content proposals. Two of the three are provably word-for-word identical to the text already in `schema.sql` and change only punctuation. The repair was validated by simulation before being written here: applying all three replacements to a copy of `app/src/schema.sql` and re-running the exact locator regex from `apply_schema_edit.py:312-315` flips it from **no match** to **match**, with the seed block's semicolon count falling from 30 to 1 (the statement terminator). Applying any subset leaves it broken, because the regex stalls at the first semicolon-bearing row.

The whole proposal was then run end to end against copies: parsed with `parse_proposal`, applied with `_apply_rewrite_description`, and the resulting schema executed with `executescript` against a copy of the live database. Outcome — themes row count 18 (unchanged, nothing added or lost), the dangling cross-reference cleared from all three rendered locales, and the EN-drift set still exactly the same three themes it was before, so these actions introduce no new drift. The live `app/data/analytics.sqlite` and `app/src/schema.sql` were not modified by any of this.

All three are `rewrite-description` ops, which do work at the file level. None of them will reach the matcher until the propagation defect in Action 4 is fixed — and that is fine, because none of them is trying to change matcher behaviour.

### Action 1: `rewrite-description` `tech.ai_chip_architecture` — de-semicolon and remove the dangling cross-reference

Two jobs in one op. First, this row carries 9 of the seed block's 29 in-literal semicolons, all introduced by last week's own rewrite. Second, its description points readers at `tech.ai_infra_private_capital`, which does not exist because last week's `add` failed — and unlike the English text, the `ja`, `es` and `fil` halves of that sentence **did** reach the database and are live on the dashboard right now. This op restructures the keyword run into semicolon-free sentences, keeps every technical token including the 2026 silicon vocabulary added last week, and re-routes the private-capital sentence to `tech.ai_macro_capital_markets`, which does exist and is currently the least-wrong home for that content. Locale text is supplied deliberately here — unlike Actions 2 and 3 — precisely because the locale columns are the ones carrying the dangling reference.

This was verified by execution rather than assumed. Applying this proposal to a copy of `app/src/schema.sql`, running the result through `executescript` against a copy of the live database — which is exactly what `db.init_db()` does on every `cli update` — and reading the row back shows `description_ja`, `description_es` and `description_fil` all losing the dangling reference (580/1128/1073 characters carrying it, to 543/1199/1097 characters clean). The English column stays at 296 characters and stays stranded, as expected, until Action 4 lands. Note also that the locale fix works *indirectly*: the new text lands as a freshly appended `UPDATE` block that executes after the stale one rather than replacing it in place. That is Defect C below.

```action
{
  "kind": "rewrite-description",
  "theme_id": "tech.ai_chip_architecture",
  "new_description_en": "AI accelerator silicon design and architecture. Core topics are memory-bandwidth-first versus peak-FLOPS positioning, HBM capacity and bandwidth tiers, HBM-free near-memory computing designs, 3D stacking, chiplet and advanced-packaging tradeoffs, process-node and EUV capacity constraints on accelerator supply, inference-ASIC challengers and non-GPU datacenter silicon, custom hyperscaler XPU programmes, the training-versus-inference SKU split, accelerator interconnect and memory hierarchy, and accelerator-specific model behaviour and kernel portability. Named parts include TPU, Trainium, MAIA, Vera Rubin, MI300X, MI355X, MI400, GB300, WSE-3 and Corsair-class silicon. (Public-market macro, capital-markets dynamics and the financing of silicon vendors are covered by tech.ai_macro_capital_markets. Revenue and segment disclosure of accelerator sales is covered by business.ai_revenue_disclosure. Multi-year capacity commitments are covered by business.compute_capex_strategy.)",
  "new_description_ja": "AIアクセラレータのシリコン設計とアーキテクチャ。主要トピックはメモリ帯域優先 対 ピークFLOPS のポジショニング、HBM 容量・帯域階層、HBM フリーの近メモリコンピューティング設計、3D スタッキング、チップレット、先端パッケージングのトレードオフ、アクセラレータ供給を制約するプロセスノードおよび EUV 能力、inference-ASIC 挑戦者と non-GPU データセンターシリコン、ハイパースケーラー独自 XPU プログラム、学習 対 推論の SKU 分割、アクセラレータのインターコネクトとメモリ階層、アクセラレータ固有のモデル挙動とカーネル移植性。対象製品は TPU、Trainium、MAIA、Vera Rubin、MI300X、MI355X、MI400、GB300、WSE-3、Corsair クラス製品。(公開市場のマクロ、資本市場ダイナミクス、およびシリコンベンダーのファイナンスは tech.ai_macro_capital_markets 側。アクセラレータ売上のセグメント開示は business.ai_revenue_disclosure 側。複数年の能力コミットメントは business.compute_capex_strategy 側。)",
  "new_description_es": "Diseño y arquitectura del silicio de aceleradores de IA. Los temas centrales son el posicionamiento de ancho de banda de memoria frente a FLOPS pico, los niveles de capacidad y ancho de banda HBM, los diseños de computación near-memory sin HBM, los compromisos de apilamiento 3D, chiplets y empaquetado avanzado, las restricciones de nodo de proceso y capacidad EUV sobre el suministro de aceleradores, los challengers de inference-ASIC y el silicio de datacenter no-GPU, los programas XPU personalizados de hyperscalers, la separación de SKU entre entrenamiento e inferencia, la interconexión y jerarquía de memoria del acelerador, y el comportamiento de modelos específico del acelerador junto con la portabilidad de kernels. Las piezas nombradas incluyen TPU, Trainium, MAIA, Vera Rubin, MI300X, MI355X, MI400, GB300, WSE-3 y silicio de clase Corsair. (Las dinámicas macro de mercados públicos, los mercados de capitales y la financiación de proveedores de silicio las cubre tech.ai_macro_capital_markets. La divulgación de ingresos y segmentos de venta de aceleradores la cubre business.ai_revenue_disclosure. Los compromisos plurianuales de capacidad los cubre business.compute_capex_strategy.)",
  "new_description_fil": "Disenyo at arkitektura ng silicon ng AI accelerator. Ang mga pangunahing paksa ay memory-bandwidth-first kontra peak-FLOPS na positioning, mga tier ng HBM capacity at bandwidth, mga disenyong HBM-free na near-memory computing, mga tradeoff sa 3D stacking, chiplet at advanced packaging, mga hadlang sa process node at EUV capacity sa suplay ng accelerator, mga inference-ASIC challenger at non-GPU datacenter silicon, mga custom na XPU program ng hyperscaler, ang hati ng SKU sa training kontra inference, ang interconnect at memory hierarchy ng accelerator, at ang asal ng modelo na tiyak sa accelerator kasama ang portability ng kernel. Kabilang sa mga pinangalanang bahagi ang TPU, Trainium, MAIA, Vera Rubin, MI300X, MI355X, MI400, GB300, WSE-3 at silicon ng klaseng Corsair. (Ang public-market macro, capital-markets dynamics at ang pagpopondo sa mga silicon vendor ay sakop ng tech.ai_macro_capital_markets. Ang revenue at segment disclosure ng benta ng accelerator ay sakop ng business.ai_revenue_disclosure. Ang multi-year capacity commitments ay sakop ng business.compute_capex_strategy.)"
}
```

### Action 2: `rewrite-description` `business.cloud_vs_local_distribution` — punctuation only, zero content change

This row carries 10 of the seed block's semicolons, introduced by the 6/28 widening that was re-emitted on 7/05 and 7/12. **The replacement text below is word-for-word identical to what is in `schema.sql` today.** It was produced mechanically from the current seed text by substituting a comma for each list semicolon and a full stop for each of the two clause semicolons in the trailing parenthetical, with sentence casing corrected after the new full stops. A normalised word-token comparison of old versus new returns identical sequences of 106 tokens. Nothing about this theme's meaning, keywords or scope is being re-proposed — last week's standing instruction against re-litigating the 6/28 widening is respected in full. Locale fields are deliberately omitted so that the `ja`, `es` and `fil` columns are left completely untouched, keeping the blast radius to the one file-level string that the `add` locator has to scan past.

```action
{
  "kind": "rewrite-description",
  "theme_id": "business.cloud_vs_local_distribution",
  "new_description_en": "How AI capability is distributed and delivered — local on-device inference versus hosted cloud frontier AI, and the channel shifts between them. Edge / on-device deployment as a distribution channel, cloud-overflow inversion (local-first with cloud burst), SMB and prosumer local-first adoption, hosted-API versus open-weight-download distribution-model shifts, per-seat local workstation distribution, privacy-driven and cost-driven local distribution choices, three-cloud versus single-vendor hosted distribution, local-first coding-agent distribution with cloud-overflow default, channel-shift economics between download, marketplace, and hosted API. (Open-weight versus proprietary licensing dynamics are covered by business.open_weight_vs_proprietary. Local inference-runtime tooling is covered by tech.local_inference_runtime. This theme is about the distribution channel and delivery model, not the license or the runtime stack.)"
}
```

### Action 3: `rewrite-description` `business.ai_revenue_disclosure` — punctuation only, zero content change

The last of the three semicolon-bearing rows, carrying 10 semicolons introduced by the 7/12 sharpening. **The replacement text is word-for-word identical to what is in `schema.sql` today**, produced by the same mechanical substitution — every list semicolon becomes a comma, and the trailing parenthetical already used full stops so it is unchanged. A normalised word-token comparison returns identical sequences of 137 tokens, and the character length is unchanged at 1251. This is emphatically **not** a re-proposal of the 7/12 sharpening, which remains correct in `schema.sql` and is still waiting on Action 4 to reach the matcher. It is the third leg of the locator repair and nothing else. Locale fields are omitted so the `ja`, `es` and `fil` columns stay untouched.

```action
{
  "kind": "rewrite-description",
  "theme_id": "business.ai_revenue_disclosure",
  "new_description_en": "The 2026 rewrite of how AI revenue is reported to capital markets, focused on disclosure-mechanic vocabulary: SEC AI-revenue concept release, Corporation Finance staff guidance and Staff Legal Bulletins on AI-accelerator IPO disclosure, audited monthly-revenue and WAU disclosure cadence as a recurring reporting primitive, per-token-margin disclosure as a recurring reporting primitive, 10-Q segment footnote breakouts as a disclosure mechanic (AI-services run-rate, AI-accelerator segment footnote, AI-business KPI footnote), AI-accelerator IPO and S-1 disclosure cohort mechanics, per-counterparty risk-factor tables in S-1 filings, hyperscaler-anchor warrant-equity disclosure language, AGI-clause / capability-attestation disclosure language in lab-hyperscaler contracts, AI-accelerator vendor forward-supply 8-K cadence as disclosure primitive, Cerebras / Tenstorrent / Anthropic IPO pricing and post-IPO disclosure mechanics specifically as filings. (Macro and capital-markets regime dynamics around these disclosures are covered by tech.ai_macro_capital_markets, not here. Compute-capex commitments are covered by business.compute_capex_strategy. Hyperscaler-lab partnership structure is covered by business.hyperscaler_frontier_lab_alliance.)"
}
```

### Action 4: Investigation (no schema edit) — the two `apply-schema-edit` emitter defects; this remains the week's priority

Three distinct bugs in `app/skills/apply_schema_edit.py`, all now confirmed by direct measurement rather than inference. **Two of the three are the same root primitive at two different call sites**, which makes the fix cheaper than last week's framing implied.

**Defect A — the English description is unreachable.** `db.init_db()` (`app/src/db.py:45-56`) executes all of `schema.sql` on every `cli update`, so the file is applied every run. But the theme seed is `INSERT OR IGNORE INTO themes(` (`app/src/schema.sql:1186`), which SQLite skips entirely for an existing `theme_id`, while the locale patches at the schema tail are unconditional `UPDATE themes SET description_ja/_es/_fil` statements that always execute. `_apply_rewrite_description()` (lines 326-361) writes the new English text into the skipped `INSERT` row and upserts locale text into the executed `UPDATE` blocks via `_upsert_locale_description()`. Census: 1 `INSERT OR IGNORE`, 24 `UPDATE themes SET` blocks with 23/25/25 `ja`/`es`/`fil` description assignments, and **0** `UPDATE themes SET description =`. Three themes are now provably split-brain, up from two. The durable fix is small: have `_apply_rewrite_description()` also emit an English `UPDATE themes SET description = '…' WHERE theme_id = '…';` into the schema tail, exactly as it already does per locale. That makes rewrites idempotent and reachable without touching the seed block, and retroactively repairs all three stranded themes on the next rebuild. Switching the seed to `INSERT OR REPLACE` is a smaller diff but riskier, since it would clobber DB-side columns absent from the seed row on every run.

**Defect B — the `add` locator, and a correction to the bisect that was handed to this review.** The received framing was that the locator fails above a semicolon *count* threshold, with 30-32 reported as passing and 57 as failing. That framing is wrong and would mislead whoever fixes this. Measured directly: the current seed block contains **30** semicolons — inside the reported passing band — and the locator nonetheless returns **no match**. The discriminator is not the count but the **position**: `(?:\([^;]*\)\s*,?\s*)*` walks row groups that may not contain a semicolon, so the walk stalls at the *first* semicolon-bearing row and can never reach the terminator. The seed's 18 rows are ordered with `tech.ai_chip_architecture` at position 7, `business.cloud_vs_local_distribution` at 9 and `business.ai_revenue_disclosure` at 17, carrying 9, 10 and 10 semicolons; the other 15 rows carry none, and the final row (`tech.frontier_model_regulatory_board`) is clean. **Any one semicolon anywhere before the terminator breaks it**, which is why Actions 1-3 must all land or none of them helps. The correct durable fix is to make the locator quote-aware — scan for the statement terminator respecting SQL string literals instead of using `[^;]*` — after which description punctuation stops being load-bearing. Actions 1-3 are a stopgap that restores `add` under the existing regex, not a substitute for that fix.

**Defect C — the same `[^;]*` primitive silently duplicates locale UPDATE blocks, and this one is new to this review.** `_theme_locale_update_re()` (lines 211-216) locates a theme's existing locale UPDATE with

    UPDATE\s+themes\s+SET[^;]*WHERE\s+theme_id\s*=\s*'<id>'\s*;\s*\n

which is the **same `[^;]*` construct as Defect B**, and it fails for exactly the same reason: once a theme's locale description contains a semicolon, the pattern cannot reach that block's `WHERE` clause. Measured: `_theme_locale_update_re('tech.ai_chip_architecture')` returns `None` against the current `schema.sql` even though locale UPDATE statements for that theme demonstrably exist at lines 1482 and 1592. `_upsert_locale_description()` (lines 365-379) treats that `None` as "no existing UPDATE" and takes its append branch, writing a brand-new block instead of editing in place. The net database result happens to be correct because the appended block executes last and last write wins — which is why Action 1's locale fix does land — but `schema.sql` now accumulates permanently dead, superseded statements. There are already **24** `UPDATE themes SET` blocks, and every future locale-carrying rewrite against a semicolon-bearing theme adds another. It is also a latent correctness trap: any future reordering or deduplication of the tail would silently promote the stale block.

The practical consequence is that **one fix closes both B and C**. Replacing `[^;]*` with a quote-aware statement scan in both `_insert_before_themes_seed_terminator()` and `_theme_locale_update_re()` restores `add`, restores in-place locale editing, and makes description punctuation stop mattering anywhere. Combined with the English `UPDATE` emitter from Defect A, that is three small changes in one file that unblock every schema operation this project has.

**Verification the parent should run after the next rebuild**: confirm `themes.description` in `app/data/analytics.sqlite` matches the `schema.sql` seed for all 18 themes, and confirm the `themes` row count has moved off 18 once an `add` is next attempted. Deleting `app/data/analytics.sqlite` to force a clean rebuild is still explicitly **not** recommended: per §6.2 the glossary candidate-to-active-to-retired flow and the `theme_candidates` accumulation are DB-owned state that is not reconstructible from files.

```action
{"kind": "log-only"}
```

### Action 5: Investigation (no schema edit) — degenerate §2.1 thresholds, a promotion path that has never executed, and the blocked private-capital theme

Four items, all advisory.

**First, the §2.1 pain-point thresholds are degenerate and should be rewritten.** The empty/underused rule (`child_ids` in {0, 1}) fires on **0 of 18** themes and the overpopulated rule (`child_ids` >= 6) fires on **18 of 18**; child counts now run 20 to 253. Both were calibrated when themes held single-digit counts, and reviews have been silently substituting primary-core judgement for months while the written policy said something else. Recommend recalibrating to primary-core and relative measures — for example underused at primary <= 2% of scope primaries, overpopulated at primary >= 25% of scope primaries, plus an explicit children-to-primary ratio flag above roughly 10:1, which is the measure that actually isolates this week's real problems (`business.hyperscaler_frontier_lab_alliance` at 16.0:1, `business.ai_security_compliance_market` at 13.7:1, `business.cloud_vs_local_distribution` at 47:1).

**Second, the candidate promotion path has never successfully executed.** All 64 rows are `pending`, `promoted_theme_id` is NULL for every row ever written, and the single `add` this project has attempted failed silently. Last week correctly diagnosed that reviews had been gating on raw-label repetition, a bar that can never be cleared because every candidate label is a unique prediction sentence; it then cleared that bar and proposed a promotion, which the tooling ate. The queue does not drain because the drain is broken, not because the bar is unmet.

**Third, `tech.ai_infra_private_capital` is genuinely warranted and should be added as soon as `add` works.** The cluster has grown from 8 to 12 organic rows in a week and is covered by no existing theme — `tech.ai_macro_capital_markets` is public-market macro, `business.ai_revenue_disclosure` is public-filing mechanics, `business.compute_capex_strategy` is multi-year capex, `business.hyperscaler_frontier_lab_alliance` is partnership structure, and none describes a venture round, a private valuation mark or an order-book-backed raise. **It is deliberately not re-emitted as an `add` block this week**, because an `add` op cannot land until either Actions 1-3 or the quote-aware locator fix in Action 4 is applied, and emitting a directive that is guaranteed to fail would waste an action slot and add a second dangling cross-reference. The specification from the 7/19 proposal remains valid and should be re-used verbatim once the locator works. Note that Action 1 above temporarily re-routes the private-capital sentence to `tech.ai_macro_capital_markets`, so that pointer must be pointed back when the theme is created.

**Fourth, carried-forward pipeline items.** Candidate extraction never re-evaluates pending rows after a schema edit, which is why seven S-1-disclosure rows sit unmatched against a `business.ai_revenue_disclosure` description that names them almost verbatim; a post-schema-edit re-evaluation pass would drain a large share of the 64 without any taxonomy change. The `export.py` secondary-attach threshold is flagged for a fifteenth week. And per §6.1, the glossary writer prompt should enforce the 25-word and 2-sentence `quick_def` limits at generation time — 47 terms trip `form/warn` on every one of 61 check dates for 3027 total rows and can never self-clear because `warn` does not flip status — with the 154 empty-`quick_def` `form/fail` terms triaged separately.

```action
{"kind": "log-only"}
```

## Why this rotation

Last week's review correctly predicted that its own `rewrite-description` would be eaten by the propagation defect, and it was. What it did not anticipate is that its `add` would fail too, leaving the taxonomy at 18 themes for a fourteenth week and stranding a cross-reference to a theme that was never created — visibly, in three of the four dashboard locales. Three defects in the same file have now blocked or corrupted every schema change this project has attempted in a month, and two of them turn out to be the same `[^;]*` regex primitive at two call sites.

The rotation is therefore spent on unblocking rather than on taxonomy content, because taxonomy content cannot currently be applied. Actions 1-3 are one indivisible repair: strip the 29 in-literal semicolons that previous `rewrite-description` runs injected into the themes seed block, which restores the `add` locator under the existing regex. Two of the three are provably word-identical to the current text and change only punctuation, so no measurement is disturbed and nothing already actioned is re-litigated; the third also removes the dangling cross-reference from the locales where it is actually rendered. The repair was simulated end to end before being proposed, and the locator flips from no-match to match only when all three land.

Action 4 carries all three root causes, corrects the semicolon-count framing that would otherwise have sent the fixer after the wrong variable, and reduces the durable fix to two changes — an English `UPDATE` emitter, and a quote-aware statement scan replacing `[^;]*` at both call sites. Action 5 records that the §2.1 thresholds fire on 0/18 and 18/18 and should be rewritten around primary core and children-to-primary ratio, that the candidate queue has never once drained because its drain has never worked, and that the private-capital theme is warranted but deliberately withheld until the tooling can accept it.

No business-scope content edit is proposed, for the third week running and for the same reason: the sharpened disclosure description still has not entered the matcher, `business.capital-supply-chain` dominance rose to 71.3% purely on re-measurement, and widening any of the five starved business themes now would confound the only clean before-and-after this taxonomy will get.

## Deferred for next week

- **Confirm the locator repair actually landed.** After apply, re-run the `apply_schema_edit.py:312-315` regex against `app/src/schema.sql` and confirm it matches, and that the seed block holds exactly one semicolon.
- **Then promote `tech.ai_infra_private_capital`.** Re-use the full `add` block from the 7/19 proposal verbatim, and repoint the private-capital sentence in `tech.ai_chip_architecture` from `tech.ai_macro_capital_markets` back to the new theme.
- **Verify EN propagation before reading any number as a trend.** Confirm `themes.description` matches the `schema.sql` seed for all 18 themes. Until it does, `business.ai_revenue_disclosure` at 142 primary, `business.capital-supply-chain` at 71.3%, `business.cloud_vs_local_distribution` at 1 and `tech.ai_chip_architecture` at 7 are all re-measurements.
- **`business.ai_revenue_disclosure` post-sharpen state.** Once the sharpened description reaches the matcher, expect primary to fall from 142 toward 40-50 and category density from 71.3% toward 50-55%. If it barely moves, escalate to the category carve-out.
- **`business.hyperscaler_frontier_lab_alliance`.** 80 children, 5 primary, 16.0:1 and worsening. First in the keyword-sharpening queue once the business measurement is clean.
- **`business.capital-supply-chain` category carve-out.** Per §2.3 needs its own design discussion. Eleven weeks running. The structural argument does not depend on any fix.
- **§2.1 threshold recalibration.** Rewrite the empty and overpopulated rules against primary core, relative share, and children-to-primary ratio.
- **Autonomous offensive-security agents cluster.** 3 organic rows. If it reaches 5-6, widen `tech.agent_runtime_security` rather than adding a theme.
- **Frontier-lab voluntary-governance cluster.** Flat at 2 backfill rows since 6/14. If it reaches 3-4, widen `tech.frontier_model_regulatory_board`.
- **Pipeline-level fixes.** Quote-aware statement scan replacing `[^;]*` in both `_insert_before_themes_seed_terminator()` and `_theme_locale_update_re()`, an English `UPDATE themes SET description` emitter, a sweep of the 24 accumulated `UPDATE themes SET` blocks for dead superseded statements, candidate post-schema-edit re-evaluation, the `export.py` secondary-attach threshold, and the glossary writer-prompt length cap.

---
