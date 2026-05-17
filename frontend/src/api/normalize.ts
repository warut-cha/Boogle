import type {
  AIMemory,
  AttackPath,
  AttackPathNodeType,
  BobOutput,
  Finding,
  FindingCategory,
  FindingSource,
  FindingType,
  Incident,
  RecommendedFixType,
  Severity,
} from "./types";

const severityValues: Severity[] = ["info", "low", "medium", "high", "critical"];

const findingTypes: FindingType[] = [
  "hardcoded_secret",
  "private_key",
  "database_url",
  "deprecated_api",
  "runtime_anomaly",
  "database_anomaly",
  "infrastructure_risk",
  "sensitive_log_exposure",
];

const findingCategories: FindingCategory[] = [
  "secret_exposure",
  "legacy_api",
  "runtime_behavior",
  "database_activity",
  "infrastructure",
  "logging",
  "unknown",
];

const findingSources: FindingSource[] = [
  "rust_scanner",
  "python_analyzer",
  "mock_data",
  "bob_analysis",
  "unknown",
];

const attackNodeTypes: AttackPathNodeType[] = [
  "secret",
  "api",
  "runtime",
  "database",
  "infrastructure",
  "impact",
];

const fixTypes: RecommendedFixType[] = [
  "immediate_action",
  "code_fix",
  "api_fix",
  "config_fix",
  "infrastructure_fix",
  "test_fix",
  "memory_rule",
];

function asString(value: unknown, fallback = ""): string {
  return typeof value === "string" ? value : fallback;
}

function asNumberOrNull(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function asArray<T>(value: unknown, fallback: T[] = []): T[] {
  return Array.isArray(value) ? (value as T[]) : fallback;
}

function asSeverity(value: unknown, fallback: Severity = "info"): Severity {
  const normalized = String(value ?? "").toLowerCase();

  return severityValues.includes(normalized as Severity)
    ? (normalized as Severity)
    : fallback;
}

function asSeverityLevel(
  value: unknown,
  fallback: 1 | 2 | 3 | 4 | 5 = 1
): 1 | 2 | 3 | 4 | 5 {
  if (value === 1 || value === 2 || value === 3 || value === 4 || value === 5) {
    return value;
  }

  return fallback;
}

function asFindingType(value: unknown): FindingType {
  const normalized = String(value ?? "");

  return findingTypes.includes(normalized as FindingType)
    ? (normalized as FindingType)
    : "runtime_anomaly";
}

function asFindingCategory(value: unknown): FindingCategory {
  const normalized = String(value ?? "");

  return findingCategories.includes(normalized as FindingCategory)
    ? (normalized as FindingCategory)
    : "unknown";
}

function asFindingSource(value: unknown): FindingSource {
  const normalized = String(value ?? "");

  return findingSources.includes(normalized as FindingSource)
    ? (normalized as FindingSource)
    : "unknown";
}

function asAttackNodeType(value: unknown): AttackPathNodeType {
  const normalized = String(value ?? "");

  return attackNodeTypes.includes(normalized as AttackPathNodeType)
    ? (normalized as AttackPathNodeType)
    : "impact";
}

function asFixType(value: unknown): RecommendedFixType {
  const normalized = String(value ?? "");

  return fixTypes.includes(normalized as RecommendedFixType)
    ? (normalized as RecommendedFixType)
    : "code_fix";
}

function makeId(prefix: string): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return `${prefix}-${crypto.randomUUID()}`;
  }

  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function normalizeFinding(input: Partial<Finding> | any): Finding {
  return {
    finding_id: asString(input?.finding_id, makeId("FIND")),
    repo_name: asString(input?.repo_name, "unknown"),
    finding_type: asFindingType(input?.finding_type ?? input?.type),
    category: asFindingCategory(input?.category),
    severity_hint: asSeverity(input?.severity_hint, "info"),
    source: asFindingSource(input?.source),
    file: typeof input?.file === "string" ? input.file : null,
    line: asNumberOrNull(input?.line),
    endpoint: typeof input?.endpoint === "string" ? input.endpoint : null,
    database_table:
      typeof input?.database_table === "string" ? input.database_table : null,
    evidence: asString(input?.evidence),
    masked_value: typeof input?.masked_value === "string" ? input.masked_value : null,
    timestamp: asString(input?.timestamp, new Date().toISOString()),
  };
}

