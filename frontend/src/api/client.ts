import axios from 'axios';
import type { Finding, Incident, BobOutput } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Set to true to use frontend mock scenarios (no backend needed)
// Set to false to call real backend at port 8000
export const USE_MOCK_DATA = true;

// ─────────────────────────────────────────────
// SCENARIO 1: Credential Leak via Abandoned API
// ─────────────────────────────────────────────

const s1Findings: Finding[] = [
  {
    finding_id: "FIND-001",
    repo_name: "legacy-backend",
    finding_type: "hardcoded_secret",
    category: "secret_exposure",
    severity_hint: "high",
    source: "rust_scanner",
    file: "legacy/old_export_api.py",
    line: 12,
    endpoint: "/api/v1/export-users",
    database_table: null,
    evidence: "Possible API key detected",
    masked_value: "sk_test_****92fa",
    timestamp: "2026-05-16T12:00:00Z"
  },
  {
    finding_id: "FIND-002",
    repo_name: "legacy-backend",
    finding_type: "deprecated_api",
    category: "legacy_api",
    severity_hint: "medium",
    source: "python_analyzer",
    file: "legacy/old_export_api.py",
    line: 8,
    endpoint: "/api/v1/export-users",
    database_table: null,
    evidence: "Deprecated export endpoint still accessible",
    masked_value: null,
    timestamp: "2026-05-16T12:01:00Z"
  },
  {
    finding_id: "FIND-003",
    repo_name: "legacy-backend",
    finding_type: "runtime_anomaly",
    category: "runtime_behavior",
    severity_hint: "medium",
    source: "python_analyzer",
    file: null,
    line: null,
    endpoint: "/api/v1/export-users",
    database_table: null,
    evidence: "Repeated access to deprecated endpoint detected",
    masked_value: null,
    timestamp: "2026-05-16T12:05:00Z"
  },
  {
    finding_id: "FIND-004",
    repo_name: "legacy-backend",
    finding_type: "database_anomaly",
    category: "database_activity",
    severity_hint: "high",
    source: "python_analyzer",
    file: null,
    line: null,
    endpoint: null,
    database_table: "users",
    evidence: "Abnormal read spike on users table",
    masked_value: null,
    timestamp: "2026-05-16T12:06:00Z"
  },
  {
    finding_id: "FIND-005",
    repo_name: "infra-config",
    finding_type: "infrastructure_risk",
    category: "infrastructure",
    severity_hint: "medium",
    source: "rust_scanner",
    file: "gateway.yml",
    line: 45,
    endpoint: "/api/v1/export-users",
    database_table: null,
    evidence: "Legacy endpoint still exposed in gateway configuration",
    masked_value: null,
    timestamp: "2026-05-16T12:02:00Z"
  }
];

const s1Incident: Incident = {
  incident_id: "INC-001",
  title: "Possible credential leakage through exposed abandoned export API",
  severity: "critical",
  severity_level: 5,
  confidence_score: 0.88,
  confidence_reasons: [
    "Hardcoded API key found in legacy code",
    "Deprecated export endpoint is still reachable",
    "Suspicious repeated access detected in logs",
    "Users table showed abnormal read activity"
  ],
  confidence_limitations: [
    "No confirmed external exfiltration destination found",
    "Unable to verify if data was actually exported"
  ],
  affected_repos: ["legacy-backend", "infra-config"],
  affected_files: ["legacy/old_export_api.py", "gateway.yml"],
  affected_endpoints: ["/api/v1/export-users"],
  affected_database_tables: ["users"],
  findings: s1Findings,
  attack_path: {
    nodes: [
      { id: "secret", label: "Hardcoded API Key", type: "secret" },
      { id: "old_api", label: "Abandoned Export API", type: "api" },
      { id: "traffic", label: "Suspicious Requests", type: "runtime" },
      { id: "db", label: "Users Table Read Spike", type: "database" },
      { id: "leak", label: "Possible Data Leak", type: "impact" }
    ],
    edges: [
      { from: "secret", to: "old_api", label: "used by" },
      { from: "old_api", to: "traffic", label: "targeted by" },
      { from: "traffic", to: "db", label: "accesses" },
      { from: "db", to: "leak", label: "may expose" }
    ]
  },
  related_memory: [
    {
      memory_type: "security_prevention_rule",
      incident_pattern: "hardcoded_secret_in_abandoned_export_api",
      root_cause: "A legacy export API contained a static credential and remained reachable.",
      signals_to_watch: [
        "secret in legacy code",
        "deprecated export endpoint",
        "repeated requests to old endpoint",
        "large reads from sensitive database table"
      ],
      prevention_rule: "Flag abandoned export/download APIs that contain static credentials or access sensitive data.",
      recommended_tests: [
        "deprecated endpoint is unreachable",
        "export endpoint requires admin role",
        "secrets are loaded from environment variables"
      ],
      severity_escalation_conditions: [
        "secret appears in logs",
        "endpoint receives unusual traffic",
        "database read spike occurs"
      ]
    }
  ]
};

