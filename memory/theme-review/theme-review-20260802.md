# Theme review — week ending 2026-08-02

Mode: routine Sunday rotation (5_weekly_theme_review), run Monday 2026-08-03 as a catch-up. Diagnostic + advisory pass over the current schema. Inputs: `app/data/analytics.sqlite` (read-only — `themes`, `prediction_scope_assignments`, `predictions`, `theme_candidates`, `graph_exports`, `glossary_terms`, `glossary_audit`), `app/src/schema.sql`, `app/skills/apply_schema_edit.py`, `app/src/ingest.py`, `memory/theme-review/theme-review-20260726.md`. The three `docs/data/graph-*.json` files are 33-40 MB each and were **not** parsed; every graph-level figure below comes from the `graph_exports` table instead, and per-theme population is measured from `prediction_scope_assignments` joined to `predictions`.

## Diagnostic summary

**The `add` operation works again. That is the week's headline, and it was verified by execution rather than assumed.** Running the exact locator regex from `apply_schema_edit.py:312-315` against the current `app/src/schema.sql` now returns a **match** — it returned no match for the previous three weeks. The themes seed block spans characters 44226-56788, holds 18 rows, and contains **zero in-literal semicolons**; the only `;` inside the matched span is the statement terminator. Last week's Actions 1-3 landed exactly as designed and the repair holds. `_apply_add`'s duplicate guard was also checked directly: it refuses on the **quoted** form `'tech.ai_infra_private_capital'`, and while the bare string still appears 3 times in `schema.sql`, the quoted form appears **0** times, so the add will not be refused.

**Last week's locale fix also reached readers.** All four description columns in the live database were queried for the string `ai_infra_private_capital`: **0 rows in `description`, `description_ja`, `description_es` and `description_fil`**. The dangling cross-reference that was rendering in three of the four dashboard locales is gone. The three surviving occurrences in `schema.sql` are at lines 1482, 1592 and 1596, all inside **superseded** locale UPDATE blocks that are overwritten later in the same script by the block at lines 1599-1603.

**The English propagation defect is unchanged and is now the only remaining apply-schema-edit blocker.** Emitter census of `app/src/schema.sql`: **1** `INSERT OR IGNORE INTO themes(`, **0** `INSERT OR REPLACE INTO themes(`, **25** `UPDATE themes SET` blocks (24 last week), and **0** occurrences of `UPDATE themes SET description =` — indeed 0 occurrences of `SET description =` anywhere in the file. `db.init_db()` executes the whole file every `cli update`, so the `INSERT OR IGNORE` is silently skipped for the 18 existing rows while every locale `UPDATE` lands unconditionally. The EN-drift set is still exactly three themes:

| Theme | schema.sql EN | DB EN | Verdict |
|---|---|---|---|
| `business.ai_revenue_disclosure` | 1251 | 590 | drift (since 7/12) |
| `business.cloud_vs_local_distribution` | 936 | 217 | drift (since 7/12) |
| `tech.ai_chip_architecture` | 983 | 296 | drift (since 7/19) |
| other 15 themes | — | — | exact match |

One correction to the figures this review was briefed with: `tech.ai_chip_architecture` is **983** characters in `schema.sql`, not 996. 996 was its pre-Action-1 length; last week's rewrite replaced that text with a shorter semicolon-free version. The DB side, 296, is unchanged and correct.

**What this means for every number below**: the matcher that produced this week's table read the same three stale English descriptions as the last three weeks. Movement in those three themes is re-measurement, not trend.

### Scope totals and growth

324 predictions in `predictions`, spanning 2026-04-19 to 2026-08-02 at a steady 3 per day. Every one of them carries a scope assignment — there are **0 predictions with no assignment**. Distinct predictions per scope: tech **271** (was 255, +16), business **309** (was 289, +20), union **324** (was 303, +21).

From `graph_exports`, the 2026-08-03 rebuild (`date_end` 2026-08-02) wrote mix at **354 nodes / 1681 links**, business at 323 / 952, tech at 287 / 693. The 2026-07-26 rebuild wrote mix 333 / 1570, business 302 / 891, tech 270 / 643. Links per node in mix scope is 4.75 against 2.41 in tech scope, so the `export.py` secondary-attach inflation persists for a sixteenth consecutive week and is still an exporter threshold property, not a schema fault.

### Per-theme population

`primary` is the count of distinct **live** predictions attached to the theme in `prediction_scope_assignments` — that is, joined to `predictions` so that identity debris is excluded (see the next subsection). `children` is the `child_ids` length supplied to this review from the mix-scope graph and is **not** independently verified here, because verifying it would require parsing a 40 MB file. No conclusion below depends on its exact value.

