# UI Specification: Future Prediction Knowledge Graph Dashboard

## 1. Overview

The dashboard is a static GitHub Pages application for exploring prediction themes as a knowledge graph.

No backend exists at runtime.

All analytics, scoring, clustering, theme generation, and graph export are performed locally or in CI. The UI only loads static JSON files.

```text
SQLite analytics DB
  → export layer
  → docs/data/*.json
  → GitHub Pages UI
```

## 2. Primary UI concept

The main interface is a scrollable, zoomable knowledge graph.

At low zoom, only themes are visible.

As the user zooms in, the graph reveals:

```text
Category
  → Theme
    → Subtheme
      → Prediction Summary
```

The graph is scope-aware:

- `tech`
- `business`

The graph is window-aware:

- `7d`
- `30d`
- `90d`

## 3. Static deployment

The dashboard must run on GitHub Pages.

Requirements:

- no backend.
- no runtime secrets.
- no API calls to private services.
- no client-side embedding or clustering.
- all graph data loaded from static JSON.
- all metrics precomputed by local/CI export layer.

Recommended layout:

```text
docs/
  index.html
  assets/
    app.js
    styles.css
  data/
    manifest.json
    graph-tech.json
    graph-business.json
```

## 4. Top-right square menu

The top-right menu is always visible and fixed.

It contains two groups:

```text
┌──────┬──────┐
│ TECH │ BIZ  │
└──────┴──────┘

┌────┬─────┬─────┐
│ 7D │ 30D │ 90D │
└────┴─────┴─────┘
```

### 4.1 Scope tabs

Allowed values:

```text
tech
business
```

Behavior:

- `TECH` loads or activates `graph-tech.json`.
- `BIZ` loads or activates `graph-business.json`.
- If selected node exists in the new scope, keep the side panel open.
- Otherwise close the panel.

### 4.2 Window buttons

Allowed values:

```text
7d
30d
90d
```

Behavior:

- Updates heatmap intensity from `node.metrics_by_window[window_id]`.
- Updates warning mark from `realization_score` in selected window.
- Updates side panel metrics.
- Updates grass strip range.
- Does not require fetching a different graph file.

Default:

```text
scope = tech
window = 30d
```

## 5. Graph JSON contract

The UI consumes:

```text
manifest.json
graph-tech.json
graph-business.json
```

Each graph file contains all supported windows.

### 5.1 Manifest

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

### 5.2 Graph file

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

### 5.3 Node schema

```json
{
  "id": "tech.agent_runtime_security",
  "type": "theme",
  "scope_id": "tech",

  "label": "Agent Runtime Security",
  "short_label": "Agent Runtime",
  "description": "Prompt injection, sandbox escape, tool misuse, RCE, CVE/CVSS issues in AI agent runtimes.",

  "category_id": "tech.security",
  "theme_id": "tech.agent_runtime_security",
  "subtheme_id": null,
  "prediction_id": null,

  "parent_ids": ["tech.security"],
  "child_ids": ["tech.subtheme.indirect_prompt_injection"],

  "metrics_by_window": {
    "7d": {
      "attention_score": 0.91,
      "realization_score": 0.78,
      "contradiction_score": 0.08,
      "grass_level": 4,
      "streak_days": 4,
      "new_signal": 0.70,
      "continuing_signal": 0.42,
      "status": "active"
    },
    "30d": {
      "attention_score": 0.84,
      "realization_score": 0.75,
      "contradiction_score": 0.12,
      "grass_level": 4,
      "streak_days": 9,
      "new_signal": 0.61,
      "continuing_signal": 0.46,
      "status": "active"
    },
    "90d": {
      "attention_score": 0.72,
      "realization_score": 0.69,
      "contradiction_score": 0.15,
      "grass_level": 3,
      "streak_days": 9,
      "new_signal": 0.50,
      "continuing_signal": 0.44,
      "status": "continuing"
    }
  },

  "visibility": {
    "min_zoom": 0.0,
    "max_zoom": null,
    "default_visible": true
  },

  "layout": {
    "x": 120,
    "y": -80,
    "z": 0,
    "radius": 24,
    "fixed": false
  },

  "detail": {
    "title": "Agent Runtime Security",
    "subtitle": "Theme · Tech / Security"
  }
}
```

### 5.4 Link schema

```json
{
  "id": "link.tech.security__tech.agent_runtime_security",
  "source": "tech.security",
  "target": "tech.agent_runtime_security",
  "type": "contains",
  "weight": 1.0,
  "status": "active"
}
```

Allowed initial types:

```text
contains
supports
contradicts
related
derived_from
```

## 6. Node ID rules

The UI uses stable IDs generated by the export layer.

```text
category node id = categories.category_id
theme node id = themes.theme_id
subtheme node id = subthemes.subtheme_id
prediction node id = predictions.prediction_id
```

Node type is explicit and must not be inferred from the ID string.

## 7. Progressive reveal

### 7.1 Zoom thresholds

Recommended:

```text
zoom < 0.75:
  show themes only

0.75 <= zoom < 1.25:
  show categories + themes

1.25 <= zoom < 2.00:
  show categories + themes + subthemes

zoom >= 2.00:
  show categories + themes + subthemes + predictions
```