const s1BobOutput: BobOutput = {
  attack_type: "Credential leakage and abandoned API abuse",
  target: "User export endpoint and users database table",
  severity: "critical",
  confidence_assessment: "High confidence (88%) because secret exposure, deprecated endpoint access, and database read spike are correlated. The attack chain is clear: hardcoded credential → abandoned API → suspicious traffic → database anomaly. However, we lack confirmation of actual data exfiltration.",
  recommended_fixes: [
    { type: "immediate_action", description: "Rotate the exposed API key immediately to prevent further unauthorized access." },
    { type: "code_fix", description: "Move the API key to an environment variable or secret manager (e.g., AWS Secrets Manager, HashiCorp Vault)." },
    { type: "api_fix", description: "Disable or protect /api/v1/export-users endpoint. If needed, require admin authentication and add rate limiting." },
    { type: "config_fix", description: "Remove the deprecated endpoint from gateway.yml or add strict access controls." },
    { type: "test_fix", description: "Add security regression tests to prevent similar issues in the future." }
  ],
  generated_security_tests: [
    {
      file: "tests/test_export_api_security.py",
      name: "test_export_endpoint_requires_admin",
      purpose: "Ensure only admins can access user export endpoint",
      code: `def test_export_endpoint_requires_admin(client):
    response = client.get('/api/v1/export-users')
    assert response.status_code in [401, 403, 410], \\
        "Export endpoint should be protected or disabled"

def test_export_endpoint_rate_limited(client, admin_token):
    headers = {'Authorization': f'Bearer {admin_token}'}
    for _ in range(10):
        response = client.get('/api/v1/export-users', headers=headers)
    assert response.status_code == 429, \\
        "Export endpoint should have rate limiting"`
    },
    {
      file: "tests/test_secret_management.py",
      name: "test_no_hardcoded_secrets",
      purpose: "Verify no hardcoded secrets exist in codebase",
      code: `import re, os

def test_no_hardcoded_secrets():
    secret_patterns = [
        r'sk_test_[a-zA-Z0-9]{24}',
        r'api[_-]?key["\']?\\s*[:=]\\s*["\'][^"\']+["\']'
    ]
    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                with open(os.path.join(root, file)) as f:
                    content = f.read()
                    for pattern in secret_patterns:
                        assert not re.search(pattern, content), \\
                            f"Hardcoded secret found in {file}"`
    }
  ],
  incident_report: `## Security Incident Report

**Incident ID:** INC-001
**Severity:** CRITICAL | **Confidence:** 88%

### Summary
A critical security incident involving a hardcoded API key in an abandoned export API endpoint.
Multiple correlated signals indicate potential credential leakage and unauthorized data access.

### Attack Chain
1. **Hardcoded API Key** — static key in \`legacy/old_export_api.py\`
2. **Abandoned Export API** — deprecated \`/api/v1/export-users\` still reachable
3. **Suspicious Requests** — repeated access attempts detected in logs
4. **Database Anomaly** — abnormal read spike on \`users\` table
5. **Possible Data Leak** — high risk of user data exfiltration

### Immediate Actions (within 1 hour)
1. Rotate the exposed API key
2. Disable /api/v1/export-users endpoint
3. Review access logs for the past 30 days

### Short-term (within 24 hours)
1. Move all API keys to environment variables or secret manager
2. Update gateway.yml to remove deprecated endpoint
3. Implement rate limiting on sensitive endpoints`,
  ai_memory: {
    memory_type: "security_prevention_rule",
    incident_pattern: "hardcoded_secret_in_abandoned_export_api",
    root_cause: "A legacy export API contained a static credential and remained reachable, creating a critical security vulnerability.",
    signals_to_watch: [
      "hardcoded secrets in legacy code paths",
      "deprecated export or download endpoints",
      "repeated requests to old endpoints",
      "large reads from sensitive database tables",
      "infrastructure configs exposing legacy endpoints"
    ],
    prevention_rule: "Flag abandoned export/download APIs that contain static credentials or access sensitive data.",
    recommended_tests: [
      "deprecated endpoints return 410 Gone or 404 Not Found",
      "export endpoints require admin role and authentication",
      "secrets are loaded from environment variables or secret managers"
    ],
    severity_escalation_conditions: [
      "secret appears in application logs",
      "endpoint receives unusual traffic volume",
      "database read spike occurs on sensitive tables"
    ]
  },
  pr_draft: {
    branch_name: "security/fix-abandoned-export-api-INC-001",
    pr_title: "Security Fix: Remove hardcoded secret and secure abandoned export API",
    pr_description: `## Security Incident: INC-001

### Changes
- Removed hardcoded API key from \`legacy/old_export_api.py\`
- Moved API key to environment variable \`EXPORT_API_KEY\`
- Added admin authentication to \`/api/v1/export-users\`
- Implemented rate limiting (10 req/hour)
- Removed deprecated endpoint from \`gateway.yml\`
- Added 3 security regression tests

### Testing
\`\`\`bash
pytest tests/test_export_api_security.py -v
pytest tests/test_secret_management.py -v
\`\`\``,
    files_to_change: [
      "legacy/old_export_api.py",
      "gateway.yml",
      ".env.example",
      "tests/test_export_api_security.py",
      "tests/test_secret_management.py"
    ]
  }
};