| Theme | Category | children | primary | vs 7/26 |
|---|---|---|---|---|
| AI-Revenue Disclosure Rewrite (`business.ai_revenue_disclosure`) | business.capital-supply-chain | 273 | 156 | +14 |
| Model Supply Chain (`tech.model_supply_chain`) | tech.security | 200 | 93 | +10 |
| Compute Capex Strategy (`business.compute_capex_strategy`) | business.capital-supply-chain | 176 | 69 | +5 |
| AI Macro & Capital Markets (`tech.ai_macro_capital_markets`) | tech.infrastructure | 111 | 43 | +1 |
| Inference Server Supply Chain (`business.inference_server_supply_chain`) | business.regulation-compliance | 150 | 34 | +1 |
| Agent Runtime Security (`tech.agent_runtime_security`) | tech.security | 98 | 27 | +1 |
| Open Weight vs Proprietary AI (`business.open_weight_vs_proprietary`) | business.competition | 82 | 24 | 0 |
| Agent Control Plane (`tech.agent_control_plane`) | tech.agents | 49 | 23 | 0 |
| Local Inference Runtime (`tech.local_inference_runtime`) | tech.inference-runtime | 34 | 22 | +1 |
| Physical AI / Robotics (`tech.physical_ai_robotics`) | tech.infrastructure | 27 | 17 | +1 |
| Frontier Model Regulatory Board (`tech.frontier_model_regulatory_board`) | tech.standards | 39 | 17 | 0 |
| Developer Toolchain Platformization (`business.developer_platformization`) | business.enterprise-adoption | 73 | 17 | 0 |
| Agent Registry Architecture (`tech.agent_registry_architecture`) | tech.standards | 43 | 11 | +1 |
| 1-bit / Edge LLM (`tech.one_bit_edge_llm`) | tech.models | 40 | 10 | 0 |
| AI Chip Architecture (`tech.ai_chip_architecture`) | tech.infrastructure | 27 | 8 | +1 |
| Hyperscaler × Frontier Lab Alliance (`business.hyperscaler_frontier_lab_alliance`) | business.market-structure | 85 | 5 | 0 |
| AI Security Compliance Market (`business.ai_security_compliance_market`) | business.regulation-compliance | 41 | 3 | 0 |
| Cloud vs Local AI Distribution (`business.cloud_vs_local_distribution`) | business.distribution | 49 | 1 | 0 |

Category density on the 324-prediction union: **`business.capital-supply-chain` 225 = 69.4%**, tech.security 120 = 37.0%, tech.infrastructure 68 = 21.0%, business.regulation-compliance 37 = 11.4%, tech.standards 28 = 8.6%, business.competition 24 = 7.4%, tech.agents 23 = 7.1%, tech.inference-runtime 22 = 6.8%, business.enterprise-adoption 17 = 5.2%, tech.models 10 = 3.1%, business.market-structure 5 = 1.5%, business.distribution 1 = 0.3%. Within business scope alone the same category is 225/309 = **72.8%**, up from 71.3% and a new high; within tech scope, tech.security is 120/271 = 44.3% and tech.infrastructure 68/271 = 25.1%.

`tech.ai_chip_architecture` moved for the first time in five weeks, 7 to 8. One prediction is not a signal, and its rewrite still has not reached the matcher, so this is noted and not interpreted.

### Prediction-identity debris — a defect this review found while recomputing

The distilled figures handed to this review were checked against the database and **all eighteen per-theme counts and the 69.4% dominance figure were reproduced exactly**. Getting there required excluding something that a naive query does not exclude, and it is worth recording because it silently corrupts the obvious query.

`prediction_scope_assignments` references **334** distinct `prediction_id` values while `predictions` holds **324**. Ten of those ids exist only in the assignment table:

`prediction.3a42ff6ffbdabd36`, `prediction.38bfc80fe3ba6729`, `prediction.eb436d794d515a46`, `prediction.c94fb5a0efdab99d`, `prediction.cbd6722140f4b5d3`, `prediction.364e4a033e10de6a`, `prediction.b7efbcd1bed41729`, `prediction.391cf45f4334c271`, `prediction.975b5a05725c3599`, `prediction.e0af7b7e4cf978f8`.

Together they carry 17 assignment rows, written 2 on 7/19, 4 on 7/30, 5 on 8/01, 4 on 8/02 and **2 on 8/03 — that is, during this very rebuild**. The same pattern appears in `prediction_evidence_links` (12 orphan rows across 3 ids) and in `theme_candidates` (3 rows). `prediction_needs`, `prediction_realization_snapshots` and `validation_rows` are clean.

The mechanism is the known re-key cascade: a prediction id is `sha1(date || body)`, ingest upserts and never deletes, so editing a body after ingest mints a new row and abandons the old one's attachments. Three of the ten are provable rather than inferred, because their abandoned rows left twins in `theme_candidates` carrying byte-identical labels under different `origin_prediction_id` values.

Querying per-theme population without the join to `predictions` inflates the top of the table and the dominance headline: `business.ai_revenue_disclosure` reads **161** instead of 156, `tech.model_supply_chain` **98** instead of 93, `business.compute_capex_strategy` **72** instead of 69, and `business.capital-supply-chain` reads 233/334 = **69.8%** on the union and 73.0% within business scope. Every one of those is wrong by the width of the debris. Carried in Action 3.

### Glossary audit (§6.1 hook)

`glossary_terms`: **126** active, 954 candidate, 234 retired (was 112 / 874 / 201). `glossary_audit` now spans 67 distinct check dates, up from 61: `dedupe/pass` 7935 rows across 304 terms, `form/pass` 4335 / 77, **`form/warn` 3421 rows across only 50 distinct terms**, `form/fail` 181 rows / 181 terms, `semantic/pass` 6, `dedupe/fail` 1, `dedupe/warn` 1. The over-length set grew 47 to 50 terms and the empty-`quick_def` set grew 154 to 181. Diagnosis unchanged for a third week: `warn` does not flip status, so the same terms are re-logged every run and can never self-clear. Carried in Action 5.

## Empty / underused themes

By the literal §2.1 rule (`child_ids` in {0, 1}) **no theme qualifies**. The smallest child count in the project is 27, which is more than an order of magnitude above the threshold. The rule has now been non-firing for months and is treated in Action 5.

Reading underuse by live primary core instead, the discriminating signal remains high linkage with near-zero primary attachment:

