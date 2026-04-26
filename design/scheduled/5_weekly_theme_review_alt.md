# Direction

Sunday-only job. Diagnostic + advisory. Reads the current state of the taxonomy and emits a markdown proposal for the human to act on. **Does not** edit `app/src/schema.sql`.

Pre-condition: `app/update_pages.bat` has run at least once for today (or today's data is already up to date in `docs/data/graph-*.json` and `app/data/analytics.sqlite`).

## Why this exists, and the principle the spec rests on

Themes and categories are hardcoded in `app/src/schema.sql`. The matcher (IDF token overlap) is best-1, so some themes can drift toward empty (no predictions match) while others absorb too much. Both shapes degrade the dashboard. The weekly review surfaces the drift early and proposes edits.

The taxonomy in `schema.sql` is treated as a **current-time view**, not a historical record. Themes can be renamed, merged, split, or deleted freely — no `status='retired'` flag, no alias table, no rename log. This is safe because every metric (`attention_score`, `realization_score`, `grass_level`, `prediction_count`, etc.) is **fully recomputed** by `update_pages.bat` against the current schema. The underlying predictions and evidence are immutable; their attachments to themes are recomputed each rebuild.

So if "Edge LLM" is renamed to "Local LLM", next week's "Local LLM" trends exactly the way "Edge LLM" was trending. If "Edge LLM" is merged into "Models", "Models" picks up Edge LLM's predictions and reflects their combined activity. An old theme name that no longer matches anything becomes a row with zero attachments — invisible on the dashboard, no cleanup required. The job's role is therefore diagnostic + advisory only; it never preserves state across renames because there is no state to preserve.

---

## Step 1. Inputs

Read these only:

- `docs/data/graph-tech.json`, `docs/data/graph-business.json`, `docs/data/graph-mix.json` — current node + child counts + per-window metrics.
- `app/data/analytics.sqlite` — read-only query into `theme_candidates` (status='pending'). Use `sqlite3` CLI or short python; do not modify rows.
- `app/src/schema.sql` — for the current taxonomy listing (theme labels, descriptions, category mappings).

Don't scan history. Today's snapshot is sufficient.

---

## Step 2. Find pain points

For each scope (`tech`, `business`, `mix`):

### 2.1 Empty / underused themes

A theme node where `len(child_ids) == 0` is **empty** — no predictions matched.

A theme where `len(child_ids) == 1` is **underused** — only one match, often a weak/forced fit. Worth flagging for description rewrite or merge.

For each, propose one of:
- **Deprecate (delete from schema.sql)** if the topic is genuinely dead.
- **Rewrite description / keywords** in `schema.sql` if the topic is alive but the matcher isn't catching it.
- **Merge** into a sibling theme if the boundary with the sibling is unclear.

### 2.2 Overpopulated themes

A theme where `len(child_ids) >= 6` is **a candidate for split**. The threshold is heuristic — also weight by whether the children visibly span multiple sub-topics.

Procedure:
- For each theme with `child_ids >= 6`, list each child prediction's `short_label` from the graph JSON.
- If the children cluster into 2-3 visibly distinct sub-topics, propose a split with suggested theme names + which children would move where.
- If the children are all on-topic for a single concept, leave it. Overpopulation is fine when the theme is genuinely the right granularity.

### 2.3 Theme candidates

Query `theme_candidates` table:

```sql
SELECT scope_id, suggested_theme_label, suggested_short_label, suggested_description,
       COUNT(*) AS hits, AVG(novelty_score) AS avg_novelty
FROM theme_candidates
WHERE status = 'pending'
GROUP BY scope_id, suggested_theme_label
HAVING hits >= 3
ORDER BY hits DESC, avg_novelty DESC;
```

For each row returned (≥ 3 hits around the same suggested label), propose a new theme: name, description draft, suggested category, list of contributing predictions/evidence.

Below the 3-hit threshold, ignore (single-mention candidates are noise).

### 2.4 Category review (lightweight)

Categories are 12 fixed by spec; rare to change. Only flag if:

- A category has zero theme children for ≥ 2 consecutive weekly reviews (suggest delete or repurpose).
- A category absorbs ≥ 50% of all predictions in its scope (suggest a new sibling category).

Otherwise category-level is silent in the proposal.

---

## Step 3. Write the proposal

Filename: `memory/theme-review/theme-review-YYYYMMDD.md`.

Format:

```markdown
# Theme review — YYYY-MM-DD

Source data: docs/data/graph-{tech,business,mix}.json + theme_candidates (pending).
Total themes: tech=N1, business=N2, mix=N3.

## Empty / underused themes

### tech
- **`Local Inference Runtime`** — 1 child (`tech.foo_bar`).
  - Suggested: rewrite description with keywords {ollama, llama.cpp, vllm, foundry-local} OR merge into `AI Chip Architecture` if the boundary is hardware-runtime.

### business
(none)

### mix
- (rolls up tech + business; mention only mix-specific findings here)

## Overpopulated themes

### tech
- **`Agent Control Plane`** — 10 children. Children list:
  - tech.agent_control_plane.foo
  - tech.agent_control_plane.bar
  - ...
  - Suggested split: `Agent Identity & Auth` (5 children: foo, bar, ...) + `Agent Runtime Orchestration` (5 children: baz, qux, ...). OR leave as-is if visibly one concept.

### business
- **`Cloud vs Local AI Distribution`** — 9 children. ...

## Theme candidates (≥ 3 pending hits)

| scope | suggested label | hits | avg novelty | proposed category | sample evidence |
|---|---|---|---|---|---|
| tech | "Inference SKU separation" | 4 | 0.71 | tech.ai_chip_architecture | ev_001, ev_017, ... |

## Category-level notes

(usually empty — only populated if §2.4 thresholds tripped)

## Recommended actions

1. (highest-impact suggestion first, e.g. "Split `Cloud vs Local AI Distribution` — 9 children clearly span SaaS pricing and local-runtime adoption")
2. ...
3. ...

(keep ≤ 5 to maintain focus; lower-priority items are still in the body of the report above)
```

Use the actual children counts and labels from today's graph JSON. **Do not invent splits**: only propose a split when the children genuinely group. If unsure, say "leave as-is, revisit next week."

---

## Step 4. Commit the proposal

```
git add memory/theme-review/theme-review-YYYYMMDD.md
git commit -m "Theme review YYYYMMDD (proposal)"
```

This commits only the proposal so the human has a stable artifact to review against. Schema changes and refreshed dashboards get committed in Step 7 once the human has acted.

---

## Step 5 (human turn). Review proposal, edit `app/src/schema.sql`

The human reads the proposal at `memory/theme-review/theme-review-YYYYMMDD.md` and chooses which suggestions to act on. Direct edits to `app/src/schema.sql`:

- **Rename**: change `theme_id`, `label`, `short_label`, `description` in place. Pick descriptions/keywords that the IDF matcher will actually match against in `report/news-*.md`.
- **Merge**: keep the surviving theme's row, delete the absorbed one(s). The matcher will reattach absorbed predictions to the survivor on the next rebuild.
- **Split**: change the existing theme row to one of the new sub-topics; add a new theme row for the other(s).
- **Delete**: remove the row entirely. Old attachments orphan harmlessly (zero attention, invisible on dashboard).
- **Add (from candidate)**: insert a new theme row with the suggested `theme_id`, `label`, `short_label`, `description`, and the proposed `category_id`.

If a candidate from §2.3 is being promoted or rejected, also update `theme_candidates` in `app/data/analytics.sqlite` so the same suggestions don't keep reappearing next week:

```sql
-- promoted
UPDATE theme_candidates
SET status='promoted', promoted_theme_id='<new theme id>'
WHERE candidate_id='<candidate id>';

-- rejected (decided not to promote)
UPDATE theme_candidates
SET status='rejected'
WHERE candidate_id='<candidate id>';
```

This is a manual SQL update for now.

---

## Step 6. Apply the schema change — run `app/update_pages.bat`

Run `app/update_pages.bat`. It rebuilds `app/data/analytics.sqlite` from the new `schema.sql` and regenerates `docs/data/graph-{tech,business,mix}.json`. The dashboard updates accordingly. The matcher re-attaches all predictions/evidence to the current taxonomy automatically — no migration step.

If it fails, follow the same fallback rules as the daily flow:

- Read the error output and identify the cause (parser error / sqlite locked / git push rejected / etc.).
- For parser/schema errors, fix `app/src/` and re-run.
- For sqlite locked, delete `app/data/analytics.sqlite` and re-run (DB rebuild).
- Confirm `cd app && python -m pytest -q` passes 21/21.

If still failing, paste the work log and abort.

---

## Step 7. Commit the refreshed dashboards + push

`app/src/schema.sql` and `app/data/analytics.sqlite` are gitignored — only the published artifacts under `docs/` get committed. Stage the refreshed graph JSON:

```
git add docs/data/
git commit -m "Schema refresh YYYYMMDD: <one-line description of the change>"
git push
```

If multiple proposals were applied in one cycle, fold them into a single descriptive commit message ("Split AI Security Compliance Market; rename Edge LLM → Local LLM").

---

## Inputs / outputs summary

| | Files | Notes |
|---|---|---|
| Read | 3 `docs/data/graph-{tech,business,mix}.json` | current snapshot before the schema change |
| Read | `app/data/analytics.sqlite` (theme_candidates only) | one query |
| Read | `app/src/schema.sql` | for label/description reference |
| Write | 1 `memory/theme-review/theme-review-YYYYMMDD.md` | proposal (Step 3) |
| Edit (human) | `app/src/schema.sql` | Step 5 |
| Edit (human) | `app/data/analytics.sqlite` (theme_candidates only) | Step 5 |
| Refresh (via .bat) | `app/data/analytics.sqlite`, 3 `docs/data/graph-*.json` | Step 6 |

Constant-cost regardless of project history.

---

## Failure modes

- **graph-*.json missing or empty at Step 1** → likely `update_pages.bat` failed earlier today. Note this at the top of the proposal and proceed with whatever JSON does exist; skip missing scopes.
- **theme_candidates query fails** → database may be locked or the table may not exist on a fresh DB. Proceed with the empty-candidates path; note at the top of the proposal.
- **No pain points found** → still emit the file with all sections empty (or "None this week"), so the human knows the job ran. Steps 5-7 then have nothing to do; skip and exit.
- **`update_pages.bat` fails at Step 6** → see Step 6 fallback. The proposal commit from Step 4 stays as-is; no schema change has been applied yet, so the repo is consistent.
- **`.git/index.lock` が EPERM で消せない sandbox 状態** (lock that's invisible to `ls`/`find`/Read but visible to `git`/`stat`, and `unlink` returns EPERM even when uid matches) → Step 4 (proposal commit) または Step 7 (refreshed dashboards commit) で発生したら、その commit を諦めてアーティファクトの書き出しまでで完了とみなす。`memory/theme-review/theme-review-YYYYMMDD.md` および `docs/data/` の差分は disk に残り、翌日のホスト側 daily commit/push job が `git add -A` で拾う。Step を fail させない。

---

## Heuristic thresholds — tunable

| H