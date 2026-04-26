# Export Layer Specification

## 1. Purpose

The export layer converts the local analytics SQLite database into static JSON artifacts consumed by the GitHub Pages dashboard.

The browser does not read SQLite directly.

```text
schema.sql SQLite DB
  → export layer
  → docs/data/manifest.json
  → docs/data/graph-tech.json
  → docs/data/graph-business.json
  → GitHub Pages UI
```

The export layer is the contract between the analytical backend and the static UI.

## 2. Responsibilities

The export layer must:

- Read scopes, categories, themes, subthemes, predictions, evidence, and metrics from SQLite.
- Build scope-specific graph JSON.
- Include metrics for all supported windows:
  - `7d`
  - `30d`
  - `90d`
- Generate stable node IDs.
- Generate taxonomy links.
- Attach layout hints.
- Attach side-panel detail data.
- Record export metadata in `graph_exports`.
- Write static files under `docs/data/`.

The export layer must not:

- Run in the browser.
- Depend on runtime secrets.
- Fetch external URLs during UI load.
- Mutate taxonomy silently.
- Recompute embeddings unless explicitly part of the analytics pipeline before export.

## 3. Input tables

Required tables:

```text
scopes
metric_windows
categories
themes
subthemes
predictions
prediction_scope_assignments
evidence_items
prediction_evidence_links
validation_rows
prediction_realization_snapshots
topic_daily_activity
category_daily_activity
graph_node_layouts
source_files
```

Optional but useful:

```text
theme_candidates
theme_history
theme_mappings
graph_exports
```

## 4. Output files

Recommended output directory:

```text
docs/data/
```

Required files:

```text
manifest.json
graph-tech.json
graph-business.json
```

Optional files:

```text
theme-taxonomy.json
prediction-index.json
evidence-index.json
```

## 5. Date-window support

The dashboard supports:

```text
7d
30d
90d
```

The export layer must include all three window metric bundles in every node.

Do not create separate graph files per window unless performance requires it.

Required graph files:

```text
graph-tech.json
graph-business.json
```

Each node contains:

```json
"metrics_by_window": {
  "7d": {},
  "30d": {},
  "90d": {}
}
```

## 6. Node ID mapping

The export layer must use these stable node IDs:

```text
category node id = categories.category_id
theme node id = themes.theme_id
subtheme node id = subthemes.subtheme_id
prediction node id = predictions.prediction_id
```

Node type must be explicit:

```text
category
theme
subtheme
prediction
```

The UI must never infer node type from the ID string.

## 7. Link generation

Initial taxonomy links:

```text
category → theme
theme → subtheme
subtheme → prediction
```

If a prediction has no subtheme:

```text
theme → prediction
```

Link schema:

```json
{
  "id": "link.<source>__<target>",
  "source": "<source_node_id>",
  "target": "<target_node_id>",
  "type": "contains",
  "weight": 1.0,
  "status": "active"
}
```

Evidence links are initially shown in detail panels, not necessarily as graph nodes.

## 8. Metric mapping

### 8.1 Category node metrics

Source:

```text
category_daily_activity
```

Fallback if missing:

```text
aggregate child theme topic_daily_activity rows
```

Aggregation:

```text
attention_score = max child theme attention_score
realization_score = weighted average by prediction_count, fallback average
contradiction_score = max child theme contradiction_signal
grass_level = grass_level(attention_score)
status = strongest child status by priority
```

Status priority:

```text
mixed
contradicted
new
active
continuing
dormant
```

### 8.2 Theme node metrics

Source:

```text
topic_daily_activity
where activity_level = 'theme'
and subtheme_id is null
```

For each window:

```text
latest row by activity_date
```

### 8.3 Subtheme node metrics

Source:

```text
topic_daily_activity
where activity_level = 'subtheme'
and subtheme_id is not null
```

For each window:

```text
latest row by activity_date
```

### 8.4 Prediction node metrics

Source:

```text
prediction_realization_snapshots
```

For each window:

```text
latest row by validation_date
```

Fallback:

```text
prediction_scope_assignments.latest_realization_score
prediction_scope_assignments.latest_contradiction_score
prediction_scope_assignments.latest_observed_relevance
```

Prediction attention can be derived from linked evidence:

```text
attention_score = max(new_evidence_relevance, continuing_evidence_relevance)
```

If unavailable:

```text
attention_score = realization_score
```

## 9. Window date ranges

The export layer computes window ranges relative to the latest available report date.

Example:

```text
latest_report_date = 2026-04-24

7d:
  start = 2026-04-18
  end = 2026-04-24

30d:
  start = 2026-03-26
  end = 2026-04-24

90d:
  start = 2026-01-25
  end = 2026-04-24
```

The exact implementation can use inclusive dates.

## 10. Manifest generation

`manifest.json` schema:

```json
{
  "schema_version": "1.0",
  "build_id": "2026-04-24T10:00:00Z",
  "latest_report_date": "2026-04-24",
  "default_scope": "tech",
  "default_window": "30d",
  "windows": [
    { "window_id": "7d", "label": "7D", "days": 7 },
    { "window_id": "30d", "label": "30D", "days": 30 },
    { "window_id": "90d", "label": "90D", "days": 90 }
  ],
  "scopes": [
    { "scope_id": "tech", "label": "Tech", "graph_file": "graph-tech.json" },
    { "scope_id": "business", "label": "Business", "graph_file": "graph-business.json" }
  ]
}
```

## 11. Graph JSON generation

For each scope:

```text
scope_id in ('tech', 'business')
```

write:

```text
graph-<scope_id>.json
```

### 11.1 Top-level shape

```json
{
  "schema_version": "1.0",
  "scope_id": "tech",
  "scope_label": "Tech",
  "generated_at": "2026-04-24T10:00:00Z",
  "date_range": {
    "start": "2026-01-25",
    "end": "2026-04-24"
  },
  "windows": {
    "7d": { "start": "2026-04-18", "end": "2026-04-24" },
    "30d": { "start": "2026-03-26", "end": "2026-04-24" },
    "90d": { "start": "2026-01-25", "end": "2026-04-24" }
  },
  "nodes": [],
  "links": [],
  "legend": {
    "heat_metric": "attention_score",
    "warning_metric": "realization_score",
    "warning_threshold": 0.4
  }
}
```

## 12. Node generation rules

### 12.1 Category nodes

For each active category in scope:

```json
{
  "id": "tech.security",
  "type": "category",
  "scope_id": "tech",
  "label": "Security",
  "short_label": "Security",
  "description": "...",
  "category_id": "tech.security",
  "theme_id": null,
  "subtheme_id": null,
  "prediction_id": null,
  "parent_ids": [],
  "child_ids": ["tech.agent_runtime_security"],
  "metrics_by_window": {},
  "visibility": {
    "min_zoom": 0.75,
    "max_zoom": null,
    "default_visible": false
  },
  "layout": {},
  "detail": {}
}
```

### 12.2 Theme nodes

For each active or candidate theme in scope:

```json
{
  "id": "tech.agent_runtime_security",
  "type": "theme",
  "scope_id": "tech",
  "label": "Agent Runtime Security",
  "short_label": "Agent Runtime",
  "description": "...",
  "category_id": "tech.security",
  "theme_id": "tech.agent_runtime_security",
  "subtheme_id": null,
  "prediction_id": null,
  "parent_ids": ["tech.security"],
  "child_ids": [],
  "metrics_by_window": {},
  "visibility": {
    "min_zoom": 0.0,
    "max_zoom": null,
    "default_visible": true
  },
  "layout": {},
  "detail": {}
}
```

### 12.3 Subtheme nodes

For each active/candidate subtheme under exported themes:

```json
{
  "id": "tech.subtheme.indirect_prompt_injection",
  "type": "subtheme",
  "scope_id": "tech",
  "label": "Indirect Prompt Injection",
  "short_label": "Prompt Injection",
  "category_id": "tech.security",
  "theme_id": "tech.agent_runtime_security",
  "subtheme_id": "tech.subtheme.indirect_prompt_injection",
  "prediction_id": null,
  "parent_ids": ["tech.agent_runtime_security"],
  "child_ids": [],
  "metrics_by_window": {},
  "visibility": {
    "min_zoom": 1.25,
    "max_zoom": null,
    "default_visible": false
  },
  "layout": {},
  "detail": {}
}
```

### 12.4 Prediction nodes

For each prediction assignment in scope:

```json
{
  "id": "prediction.<hash-or-id>",
  "type": "prediction",
  "scope_id": "tech",
  "label": "間接プロンプトインジェクションが CVE の主カテゴリ化...",
  "short_label": "Prompt Injection CVE化",
  "description": null,
  "category_id": "tech.security",
  "theme_id": "tech.agent_runtime_security",
  "subtheme_id": "tech.subtheme.indirect_prompt_injection",
  "prediction_id": "prediction.<hash-or-id>",
  "parent_ids": ["tech.subtheme.indirect_prompt_injection"],
  "child_ids": [],
  "metrics_by_window": {},
  "visibility": {
    "min_zoom": 2.0,
    "max_zoom": null,
    "default_visible": false
  },
  "layout": {},
  "detail": {}
}
```

If `subtheme_id` is null:

```text
parent_ids = [theme_id]
```

## 13. Layout export rules

Source:

```text
graph_node_layouts
```

If a layout exists:

```text
use stored x/y/z/radius/fixed
```

If no layout exists:

```text
generate deterministic initial layout
```

Suggested deterministic layout:

```text
category:
  place on outer ring

theme:
  place around parent category

subtheme:
  place around parent theme

prediction:
  place near parent subtheme or theme
```