- **`business.cloud_vs_local_distribution` — 1 primary, eighth consecutive week at 1.** Ratio 49:1, the worst in the project. Its widened description has been correct in `schema.sql` since 7/12 and has still never reached the matcher. Not a merge candidate on this evidence, because the evidence has never been collected.
- **`business.hyperscaler_frontier_lab_alliance` — 5 primary, 17.0:1** (was 16.0:1; children grew while primary stayed flat). Still first in the keyword-sharpening queue, and still deliberately not sharpened — see the Action 2 rationale about which edits are worth an action slot while English is unreachable.
- **`business.ai_security_compliance_market` — 3 primary, 13.7:1.** Flat for a sixth week. Competes with `business.inference_server_supply_chain` inside `business.regulation-compliance`. Log-only watch, unchanged.
- **`tech.ai_chip_architecture` — 8 primary, 3.4:1.** Moved off 7 for the first time since 6/28. Its corrective rewrite exists in `schema.sql` and remains unreachable.

Every other theme sits at 4.4:1 or below, so the ratio measure cleanly isolates exactly the three themes that reviews have been flagging by judgement for two months.

## Overpopulated themes

By the literal §2.1 rule (`child_ids` >= 6) **all 18 themes qualify**, since the smallest is 27. The rule carries zero information at this pool size and **no splits are proposed on the strength of it** — proposing 18 splits because a threshold calibrated for single-digit themes fires on everything would be a tooling artifact, not a taxonomy judgement. Recalibration is Action 5.

Reading the §2.1 intent instead — high population *plus* separable sub-topics:

- **`business.ai_revenue_disclosure` — 156 primary, 48.1% of the business scope.** Still the largest theme in any scope and the fastest grower again at +14. Assessment unchanged: a large share defaults to it because its **live** description is the broadest in the business scope, and the sharpening that would fix that has been correct in `schema.sql` since 7/12 and unreachable since. No content change proposed, for the fourth week running and for the same reason.
- `tech.model_supply_chain` (93 primary, +10) — largest tech theme. Primary core stays coherent around signing, provenance and loader verification and still does not separate into a clean second cluster. Leave as-is.
- `business.compute_capex_strategy` (69 primary, +5) — coherent around multi-year commitments and GW-scale buildouts. Leave as-is.
- `business.inference_server_supply_chain` (34 primary) — primary core coherent; the high child count is secondary-attach inflation. Leave as-is.
- `tech.ai_macro_capital_markets` (43 primary) — coherent around public-market macro. Action 1 finally carves the private-capital cluster out from under it; Action 2 repoints the cross-reference that has been temporarily parked on it since last week.

## Theme candidates

**71 pending rows, up from 64. All 71 are `status='pending'`, all `candidate_reason='no_keyword_match'`, all with `nearest_theme_id` NULL, and `promoted_theme_id` is NULL for every row in the table's entire history.** The promotion path has still never executed end to end. 37 of the 71 are the single 2026-06-09 bulk backfill; 34 arrived organically since.

**The one label that clears the §2.1 three-hit bar does not represent three hits.** The table holds 71 rows but only **68 distinct labels**, and it holds **71 distinct `origin_prediction_id` values** — so the duplicates are not repeated inserts of one prediction, they are one prediction wearing three different ids. `_upsert_candidate` at `app/src/ingest.py:440` keys the row as `_hash_id("candidate", scope_id, prediction_id)`, so a re-keyed prediction mints a brand-new candidate row and `INSERT OR IGNORE` never touches the old one.

- *Samsung's handset unit stays loss-making in every quarter reported by H1 2027* — 3 rows, all created 2026-07-30, three distinct origin ids of which **two are dead** and one (`prediction.1a47890402ef2c78`) is live.
- *Amazon publishes an earnings figure excluding its Anthropic mark by H2 2027* — 2 rows, created 2026-08-01, two distinct origin ids of which **one is dead** and one (`prediction.307ab0e4fadaca81`) is live.

Deduplicated by label, **no candidate cluster in the table reaches 3 identical labels**, and the correct reading of the briefing note that "one label reaches the threshold" is that zero do. Nothing is promoted on that basis this week.

Clustering on genuine content:

- **AI-infrastructure private capital — 12 organic rows, unchanged this week, and the only cluster that clears §2.1 on distinct content.** The 12 span 6/17 through 7/26: Corsair-class inference silicon booking a named hyperscaler deployment, OpenAI locking equity-coupled HBM allocation, a sovereign-AI unicorn crossing, OpenAI's public-listing step with a US-government stake, standalone infrastructure funding for non-GPU datacenter silicon, an inference-ASIC challenger anchoring a raise on a $1B-plus order book, SK Hynix converting ADR proceeds into booked EUV orders, a European defense-AI institutional mega-round, a Together or Baseten $5B-plus raise, AMD converting MI450 co-design into a firm rack-scale commitment, self-financed multi-decade power deals reaching a second frontier lab, and Etched converting SK hynix equity into a disclosed HBM agreement. No existing theme covers venture rounds, private valuation marks or order-book-backed raises. **It is promoted in Action 1, because for the first time in three weeks the tooling can accept it.**
- **All seven new rows this week are earnings- and segment-disclosure content that an existing theme already names.** Four distinct labels: OpenAI's four-account tally rising on outside disclosure (7/29), Meta breaking out AI compute revenue as its own reported line (7/30), the Samsung handset segment triple (7/30), and the Amazon ex-Anthropic earnings pair (8/01). The `business.ai_revenue_disclosure` description in `schema.sql` explicitly lists 10-Q segment footnote breakouts, AI-services run-rate, AI-accelerator segment footnotes and AI-business KPI footnotes — every one of these rows would very likely match it. They are unmatched because the matcher reads the 590-character stale English column and not the 1251-character text that names them. This is the cleanest cost estimate of the propagation defect yet produced: it is generating roughly one unhomeable candidate per day.
- **Autonomous offensive-security agents** — still exactly 3 organic rows (6/22, 6/25, 7/09), unchanged for three weeks. If it reaches 5-6, prefer widening `tech.agent_runtime_security` over adding a theme. No action now.
- **Securities-disclosure for AI hardware** — still seven 6/09 backfill rows, still already named almost verbatim in the `business.ai_revenue_disclosure` schema text, still unmatched only because candidate extraction never re-evaluates pending rows after a schema edit. Promoting here would duplicate an existing theme.
- **Frontier-lab voluntary governance** — still exactly 2 tightly-worded 6/09 rows, unchanged since 6/14. Below the bar. If it reaches 3-4, widen `tech.frontier_model_regulatory_board`.
- **Sub-threshold scattered rows** — DeepMind retention packages, DOJ Apple-Siri search remedies, OpenSharing cross-org protocol, x402 settlement metrics, Inkling managed fine-tuning, OpenRouter priced spend-control tier, coding-agent unrequested-upload findings, frontier mid-tier API pricing below $1 per million input tokens, HBM-free near-memory second Chinese entrant. One row each.

