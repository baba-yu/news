# PRD: Future Prediction Theme Intelligence Dashboard

## 1. Purpose

Build a static GitHub Pages dashboard that visualizes future predictions from daily AI/news reports as a scope-aware knowledge graph.

The system tracks:

- Technical trend structure.
- Business trend structure.
- Prediction theme classification.
- Theme generation from leading news.
- Theme continuity over time.
- Whether a predicted theme appears to be materializing.
- Hierarchical drill-down from categories to original prediction summaries.

The dashboard has no backend. All analytics run locally or in CI, and the dashboard consumes static JSON artifacts.

## 2. Input sources

### 2.1 Daily news reports

Path pattern:

```text
report/news-YYYYMMDD.md
```

Expected structure:

```text
# ニュースレポート YYYY-MM-DD

## Headlines
## Future
## News
## Sources
```

The `Future` section contains prediction summaries generated from that day's curated news.

### 2.2 Future prediction validation reports

Path pattern:

```text
future-prediction/future-prediction-YYYYMMDD.md
```

Expected table columns:

```text
Prediction (summary)
Prediction date
Related item(s) in today's report (...)
Relevance
Reference link(s)
```

The existing relevance value is treated as observed/new evidence relevance, not as the entire truth signal.

## 3. Core product model

The product uses this hierarchy:

```text
Scope
  → Category
    → Theme
      → Subtheme
        → Prediction Summary
          → Evidence
```

### 3.1 Scope

A semantic viewpoint.

Initial scopes:

- `tech`
  - Technical mechanisms, models, security, infrastructure, protocols, runtime behavior.
- `business`
  - Market structure, competition, adoption, regulation, distribution, capital allocation.

The same prediction can be assigned in both scopes with different categories and themes.

### 3.2 Category

A stable grouping inside a scope.

Categories are used for navigation and aggregation. They change rarely.

### 3.3 Theme

A human-editable evolving topic.

Themes are the primary unit of visualization and grass-style continuity tracking.

Principle:

```text
Lead news has initial naming authority.
Human editing has final authority.
```

Themes can be:

- System-generated from leading news.
- Promoted from candidate to active.
- Renamed.
- Merged.
- Split.
- Moved.
- Retired.

### 3.4 Subtheme

A finer-grained cluster under a theme.

Subthemes may be automatically generated from prediction/evidence embeddings and later edited.

### 3.5 Prediction Summary

The original prediction text from the `Future` section.

Prediction summaries are immutable leaves in the hierarchy.

### 3.6 Evidence

A news item, URL, or validation item used to support, contradict, or contextualize a prediction.

Evidence may be:

- newly cited in today's report.
- previously cited but still active in memory.
- expired from active memory.

URLs may be excluded from future rendered reports to avoid repetition, but must remain usable as analysis memory.

## 4. Core scores

### 4.1 Attention score

Represents whether a theme is still visible or active.

Used for:

- node heatmap color.
- grass intensity.
- scope/category/theme activity summaries.

Attention is not the same as correctness.

### 4.2 Realization score

Represents whether the prediction appears to be materializing.

Used for:

- prediction status.
- warning marks on low-realization nodes.
- theme-level realization summaries.

### 4.3 Contradiction score

Represents evidence against the prediction or theme.

Examples:

- Prediction says headless architectures become standard.
- Evidence shows GUI-centric workflows expanding.
- Contradiction score increases.

### 4.4 New evidence signal

Represents newly observed support in the selected date window.

### 4.5 Continuing evidence signal

Represents decayed support from prior evidence that remains active.

## 5. Date windows

The dashboard supports three date windows:

```text
7d
30d
90d
```

The selected window affects:

- node attention score.
- node realization score.
- grass strip shown in the right-side panel.
- graph heatmap intensity.
- category/theme/subtheme aggregation.
- scope overview metrics.

The square menu in the top-right must contain both:

```text
scope tabs: TECH / BIZ
window buttons: 7D / 30D / 90D
```

Default:

```text
scope = tech
window = 30d
```

## 6. Scoring model

### 6.1 Evidence decay

For continuing evidence:

```text
decay(age_days) = exp(-age_days / tau)
```

Recommended defaults:

```text
release/model/news item: 14d
security/CVE/compliance: 30d
business alliance/capex/platform shift: 60d
short-lived event: 7d
```

### 6.2 New signal

```text
new_signal = max(
  relatedness_score * evidence_strength
  for new supporting evidence in selected window
)
```

### 6.3 Continuing signal

```text
continuing_signal = max(
  relatedness_score * evidence_strength * decay(age_days)
  for active prior supporting evidence in selected window
)
```

### 6.4 Attention score

```text
attention_score = min(1.0, new_signal + 0.5 * continuing_signal)
```

### 6.5 Realization score

```text
realization_score =
  0.65 * new_evidence_relevance
  + 0.35 * continuing_evidence_relevance
  - 0.50 * contradiction_score
```

Clamp to:

```text
0.0 <= realization_score <= 1.0
```

### 6.6 Grass level

```text
0: attention_score <= 0.05
1: attention_score <= 0.25
2: attention_score <= 0.50
3: attention_score <= 0.75
4: attention_score >  0.75
```

### 6.7 Theme status

Allowed values:

```text
new
active
continuing
dormant
contradicted
mixed
```

Suggested logic:

```python
if contradiction_signal >= 0.6 and max(new_signal, continuing_signal) >= 0.4:
    status = "mixed"
elif contradiction_signal >= 0.6:
    status = "contradicted"
elif first_seen_date == date and new_signal >= 0.5:
    status = "new"
elif new_signal >= 0.5 and continuing_signal >= 0.4:
    status = "active"
elif continuing_signal >= 0.4:
    status = "continuing"
else:
    status = "dormant"
```

### 6.8 Prediction observation status

Allowed values:

```text
supported
weakly_supported
no_signal
mixed
contradicted
```

Suggested logic:

```text
supported:
  realization_score >= 0.70 and contradiction_score < 0.40

weakly_supported:
  realization_score >= 0.40 and contradiction_score < 0.50

mixed:
  realization_score >= 0.40 and contradiction_score >= 0.40

contradicted:
  contradiction_score >= 0.60 and realization_score < 0.40

no_signal:
  otherwise
```

## 7. Required UI

### 7.1 Knowledge graph

The main UI is an interactive knowledge graph.

Progressive reveal:

```text
low zoom:
  themes only

medium zoom:
  categories + themes

higher zoom:
  categories + themes + subthemes

highest zoom / focused:
  prediction summaries
```

### 7.2 Heatmap nodes

Node heat encodes:

```text
attention_score for selected window
```

Low realization nodes show:

```text
!
```

at the center.

Threshold:

```text
realization_score < 0.40
```

Very low realization:

```text
realization_score < 0.25
```

should use stronger warning styling.

### 7.3 Right-side detail panel

Clicking any node opens a shared slide-in panel from the right.

All node panels show:

- title.
- node type.
- scope.
- selected window.
- continuing attention score.
- realization score.
- contradiction score.
- status.

Contextual display:

Category node:

- child themes.

Theme node:

- parent category.
- subthemes.
- prediction summaries.

Subtheme node:

- parent category.
- parent theme.
- prediction summaries.

Prediction node:

- parent category.
- parent theme.
- parent subtheme.
- source report.
- validation report.
- evidence links.

### 7.4 Top-right square menu

The top-right menu is always visible.

It contains two groups:

```text
[ TECH ][ BIZ  ]

[ 7D ][ 30D ][ 90D ]
```

Behavior:

- Switching scope loads the corresponding graph JSON.
- Switching window changes the active metric bundle inside the current graph JSON.
- The graph should smoothly update node heat and labels without a full page reload.
- If selected node exists in the new scope/window, keep it selected.
- Otherwise close or reset the detail panel.

## 8. Data artifacts

The dashboard consumes:

```text
docs/data/manifest.json
docs/data/graph-tech.json
docs/data/graph-business.json
```

Each graph file must contain metrics for all windows:

```text
7d
30d
90d
```

The frontend must not compute analytics from raw markdown.

## 9. Human editing

Human edits happen outside the dashboard at first.

Supported operations:

- rename theme.
- promote candidate theme.
- merge themes.
- split theme.
- move theme.
- retire theme.
- update theme description.
- update anchor keywords/examples.

All edits must be recorded in history tables and reflected in generated JSON.

## 10. Initial taxonomy

### 10.1 Tech categories

```yaml
tech:
  models:
    description: "Model architecture, training, quantization, open weights, model releases."
  agents:
    description: "Agent frameworks, registries, tools, workflows, runtime behavior."
  security:
    description: "Prompt injection, CVEs, sandbox escape, RCE, secrets, supply-chain attacks."
  inference-runtime:
    description: "Local inference, serving stacks, llama.cpp, vLLM, SGLang, Ollama, MLX, GGUF."
  infrastructure:
    description: "GPU, TPU, Trainium, data centers, cloud training and inference systems."
  standards:
    description: "MCP, registries, schemas, governance protocols, interoperability."
```

### 10.2 Business categories

```yaml
business:
  market-structure:
    description: "Industry structure, platform consolidation, hyperscaler/frontier lab alignment."
  distribution:
    description: "Cloud versus local, hosted versus open-weight, edge deployment, channel shifts."
  competition:
    description: "Vendor competition, model differentiation, proprietary versus open ecosystems."
  enterprise-adoption:
    description: "Enterprise usage, procurement, workflow integration, developer tooling."
  regulation-compliance:
    description: "CVE/CVSS/OWASP, AI regulation, auditability, legal and compliance pressure."
  capital-supply-chain:
    description: "Compute capex, chip supply, data center commitments, cloud capacity strategy."
```

## 11. Acceptance criteria

The product is acceptable when:

- The dashboard runs on GitHub Pages with no backend.
- Local/CI processing emits static JSON.
- UI can switch `tech` / `business`.
- UI can switch `7d` / `30d` / `90d`.
- Nodes use attention heatmap for selected window.
- Low-realization nodes show `!`.
- The graph progressively reveals hierarchy by zoom.
- Clicking a node opens the right-side panel.
- Prediction summaries are reachable as leaf nodes.
- Evidence links are visible for prediction nodes.
- Theme edit history is preserved in the DB.
- Static JSON is fully derivable from the SQLite schema via the export layer.