Determinism matters so graph layout does not jump between exports.

## 14. Detail payload generation

### 14.1 Common detail fields

Every node detail should include:

```json
{
  "title": "...",
  "subtitle": "...",
  "description": "...",
  "scope_id": "tech",
  "node_type": "theme"
}
```

### 14.2 Category details

Include:

```text
child themes
active_theme_count
prediction_count
```

### 14.3 Theme details

Include:

```text
parent category
subthemes
prediction summaries
origin evidence
supporting evidence count
contradicting evidence count
```

### 14.4 Subtheme details

Include:

```text
parent category
parent theme
prediction summaries
supporting evidence
contradicting evidence
```

### 14.5 Prediction details

Include:

```text
full prediction summary
prediction date
source report path
validation report path
parent category
parent theme
parent subtheme
new evidence relevance
continuing evidence relevance
realization score
contradiction score
observation status
supporting evidence links
contradicting evidence links
```

## 15. Evidence export

Prediction node details must include evidence links.

Evidence detail shape:

```json
{
  "evidence_id": "evidence.<hash>",
  "title": "Google Antigravity Prompt Injection → RCE",
  "url": "https://example.com/article",
  "source_name": "CSO Online",
  "source_type": "news",
  "support_direction": "support",
  "relatedness_score": 0.91,
  "evidence_strength": 0.88,
  "validation_date": "2026-04-22",
  "evidence_recency_type": "new"
}
```

## 16. Export algorithm

### 16.1 High-level steps

```text
1. Load manifest metadata:
   - scopes
   - metric windows
   - latest report date

2. For each scope:
   - load categories
   - load active/candidate themes
   - load subthemes
   - load prediction assignments
   - load latest metrics for 7d, 30d, 90d
   - load graph layouts
   - build nodes
   - build links
   - attach detail payloads
   - write graph-<scope>.json

3. Write manifest.json

4. Insert rows into graph_exports
```

### 16.2 Pseudo-code

```python
for scope in ["tech", "business"]:
    graph = Graph(scope)

    categories = load_categories(scope)
    themes = load_themes(scope)
    subthemes = load_subthemes(scope)
    predictions = load_prediction_assignments(scope)

    for category in categories:
        graph.add_category_node(category, metrics=load_category_metrics(category))

    for theme in themes:
        graph.add_theme_node(theme, metrics=load_theme_metrics(theme))

    for subtheme in subthemes:
        graph.add_subtheme_node(subtheme, metrics=load_subtheme_metrics(subtheme))

    for prediction in predictions:
        graph.add_prediction_node(prediction, metrics=load_prediction_metrics(prediction))

    graph.add_taxonomy_links()
    graph.attach_layouts()
    graph.attach_details()
    graph.write(f"docs/data/graph-{scope}.json")
```

## 17. Metric bundle shape

Every node must have this for each window:

```json
{
  "attention_score": 0.0,
  "realization_score": 0.0,
  "contradiction_score": 0.0,
  "grass_level": 0,
  "streak_days": 0,
  "new_signal": 0.0,
  "continuing_signal": 0.0,
  "status": "dormant"
}
```

If a metric is unknown:

```text
score = 0.0
status = no_signal or dormant
```

For category/theme/subtheme nodes:

```text
status values:
new / active / continuing / dormant / contradicted / mixed
```

For prediction nodes:

```text
status values:
supported / weakly_supported / no_signal / mixed / contradicted
```

The UI should render these without assuming a single enum across all node types.

## 18. Validation rules

The export layer should fail or warn if:

- a node has no `metrics_by_window.7d`.
- a node has no `metrics_by_window.30d`.
- a node has no `metrics_by_window.90d`.
- a link references a missing node.
- a theme references a missing category.
- a subtheme references a missing theme.
- a prediction assignment references no theme.
- a prediction node has no parent.
- a layout has invalid numeric values.
- required manifest fields are missing.

## 19. Recording exports

After writing each graph file, insert:

```sql
INSERT INTO graph_exports (
  export_id,
  scope_id,
  window_id,
  output_path,
  schema_version,
  generated_at,
  node_count,
  link_count,
  date_start,
  date_end,
  content_sha
)
VALUES (...);
```

For graph files that contain all windows:

```text
window_id = NULL
```

For optional per-window files:

```text
window_id = '7d' / '30d' / '90d'
```

## 20. Acceptance criteria

The export layer is acceptable when:

- It writes `manifest.json`.
- It writes `graph-tech.json`.
- It writes `graph-business.json`.
- Each graph includes all 7d/30d/90d metric bundles.
- All links reference existing nodes.
- Category/theme/subtheme/prediction nodes use stable IDs.
- Layout hints are present for every node.
- Detail payloads support the right-side panel.
- The UI can switch scope without recomputing data.
- The UI can switch window without fetching a new graph file.
- Export metadata is recorded in `graph_exports`.