// ─────────────────────────────────────────────────
// SCENARIO 2: SQL Injection → Payment Data Exfil
// ─────────────────────────────────────────────────

const s2Findings: Finding[] = [
  {
    finding_id: "FIND-201",
    repo_name: "ecommerce-api",
    finding_type: "hardcoded_secret",
    category: "secret_exposure",
    severity_hint: "critical",
    source: "rust_scanner",
    file: "api/search.py",
    line: 23,
    endpoint: "/api/v2/products/search",
    database_table: null,
    evidence: "Production database password hardcoded in source",
    masked_value: "db_prod_p4ss****mko9",
    timestamp: "2026-05-16T09:14:00Z"
  },
  {
    finding_id: "FIND-202",
    repo_name: "ecommerce-api",
    finding_type: "database_url",
    category: "secret_exposure",
    severity_hint: "critical",
    source: "rust_scanner",
    file: "api/search.py",
    line: 45,
    endpoint: "/api/v2/products/search",
    database_table: null,
    evidence: "f-string SQL query without parameterization: SELECT * FROM products WHERE name='{query}'",
    masked_value: null,
    timestamp: "2026-05-16T09:14:01Z"
  },
  {
    finding_id: "FIND-203",
    repo_name: "ecommerce-api",
    finding_type: "deprecated_api",
    category: "legacy_api",
    severity_hint: "high",
    source: "python_analyzer",
    file: "api/admin_users.py",
    line: 7,
    endpoint: "/api/v1/admin/users",
    database_table: null,
    evidence: "Admin endpoint with no authentication check — @app.route with no @login_required",
    masked_value: null,
    timestamp: "2026-05-16T09:15:00Z"
  },
  {
    finding_id: "FIND-204",
    repo_name: "ecommerce-api",
    finding_type: "runtime_anomaly",
    category: "runtime_behavior",
    severity_hint: "critical",
    source: "python_analyzer",
    file: null,
    line: null,
    endpoint: "/api/v2/products/search",
    database_table: null,
    evidence: "UNION SELECT detected in query param: ?q=' UNION SELECT card_number,cvv,expiry FROM payment_cards--",
    masked_value: null,
    timestamp: "2026-05-16T09:22:17Z"
  },
  {
    finding_id: "FIND-205",
    repo_name: "ecommerce-api",
    finding_type: "database_anomaly",
    category: "database_activity",
    severity_hint: "critical",
    source: "python_analyzer",
    file: null,
    line: null,
    endpoint: null,
    database_table: "payment_cards",
    evidence: "12,847 rows read from payment_cards in 4 seconds — 340x above baseline",
    masked_value: null,
    timestamp: "2026-05-16T09:22:19Z"
  }
];

