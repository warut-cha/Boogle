// Shared API contract types for Bob Sentinel
export type Severity = "info" | "low" | "medium" | "high" | "critical";

export type FindingType =
  | "hardcoded_secret"
  | "private_key"
  | "database_url"
  | "deprecated_api"
  | "runtime_anomaly"
  | "database_anomaly"
  | "infrastructure_risk"
  | "sensitive_log_exposure";

export type FindingCategory =
  | "secret_exposure"
  | "legacy_api"
  | "runtime_behavior"
  | "database_activity"
  | "infrastructure"
  | "logging"
  | "unknown";

export type FindingSource =
  | "rust_scanner"
  | "python_analyzer"
  | "mock_data"
  | "bob_analysis";

export type Finding = {
  finding_id: string;
  repo_name: string;
  finding_type: FindingType;
  category: FindingCategory;
  severity_hint: Severity;
  source: FindingSource;
  file: string;
  line: number | null;
  endpoint: string | null;
  database_table: string | null;
  evidence: string;
  masked_value: string | null;
  timestamp: string;
};

export type AttackPathNodeType =
  | "secret"
  | "api"
  | "runtime"
  | "database"
  | "infrastructure"
  | "impact";

export type AttackPathNode = {
  id: string;
  label: string;
  type: AttackPathNodeType;
};

export type AttackPathEdge = {
  from: string;
  to: string;
  label: string;
};

export type AttackPath = {
  nodes: AttackPathNode[];
  edges: AttackPathEdge[];
};

export type AIMemoryType =
  | "security_prevention_rule"
  | "incident_pattern"
  | "false_positive_rule";

export type AIMemory = {
  memory_type: AIMemoryType;
  incident_pattern: string;
  root_cause: string;
  signals_to_watch: string[];
  prevention_rule: string;
  recommended_tests: string[];
  severity_escalation_conditions?: string[];
};

export type Incident = {
  incident_id: string;
  title: string;
  severity: Severity;
  severity_level: 1 | 2 | 3 | 4 | 5;
  confidence_score: number; // from 0 to 1 example: 0.8 = 80& confidence
  confidence_reasons: string[];
  confidence_limitations: string[];
  affected_repos: string[];
  affected_files: string[];
  affected_endpoints: string[];
  affected_database_tables: string[];
  findings: Finding[];
  attack_path: AttackPath;
  related_memory: AIMemory[];
};

export type RecommendedFixType =
  | "immediate_action"
  | "code_fix"
  | "api_fix"
  | "config_fix"
  | "test_fix"
  | "memory_rule";

export type RecommendedFix = {
  type: RecommendedFixType;
  description: string;
};

export type GeneratedSecurityTest = {
  file: string;
  name: string;
  purpose: string;
  code: string;
};

export type PRDraft = {
  branch_name: string;
  pr_title: string;
  pr_description: string;
  files_to_change: string[];
};

export type BobOutput = {
  attack_type: string;
  target: string;
  severity: Severity;
  confidence_assessment: string;
  recommended_fixes: RecommendedFix[];
  generated_security_tests: GeneratedSecurityTest[];
  incident_report: string;
  ai_memory: AIMemory;
  pr_draft: PRDraft;
};