## Category-level notes

Exactly one scope-category pair is over the 50% dominance threshold: **`business.capital-supply-chain`**, at 69.4% of the 324-prediction union and 72.8% within business scope, up from 71.3%. It is the only one in any scope; the runner-up is `tech.security` at 37.0% of the union. The structural half of the finding does not depend on any pending fix: only two of eight business themes live in `business.capital-supply-chain`, and those two now carry 225 of 309 business-scope primaries, so any capital-, funding-, supply- or filing-flavoured business prediction has nowhere else to land. Action 1 adds a third home for exactly that content, but it lands in `tech.infrastructure`, so it will relieve the tech side of the pressure and not the business side. Per §2.3 the `business.capital-markets` carve-out remains a design-discussion item, now flagged twelve weeks running. No new category is proposed here.

## Recommended actions

Two schema-editing actions and three advisory ones. The two schema edits were validated by execution before being written here: the whole proposal was parsed with `parse_proposal`, applied with `_apply_one` against a copy of `app/src/schema.sql`, and the result executed with `executescript` against a copy of the live database. Neither the live schema nor the live database was modified.

A selection principle applies while the English column is unreachable. A `rewrite-description` whose purpose is to change **matcher** behaviour is worthless right now, because the matcher reads the one column no statement can update — that is why `business.hyperscaler_frontier_lab_alliance` is still not sharpened despite being the worst ratio in the project, and why `business.ai_revenue_disclosure` is untouched for a fourth week. Only two kinds of edit are worth an action slot today: an `add`, whose `INSERT OR IGNORE` fires normally for a genuinely new `theme_id` and therefore lands in English too, and a `rewrite-description` whose value is entirely in the locale columns that do land. Action 1 is the first kind and Action 2 is the second.

Both descriptions below are **semicolon-free in all four locales**, verified programmatically. This is load-bearing: the `add` locator's `(?:\([^;]*\)\s*,?\s*)*` row walk stalls at the first semicolon-bearing seed row, which is precisely how the operation was broken for three weeks, and a single `;` reintroduced into the seed block would break it again for everyone.

### Action 1: Add `tech.ai_infra_private_capital` theme under `tech.infrastructure` — promote the AI-infrastructure financing cluster

This is the deferred item from 7/19 and 7/26, finally actionable. The cluster stands at 12 organic candidate rows spanning 6/17 to 7/26 and is covered by no existing theme: `tech.ai_macro_capital_markets` is public-market macro, `business.ai_revenue_disclosure` is public-filing mechanics, `business.compute_capex_strategy` is multi-year capex, `business.hyperscaler_frontier_lab_alliance` is partnership structure, and none of them describes a venture round, a private valuation mark or an order-book-backed raise. It clears the §2.1 bar four times over.

Three things were checked before emitting this. First, the locator matches, so `_insert_before_themes_seed_terminator` will find the terminator instead of raising. Second, `_apply_add`'s duplicate guard searches for the **quoted** `'tech.ai_infra_private_capital'`, which appears 0 times in `schema.sql` — the 3 bare occurrences are inside superseded locale UPDATE literals and do not trip it. Third, and most important, **this action is not gated on the English propagation defect**: `INSERT OR IGNORE` skips rows that already exist, and this `theme_id` does not exist, so the seed fires and the English description lands in the matcher on the next rebuild. It is the only operation in the current vocabulary with that property.

The specification is the 7/19 block with three changes: every semicolon replaced by a comma or a full stop so the seed block stays clean, a clause added for the self-financed multi-decade power-deal content that has since accumulated, and the cross-reference set left intact. Risk is additive and self-limiting — `tech.infrastructure` sits at 25.1% of tech-scope density with headroom, and if it draws few primaries next week that is itself the answer.