const s2Incident: Incident = {
  incident_id: "INC-002",
  title: "SQL injection exploit chain targeting payment card data via unprotected search endpoint",
  severity: "critical",
  severity_level: 5,
  confidence_score: 0.93,
  confidence_reasons: [
    "UNION SELECT payload captured verbatim in access logs",
    "payment_cards table read spike directly follows malicious request (2-second delta)",
    "Search endpoint confirmed to use unsanitized f-string query",
    "Hardcoded DB credential gives attacker direct DB access if app-layer bypass fails"
  ],
  confidence_limitations: [
    "Cannot confirm whether full card numbers were successfully returned to attacker",
    "TLS termination at load balancer — response body not logged"
  ],
  affected_repos: ["ecommerce-api"],
  affected_files: ["api/search.py", "api/admin_users.py"],
  affected_endpoints: ["/api/v2/products/search", "/api/v1/admin/users"],
  affected_database_tables: ["payment_cards", "orders"],
  findings: s2Findings,
  attack_path: {
    nodes: [
      { id: "sqli", label: "SQLi Payload in Search", type: "runtime" },
      { id: "search_ep", label: "Unparameterized Search Endpoint", type: "api" },
      { id: "db_cred", label: "Hardcoded DB Credential", type: "secret" },
      { id: "payment_db", label: "payment_cards Table (12K rows)", type: "database" },
      { id: "admin_ep", label: "Unauthenticated Admin Endpoint", type: "api" },
      { id: "breach", label: "PCI Data Breach", type: "impact" }
    ],
    edges: [
      { from: "sqli", to: "search_ep", label: "injected into" },
      { from: "search_ep", to: "payment_db", label: "UNION SELECT" },
      { from: "db_cred", to: "payment_db", label: "direct access" },
      { from: "admin_ep", to: "payment_db", label: "bypasses auth" },
      { from: "payment_db", to: "breach", label: "12,847 rows exposed" }
    ]
  },
  related_memory: [
    {
      memory_type: "security_prevention_rule",
      incident_pattern: "sqli_unprotected_admin_payment_data",
      root_cause: "Search endpoint used f-string query construction instead of parameterized queries, and admin endpoint lacked authentication.",
      signals_to_watch: [
        "UNION SELECT in request parameters",
        "admin endpoints without @login_required",
        "f-string SQL patterns in source",
        "sudden spike in payment_cards table reads"
      ],
      prevention_rule: "All SQL queries must use parameterized statements. Admin endpoints must have authentication. Payment data tables must have access alerts.",
      recommended_tests: [
        "search endpoint rejects UNION SELECT payloads",
        "admin endpoints return 401 without valid token",
        "no f-string SQL in codebase (AST check)",
        "payment_cards read rate alerting active"
      ],
      severity_escalation_conditions: [
        "UNION SELECT in logs followed by large table read",
        "payment_cards rows read > 100x baseline",
        "admin endpoint access from unknown IP"
      ]
    }
  ]
};