### 7.2 Focus mode

When a node is clicked:

- keep selected node fully opaque.
- show immediate parents.
- show immediate children.
- fade unrelated nodes.
- keep side panel open.

## 8. Visual design

### 8.1 Background

Cold low-temperature palette.

Recommended CSS variables:

```css
--bg-0: #07111f;
--bg-1: #0b1728;
--bg-2: #10233a;
--grid-line: rgba(130, 170, 210, 0.08);
--text-main: #d8e7f7;
--text-muted: #8fa8c2;
```

Recommended background:

```css
background:
  radial-gradient(circle at 40% 35%, rgba(40, 80, 120, 0.22), transparent 42%),
  linear-gradient(180deg, #07111f 0%, #0b1728 55%, #08111d 100%);
```

### 8.2 Heatmap

Heat encodes attention score for the selected window.

Color stops:

```css
--heat-0: #203047;
--heat-1: #2464a8;
--heat-2: #18c7d8;
--heat-3: #ffb84d;
--heat-4: #ff4d2e;
--heat-core: #fff3c4;
```

### 8.3 Warning mark

If:

```text
realization_score < 0.40
```

render:

```text
!
```

at the center of the node.

If:

```text
realization_score < 0.25
```

also render a pulsing outline.

If:

```text
contradiction_score >= 0.60
```

render an additional contradiction style, such as a purple/red ring or diagonal slash.

### 8.4 Labels

Labels appear directly below nodes.

Rules:

- centered below the node.
- visible for categories/themes at medium zoom.
- visible for subthemes at high zoom.
- visible for predictions only at highest zoom or focus mode.
- prediction labels are truncated.
- full text appears in the side panel.

Suggested radii:

```text
category: 28
theme: 24
subtheme: 16
prediction: 9
```

## 9. Graph interactions

### 9.1 Node drag

Nodes can be dragged.

Behavior:

- pointer down fixes the node.
- pointer move drags the node.
- pointer up releases the node.
- released node keeps some velocity.
- elastic relaxation pulls it slightly back toward graph equilibrium.

### 9.2 Empty-space drag rotation

Dragging graph background rotates the graph plane.

Axis lock:

```text
horizontal drag → rotate around y-axis
vertical drag → rotate around x-axis
diagonal drag → combine x/y rotation
```

Pseudo-code:

```js
const dx = current.x - start.x;
const dy = current.y - start.y;

if (!axisLocked && Math.hypot(dx, dy) > 8) {
  axisLocked = Math.abs(dx) > Math.abs(dy) ? "y" : "x";
}

if (axisLocked === "y") {
  rotationY += dx * 0.005;
} else {
  rotationX += dy * 0.005;
}
```

### 9.3 Zoom and pan

```text
wheel:
  zoom

node drag:
  move node

empty-space drag:
  rotate

shift + empty-space drag:
  pan

space + drag:
  pan
```

## 10. Right-side detail panel

Clicking any node opens a slide-in panel from the right.

Panel behavior:

- opens over the graph.
- closes with Escape.
- closes with close button.
- updates when another node is clicked.
- displays selected window metrics.

### 10.1 Common fields

All node panels show:

- title.
- node type.
- scope.
- selected window.
- attention score.
- realization score.
- contradiction score.
- grass level.
- status.
- description.
- mini grass strip.

### 10.2 Category panel

Show:

- child themes.
- latest window metrics.
- average realization.
- active theme count.

### 10.3 Theme panel

Show:

- parent category.
- subthemes.
- prediction summaries.
- origin evidence if available.
- supporting / contradicting evidence summary.

### 10.4 Subtheme panel

Show:

- parent category.
- parent theme.
- prediction summaries.
- supporting and contradicting evidence links.

### 10.5 Prediction panel

Show:

- full prediction summary.
- prediction date.
- parent category.
- parent theme.
- parent subtheme.
- source report path.
- validation report path.
- new evidence relevance.
- continuing evidence relevance.
- realization score.
- contradiction score.
- observation status.
- evidence links.

## 11. Frontend state

```ts
type DashboardState = {
  scopeId: "tech" | "business";
  windowId: "7d" | "30d" | "90d";
  selectedNodeId: string | null;
  focusedNodeId: string | null;
  zoom: number;
  pan: { x: number; y: number };
  rotation: { x: number; y: number };
  showLabels: boolean;
  showPredictions: boolean;
};
```

## 12. Recommended implementation stack

Recommended first version:

```text
HTML
CSS
TypeScript or plain JavaScript
D3-force
Canvas rendering
HTML labels and side panel
```

No backend framework is required.

## 13. Acceptance criteria

The UI is acceptable when:

- It runs on GitHub Pages.
- It loads `manifest.json`.
- It loads `graph-tech.json` and `graph-business.json`.
- Top-right square menu switches scope.
- Top-right square menu switches 7d/30d/90d window.
- Node heat updates when window changes.
- Warning marks update when window changes.
- Initial graph shows themes.
- Zoom reveals categories, subthemes, and prediction summaries.
- Nodes are draggable.
- Released nodes have elastic relaxation.
- Empty-space drag rotates graph plane.
- Clicking a node opens right slide-in detail panel.
- Panel content changes by node type.
- Prediction summary leaves show evidence links.