```action
{
  "kind": "add",
  "theme_id": "tech.ai_infra_private_capital",
  "category_id": "tech.infrastructure",
  "label_en": "AI Infrastructure Private Capital",
  "short_label_en": "Infra Capital",
  "tooltip_en": "AI Infrastructure Private Capital",
  "description_en": "Private-market financing of AI infrastructure and silicon. Core topics are venture and growth rounds for inference providers and model-serving platforms, private valuation marks and unicorn crossings, order-book-backed raises by inference-ASIC and accelerator challengers, standalone infrastructure funding for non-GPU datacenter silicon, sovereign-AI national champion funding, defense-AI institutional mega-rounds, memory and foundry vendors converting share or depositary-receipt proceeds into booked equipment orders, equity-coupled supply allocation between labs and component makers, self-financed multi-decade power and energy deals behind frontier-lab buildouts, pre-listing and confidential-filing steps by frontier labs and accelerator vendors, and secondary-market marks on private AI infrastructure. (Public-market macro and capital-markets regime dynamics are covered by tech.ai_macro_capital_markets. The mechanics of how AI revenue is disclosed in public filings are covered by business.ai_revenue_disclosure. Multi-year compute capex commitments are covered by business.compute_capex_strategy. Hyperscaler and frontier-lab partnership structure is covered by business.hyperscaler_frontier_lab_alliance. Chip design and architecture are covered by tech.ai_chip_architecture.)",
  "label_ja": "AIインフラ民間資本",
  "short_label_ja": "インフラ資本",
  "description_ja": "AIインフラおよび半導体の民間市場ファイナンス。主要トピックは推論プロバイダーおよびモデルサービング基盤へのベンチャー・グロースラウンド、未公開企業のバリュエーション評価およびユニコーン到達、inference-ASIC およびアクセラレータ挑戦者による受注残高を裏付けとした資金調達、non-GPU データセンターシリコンへの独立系インフラ資金、ソブリンAIナショナルチャンピオンの資金調達、防衛AIの機関投資家メガラウンド、メモリ・ファウンドリベンダーによる株式・預託証券調達資金の装置発注への転換、ラボと部品メーカー間のエクイティ連動供給枠、フロンティアラボの建設を支える自己資金による超長期の電力・エネルギー契約、フロンティアラボおよびアクセラレータベンダーによる上場前・秘密提出ステップ、未公開AIインフラのセカンダリー市場評価。(公開市場のマクロおよび資本市場レジームのダイナミクスは tech.ai_macro_capital_markets 側。公開書類におけるAI売上開示のメカニクスは business.ai_revenue_disclosure 側。複数年の計算 capex コミットメントは business.compute_capex_strategy 側。ハイパースケーラーとフロンティアラボの提携構造は business.hyperscaler_frontier_lab_alliance 側。チップ設計・アーキテクチャは tech.ai_chip_architecture 側。)",
  "label_es": "Capital Privado de Infraestructura IA",
  "short_label_es": "Capital Infra",
  "description_es": "Financiación en mercados privados de infraestructura y silicio de IA. Los temas centrales son las rondas de venture y growth para proveedores de inferencia y plataformas de model-serving, las marcas de valoración privada y los cruces de unicornio, las rondas respaldadas por cartera de pedidos de challengers de inference-ASIC y aceleradores, la financiación de infraestructura independiente para silicio de datacenter no-GPU, la financiación de campeones nacionales de IA soberana, las mega-rondas institucionales de IA de defensa, los proveedores de memoria y foundry que convierten fondos de acciones o certificados de depósito en pedidos de equipo en firme, la asignación de suministro acoplada a participación entre laboratorios y fabricantes de componentes, los acuerdos autofinanciados de energía a varias décadas detrás de las construcciones de laboratorios frontera, los pasos previos a la salida a bolsa y las presentaciones confidenciales de laboratorios frontera y proveedores de aceleradores, y las marcas de mercado secundario sobre infraestructura de IA privada. (Las dinámicas macro y de régimen de mercados públicos las cubre tech.ai_macro_capital_markets. Las mecánicas de divulgación de ingresos de IA en presentaciones públicas las cubre business.ai_revenue_disclosure. Los compromisos plurianuales de capex de cómputo los cubre business.compute_capex_strategy. La estructura de partnerships hyperscaler-laboratorio la cubre business.hyperscaler_frontier_lab_alliance. El diseño y la arquitectura de chips los cubre tech.ai_chip_architecture.)",
  "label_fil": "Pribadong Kapital sa AI Infrastructure",
  "short_label_fil": "Kapital Infra",
  "description_fil": "Pribadong-merkado na pagpopondo ng AI infrastructure at silicon. Ang mga pangunahing paksa ay venture at growth rounds para sa mga inference provider at model-serving platform, mga pribadong valuation mark at pag-abot ng unicorn, mga raise na nakasandal sa order book ng mga inference-ASIC at accelerator challenger, standalone na infrastructure funding para sa non-GPU datacenter silicon, pagpopondo ng sovereign-AI national champion, mga institutional mega-round sa defense-AI, mga memory at foundry vendor na kinokonberte ang share o depositary-receipt proceeds tungo sa nakabook na equipment order, equity-coupled na supply allocation sa pagitan ng mga lab at component maker, mga self-financed na multi-dekadang power deal sa likod ng mga buildout ng frontier lab, mga pre-listing at confidential-filing na hakbang ng frontier labs at accelerator vendor, at mga secondary-market mark sa pribadong AI infrastructure. (Ang public-market macro at capital-markets regime dynamics ay sakop ng tech.ai_macro_capital_markets. Ang mekanika ng AI revenue disclosure sa public filings ay sakop ng business.ai_revenue_disclosure. Ang multi-year compute capex commitments ay sakop ng business.compute_capex_strategy. Ang hyperscaler at frontier-lab partnership structure ay sakop ng business.hyperscaler_frontier_lab_alliance. Ang chip design at architecture ay sakop ng tech.ai_chip_architecture.)"
}
```

### Action 2: `rewrite-description` `tech.ai_chip_architecture` — repoint the private-capital cross-reference at the theme that now exists

Last week's Action 1 temporarily routed the private-market silicon-financing sentence to `tech.ai_macro_capital_markets`, because that was the least-wrong existing home while the `add` was broken. The 7/26 deferred list explicitly asks for that pointer to be pointed back once the theme is created. This action does that, in all four locales, and adds nothing else — every other word of the description is preserved byte-for-byte, generated by mechanical substitution of the single cross-reference clause rather than by rewriting the text.