const s2BobOutput: BobOutput = {
  attack_type: "SQL Injection leading to payment card data exfiltration",
  target: "ecommerce-api search endpoint and payment_cards database table",
  severity: "critical",
  confidence_assessment: "Very high confidence (93%). UNION SELECT payload was captured verbatim in logs, and a payment_cards read spike of 340x baseline occurred 2 seconds later. The attack chain is unambiguous. Only uncertainty: whether card data was successfully returned through TLS-terminated connection.",
  recommended_fixes: [
    { type: "immediate_action", description: "Take /api/v2/products/search offline or add a WAF rule blocking UNION SELECT patterns immediately." },
    { type: "immediate_action", description: "Rotate the hardcoded production database password (FIND-201) — treat it as compromised." },
    { type: "code_fix", description: "Replace f-string query in api/search.py:45 with parameterized query: cursor.execute('SELECT * FROM products WHERE name = %s', (query,))" },
    { type: "api_fix", description: "Add @login_required decorator to /api/v1/admin/users in api/admin_users.py:7" },
    { type: "config_fix", description: "Enable PCI DSS alerting on payment_cards table — alert when reads exceed 200x baseline within 60 seconds." },
    { type: "test_fix", description: "Add SQL injection regression tests and static analysis rule to CI/CD pipeline." }
  ],
  generated_security_tests: [
    {
      file: "tests/test_search_sqli.py",
      name: "test_search_rejects_union_select",
      purpose: "Verify search endpoint blocks SQL injection payloads",
      code: `import pytest

SQLI_PAYLOADS = [
    "' UNION SELECT card_number,cvv,expiry FROM payment_cards--",
    "' OR 1=1--",
    "'; DROP TABLE products--",
    "' AND SLEEP(5)--",
]

def test_search_rejects_sqli(client):
    for payload in SQLI_PAYLOADS:
        resp = client.get(f'/api/v2/products/search?q={payload}')
        assert resp.status_code in [400, 403], \\
            f"SQLi payload not blocked: {payload}"
        assert 'payment_cards' not in resp.text.lower()`
    },
    {
      file: "tests/test_admin_auth.py",
      name: "test_admin_requires_authentication",
      purpose: "Ensure admin endpoints reject unauthenticated requests",
      code: `def test_admin_users_requires_auth(client):
    resp = client.get('/api/v1/admin/users')
    assert resp.status_code in [401, 403], \\
        "Admin endpoint must require authentication"

def test_admin_users_with_valid_token(client, admin_token):
    headers = {'Authorization': f'Bearer {admin_token}'}
    resp = client.get('/api/v1/admin/users', headers=headers)
    assert resp.status_code == 200`
    },
    {
      file: "tests/test_no_fstring_sql.py",
      name: "test_no_fstring_sql_patterns",
      purpose: "AST check to ensure no f-string SQL in codebase",
      code: `import ast, os, glob

def test_no_fstring_sql():
    sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP']
    for path in glob.glob('api/**/*.py', recursive=True):
        tree = ast.parse(open(path).read())
        for node in ast.walk(tree):
            if isinstance(node, ast.JoinedStr):  # f-string
                src = ast.unparse(node)
                for kw in sql_keywords:
                    assert kw not in src.upper(), \\
                        f"f-string SQL found in {path}: {src[:60]}"`
    }
  ],
  incident_report: `## Security Incident Report

**Incident ID:** INC-002
**Severity:** CRITICAL | **Confidence:** 93% | **PCI DSS Scope:** YES

### Summary
A SQL injection attack was executed against the product search endpoint, exploiting an unparameterized f-string query to extract data from the \`payment_cards\` table.
12,847 rows were read in 4 seconds — 340x above baseline.

### Attack Chain
1. **SQLi Payload** — \`' UNION SELECT card_number,cvv,expiry FROM payment_cards--\` in search param
2. **Vulnerable Endpoint** — \`api/search.py:45\` uses f-string query construction
3. **Hardcoded DB Credential** — \`db_prod_p4ss****mko9\` allows direct DB fallback
4. **Payment Cards Breach** — 12,847 rows read in 4 seconds
5. **Admin Bypass** — \`/api/v1/admin/users\` accessible without authentication

### PCI DSS Implications
- Cardholder data (PAN, CVV, expiry) potentially exfiltrated
- PCI DSS Requirement 6.3.1 violated: unsanitized input
- Mandatory breach notification may be required within 72 hours

### Immediate Actions (within 1 hour)
1. Block UNION SELECT patterns at WAF level
2. Take search endpoint offline until patched
3. Rotate production database credentials
4. Notify legal/compliance team re: PCI DSS breach notification obligation`,
  ai_memory: {
    memory_type: "security_prevention_rule",
    incident_pattern: "sqli_fstring_payment_data_exfil",
    root_cause: "f-string SQL query construction allowed UNION SELECT injection; no WAF rule for payment table access patterns.",
    signals_to_watch: [
      "UNION SELECT in any request parameter",
      "payment_cards or credit_cards table reads > 100x baseline",
      "admin endpoints without authentication decorator",
      "f-string patterns adjacent to SQL keywords in source"
    ],
    prevention_rule: "Enforce parameterized queries via AST linting in CI. Payment table access triggers alert at 100x baseline.",
    recommended_tests: [
      "SQLI payload list against all endpoints returning DB data",
      "Admin endpoints return 401 without valid JWT",
      "payment_cards row-read rate alerting in staging"
    ],
    severity_escalation_conditions: [
      "SQLi payload in logs AND payment table spike within 60 seconds",
      "admin endpoint accessed from external IP",
      "database credential in plaintext detected in any log"
    ]
  },
  pr_draft: {
    branch_name: "security/fix-sqli-payment-breach-INC-002",
    pr_title: "Security Fix: Parameterize SQL queries and add admin auth (INC-002)",
    pr_description: `## Security Incident: INC-002 — PCI DSS Scope

### Root Cause
f-string SQL in \`api/search.py:45\` allowed UNION SELECT injection into \`payment_cards\`.

### Changes
- \`api/search.py:45\` — replaced f-string with parameterized query
- \`api/search.py:23\` — removed hardcoded DB password, use \`os.environ['DB_PASSWORD']\`
- \`api/admin_users.py:7\` — added \`@login_required\` decorator
- Added WAF rule: block UNION SELECT in query params
- 3 new security regression tests

### Testing
\`\`\`bash
pytest tests/test_search_sqli.py -v
pytest tests/test_admin_auth.py -v
pytest tests/test_no_fstring_sql.py -v
\`\`\`

> **IMPORTANT:** Rotate \`DB_PASSWORD\` before deployment. Notify compliance team.`,
    files_to_change: [
      "api/search.py",
      "api/admin_users.py",
      ".env.example",
      "tests/test_search_sqli.py",
      "tests/test_admin_auth.py",
      "tests/test_no_fstring_sql.py"
    ]
  }
};

// ─────────────────────────────────────────────────────
// SCENARIO 3: Insider Threat — Anomalous Data Access
// ─────────────────────────────────────────────────────

