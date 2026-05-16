import axios from 'axios';
import type { Finding, Incident, BobOutput } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Mock mode flag - set to true for demo without backend
const USE_MOCK_DATA = true;

// Mock data
const mockFindings: Finding[] = [
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

const mockIncident: Incident = {
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
  findings: mockFindings,
  attack_path: {
    nodes: [
      {
        id: "secret",
        label: "Hardcoded API Key",
        type: "secret"
      },
      {
        id: "old_api",
        label: "Abandoned Export API",
        type: "api"
      },
      {
        id: "traffic",
        label: "Suspicious Requests",
        type: "runtime"
      },
      {
        id: "db",
        label: "Users Table Read Spike",
        type: "database"
      },
      {
        id: "leak",
        label: "Possible Data Leak",
        type: "impact"
      }
    ],
    edges: [
      {
        from: "secret",
        to: "old_api",
        label: "used by"
      },
      {
        from: "old_api",
        to: "traffic",
        label: "targeted by"
      },
      {
        from: "traffic",
        to: "db",
        label: "accesses"
      },
      {
        from: "db",
        to: "leak",
        label: "may expose"
      }
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

const mockBobOutput: BobOutput = {
  attack_type: "Credential leakage and abandoned API abuse",
  target: "User export endpoint and users database table",
  severity: "critical",
  confidence_assessment: "High confidence (88%) because secret exposure, deprecated endpoint access, and database read spike are correlated. The attack chain is clear: hardcoded credential → abandoned API → suspicious traffic → database anomaly. However, we lack confirmation of actual data exfiltration.",
  recommended_fixes: [
    {
      type: "immediate_action",
      description: "Rotate the exposed API key immediately to prevent further unauthorized access."
    },
    {
      type: "code_fix",
      description: "Move the API key to an environment variable or secret manager (e.g., AWS Secrets Manager, HashiCorp Vault)."
    },
    {
      type: "api_fix",
      description: "Disable or protect /api/v1/export-users endpoint. If needed, require admin authentication and add rate limiting."
    },
    {
      type: "config_fix",
      description: "Remove the deprecated endpoint from gateway.yml or add strict access controls."
    },
    {
      type: "test_fix",
      description: "Add security regression tests to prevent similar issues in the future."
    }
  ],
  generated_security_tests: [
    {
      file: "tests/test_export_api_security.py",
      name: "test_export_endpoint_requires_admin",
      purpose: "Ensure only admins can access user export endpoint",
      code: `def test_export_endpoint_requires_admin(client):
    """Test that export endpoint requires admin authentication"""
    response = client.get('/api/v1/export-users')
    assert response.status_code in [401, 403, 410], \\
        "Export endpoint should be protected or disabled"
    
def test_export_endpoint_rate_limited(client, admin_token):
    """Test that export endpoint has rate limiting"""
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
      code: `import re
import os

def test_no_hardcoded_secrets():
    """Scan for hardcoded API keys and secrets"""
    secret_patterns = [
        r'sk_test_[a-zA-Z0-9]{24}',
        r'sk_live_[a-zA-Z0-9]{24}',
        r'api[_-]?key["\']?\\s*[:=]\\s*["\'][^"\']+["\']'
    ]
    
    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                    for pattern in secret_patterns:
                        assert not re.search(pattern, content), \\
                            f"Potential hardcoded secret found in {filepath}"`
    },
    {
      file: "tests/test_database_access.py",
      name: "test_users_table_access_logged",
      purpose: "Ensure all users table access is properly logged and monitored",
      code: `def test_users_table_access_logged(db_session, caplog):
    """Test that users table access is logged"""
    # Simulate a query to users table
    db_session.execute("SELECT * FROM users LIMIT 1")
    
    # Check that access was logged
    assert any("users table accessed" in record.message 
               for record in caplog.records), \\
        "Users table access should be logged for monitoring"`
    }
  ],
  incident_report: `## 🚨 Security Incident Report

**Incident ID:** INC-001  
**Severity:** CRITICAL  
**Confidence:** 88%  
**Date:** 2026-05-16

### Executive Summary

A critical security incident has been detected involving a hardcoded API key in an abandoned export API endpoint. The system has correlated multiple security signals indicating potential credential leakage and unauthorized data access.

### Attack Chain

1. **Hardcoded API Key** - A static API key was discovered in \`legacy/old_export_api.py\`
2. **Abandoned Export API** - The deprecated endpoint \`/api/v1/export-users\` remains accessible
3. **Suspicious Requests** - Repeated access attempts to the old endpoint were detected
4. **Database Anomaly** - Abnormal read spike on the \`users\` table
5. **Possible Data Leak** - High risk of user data exfiltration

### Affected Assets

- **Repositories:** legacy-backend, infra-config
- **Files:** legacy/old_export_api.py, gateway.yml
- **Endpoints:** /api/v1/export-users
- **Database Tables:** users

### Evidence

- **FIND-001:** Hardcoded secret detected (sk_test_****92fa)
- **FIND-002:** Deprecated API endpoint still accessible
- **FIND-003:** Repeated suspicious access patterns
- **FIND-004:** Users table read spike (abnormal activity)
- **FIND-005:** Legacy endpoint exposed in gateway configuration

### Confidence Assessment

**Score:** 88% (High Confidence)

**Supporting Factors:**
- Clear correlation between secret exposure and API access
- Multiple independent signals confirm the attack pattern
- Database activity aligns with endpoint access timeline
- Infrastructure configuration confirms endpoint exposure

**Limitations:**
- No confirmed external exfiltration destination
- Unable to verify if data was actually exported

### Recommended Actions

#### Immediate (Within 1 hour)
1. Rotate the exposed API key
2. Disable /api/v1/export-users endpoint
3. Review access logs for the past 30 days

#### Short-term (Within 24 hours)
1. Move all API keys to environment variables or secret manager
2. Update gateway.yml to remove deprecated endpoint
3. Implement rate limiting on sensitive endpoints
4. Add authentication requirements for data export operations

#### Long-term (Within 1 week)
1. Conduct full security audit of legacy codebase
2. Implement automated secret scanning in CI/CD pipeline
3. Add database access monitoring and alerting
4. Deploy security regression tests

### Generated Security Tests

3 security tests have been automatically generated to prevent regression:
- test_export_endpoint_requires_admin
- test_no_hardcoded_secrets
- test_users_table_access_logged

### AI Memory Created

A new security prevention rule has been stored in the AI memory system to detect similar patterns in the future.

---

**Report Generated by:** IBM Bob Sentinel  
**Analysis Engine:** IBM Bob AI Reasoning Layer`,
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
    prevention_rule: "Flag abandoned export/download APIs that contain static credentials or access sensitive data. Correlate with runtime traffic and database activity.",
    recommended_tests: [
      "deprecated endpoints return 410 Gone or 404 Not Found",
      "export endpoints require admin role and authentication",
      "secrets are loaded from environment variables or secret managers",
      "database access to sensitive tables is logged and monitored",
      "rate limiting is enforced on data export operations"
    ],
    severity_escalation_conditions: [
      "secret appears in application logs",
      "endpoint receives unusual traffic volume",
      "database read spike occurs on sensitive tables",
      "multiple findings correlate into attack chain",
      "infrastructure still exposes deprecated endpoints"
    ]
  },
  pr_draft: {
    branch_name: "security/fix-abandoned-export-api-INC-001",
    pr_title: "🔒 Security Fix: Remove hardcoded secret and secure abandoned export API",
    pr_description: `## Security Incident: INC-001

This PR addresses a critical security incident involving credential leakage through an abandoned export API.

### Changes

#### 1. Remove Hardcoded API Key
- ✅ Removed hardcoded API key from \`legacy/old_export_api.py\`
- ✅ Moved API key to environment variable \`EXPORT_API_KEY\`
- ✅ Updated \`.env.example\` with placeholder

#### 2. Secure Export Endpoint
- ✅ Added admin authentication requirement to \`/api/v1/export-users\`
- ✅ Implemented rate limiting (10 requests per hour)
- ✅ Added audit logging for all export operations

#### 3. Infrastructure Updates
- ✅ Removed deprecated endpoint from \`gateway.yml\`
- ✅ Added strict access controls in gateway configuration

#### 4. Security Tests
- ✅ Added \`test_export_endpoint_requires_admin\`
- ✅ Added \`test_no_hardcoded_secrets\`
- ✅ Added \`test_users_table_access_logged\`

### Security Impact

**Before:**
- Hardcoded API key exposed in source code
- Deprecated endpoint accessible without authentication
- No rate limiting or monitoring

**After:**
- API key stored securely in environment variables
- Endpoint requires admin authentication
- Rate limiting and audit logging enabled
- Automated tests prevent regression

### Testing

\`\`\`bash
# Run security tests
pytest tests/test_export_api_security.py -v
pytest tests/test_secret_management.py -v
pytest tests/test_database_access.py -v
\`\`\`

### Deployment Notes

1. Set \`EXPORT_API_KEY\` environment variable before deployment
2. Rotate the old API key immediately after deployment
3. Monitor logs for any unauthorized access attempts
4. Review database access logs for the past 30 days

### Related

- Incident Report: INC-001
- Severity: Critical
- Confidence: 88%
- AI Memory: security_prevention_rule created

---

**Generated by IBM Bob Sentinel**  
**Reviewed by:** [Pending Security Team Review]`,
    files_to_change: [
      "legacy/old_export_api.py",
      "gateway.yml",
      ".env.example",
      "tests/test_export_api_security.py",
      "tests/test_secret_management.py",
      "tests/test_database_access.py",
      "requirements.txt"
    ]
  }
};

// API client functions
export const apiClient = {
  async getFindings(): Promise<Finding[]> {
    if (USE_MOCK_DATA) {
      return Promise.resolve(mockFindings);
    }
    const response = await axios.get(`${API_BASE_URL}/api/findings`);
    return response.data;
  },

  async getIncidents(): Promise<Incident[]> {
    if (USE_MOCK_DATA) {
      return Promise.resolve([mockIncident]);
    }
    const response = await axios.get(`${API_BASE_URL}/api/incidents`);
    return response.data;
  },

  async getIncident(id: string): Promise<Incident> {
    if (USE_MOCK_DATA) {
      return Promise.resolve(mockIncident);
    }
    const response = await axios.get(`${API_BASE_URL}/api/incidents/${id}`);
    return response.data;
  },

  async getBobAnalysis(incidentId: string): Promise<BobOutput> {
    if (USE_MOCK_DATA) {
      return Promise.resolve(mockBobOutput);
    }
    const response = await axios.post(`${API_BASE_URL}/api/incidents/${incidentId}/analyze-with-bob`);
    return response.data;
  }
};

// Export mock data for direct use in components if needed
export { mockFindings, mockIncident, mockBobOutput };

// Made with Bob