Two honest caveats, stated plainly. First, **the English column will not change until the propagation defect in Action 4 is fixed.** This op writes 1060 characters of English into the seed row, `schema.sql` becomes correct, and `themes.description` stays at 296 characters because `INSERT OR IGNORE` skips the row. That is understood and accepted: the entire reader-facing value of this action is in `description_ja`, `description_es` and `description_fil`, which do land, and which are the columns that were carrying the dangling reference until last week. Second, this op does **not** add debris: `_theme_locale_update_re('tech.ai_chip_architecture')` was tested against the current file and matches the live block at lines 1599-1603, so the three locale columns are edited in place rather than appended. The generated text runs 588 / 1285 / 1184 characters for ja / es / fil and contains no semicolons, so the block stays matchable next week.

```action
{
  "kind": "rewrite-description",
  "theme_id": "tech.ai_chip_architecture",
  "new_description_en": "AI accelerator silicon design and architecture. Core topics are memory-bandwidth-first versus peak-FLOPS positioning, HBM capacity and bandwidth tiers, HBM-free near-memory computing designs, 3D stacking, chiplet and advanced-packaging tradeoffs, process-node and EUV capacity constraints on accelerator supply, inference-ASIC challengers and non-GPU datacenter silicon, custom hyperscaler XPU programmes, the training-versus-inference SKU split, accelerator interconnect and memory hierarchy, and accelerator-specific model behaviour and kernel portability. Named parts include TPU, Trainium, MAIA, Vera Rubin, MI300X, MI355X, MI400, GB300, WSE-3 and Corsair-class silicon. (Private-market financing of AI infrastructure and silicon vendors is covered by tech.ai_infra_private_capital. Public-market macro and capital-markets dynamics are covered by tech.ai_macro_capital_markets. Revenue and segment disclosure of accelerator sales is covered by business.ai_revenue_disclosure. Multi-year capacity commitments are covered by business.compute_capex_strategy.)",
  "new_description_ja": "AIアクセラレータのシリコン設計とアーキテクチャ。主要トピックはメモリ帯域優先 対 ピークFLOPS のポジショニング、HBM 容量・帯域階層、HBM フリーの近メモリコンピューティング設計、3D スタッキング、チップレット、先端パッケージングのトレードオフ、アクセラレータ供給を制約するプロセスノードおよび EUV 能力、inference-ASIC 挑戦者と non-GPU データセンターシリコン、ハイパースケーラー独自 XPU プログラム、学習 対 推論の SKU 分割、アクセラレータのインターコネクトとメモリ階層、アクセラレータ固有のモデル挙動とカーネル移植性。対象製品は TPU、Trainium、MAIA、Vera Rubin、MI300X、MI355X、MI400、GB300、WSE-3、Corsair クラス製品。(AIインフラおよびシリコンベンダーの民間市場ファイナンスは tech.ai_infra_private_capital 側。公開市場のマクロおよび資本市場ダイナミクスは tech.ai_macro_capital_markets 側。アクセラレータ売上のセグメント開示は business.ai_revenue_disclosure 側。複数年の能力コミットメントは business.compute_capex_strategy 側。)",
  "new_description_es": "Diseño y arquitectura del silicio de aceleradores de IA. Los temas centrales son el posicionamiento de ancho de banda de memoria frente a FLOPS pico, los niveles de capacidad y ancho de banda HBM, los diseños de computación near-memory sin HBM, los compromisos de apilamiento 3D, chiplets y empaquetado avanzado, las restricciones de nodo de proceso y capacidad EUV sobre el suministro de aceleradores, los challengers de inference-ASIC y el silicio de datacenter no-GPU, los programas XPU personalizados de hyperscalers, la separación de SKU entre entrenamiento e inferencia, la interconexión y jerarquía de memoria del acelerador, y el comportamiento de modelos específico del acelerador junto con la portabilidad de kernels. Las piezas nombradas incluyen TPU, Trainium, MAIA, Vera Rubin, MI300X, MI355X, MI400, GB300, WSE-3 y silicio de clase Corsair. (La financiación en mercados privados de infraestructura de IA y de proveedores de silicio la cubre tech.ai_infra_private_capital. Las dinámicas macro de mercados públicos y de mercados de capitales las cubre tech.ai_macro_capital_markets. La divulgación de ingresos y segmentos de venta de aceleradores la cubre business.ai_revenue_disclosure. Los compromisos plurianuales de capacidad los cubre business.compute_capex_strategy.)",
  "new_description_fil": "Disenyo at arkitektura ng silicon ng AI accelerator. Ang mga pangunahing paksa ay memory-bandwidth-first kontra peak-FLOPS na positioning, mga tier ng HBM capacity at bandwidth, mga disenyong HBM-free na near-memory computing, mga tradeoff sa 3D stacking, chiplet at advanced packaging, mga hadlang sa process node at EUV capacity sa suplay ng accelerator, mga inference-ASIC challenger at non-GPU datacenter silicon, mga custom na XPU program ng hyperscaler, ang hati ng SKU sa training kontra inference, ang interconnect at memory hierarchy ng accelerator, at ang asal ng modelo na tiyak sa accelerator kasama ang portability ng kernel. Kabilang sa mga pinangalanang bahagi ang TPU, Trainium, MAIA, Vera Rubin, MI300X, MI355X, MI400, GB300, WSE-3 at silicon ng klaseng Corsair. (Ang pribadong-merkado na pagpopondo ng AI infrastructure at ng mga silicon vendor ay sakop ng tech.ai_infra_private_capital. Ang public-market macro at capital-markets dynamics ay sakop ng tech.ai_macro_capital_markets. Ang revenue at segment disclosure ng benta ng accelerator ay sakop ng business.ai_revenue_disclosure. Ang multi-year capacity commitments ay sakop ng business.compute_capex_strategy.)"
}
```

### Action 3: Investigation (no schema edit) — the prediction re-key cascade is leaving debris in three tables and is actively growing