const s3Findings: Finding[] = [
  {
    finding_id: "FIND-301",
    repo_name: "internal-portal",
    finding_type: "runtime_anomaly",
    category: "runtime_behavior",
    severity_hint: "high",
    source: "python_analyzer",
    file: null,
    line: null,
    endpoint: "/api/v1/reports/export",
    database_table: "financial_records",
    evidence: "user_id=1042 exported 50,000 records at 2:47 AM — 8x their 30-day average",
    masked_value: null,
    timestamp: "2026-05-15T02:47:31Z"
  },
  {
    finding_id: "FIND-302",
    repo_name: "internal-portal",
    finding_type: "runtime_anomaly",
    category: "runtime_behavior",
    severity_hint: "medium",
    source: "python_analyzer",
    file: null,
    line: null,
    endpoint: "/api/v1/reports/financial",
    database_table: "financial_records",
    evidence: "Access to quarterly financial reports outside business hours (02:31 AM–03:14 AM) — user has never accessed this endpoint before",
    masked_value: null,
    timestamp: "2026-05-15T02:31:00Z"
  },
  {
    finding_id: "FIND-303",
    repo_name: "internal-portal",
    finding_type: "runtime_anomaly",
    category: "runtime_behavior",
    severity_hint: "high",
    source: "python_analyzer",
    file: null,
    line: null,
    endpoint: null,
    database_table: null,
    evidence: "Login from 185.220.101.45 (known Tor exit node, AS209201) — user's normal location: Chicago IL",
    masked_value: null,
    timestamp: "2026-05-15T02:28:44Z"
  },
  {
    finding_id: "FIND-304",
    repo_name: "internal-portal",
    finding_type: "runtime_anomaly",
    category: "runtime_behavior",
    severity_hint: "medium",
    source: "python_analyzer",
    file: null,
    line: null,
    endpoint: "/auth/mfa",
    database_table: null,
    evidence: "15 failed MFA attempts in 3 minutes before successful auth — possible MFA fatigue attack",
    masked_value: null,
    timestamp: "2026-05-15T02:26:17Z"
  },
  {
    finding_id: "FIND-305",
    repo_name: "internal-portal",
    finding_type: "infrastructure_risk",
    category: "infrastructure",
    severity_hint: "high",
    source: "python_analyzer",
    file: null,
    line: null,
    endpoint: null,
    database_table: null,
    evidence: "2.3 GB upload to s3://ext-transfer-4829f — bucket not in approved vendor list, no encryption at rest",
    masked_value: null,
    timestamp: "2026-05-15T03:09:52Z"
  }
];

const s3Incident: Incident = {
  incident_id: "INC-003",
  title: "Suspected insider threat: compromised credentials used for bulk financial data exfiltration",
  severity: "high",
  severity_level: 4,
  confidence_score: 0.76,
  confidence_reasons: [
    "Tor exit node login directly precedes bulk export — 18 minute gap",
    "MFA fatigue pattern (15 failures then success) suggests credential was stolen, not insider",
    "Export volume (50K records) is 8x user's historical average",
    "Upload destination is unknown external S3 bucket outside approved vendor list"
  ],
  confidence_limitations: [
    "Could be legitimate: user may have authorized off-hours work",
    "No confirmed data receipt at external destination — S3 bucket may be unmonitored",
    "MFA success could mean user approved notification, not fatigue attack"
  ],
  affected_repos: ["internal-portal"],
  affected_files: [],
  affected_endpoints: ["/api/v1/reports/export", "/api/v1/reports/financial", "/auth/mfa"],
  affected_database_tables: ["financial_records"],
  findings: s3Findings,
  attack_path: {
    nodes: [
      { id: "mfa", label: "MFA Fatigue Attack", type: "runtime" },
      { id: "tor", label: "Tor Exit Node Login", type: "infrastructure" },
      { id: "session", label: "Stolen Active Session", type: "secret" },
      { id: "fin_report", label: "Financial Reports Access", type: "api" },
      { id: "bulk_export", label: "50K Record Bulk Export", type: "database" },
      { id: "s3_upload", label: "2.3 GB to Unknown S3 Bucket", type: "impact" }
    ],
    edges: [
      { from: "mfa", to: "session", label: "bypasses" },
      { from: "tor", to: "session", label: "anonymizes attacker" },
      { from: "session", to: "fin_report", label: "accesses" },
      { from: "fin_report", to: "bulk_export", label: "triggers" },
      { from: "bulk_export", to: "s3_upload", label: "exfiltrated to" }
    ]
  },
  related_memory: [
    {
      memory_type: "security_prevention_rule",
      incident_pattern: "mfa_fatigue_bulk_export_exfil",
      root_cause: "MFA push fatigue allowed credential takeover; bulk export endpoint lacked volume-based anomaly detection.",
      signals_to_watch: [
        "multiple MFA failures then success within 5 minutes",
        "login from Tor/VPN followed by sensitive data access",
        "export volume > 3x user historical average",
        "upload to S3 bucket not in approved vendor list"
      ],
      prevention_rule: "Block accounts after 5 consecutive MFA failures for 30 minutes. Alert on bulk exports > 2x user average. S3 uploads require pre-approved bucket allowlist.",
      recommended_tests: [
        "account lockout after MFA failure threshold",
        "bulk export triggers alert above volume threshold",
        "S3 upload to unknown bucket is blocked"
      ],
      severity_escalation_conditions: [
        "upload to external destination confirmed received",
        "financial records include unreported earnings",
        "user account shows no legitimate business reason for access"
      ]
    }
  ]
};