export function normalizeAttackPath(input: Partial<AttackPath> | any): AttackPath {
  const nodes = asArray<any>(input?.nodes).map((node) => ({
    id: asString(node?.id, makeId("node")),
    label: asString(node?.label, "Unknown"),
    type: asAttackNodeType(node?.type),
  }));

  const edges = asArray<any>(input?.edges).map((edge, index) => ({
    from: asString(edge?.from),
    to: asString(edge?.to),
    label: asString(edge?.label, `edge-${index}`),
  }));

  return { nodes, edges };
}

export function normalizeAIMemory(input: Partial<AIMemory> | any): AIMemory {
  return {
    memory_type:
      input?.memory_type === "incident_pattern" ||
      input?.memory_type === "false_positive_rule"
        ? input.memory_type
        : "security_prevention_rule",
    incident_pattern: asString(input?.incident_pattern, "unknown_pattern"),
    root_cause: asString(input?.root_cause, "Unknown root cause"),
    signals_to_watch: asArray<string>(input?.signals_to_watch),
    prevention_rule: asString(input?.prevention_rule, "No prevention rule provided."),
    recommended_tests: asArray<string>(input?.recommended_tests),
    severity_escalation_conditions: asArray<string>(
      input?.severity_escalation_conditions
    ),
  };
}

export function normalizeIncident(input: Partial<Incident> | any): Incident {
  const severity = asSeverity(input?.severity, "info");

  const defaultLevel: 1 | 2 | 3 | 4 | 5 =
    severity === "critical"
      ? 5
      : severity === "high"
        ? 4
        : severity === "medium"
          ? 3
          : severity === "low"
            ? 2
            : 1;

  return {
    incident_id: asString(input?.incident_id, makeId("INC")),
    title: asString(input?.title, "Unknown incident"),
    severity,
    severity_level: asSeverityLevel(input?.severity_level, defaultLevel),
    confidence_score:
      typeof input?.confidence_score === "number" &&
      Number.isFinite(input.confidence_score)
        ? input.confidence_score
        : 0,
    confidence_reasons: asArray<string>(input?.confidence_reasons),
    confidence_limitations: asArray<string>(input?.confidence_limitations),
    affected_repos: asArray<string>(input?.affected_repos),
    affected_files: asArray<string>(input?.affected_files),
    affected_endpoints: asArray<string>(input?.affected_endpoints),
    affected_database_tables: asArray<string>(input?.affected_database_tables),
    findings: asArray<any>(input?.findings).map(normalizeFinding),
    attack_path: normalizeAttackPath(input?.attack_path),
    related_memory: asArray<any>(input?.related_memory).map(normalizeAIMemory),
    timestamp: typeof input?.timestamp === "string" ? input.timestamp : undefined,
  };
}

export function normalizeBobOutput(input: Partial<BobOutput> | any): BobOutput {
  return {
    attack_type: asString(input?.attack_type, "Unknown attack type"),
    target: asString(input?.target, "Unknown target"),
    severity: asSeverity(input?.severity, "info"),
    confidence_assessment: asString(
      input?.confidence_assessment,
      "No confidence assessment provided."
    ),
    recommended_fixes: asArray<any>(input?.recommended_fixes).map((fix) => ({
      type: asFixType(fix?.type),
      description: asString(fix?.description, "No fix description provided."),
      file: typeof fix?.file === "string" ? fix.file : undefined,
      endpoint: typeof fix?.endpoint === "string" ? fix.endpoint : undefined,
    })),
    generated_security_tests: asArray<any>(input?.generated_security_tests).map(
      (test) => ({
        file: asString(test?.file, "tests/generated_security_test.py"),
        name: asString(test?.name, "generated_security_test"),
        purpose: asString(test?.purpose, "Generated security regression test"),
        code: asString(test?.code),
      })
    ),
    incident_report: asString(
      input?.incident_report,
      "No incident report generated."
    ),
    ai_memory: normalizeAIMemory(input?.ai_memory),
  };
}