Ten `prediction_id` values appear in `prediction_scope_assignments` but not in `predictions`, carrying 17 rows; `prediction_evidence_links` carries 12 more across 3 ids; `theme_candidates` carries 3. Rows were written on 7/19, 7/30, 8/01, 8/02 and 8/03, so this is not a historical artifact — the most recent two rows were written by the rebuild that produced the data for this review.

The mechanism is `sha1(date || body)` identity plus upsert-only ingest. `ingest.py` has `INSERT ... ON CONFLICT DO UPDATE` for assignments and `INSERT OR IGNORE` for candidates and no `DELETE` anywhere, so editing a prediction body after ingest re-keys it and orphans every attachment made under the old id. Three of the ten are provable rather than merely consistent with the theory: their orphaned ids left `theme_candidates` twins carrying byte-identical `suggested_theme_label` values.

Two concrete harms, both measured. **First, it corrupts the taxonomy metrics that this review exists to produce.** Without the join to `predictions`, `business.capital-supply-chain` reads 69.8% instead of 69.4% and 73.0% instead of 72.8%, `business.ai_revenue_disclosure` reads 161 instead of 156, `tech.model_supply_chain` 98 instead of 93, and `business.compute_capex_strategy` 72 instead of 69. **Second, it corrupts the candidate-promotion signal**, which is the one input §2.1 uses to authorise adding a theme: the only label in the table that reaches the three-hit bar reaches it entirely through re-key twins of a single prediction. A reviewer trusting the raw count would propose a theme for a cluster of size one.

Recommended fix, in order of value. Have ingest delete attachments for prediction ids that are no longer present in `predictions` at the end of each run, or enable `PRAGMA foreign_keys` with `ON DELETE CASCADE` on the four child tables. Key `theme_candidates` on the normalised label rather than on `origin_prediction_id`, or add a uniqueness constraint on `(scope_id, suggested_theme_label)`, so a re-key updates a row instead of minting one. Until either lands, **every consumer of `prediction_scope_assignments` must join to `predictions`**, and this review's own queries now do.

```action
{"kind": "log-only"}
```

### Action 4: Investigation (no schema edit) — the English column is now the only blocker, and the dead-block sweep is overdue

**Defect A, the English description is unreachable — unchanged, and now the sole remaining blocker.** Census re-run against the current file: 1 `INSERT OR IGNORE INTO themes(`, 0 `INSERT OR REPLACE`, 25 `UPDATE themes SET` blocks, 0 `UPDATE themes SET description =`, 0 `SET description =` anywhere. Three themes remain split-brain. The durable fix is unchanged and small: have `_apply_rewrite_description()` also emit an English `UPDATE themes SET description = '…' WHERE theme_id = '…'` into the schema tail, exactly as it already does per locale. That makes rewrites idempotent and reachable without touching the seed block, and retroactively repairs all three stranded themes on the next rebuild. Switching the seed to `INSERT OR REPLACE` remains the smaller diff and the riskier one, since it would clobber DB-side columns absent from the seed row on every run. The new evidence for urgency is in the candidates section: all seven new candidate rows this week are content that the stranded `business.ai_revenue_disclosure` text already names, so the defect is now generating roughly one unhomeable candidate per day.

**Defect B, the `add` locator — fixed, and it should be made permanent.** Last week's semicolon strip worked and is verified working today, but it is a stopgap that makes description punctuation load-bearing forever. The durable fix is still to make the locator quote-aware, scanning for the statement terminator while respecting SQL string literals instead of using `[^;]*`. Until that lands, every future proposal author must keep every seed description semicolon-free, and nothing in the toolchain enforces it — there is no test, no lint and no validation step that would catch a reintroduced `;` before it silently disables `add` for another month.

**Defect C, duplicated locale UPDATE blocks — still live, and now measurable per-theme.** `_theme_locale_update_re()` uses the same `[^;]*` primitive and was tested against all 18 themes: it returns a match for 16 and **None for `business.ai_revenue_disclosure` and `business.cloud_vs_local_distribution`**, whose *locale* literals still carry semicolons even though their seed rows no longer do. For those two, `_upsert_locale_description()` will take its append branch and add yet another block. The file already holds 25 `UPDATE themes SET` blocks where 18 would do, and lines 1591-1597 are two **provably dead** blocks that set superseded Spanish and Filipino text for `tech.ai_chip_architecture` and hold the last 3 references to `tech.ai_infra_private_capital` in the repo. They are inert only because the block at 1599-1603 executes after them. The practical guidance for the next few weeks: do not attach locale fields to a `rewrite-description` on those two themes until the quote-aware scan lands, and sweep the six superseded blocks in the same change.

```action
{"kind": "log-only"}
```

### Action 5: Investigation (no schema edit) — degenerate §2.1 thresholds, the never-drained candidate queue, and carried pipeline items

**The §2.1 pain-point thresholds are degenerate and should be rewritten.** The empty/underused rule fires on **0 of 18** themes and the overpopulated rule on **18 of 18**; child counts now run 27 to 273 against thresholds of 1 and 6. Both were calibrated when themes held single-digit counts, and reviews have been substituting primary-core judgement for months while the written policy said something else. Recommend recalibrating to primary-core and relative measures — underused at primary <= 2% of scope primaries, overpopulated at primary >= 25% of scope primaries, plus an explicit children-to-primary ratio flag above roughly 10:1. That ratio measure is the one that works: it isolates exactly `business.cloud_vs_local_distribution` at 49:1, `business.hyperscaler_frontier_lab_alliance` at 17.0:1 and `business.ai_security_compliance_market` at 13.7:1, with the next theme down at 4.4:1 and no ambiguity in between.