const s3BobOutput: BobOutput = {
  attack_type: "MFA fatigue credential takeover leading to insider-style data exfiltration",
  target: "internal-portal financial records and external S3 bucket",
  severity: "high",
  confidence_assessment: "Moderate-high confidence (76%). The behavioral sequence — Tor login → MFA fatigue → after-hours bulk export → unknown S3 upload — is a textbook credential takeover pattern. However, we cannot rule out a legitimate authorized session. The 2.3 GB upload to an unknown bucket is the most actionable indicator.",
  recommended_fixes: [
    { type: "immediate_action", description: "Suspend user_id=1042 session tokens immediately and force re-authentication from a known device and location." },
    { type: "immediate_action", description: "Block outbound traffic to s3://ext-transfer-4829f and identify bucket owner — if external, initiate data deletion request." },
    { type: "api_fix", description: "Add volume-based rate limiting to /api/v1/reports/export: alert when single session exports > 5,000 records, require manager approval above 10,000." },
    { type: "config_fix", description: "Enable number-matching MFA (show code on device before approving push) to defeat fatigue attacks." },
    { type: "config_fix", description: "Enable geo-fencing: block logins from Tor/VPN exit nodes for accounts with access to financial_records." },
    { type: "test_fix", description: "Add behavioral anomaly regression tests for bulk export and MFA failure thresholds." }
  ],
  generated_security_tests: [
    {
      file: "tests/test_bulk_export_limits.py",
      name: "test_bulk_export_requires_approval_above_threshold",
      purpose: "Ensure large data exports trigger approval workflow",
      code: `def test_bulk_export_triggers_alert(client, user_token, mock_alert):
    headers = {'Authorization': f'Bearer {user_token}'}
    resp = client.post('/api/v1/reports/export',
        headers=headers,
        json={'limit': 15000, 'table': 'financial_records'})
    assert resp.status_code == 202, "Large export should require approval"
    assert mock_alert.called, "Security alert should be triggered"

def test_bulk_export_normal_volume_allowed(client, user_token):
    headers = {'Authorization': f'Bearer {user_token}'}
    resp = client.post('/api/v1/reports/export',
        headers=headers,
        json={'limit': 100, 'table': 'financial_records'})
    assert resp.status_code == 200`
    },
    {
      file: "tests/test_mfa_lockout.py",
      name: "test_mfa_lockout_after_failures",
      purpose: "Verify account lockout after repeated MFA failures",
      code: `def test_account_locked_after_mfa_failures(client, user_credentials):
    for i in range(5):
        resp = client.post('/auth/mfa', json={
            **user_credentials,
            'mfa_code': '000000'  # wrong code
        })
    # 6th attempt should be blocked
    resp = client.post('/auth/mfa', json={
        **user_credentials,
        'mfa_code': '000000'
    })
    assert resp.status_code == 429, \\
        "Account should be locked after 5 MFA failures"
    assert 'retry_after' in resp.json()`
    }
  ],
  incident_report: `## Security Incident Report

**Incident ID:** INC-003
**Severity:** HIGH | **Confidence:** 76% | **Type:** Credential Takeover / Data Exfiltration

### Summary
A possible credential takeover via MFA fatigue resulted in after-hours access to financial records
and a 2.3 GB upload to an unknown external S3 bucket. Attribution is not yet confirmed.

### Attack Chain
1. **MFA Fatigue** — 15 failed MFA pushes then success at 02:26 AM
2. **Tor Exit Node Login** — login from 185.220.101.45, user normally in Chicago
3. **Financial Data Access** — quarterly reports accessed, never previously accessed by this user
4. **Bulk Export** — 50,000 records (8x user average) exported at 02:47 AM
5. **External Upload** — 2.3 GB to s3://ext-transfer-4829f (not in approved vendor list)

### Why 76% (not higher)
- User may have authorized off-hours work
- S3 upload destination not confirmed as malicious
- No data confirmed received at external destination

### Immediate Actions (within 2 hours)
1. Suspend user_id=1042 all active sessions
2. Block s3://ext-transfer-4829f at network egress
3. Interview user — determine if authorized or account takeover
4. Review financial_records for PII/sensitive classification`,
  ai_memory: {
    memory_type: "security_prevention_rule",
    incident_pattern: "mfa_fatigue_after_hours_bulk_exfil",
    root_cause: "Push-based MFA susceptible to fatigue; bulk export endpoint had no volume anomaly detection; S3 egress had no allowlist enforcement.",
    signals_to_watch: [
      "5+ MFA failures then success within 10 minutes",
      "login from Tor/proxy immediately before sensitive data access",
      "export volume > 3x user 30-day average",
      "S3 upload to bucket not in approved vendor list"
    ],
    prevention_rule: "MFA fatigue mitigations (number-match or lockout after 5 failures). Export volume anomaly alerting. S3 egress allowlist enforcement.",
    recommended_tests: [
      "MFA lockout triggers after failure threshold",
      "bulk export above threshold requires approval workflow",
      "S3 upload to unknown bucket is blocked at network level"
    ],
    severity_escalation_conditions: [
      "external bucket confirmed to have received data",
      "user denies authorizing the session",
      "financial data includes material non-public information"
    ]
  },
  pr_draft: {
    branch_name: "security/fix-mfa-bulk-export-INC-003",
    pr_title: "Security: MFA lockout + bulk export approval workflow (INC-003)",
    pr_description: `## Security Incident: INC-003

### Root Cause
Push MFA susceptible to fatigue attacks; no volume-based anomaly detection on export endpoint.

### Changes
- Added MFA failure lockout: 5 failures → 30-min block
- Added export volume alerting: > 5K records triggers alert, > 10K requires manager approval
- Added geo-fencing: Tor/VPN blocked for financial_records scope
- Added S3 egress allowlist enforcement
- 2 new behavioral security tests

### Testing
\`\`\`bash
pytest tests/test_bulk_export_limits.py -v
pytest tests/test_mfa_lockout.py -v
\`\`\`

> **NOTE:** Confirm with HR/Legal whether user_id=1042 incident requires formal investigation.`,
    files_to_change: [
      "auth/mfa_handler.py",
      "api/reports/export.py",
      "config/s3_allowlist.json",
      "tests/test_bulk_export_limits.py",
      "tests/test_mfa_lockout.py"
    ]
  }
};

