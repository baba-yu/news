-- Future Prediction Theme Intelligence Schema
-- SQLite-compatible.
-- This schema backs a local/CI analytics pipeline.
-- The GitHub Pages UI consumes exported JSON, not this database directly.

PRAGMA foreign_keys = ON;

-- ============================================================
-- 1. Source files
-- ============================================================

CREATE TABLE IF NOT EXISTS source_files (
  source_file_id TEXT PRIMARY KEY,
  path TEXT NOT NULL UNIQUE,
  file_type TEXT NOT NULL CHECK (file_type IN ('daily_report', 'future_prediction_report', 'other')),
  report_date TEXT,
  content_sha TEXT,
  parsed_at TEXT,
  locale TEXT NOT NULL DEFAULT 'en' CHECK (locale IN ('en', 'ja', 'es', 'fil')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_source_files_report_date
ON source_files(report_date);

-- ============================================================
-- 2. Scopes, windows, and categories
-- ============================================================

CREATE TABLE IF NOT EXISTS scopes (
  scope_id TEXT PRIMARY KEY,
  label TEXT NOT NULL,
  description TEXT,
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT
);

CREATE TABLE IF NOT EXISTS metric_windows (
  window_id TEXT PRIMARY KEY CHECK (window_id IN ('7d', '30d', '90d')),
  label TEXT NOT NULL,
  days INTEGER NOT NULL CHECK (days IN (7, 30, 90)),
  sort_order INTEGER NOT NULL,
  is_default INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS categories (
  category_id TEXT PRIMARY KEY,
  scope_id TEXT NOT NULL,
  label TEXT NOT NULL,
  short_label TEXT,
  description TEXT,
  -- Locale columns: NULL means "fall back to the canonical English value".
  label_ja TEXT,
  label_es TEXT,
  label_fil TEXT,
  short_label_ja TEXT,
  short_label_es TEXT,
  short_label_fil TEXT,
  description_ja TEXT,
  description_es TEXT,
  description_fil TEXT,
  sort_order INTEGER DEFAULT 0,
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT,
  FOREIGN KEY (scope_id) REFERENCES scopes(scope_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_categories_scope_label
ON categories(scope_id, label);

-- ============================================================
-- 3. Evidence items
-- ============================================================

CREATE TABLE IF NOT EXISTS evidence_items (
  evidence_id TEXT PRIMARY KEY,
  url TEXT,
  canonical_url TEXT,
  title TEXT,
  -- Localized titles. URL stays canonical (whatever the source serves).
  title_ja TEXT,
  title_es TEXT,
  title_fil TEXT,
  summary TEXT,

  source_name TEXT,
  source_type TEXT CHECK (
    source_type IN (
      'official',
      'vendor_blog',
      'github',
      'security_advisory',
      'news',
      'analysis',
      'social',
      'paper',
      'unknown'
    )
  ) DEFAULT 'unknown',

  first_seen_date TEXT,
  last_seen_date TEXT,

  memory_status TEXT NOT NULL DEFAULT 'cited_today'
    CHECK (memory_status IN ('cited_today', 'active_memory', 'expired_memory')),

  active_until TEXT,

  source_file_id TEXT,
  raw_markdown TEXT,
  raw_json TEXT,

  embedding_model TEXT,
  embedding_version TEXT,
  embedding_json TEXT,

  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT,

  FOREIGN KEY (source_file_id) REFERENCES source_files(source_file_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_evidence_canonical_url_unique
ON evidence_items(canonical_url)
WHERE canonical_url IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_evidence_first_seen
ON evidence_items(first_seen_date);

CREATE INDEX IF NOT EXISTS idx_evidence_memory_status
ON evidence_items(memory_status, active_until);

-- ============================================================
-- 4. Themes and subthemes
-- ============================================================

CREATE TABLE IF NOT EXISTS themes (
  theme_id TEXT PRIMARY KEY,
  scope_id TEXT NOT NULL,
  category_id TEXT NOT NULL,

  canonical_label TEXT NOT NULL,
  short_label TEXT,
  generated_label TEXT,
  description TEXT,

  -- Locale columns. NULL = fall back to the canonical English value.
  label_ja TEXT,
  label_es TEXT,
  label_fil TEXT,
  short_label_ja TEXT,
  short_label_es TEXT,
  short_label_fil TEXT,
  description_ja TEXT,
  description_es TEXT,
  description_fil TEXT,

  origin_evidence_id TEXT,

  status TEXT NOT NULL DEFAULT 'candidate'
    CHECK (status IN ('candidate', 'active', 'merged', 'retired')),

  merged_into_theme_id TEXT,

  centroid_json TEXT,
  anchor_keywords_json TEXT,
  anchor_examples_json TEXT,

  first_seen_date TEXT,
  last_seen_date TEXT,

  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT,

  FOREIGN KEY (scope_id) REFERENCES scopes(scope_id),
  FOREIGN KEY (category_id) REFERENCES categories(category_id),
  FOREIGN KEY (origin_evidence_id) REFERENCES evidence_items(evidence_id),
  FOREIGN KEY (merged_into_theme_id) REFERENCES themes(theme_id)
);

CREATE INDEX IF NOT EXISTS idx_themes_scope_category
ON themes(scope_id, category_id);

CREATE INDEX IF NOT EXISTS idx_themes_status
ON themes(status);

CREATE TABLE IF NOT EXISTS subthemes (
  subtheme_id TEXT PRIMARY KEY,
  theme_id TEXT NOT NULL,
  canonical_label TEXT NOT NULL,
  short_label TEXT,
  generated_label TEXT,
  description TEXT,
  -- Locale columns. NULL = fall back to canonical English.
  label_ja TEXT,
  label_es TEXT,
  label_fil TEXT,
  short_label_ja TEXT,
  short_label_es TEXT,
  short_label_fil TEXT,
  description_ja TEXT,
  description_es TEXT,
  description_fil TEXT,
  status TEXT NOT NULL DEFAULT 'candidate'
    CHECK (status IN ('candidate', 'active', 'merged', 'retired')),
  merged_into_subtheme_id TEXT,
  centroid_json TEXT,
  first_seen_date TEXT,
  last_seen_date TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT,
  FOREIGN KEY (theme_id) REFERENCES themes(theme_id),
  FOREIGN KEY (merged_into_subtheme_id) REFERENCES subthemes(subtheme_id)
);

CREATE INDEX IF NOT EXISTS idx_subthemes_theme
ON subthemes(theme_id);

-- ============================================================
-- 5. Theme history and mappings
-- ============================================================

CREATE TABLE IF NOT EXISTS theme_history (
  theme_history_id TEXT PRIMARY KEY,
  theme_id TEXT NOT NULL,

  operation TEXT NOT NULL CHECK (
    operation IN (
      'create',
      'rename',
      'merge',
      'split',
      'move',
      'promote',
      'retire',
      'reactivate',
      'description_update',
      'anchor_update'
    )
  ),

  old_value_json TEXT,
  new_value_json TEXT,
  effective_date TEXT NOT NULL,
  note TEXT,

  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (theme_id) REFERENCES themes(theme_id)
);

CREATE INDEX IF NOT EXISTS idx_theme_history_theme_date
ON theme_history(theme_id, effective_date);

CREATE TABLE IF NOT EXISTS theme_mappings (
  mapping_id TEXT PRIMARY KEY,
  scope_id TEXT NOT NULL,
  old_theme_id TEXT NOT NULL,
  new_theme_id TEXT NOT NULL,

  mapping_type TEXT NOT NULL CHECK (
    mapping_type IN ('same', 'rename', 'merge', 'split', 'move', 'deprecated')
  ),

  effective_date TEXT NOT NULL,
  similarity REAL,

  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (scope_id) REFERENCES scopes(scope_id),
  FOREIGN KEY (old_theme_id) REFERENCES themes(theme_id),
  FOREIGN KEY (new_theme_id) REFERENCES themes(theme_id)
);

CREATE INDEX IF NOT EXISTS idx_theme_mappings_old
ON theme_mappings(old_theme_id, effective_date);

CREATE INDEX IF NOT EXISTS idx_theme_mappings_new
ON theme_mappings(new_theme_id, effective_date);

-- ============================================================
-- 6. Predictions
-- ============================================================

CREATE TABLE IF NOT EXISTS predictions (
  prediction_id TEXT PRIMARY KEY,

  prediction_summary TEXT NOT NULL,
  prediction_short_label TEXT,
  prediction_date TEXT,

  -- TTL-based "huge longshot hit" marker. NULL = no longshot revival yet.
  -- Set to ISO date when daily task 2 detects a [REVIVED] marker on a
  -- validation row referencing this prediction. Frontend highlights
  -- predictions whose timestamp is within 14 days of today.
  huge_longshot_hit_at TEXT,

  -- Locale columns. NULL = fall back to canonical English summary/label.
  prediction_summary_ja TEXT,
  prediction_summary_es TEXT,
  prediction_summary_fil TEXT,
  prediction_short_label_ja TEXT,
  prediction_short_label_es TEXT,
  prediction_short_label_fil TEXT,

  source_file_id TEXT,
  source_row_index INTEGER,

  raw_text TEXT,
  raw_json TEXT,

  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT,

  FOREIGN KEY (source_file_id) REFERENCES source_files(source_file_id)
);

CREATE INDEX IF NOT EXISTS idx_predictions_date
ON predictions(prediction_date);

CREATE TABLE IF NOT EXISTS prediction_scope_assignments (
  prediction_id TEXT NOT NULL,
  scope_id TEXT NOT NULL,

  category_id TEXT,
  theme_id TEXT,
  subtheme_id TEXT,

  assignment_method TEXT DEFAULT 'centroid'
    CHECK (assignment_method IN ('anchor', 'centroid', 'llm', 'manual', 'candidate')),

  assignment_score REAL,
  confidence REAL,

  latest_observed_relevance INTEGER CHECK (latest_observed_relevance BETWEEN 1 AND 5),
  latest_realization_score REAL,
  latest_contradiction_score REAL,

  latest_observation_status TEXT CHECK (
    latest_observation_status IN (
      'supported',
      'weakly_supported',
      'no_signal',
      'mixed',
      'contradicted'
    )
  ),

  embedding_model TEXT,
  embedding_version TEXT,
  embedding_json TEXT,

  assigned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT,

  PRIMARY KEY (prediction_id, scope_id),

  FOREIGN KEY (prediction_id) REFERENCES predictions(prediction_id),
  FOREIGN KEY (scope_id) REFERENCES scopes(scope_id),
  FOREIGN KEY (category_id) REFERENCES categories(category_id),
  FOREIGN KEY (theme_id) REFERENCES themes(theme_id),
  FOREIGN KEY (subtheme_id) REFERENCES subthemes(subtheme_id)
);

CREATE INDEX IF NOT EXISTS idx_prediction_scope_theme
ON prediction_scope_assignments(scope_id, theme_id);

CREATE INDEX IF NOT EXISTS idx_prediction_scope_category
ON prediction_scope_assignments(scope_id, category_id);

-- ============================================================
-- 7. Evidence assignments and prediction-evidence links
-- ============================================================

CREATE TABLE IF NOT EXISTS evidence_scope_assignments (
  evidence_id TEXT NOT NULL,
  scope_id TEXT NOT NULL,
  category_id TEXT,
  theme_id TEXT,
  subtheme_id TEXT,

  assignment_score REAL,
  confidence REAL,

  assigned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT,

  PRIMARY KEY (evidence_id, scope_id),

  FOREIGN KEY (evidence_id) REFERENCES evidence_items(evidence_id),
  FOREIGN KEY (scope_id) REFERENCES scopes(scope_id),
  FOREIGN KEY (category_id) REFERENCES categories(category_id),
  FOREIGN KEY (theme_id) REFERENCES themes(theme_id),
  FOREIGN KEY (subtheme_id) REFERENCES subthemes(subtheme_id)
);

CREATE INDEX IF NOT EXISTS idx_evidence_scope_theme
ON evidence_scope_assignments(scope_id, theme_id);

CREATE TABLE IF NOT EXISTS prediction_evidence_links (
  prediction_id TEXT NOT NULL,
  evidence_id TEXT NOT NULL,
  scope_id TEXT NOT NULL,

  support_direction TEXT NOT NULL
    CHECK (support_direction IN ('support', 'contradict', 'neutral')),

  relatedness_score REAL NOT NULL DEFAULT 0,
  evidence_strength REAL NOT NULL DEFAULT 0,
  novelty_score REAL,
  contradiction_score REAL,

  evidence_recency_type TEXT NOT NULL
    CHECK (evidence_recency_type IN ('new', 'continuing')),

  validation_date TEXT NOT NULL,

  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT,

  PRIMARY KEY (prediction_id, evidence_id, scope_id, validation_date),

  FOREIGN KEY (prediction_id) REFERENCES predictions(prediction_id),
  FOREIGN KEY (evidence_id) REFERENCES evidence_items(evidence_id),
  FOREIGN KEY (scope_id) REFERENCES scopes(scope_id)
);

CREATE INDEX IF NOT EXISTS idx_prediction_evidence_validation
ON prediction_evidence_links(validation_date, scope_id);

CREATE INDEX IF NOT EXISTS idx_prediction_evidence_prediction
ON prediction_evidence_links(prediction_id, scope_id);

-- ============================================================
-- 8. Validation rows and realization snapshots
-- ============================================================

CREATE TABLE IF NOT EXISTS validation_rows (
  validation_row_id TEXT PRIMARY KEY,

  source_file_id TEXT NOT NULL,
  validation_date TEXT NOT NULL,

  prediction_id TEXT,
  prediction_summary TEXT NOT NULL,
  -- Re-cited prediction summary in non-EN locales (NULL = fall back to EN).
  prediction_summary_ja TEXT,
  prediction_summary_es TEXT,
  prediction_summary_fil TEXT,
  prediction_date TEXT,

  related_items_text TEXT,
  reference_links_json TEXT,

  observed_relevance INTEGER CHECK (observed_relevance BETWEEN 1 AND 5),

  raw_row_markdown TEXT,
  raw_json TEXT,

  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (source_file_id) REFERENCES source_files(source_file_id),
  FOREIGN KEY (prediction_id) REFERENCES predictions(prediction_id)
);

CREATE INDEX IF NOT EXISTS idx_validation_rows_date
ON validation_rows(validation_date);

CREATE INDEX IF NOT EXISTS idx_validation_rows_prediction
ON validation_rows(prediction_id);

CREATE TABLE IF NOT EXISTS prediction_realization_snapshots (
  prediction_id TEXT NOT NULL,
  scope_id TEXT NOT NULL,
  validation_date TEXT NOT NULL,
  window_id TEXT NOT NULL CHECK (window_id IN ('7d', '30d', '90d')),

  validation_row_id TEXT,

  new_evidence_relevance REAL,
  continuing_evidence_relevance REAL,
  observed_relevance INTEGER CHECK (observed_relevance BETWEEN 1 AND 5),
  realization_score REAL,
  contradiction_score REAL,

  observation_status TEXT CHECK (
    observation_status IN (
      'supported',
      'weakly_supported',
      'no_signal',
      'mixed',
      'contradicted'
    )
  ),

  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (prediction_id, scope_id, validation_date, window_id),

  FOREIGN KEY (prediction_id) REFERENCES predictions(prediction_id),
  FOREIGN KEY (scope_id) REFERENCES scopes(scope_id),
  FOREIGN KEY (window_id) REFERENCES metric_windows(window_id),
  FOREIGN KEY (validation_row_id) REFERENCES validation_rows(validation_row_id)
);

CREATE INDEX IF NOT EXISTS idx_prediction_realization_window
ON prediction_realization_snapshots(scope_id, validation_date, window_id);

-- ============================================================
-- 9. Daily activity for themes and subthemes
-- ============================================================

CREATE TABLE IF NOT EXISTS topic_daily_activity (
  activity_id TEXT PRIMARY KEY,

  activity_date TEXT NOT NULL,
  window_id TEXT NOT NULL CHECK (window_id IN ('7d', '30d', '90d')),
  scope_id TEXT NOT NULL,

  category_id TEXT,
  theme_id TEXT NOT NULL,
  subtheme_id TEXT,

  activity_level TEXT NOT NULL CHECK (activity_level IN ('theme', 'subtheme')),

  new_signal REAL NOT NULL DEFAULT 0,
  continuing_signal REAL NOT NULL DEFAULT 0,
  contradiction_signal REAL NOT NULL DEFAULT 0,

  attention_score REAL NOT NULL DEFAULT 0,
  realization_score REAL,
  grass_level INTEGER NOT NULL DEFAULT 0 CHECK (grass_level BETWEEN 0 AND 4),

  new_evidence_count INTEGER NOT NULL DEFAULT 0,
  active_prior_evidence_count INTEGER NOT NULL DEFAULT 0,
  prediction_count INTEGER NOT NULL DEFAULT 0,

  max_observed_relevance INTEGER,
  avg_observed_relevance REAL,

  status TEXT NOT NULL DEFAULT 'dormant'
    CHECK (status IN ('new', 'active', 'continuing', 'dormant', 'contradicted', 'mixed')),

  streak_days INTEGER DEFAULT 0,
  last_active_date TEXT,

  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT,

  FOREIGN KEY (window_id) REFERENCES metric_windows(window_id),
  FOREIGN KEY (scope_id) REFERENCES scopes(scope_id),
  FOREIGN KEY (category_id) REFERENCES categories(category_id),
  FOREIGN KEY (theme_id) REFERENCES themes(theme_id),
  FOREIGN KEY (subtheme_id) REFERENCES subthemes(subtheme_id),

  CHECK (
    (activity_level = 'theme' AND subtheme_id IS NULL)
    OR
    (activity_level = 'subtheme' AND subtheme_id IS NOT NULL)
  )
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_topic_daily_theme_activity
ON topic_daily_activity(activity_date, window_id, scope_id, theme_id)
WHERE activity_level = 'theme';

CREATE UNIQUE INDEX IF NOT EXISTS idx_topic_daily_subtheme_activity
ON topic_daily_activity(activity_date, window_id, scope_id, theme_id, subtheme_id)
WHERE activity_level = 'subtheme';

CREATE INDEX IF NOT EXISTS idx_topic_daily_scope_date_window
ON topic_daily_activity(scope_id, activity_date, window_id);

CREATE INDEX IF NOT EXISTS idx_topic_daily_theme_date_window
ON topic_daily_activity(theme_id, activity_date, window_id);

-- ============================================================
-- 10. Category daily activity
-- ============================================================

CREATE TABLE IF NOT EXISTS category_daily_activity (
  category_activity_id TEXT PRIMARY KEY,

  activity_date TEXT NOT NULL,
  window_id TEXT NOT NULL CHECK (window_id IN ('7d', '30d', '90d')),
  scope_id TEXT NOT NULL,
  category_id TEXT NOT NULL,

  attention_score REAL NOT NULL DEFAULT 0,
  realization_score REAL,
  contradiction_signal REAL NOT NULL DEFAULT 0,
  grass_level INTEGER NOT NULL DEFAULT 0 CHECK (grass_level BETWEEN 0 AND 4),

  theme_count INTEGER NOT NULL DEFAULT 0,
  active_theme_count INTEGER NOT NULL DEFAULT 0,
  prediction_count INTEGER NOT NULL DEFAULT 0,

  status TEXT NOT NULL DEFAULT 'dormant'
    CHECK (status IN ('new', 'active', 'continuing', 'dormant', 'contradicted', 'mixed')),

  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT,

  FOREIGN KEY (window_id) REFERENCES metric_windows(window_id),
  FOREIGN KEY (scope_id) REFERENCES scopes(scope_id),
  FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_category_daily_unique
ON category_daily_activity(activity_date, window_id, scope_id, category_id);

-- ============================================================
-- 11. Theme candidates
-- ============================================================

CREATE TABLE IF NOT EXISTS theme_candidates (
  candidate_id TEXT PRIMARY KEY,

  scope_id TEXT NOT NULL,
  suggested_category_id TEXT,
  suggested_theme_label TEXT NOT NULL,
  suggested_short_label TEXT,
  suggested_description TEXT,

  origin_evidence_id TEXT,
  origin_prediction_id TEXT,

  candidate_reason TEXT,
  novelty_score REAL,
  nearest_theme_id TEXT,
  nearest_theme_similarity REAL,

  status TEXT NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending', 'promoted', 'merged', 'rejected', 'ignored')),

  promoted_theme_id TEXT,

  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT,

  FOREIGN KEY (scope_id) REFERENCES scopes(scope_id),
  FOREIGN KEY (suggested_category_id) REFERENCES categories(category_id),
  FOREIGN KEY (origin_evidence_id) REFERENCES evidence_items(evidence_id),
  FOREIGN KEY (origin_prediction_id) REFERENCES predictions(prediction_id),
  FOREIGN KEY (nearest_theme_id) REFERENCES themes(theme_id),
  FOREIGN KEY (promoted_theme_id) REFERENCES themes(theme_id)
);

CREATE INDEX IF NOT EXISTS idx_theme_candidates_status
ON theme_candidates(status, scope_id);

-- ============================================================
-- 12. Graph layout and export metadata
-- ============================================================

CREATE TABLE IF NOT EXISTS graph_node_layouts (
  scope_id TEXT NOT NULL,
  node_id TEXT NOT NULL,
  node_type TEXT NOT NULL CHECK (node_type IN ('category', 'theme', 'subtheme', 'prediction')),

  x REAL,
  y REAL,
  z REAL,
  radius REAL,
  fixed INTEGER NOT NULL DEFAULT 0,

  layout_version TEXT,
  updated_at TEXT,

  PRIMARY KEY (scope_id, node_id),

  FOREIGN KEY (scope_id) REFERENCES scopes(scope_id)
);

CREATE TABLE IF NOT EXISTS graph_exports (
  export_id TEXT PRIMARY KEY,

  scope_id TEXT NOT NULL,
  window_id TEXT CHECK (window_id IN ('7d', '30d', '90d')),

  output_path TEXT NOT NULL,
  schema_version TEXT NOT NULL,
  generated_at TEXT NOT NULL,

  node_count INTEGER,
  link_count INTEGER,

  date_start TEXT,
  date_end TEXT,

  content_sha TEXT,

  FOREIGN KEY (scope_id) REFERENCES scopes(scope_id),
  FOREIGN KEY (window_id) REFERENCES metric_windows(window_id)
);

CREATE INDEX IF NOT EXISTS idx_graph_exports_scope_window
ON graph_exports(scope_id, window_id, generated_at);

-- ============================================================
-- 13. Embedding run metadata
-- ============================================================

CREATE TABLE IF NOT EXISTS embedding_runs (
  embedding_run_id TEXT PRIMARY KEY,
  embedding_model TEXT NOT NULL,
  embedding_version TEXT,
  scope_id TEXT,
  input_count INTEGER,
  started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  finished_at TEXT,
  notes TEXT,
  FOREIGN KEY (scope_id) REFERENCES scopes(scope_id)
);

-- ============================================================
-- 14. Seed data
-- ============================================================

INSERT OR IGNORE INTO scopes(scope_id, label, description)
VALUES
  ('tech', 'Technology', 'Technical mechanisms, architecture, models, security, infrastructure, and standards.'),
  ('business', 'Business', 'Market structure, competition, distribution, adoption, regulation, and capital strategy.');

INSERT OR IGNORE INTO metric_windows(window_id, label, days, sort_order, is_default)
VALUES
  ('7d', '7D', 7, 10, 0),
  ('30d', '30D', 30, 20, 1),
  ('90d', '90D', 90, 30, 0);

INSERT OR IGNORE INTO categories(category_id, scope_id, label, short_label, description, sort_order)
VALUES
  ('tech.models', 'tech', 'Models', 'Models', 'Model architecture, training, quantization, open weights, model releases.', 10),
  ('tech.agents', 'tech', 'Agents', 'Agents', 'Agent frameworks, registries, tools, workflows, runtime behavior.', 20),
  ('tech.security', 'tech', 'Security', 'Security', 'Prompt injection, CVEs, sandbox escape, RCE, secrets, supply-chain attacks.', 30),
  ('tech.inference-runtime', 'tech', 'Inference Runtime', 'Runtime', 'Local inference, serving stacks, llama.cpp, vLLM, SGLang, Ollama, MLX, GGUF.', 40),
  ('tech.infrastructure', 'tech', 'Infrastructure', 'Infra', 'GPU, TPU, Trainium, data centers, cloud training and inference systems.', 50),
  ('tech.standards', 'tech', 'Standards', 'Standards', 'MCP, registries, schemas, governance protocols, interoperability.', 60),

  ('business.market-structure', 'business', 'Market Structure', 'Market', 'Industry structure, platform consolidation, hyperscaler/frontier lab alignment.', 10),
  ('business.distribution', 'business', 'Distribution', 'Distribution', 'Cloud versus local, hosted versus open-weight, edge deployment, channel shifts.', 20),
  ('business.competition', 'business', 'Competition', 'Competition', 'Vendor competition, model differentiation, proprietary versus open ecosystems.', 30),
  ('business.enterprise-adoption', 'business', 'Enterprise Adoption', 'Adoption', 'Enterprise usage, procurement, workflow integration, developer tooling.', 40),
  ('business.regulation-compliance', 'business', 'Regulation / Compliance', 'Compliance', 'CVE/CVSS/OWASP, AI regulation, auditability, legal and compliance pressure.', 50),
  ('business.capital-supply-chain', 'business', 'Capital / Supply Chain', 'Capital', 'Compute capex, chip supply, data center commitments, cloud capacity strategy.', 60);

INSERT OR IGNORE INTO themes(theme_id, scope_id, category_id, canonical_label, short_label, generated_label, description, status)
VALUES
  ('tech.one_bit_edge_llm', 'tech', 'tech.models', '1-bit / Edge LLM', '1-bit Edge LLM', '1-bit / Edge LLM',
   '1-bit native training, quantization alternatives, compact local models, Qwen/Llama derivatives, GGUF/MLX deployment.', 'active'),

  ('tech.agent_control_plane', 'tech', 'tech.agents', 'Agent Control Plane', 'Control Plane', 'Agent Control Plane',
   'Agent control plane, agent registry, managed harness, workspace agents, OAuth cross-trust, identity for AI agents, Entra Agent ID, Okta for AI Agents, Keycard, AgentCore, coding agents, Claude Code, Codex, Cursor, Kiro, agent tool permissions, agent lifecycle.', 'active'),

  ('tech.agent_runtime_security', 'tech', 'tech.security', 'Agent Runtime Security', 'Agent Runtime', 'Agent Runtime Security',
   'Prompt injection, sandbox escape, tool misuse, RCE, CVE/CVSS issues in AI agent runtimes.', 'active'),

  ('tech.model_supply_chain', 'tech', 'tech.security', 'Model Supply Chain', 'Model Supply', 'Model Supply Chain',
   'Malicious model files, GGUF supply-chain risk, tokenizer templates, Hugging Face/Ollama/ModelScope distribution risks.', 'active'),

  ('tech.agent_registry_architecture', 'tech', 'tech.standards', 'Agent Registry Architecture', 'Agent Registry', 'Agent Registry Architecture',
   'Registries for skills, tool permissions, audit traces, MCP-adjacent metadata, and agent artifacts.', 'active'),

  ('tech.local_inference_runtime', 'tech', 'tech.inference-runtime', 'Local Inference Runtime', 'Local Runtime', 'Local Inference Runtime',
   'Local inference stacks, llama.cpp, Ollama, MLX, WebGPU, OpenVINO, on-device deployment.', 'active'),

  ('tech.ai_chip_architecture', 'tech', 'tech.infrastructure', 'AI Chip Architecture', 'AI Chips', 'AI Chip Architecture',
   'TPU, Trainium, MAIA, MI300X, training/inference SKU separation, accelerator-specific model behavior.', 'active'),

  ('business.cloud_vs_local_distribution', 'business', 'business.distribution', 'Cloud vs Local AI Distribution', 'Cloud vs Local', 'Cloud vs Local AI Distribution',
   'Shift between cloud-hosted frontier AI and local or edge AI adoption, including privacy, cost, and SMB deployment.', 'active'),

  ('business.hyperscaler_frontier_lab_alliance', 'business', 'business.market-structure', 'Hyperscaler × Frontier Lab Alliance', 'Hyperscaler Alliance', 'Hyperscaler × Frontier Lab Alliance',
   'Exclusive or semi-exclusive alliances between hyperscalers and frontier labs, compute commitments, and platform lock-in.', 'active'),

  ('business.open_weight_vs_proprietary', 'business', 'business.competition', 'Open Weight vs Proprietary AI', 'Open vs Proprietary', 'Open Weight vs Proprietary AI',
   'Open-weight versus hosted-only model dynamics, geopolitical fragmentation, and proprietary frontier model gating.', 'active'),

  ('business.ai_security_compliance_market', 'business', 'business.regulation-compliance', 'AI Security Compliance Market', 'AI Security Compliance', 'AI Security Compliance Market',
   'AI vulnerabilities becoming compliance, CVE/CVSS/OWASP categories, enterprise risk budgets, and security tooling demand.', 'active'),

  ('business.developer_platformization', 'business', 'business.enterprise-adoption', 'Developer Toolchain Platformization', 'Dev Platformization', 'Developer Toolchain Platformization',
   'AI coding tools, CI/CD agents, tool registries, and enterprise developer workflow consolidation.', 'active'),

  ('business.compute_capex_strategy', 'business', 'business.capital-supply-chain', 'Compute Capex Strategy', 'Compute Capex', 'Compute Capex Strategy',
   'AI chip investments, data center capex, accelerator differentiation, and cloud capacity constraints.', 'active');

-- ============================================================
-- 15. Views for exporter
-- ============================================================

CREATE VIEW IF NOT EXISTS v_prediction_assignments AS
SELECT
  p.prediction_id,
  p.prediction_summary,
  p.prediction_short_label,
  p.prediction_date,
  sf.path AS source_report_path,
  psa.scope_id,
  psa.category_id,
  c.label AS category_label,
  c.short_label AS category_short_label,
  psa.theme_id,
  t.canonical_label AS theme_label,
  t.short_label AS theme_short_label,
  psa.subtheme_id,
  st.canonical_label AS subtheme_label,
  st.short_label AS subtheme_short_label,
  psa.assignment_method,
  psa.assignment_score,
  psa.latest_observed_relevance,
  psa.latest_realization_score,
  psa.latest_contradiction_score,
  psa.latest_observation_status
FROM predictions p
JOIN prediction_scope_assignments psa ON p.prediction_id = psa.prediction_id
LEFT JOIN source_files sf ON p.source_file_id = sf.source_file_id
LEFT JOIN categories c ON psa.category_id = c.category_id
LEFT JOIN themes t ON psa.theme_id = t.theme_id
LEFT JOIN subthemes st ON psa.subtheme_id = st.subtheme_id;

CREATE VIEW IF NOT EXISTS v_latest_topic_activity AS
SELECT tda.*
FROM topic_daily_activity tda
JOIN (
  SELECT
    scope_id,
    window_id,
    theme_id,
    activity_level,
    COALESCE(subtheme_id, '') AS subtheme_key,
    MAX(activity_date) AS max_activity_date
  FROM topic_daily_activity
  GROUP BY scope_id, window_id, theme_id, activity_level, COALESCE(subtheme_id, '')
) latest
ON tda.scope_id = latest.scope_id
AND tda.window_id = latest.window_id
AND tda.theme_id = latest.theme_id
AND tda.activity_level = latest.activity_level
AND COALESCE(tda.subtheme_id, '') = latest.subtheme_key
AND tda.activity_date = latest.max_activity_date;

CREATE VIEW IF NOT EXISTS v_latest_category_activity AS
SELECT cda.*
FROM category_daily_activity cda
JOIN (
  SELECT scope_id, window_id, category_id, MAX(activity_date) AS max_activity_date
  FROM category_daily_activity
  GROUP BY scope_id, window_id, category_id
) latest
ON cda.scope_id = latest.scope_id
AND cda.window_id = latest.window_id
AND cda.category_id = latest.category_id
AND cda.activity_date = latest.max_activity_date;


-- ============================================================
-- 16. Locale seed translations (categories + themes)
-- ============================================================
--
-- The English seed values above are the canonical labels. The UPDATE
-- statements below populate the *_ja, *_es, *_fil columns with hand
-- translations so a fresh DB ships with all 4 locales pre-filled.
-- These updates are idempotent: re-running schema.sql on an existing
-- DB simply overwrites the locale columns with the same values.
--
-- Locale notes:
--   - 'ja' = Japanese; 'es' = Spanish; 'fil' = Filipino (Tagalog).
--   - Where a tech term is universally retained in English (e.g. "AI",
--     "TPU", "MCP"), we keep it verbatim per locale convention.
--   - description_* is intentionally not always translated when the EN
--     description is dense with English-only proper nouns.

-- Categories ---------------------------------------------------

UPDATE categories SET
  label_ja = 'モデル', short_label_ja = 'モデル',
  label_es = 'Modelos', short_label_es = 'Modelos',
  label_fil = 'Mga Modelo', short_label_fil = 'Mga Modelo',
  description_ja = 'モデルアーキテクチャ、学習、量子化、オープン重み、モデルリリース。',
  description_es = 'Arquitectura, entrenamiento, cuantización, pesos abiertos y lanzamientos de modelos.',
  description_fil = 'Arkitektura, pagsasanay, quantization, open weights, at paglabas ng mga modelo.'
WHERE category_id = 'tech.models';

UPDATE categories SET
  label_ja = 'エージェント', short_label_ja = 'エージェント',
  label_es = 'Agentes', short_label_es = 'Agentes',
  label_fil = 'Mga Ahente', short_label_fil = 'Mga Ahente',
  description_ja = 'エージェント基盤、レジストリ、ツール、ワークフロー、ランタイム挙動。',
  description_es = 'Marcos de agentes, registros, herramientas, flujos de trabajo y comportamiento en tiempo de ejecución.',
  description_fil = 'Mga framework, registry, tools, workflows, at runtime ng mga ahente.'
WHERE category_id = 'tech.agents';

UPDATE categories SET
  label_ja = 'セキュリティ', short_label_ja = 'セキュリティ',
  label_es = 'Seguridad', short_label_es = 'Seguridad',
  label_fil = 'Seguridad', short_label_fil = 'Seguridad',
  description_ja = 'プロンプトインジェクション、CVE、サンドボックス脱出、RCE、シークレット、サプライチェーン攻撃。',
  description_es = 'Inyección de prompts, CVE, escape de sandbox, RCE, secretos y ataques a la cadena de suministro.',
  description_fil = 'Prompt injection, CVE, sandbox escape, RCE, secrets, at supply-chain attacks.'
WHERE category_id = 'tech.security';

UPDATE categories SET
  label_ja = '推論ランタイム', short_label_ja = 'ランタイム',
  label_es = 'Tiempo de ejecución', short_label_es = 'Runtime',
  label_fil = 'Inference Runtime', short_label_fil = 'Runtime',
  description_ja = 'ローカル推論、サービングスタック、llama.cpp、vLLM、SGLang、Ollama、MLX、GGUF。',
  description_es = 'Inferencia local, stacks de servicio, llama.cpp, vLLM, SGLang, Ollama, MLX, GGUF.',
  description_fil = 'Lokal na inference, serving stacks, llama.cpp, vLLM, SGLang, Ollama, MLX, GGUF.'
WHERE category_id = 'tech.inference-runtime';

UPDATE categories SET
  label_ja = 'インフラ', short_label_ja = 'インフラ',
  label_es = 'Infraestructura', short_label_es = 'Infra',
  label_fil = 'Imprastraktura', short_label_fil = 'Infra',
  description_ja = 'GPU、TPU、Trainium、データセンター、クラウド学習・推論システム。',
  description_es = 'GPU, TPU, Trainium, centros de datos, sistemas de entrenamiento e inferencia en la nube.',
  description_fil = 'GPU, TPU, Trainium, data centers, cloud training at inference systems.'
WHERE category_id = 'tech.infrastructure';

UPDATE categories SET
  label_ja = '標準', short_label_ja = '標準',
  label_es = 'Estándares', short_label_es = 'Estándares',
  label_fil = 'Mga Pamantayan', short_label_fil = 'Pamantayan',
  description_ja = 'MCP、レジストリ、スキーマ、ガバナンスプロトコル、相互運用性。',
  description_es = 'MCP, registros, esquemas, protocolos de gobernanza e interoperabilidad.',
  description_fil = 'MCP, registries, schemas, governance protocols, interoperability.'
WHERE category_id = 'tech.standards';

UPDATE categories SET
  label_ja = '市場構造', short_label_ja = '市場',
  label_es = 'Estructura de mercado', short_label_es = 'Mercado',
  label_fil = 'Istruktura ng Merkado', short_label_fil = 'Merkado',
  description_ja = '産業構造、プラットフォーム集約、ハイパースケーラ／フロンティアラボ提携。',
  description_es = 'Estructura de la industria, consolidación de plataformas y alianzas hyperscaler/laboratorios frontier.',
  description_fil = 'Istruktura ng industriya, platform consolidation, hyperscaler/frontier lab alignment.'
WHERE category_id = 'business.market-structure';

UPDATE categories SET
  label_ja = '配信', short_label_ja = '配信',
  label_es = 'Distribución', short_label_es = 'Distribución',
  label_fil = 'Distribusyon', short_label_fil = 'Distribusyon',
  description_ja = 'クラウド対ローカル、ホスト型対オープン重み、エッジ展開、チャネルシフト。',
  description_es = 'Nube vs local, hospedado vs pesos abiertos, despliegue en el edge, cambios de canal.',
  description_fil = 'Cloud vs local, hosted vs open-weight, edge deployment, channel shifts.'
WHERE category_id = 'business.distribution';

UPDATE categories SET
  label_ja = '競争', short_label_ja = '競争',
  label_es = 'Competencia', short_label_es = 'Competencia',
  label_fil = 'Kompetisyon', short_label_fil = 'Kompetisyon',
  description_ja = 'ベンダー競争、モデル差別化、プロプライエタリ対オープンエコシステム。',
  description_es = 'Competencia entre proveedores, diferenciación de modelos, ecosistemas propietarios vs abiertos.',
  description_fil = 'Kompetisyon ng vendor, pagkakaiba ng modelo, proprietary vs open ecosystems.'
WHERE category_id = 'business.competition';

UPDATE categories SET
  label_ja = 'エンタープライズ採用', short_label_ja = '採用',
  label_es = 'Adopción empresarial', short_label_es = 'Adopción',
  label_fil = 'Adopsyon ng Enterprise', short_label_fil = 'Adopsyon',
  description_ja = 'エンタープライズ利用、調達、ワークフロー統合、開発者ツーリング。',
  description_es = 'Uso empresarial, adquisición, integración de flujos de trabajo y herramientas de desarrollo.',
  description_fil = 'Paggamit sa enterprise, procurement, workflow integration, developer tooling.'
WHERE category_id = 'business.enterprise-adoption';

UPDATE categories SET
  label_ja = '規制／コンプライアンス', short_label_ja = 'コンプラ',
  label_es = 'Regulación / Cumplimiento', short_label_es = 'Cumplimiento',
  label_fil = 'Regulasyon / Pagsunod', short_label_fil = 'Pagsunod',
  description_ja = 'CVE/CVSS/OWASP、AI規制、監査可能性、法務およびコンプライアンス圧力。',
  description_es = 'CVE/CVSS/OWASP, regulación de IA, auditabilidad, presión legal y de cumplimiento.',
  description_fil = 'CVE/CVSS/OWASP, regulasyon ng AI, auditability, legal at compliance pressure.'
WHERE category_id = 'business.regulation-compliance';

UPDATE categories SET
  label_ja = '資本／サプライチェーン', short_label_ja = '資本',
  label_es = 'Capital / Cadena de suministro', short_label_es = 'Capital',
  label_fil = 'Kapital / Supply Chain', short_label_fil = 'Kapital',
  description_ja = '計算資源 capex、チップ供給、データセンター契約、クラウド容量戦略。',
  description_es = 'Capex de cómputo, suministro de chips, compromisos de centros de datos y capacidad de la nube.',
  description_fil = 'Compute capex, chip supply, data center commitments, cloud capacity strategy.'
WHERE category_id = 'business.capital-supply-chain';

-- Themes -------------------------------------------------------

UPDATE themes SET
  label_ja = '1ビット／エッジLLM', short_label_ja = '1ビット エッジLLM',
  label_es = 'LLM de 1 bit / Edge', short_label_es = 'LLM 1-bit Edge',
  label_fil = '1-bit / Edge LLM', short_label_fil = '1-bit Edge LLM'
WHERE theme_id = 'tech.one_bit_edge_llm';

UPDATE themes SET
  label_ja = 'エージェント制御プレーン', short_label_ja = '制御プレーン',
  label_es = 'Plano de control de agentes', short_label_es = 'Plano de control',
  label_fil = 'Agent Control Plane', short_label_fil = 'Control Plane'
WHERE theme_id = 'tech.agent_control_plane';

UPDATE themes SET
  label_ja = 'エージェントランタイムセキュリティ', short_label_ja = 'エージェントランタイム',
  label_es = 'Seguridad del runtime de agentes', short_label_es = 'Runtime de agentes',
  label_fil = 'Seguridad ng Agent Runtime', short_label_fil = 'Agent Runtime'
WHERE theme_id = 'tech.agent_runtime_security';

UPDATE themes SET
  label_ja = 'モデルサプライチェーン', short_label_ja = 'モデル供給',
  label_es = 'Cadena de suministro de modelos', short_label_es = 'Suministro de modelos',
  label_fil = 'Model Supply Chain', short_label_fil = 'Model Supply'
WHERE theme_id = 'tech.model_supply_chain';

UPDATE themes SET
  label_ja = 'エージェントレジストリアーキテクチャ', short_label_ja = 'エージェントレジストリ',
  label_es = 'Arquitectura de registro de agentes', short_label_es = 'Registro de agentes',
  label_fil = 'Arkitektura ng Agent Registry', short_label_fil = 'Agent Registry'
WHERE theme_id = 'tech.agent_registry_architecture';

UPDATE themes SET
  label_ja = 'ローカル推論ランタイム', short_label_ja = 'ローカルランタイム',
  label_es = 'Tiempo de ejecución local', short_label_es = 'Runtime local',
  label_fil = 'Lokal na Inference Runtime', short_label_fil = 'Local Runtime'
WHERE theme_id = 'tech.local_inference_runtime';

UPDATE themes SET
  label_ja = 'AIチップアーキテクチャ', short_label_ja = 'AIチップ',
  label_es = 'Arquitectura de chips de IA', short_label_es = 'Chips de IA',
  label_fil = 'Arkitektura ng AI Chip', short_label_fil = 'AI Chips'
WHERE theme_id = 'tech.ai_chip_architecture';

UPDATE themes SET
  label_ja = 'クラウド対ローカルAI配信', short_label_ja = 'クラウド対ローカル',
  label_es = 'Distribución de IA: nube vs local', short_label_es = 'Nube vs Local',
  label_fil = 'Cloud vs Lokal na AI', short_label_fil = 'Cloud vs Lokal'
WHERE theme_id = 'business.cloud_vs_local_distribution';

UPDATE themes SET
  label_ja = 'ハイパースケーラ × フロンティアラボ提携', short_label_ja = 'ハイパースケーラ提携',
  label_es = 'Alianza hyperscaler × laboratorio frontier', short_label_es = 'Alianza hyperscaler',
  label_fil = 'Hyperscaler x Frontier Lab Alliance', short_label_fil = 'Hyperscaler Alliance'
WHERE theme_id = 'business.hyperscaler_frontier_lab_alliance';

UPDATE themes SET
  label_ja = 'オープン重み対プロプライエタリAI', short_label_ja = 'オープン対プロプライエタリ',
  label_es = 'IA de pesos abiertos vs propietaria', short_label_es = 'Abierto vs Propietario',
  label_fil = 'Open-Weight vs Proprietary AI', short_label_fil = 'Open vs Proprietary'
WHERE theme_id = 'business.open_weight_vs_proprietary';

UPDATE themes SET
  label_ja = 'AIセキュリティ・コンプライアンス市場', short_label_ja = 'AIセキュリティ・コンプラ',
  label_es = 'Mercado de cumplimiento de seguridad de IA', short_label_es = 'Cumplimiento IA',
  label_fil = 'Merkado ng AI Security Compliance', short_label_fil = 'AI Security Compliance'
WHERE theme_id = 'business.ai_security_compliance_market';

UPDATE themes SET
  label_ja = '開発者ツールチェーンのプラットフォーム化', short_label_ja = '開発プラットフォーム化',
  label_es = 'Plataformización de herramientas de desarrollo', short_label_es = 'Plat. de Dev',
  label_fil = 'Platformization ng Developer Toolchain', short_label_fil = 'Dev Platformization'
WHERE theme_id = 'business.developer_platformization';

UPDATE themes SET
  label_ja = 'コンピュート資本戦略', short_label_ja = 'コンピュート資本',
  label_es = 'Estrategia de capex de cómputo', short_label_es = 'Capex de cómputo',
  label_fil = 'Estratehiya ng Compute Capex', short_label_fil = 'Compute Capex'
WHERE theme_id = 'business.compute_capex_strategy';

-- ============================================================
-- 17. Migration note for ALTER TABLE
-- ============================================================
--
-- SQLite cannot ADD COLUMN IF NOT EXISTS. The columns added in this
-- branch are picked up automatically when init_db() runs against an
-- empty database. To migrate an *existing* analytics.sqlite to this
-- schema, the simplest path is:
--
--     rm app/data/analytics2.sqlite
--     python -m src.cli update     # rebuilds DB from scratch
--
-- That is the documented procedure for the locale branch since the
-- ingest pipeline is fully reproducible from the markdown corpus.