**The candidate promotion path has still never executed.** All 71 rows are `pending` and `promoted_theme_id` is NULL for every row ever written. Action 1 is the first attempt since the tooling was repaired, so next week's review has a genuine test to run rather than a diagnosis to repeat: if `theme_candidates` still shows 0 promotions after Action 1 lands, the failure is in the promotion bookkeeping and not in the `add` operation, since `add` and `promote-candidate` are separate code paths and only the former is exercised here. Note that Action 1 will **not** flip any candidate row to `promoted` — nothing in `_apply_add` writes to `theme_candidates` — so the 12 rows it homes will stay `pending` and keep being re-counted as unhomed until the re-evaluation pass below exists.

**Carried-forward pipeline items.** Candidate extraction never re-evaluates pending rows after a schema edit, which is why seven S-1-disclosure rows sit unmatched against a description that names them almost verbatim, and why Action 1's 12 rows will stay pending; a post-schema-edit re-evaluation pass would drain a large share of the 71 without any further taxonomy change. The `export.py` secondary-attach threshold is flagged for a sixteenth week at 4.75 links per node in mix scope against 2.41 in tech. And per §6.1 the glossary writer prompt should enforce the 25-word and 2-sentence `quick_def` limits at generation time — 50 terms now trip `form/warn` across 67 check dates for 3421 total rows and can never self-clear because `warn` does not flip status — with the 181 empty-`quick_def` `form/fail` terms triaged separately.

```action
{"kind": "log-only"}
```

## Why this rotation

For three weeks the taxonomy could not be changed at all, and every rotation was spent on unblocking. That is over: the locator repair landed, the reader-facing dangling cross-reference cleared from all three locales, and the seed block is clean. So this rotation spends its two schema slots on the thing that has been deferred since 7/19 — creating `tech.ai_infra_private_capital` and pointing the chip-architecture cross-reference back at it.

Action 1 is chosen over any description sharpening because it is the only operation in the vocabulary that is not gated on the English propagation defect: `INSERT OR IGNORE` fires for a new `theme_id`, so unlike a rewrite it reaches the matcher on the next rebuild. Action 2 is chosen because its entire value sits in the three locale columns that do land, which is the only other way to get reader-facing value out of the toolchain this week. On the same reasoning, no business-scope content edit is proposed for a fourth week: the sharpened disclosure description still has not entered the matcher, dominance rose to 72.8% purely on re-measurement, and widening a starved business theme now would confound the only clean before-and-after this taxonomy will get.

Two things this review found by recomputing rather than trusting. The prediction re-key cascade is leaving debris in three tables and grew during this rebuild; it inflates every headline figure by a few points if the obvious query is used, and Action 3 records both the mechanism and the fix. And the single candidate label that appears to clear the §2.1 three-hit bar is one prediction wearing three ids, so the correct count of qualifying clusters by that rule is zero — which is why nothing is promoted on label frequency and Action 1 rests on 12 distinct predictions instead.

Action 4 records that Defect A is now the last blocker and that Defect B's fix is a stopgap nothing enforces, and Action 5 records that both §2.1 thresholds fire degenerately and should be rewritten around primary core and children-to-primary ratio.

## Deferred for next week

- **Confirm Action 1 actually landed, in the database and not just in the file.** Check `SELECT COUNT(*) FROM themes` has moved from 18 to 19 and that `themes.description` for `tech.ai_infra_private_capital` is non-empty. This is the first end-to-end test of `add` this project has ever completed, and it is also the cleanest available test of whether `INSERT OR IGNORE` really does reach English for new rows.
- **Read the first-week draw.** If `tech.ai_infra_private_capital` takes primaries, check whether `tech.ai_macro_capital_markets` shed any — a small shed is the intended boundary working, a large one means the cross-reference language needs tightening.
- **Re-run the locator regex and confirm the seed block still holds exactly one semicolon** after Action 1 appends its row. Any future proposal that reintroduces one silently disables `add` again.
- **Verify EN propagation before reading any number as a trend.** Until `themes.description` matches the `schema.sql` seed for all 18 pre-existing themes, `business.ai_revenue_disclosure` at 156, `business.capital-supply-chain` at 72.8%, `business.cloud_vs_local_distribution` at 1 and `tech.ai_chip_architecture` at 8 are all re-measurements.
- **Sweep the orphaned attachments and re-check the count.** Ten orphan prediction ids today, growing weekly. Every metric in this file joins to `predictions` to exclude them; the next review should confirm the count has gone down rather than up.
- **Dedupe `theme_candidates` by label and re-read the clusters.** 71 rows across 68 labels today. The de-duplicated count is the one §2.1 should be applied to.
- **`business.hyperscaler_frontier_lab_alliance`.** 5 primary, 17.0:1 and worsening. First in the keyword-sharpening queue the moment English reaches the matcher.
- **`business.capital-supply-chain` category carve-out.** Per §2.3 needs its own design discussion. Twelve weeks running. The structural argument does not depend on any fix.
- **§2.1 threshold recalibration.** Rewrite the empty and overpopulated rules against primary core, relative share, and children-to-primary ratio.
- **Autonomous offensive-security agents cluster.** Flat at 3 organic rows for three weeks. If it reaches 5-6, widen `tech.agent_runtime_security` rather than adding a theme.
- **Pipeline-level fixes.** Quote-aware statement scan replacing `[^;]*` in both `_insert_before_themes_seed_terminator()` and `_theme_locale_update_re()`, an English `UPDATE themes SET description` emitter, a sweep of the six superseded `UPDATE themes SET` blocks at `schema.sql:1575-1597`, a lint or test that fails on a semicolon inside the themes seed block, orphan-attachment cleanup in ingest, candidate post-schema-edit re-evaluation, the `export.py` secondary-attach threshold, and the glossary writer-prompt length cap.

---