// ─────────────────────────────────
// Scenario Registry
// ─────────────────────────────────

export type ScenarioMeta = {
  id: string;
  label: string;
  subtitle: string;
  severity: 'critical' | 'high';
  findings: Finding[];
  incident: Incident;
  bobOutput: BobOutput;
};

export const SCENARIOS: ScenarioMeta[] = [
  {
    id: 'inc-001',
    label: 'Credential Leak',
    subtitle: 'Abandoned API + Hardcoded Secret',
    severity: 'critical',
    findings: s1Findings,
    incident: s1Incident,
    bobOutput: s1BobOutput
  },
  {
    id: 'inc-002',
    label: 'SQL Injection',
    subtitle: 'Payment Data Exfiltration Chain',
    severity: 'critical',
    findings: s2Findings,
    incident: s2Incident,
    bobOutput: s2BobOutput
  },
  {
    id: 'inc-003',
    label: 'Insider Threat',
    subtitle: 'MFA Fatigue + Bulk Data Exfil',
    severity: 'high',
    findings: s3Findings,
    incident: s3Incident,
    bobOutput: s3BobOutput
  }
];

// ─────────────────────────────────
// API Client
// ─────────────────────────────────

export const apiClient = {
  async getFindings(scenarioId = 'inc-001', useMock?: boolean): Promise<Finding[]> {
    const shouldUseMock = useMock !== undefined ? useMock : USE_MOCK_DATA;
    if (shouldUseMock) {
      const s = SCENARIOS.find(x => x.id === scenarioId);
      return Promise.resolve(s?.findings ?? s1Findings);
    }
    const response = await axios.get(`${API_BASE_URL}/api/findings`);
    return response.data;
  },

  async getIncidents(scenarioId = 'inc-001', useMock?: boolean): Promise<Incident[]> {
    const shouldUseMock = useMock !== undefined ? useMock : USE_MOCK_DATA;
    if (shouldUseMock) {
      const s = SCENARIOS.find(x => x.id === scenarioId);
      return Promise.resolve([s?.incident ?? s1Incident]);
    }
    const response = await axios.get(`${API_BASE_URL}/api/incidents`);
    return response.data;
  },

  async getIncident(id: string, scenarioId = 'inc-001', useMock?: boolean): Promise<Incident> {
    const shouldUseMock = useMock !== undefined ? useMock : USE_MOCK_DATA;
    if (shouldUseMock) {
      const s = SCENARIOS.find(x => x.id === scenarioId);
      return Promise.resolve(s?.incident ?? s1Incident);
    }
    const response = await axios.get(`${API_BASE_URL}/api/incidents/${id}`);
    return response.data;
  },

  async getBobAnalysis(incidentId: string, scenarioId = 'inc-001', useMock?: boolean): Promise<BobOutput> {
    const shouldUseMock = useMock !== undefined ? useMock : USE_MOCK_DATA;
    if (shouldUseMock) {
      const s = SCENARIOS.find(x => x.id === scenarioId);
      return Promise.resolve(s?.bobOutput ?? s1BobOutput);
    }
    const response = await axios.post(`${API_BASE_URL}/api/incidents/${incidentId}/analyze-with-bob`);
    return response.data;
  },

  async runScan(params: { paths: string[]; use_mock: boolean; use_bob: boolean }): Promise<any> {
    const response = await axios.post(`${API_BASE_URL}/api/analyze`, params);
    return response.data;
  }
};

// Legacy named exports for backward compatibility
export const mockFindings = s1Findings;
export const mockIncident = s1Incident;
export const mockBobOutput = s1BobOutput;

// Made with Bob
