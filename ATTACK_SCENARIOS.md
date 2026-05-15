# Attack Scenarios Specification

This document defines realistic, coordinated multi-vector attack scenarios for testing the AI-powered security analyst system.

## Overview

Each scenario represents a sophisticated, multi-stage attack that combines multiple vulnerabilities and techniques. The system must detect individual findings AND correlate them into unified incidents.

## Scenario 1: Coordinated Credential Theft and Data Exfiltration

### Attack ID
`SCENARIO-001`

### Attack Name
"The Midnight Heist" - AWS Credential Abuse Leading to Customer Data Breach

### Severity
**Level 5 (Critical)**

### Attack Timeline

```mermaid
gantt
    title Scenario 1 Attack Timeline
    dateFormat HH:mm
    section Reconnaissance
    Scan public repos     :01:00, 30m
    section Initial Access
    Discover leaked AWS key :01:30, 15m
    section Credential Access
    Test AWS credentials    :01:45, 15m
    section Discovery
    List S3 buckets        :02:00, 10m
    section Collection
    Download DB backup     :02:10, 20m
    section Exfiltration
    Export customer data   :02:30, 30m
    section Impact
    Access admin panel     :03:00, 15m
```

### Attack Stages

#### Stage 1: Reconnaissance (01:00 - 01:30 UTC)
**Attacker Action**: Automated scanning of public GitHub repositories

**Evidence to Plant**:
- File: `mock_data/repos/ecommerce_app/src/config.py`
- Line 15: `AWS_ACCESS_KEY_ID = "AKIA2E3F4G5H6I7J8K9L"`
- Line 16: `AWS_SECRET_ACCESS_KEY = "abcdefghijklmnopqrstuvwxyz1234567890ABCD"`
- Commit: Accidentally committed 6 months ago
- Git history: Never removed, still in current HEAD

**Expected Detection**:
- Static analyzer finds AWS credentials
- Pattern match: `AKIA[0-9A-Z]{16}`
- Severity: Level 4 (High) - before exploitation

#### Stage 2: Initial Access (01:30 - 02:00 UTC)
**Attacker Action**: Validate stolen credentials and enumerate AWS resources

**Evidence to Plant**:
- Log: `mock_data/logs/access_logs/aws_cloudtrail.log`
```
2026-05-15T01:45:33Z sts:GetCallerIdentity 192.168.1.100 SUCCESS
2026-05-15T01:46:12Z s3:ListBuckets 192.168.1.100 SUCCESS
2026-05-15T01:47:05Z s3:ListObjects bucket=customer-data-backup 192.168.1.100 SUCCESS
```

**Expected Detection**:
- Runtime analyzer flags unusual AWS API calls
- Geographic anomaly: Access from unexpected IP
- Time anomaly: Activity at 1-2 AM
- Correlation: Same AWS key from config.py

#### Stage 3: Data Collection (02:00 - 02:30 UTC)
**Attacker Action**: Download database backup from S3

**Evidence to Plant**:
- Log: `mock_data/logs/access_logs/aws_cloudtrail.log`
```
2026-05-15T02:10:15Z s3:GetObject bucket=customer-data-backup key=db_backup_2026-05-14.sql.gz 192.168.1.100 SUCCESS bytes=524288000
```
- Database log: `mock_data/logs/app_logs/application.log`
```
2026-05-15T02:15:33Z INFO Database export initiated table=customers rows=50000 user=admin
2026-05-15T02:16:45Z INFO Database export completed size=45MB duration=72s
```

**Expected Detection**:
- Large data transfer detected (500MB)
- Database export anomaly (50k rows)
- Off-hours activity
- Correlation: Same attacker IP and timeframe

#### Stage 4: Lateral Movement (02:30 - 03:00 UTC)
**Attacker Action**: Use extracted credentials to access admin panel

**Evidence to Plant**:
- Log: `mock_data/logs/access_logs/access.log`
```
2026-05-15T02:45:12Z POST /api/auth/login ip=192.168.1.100 user=admin status=200
2026-05-15T02:45:45Z GET /api/admin/users ip=192.168.1.100 status=200 rows=50000
2026-05-15T02:46:30Z GET /api/deprecated/v1/export ip=192.168.1.100 status=200 size=45MB
```

**Expected Detection**:
- Admin access from suspicious IP
- Access to deprecated API endpoint
- Large data export via old API
- Correlation: Complete attack chain identified

### Expected System Response

#### Incident Correlation
The system MUST group all findings into ONE incident:
- Incident ID: `INC-2026-001`
- Title: "Coordinated AWS Credential Theft and Customer Data Exfiltration"
- Severity: Level 5 (Critical)
- Confidence: 0.95

#### Correlated Findings
1. AWS credentials in `config.py` (Static Analysis)
2. Unauthorized AWS API calls (Runtime Analysis)
3. Large S3 data download (Runtime Analysis)
4. Database export anomaly (Runtime Analysis)
5. Admin panel access from suspicious IP (Runtime Analysis)
6. Deprecated API exploitation (Static + Runtime)

#### Correlation Logic
- **Temporal**: All events within 120-minute window
- **Credential**: Same AWS key used across all stages
- **Actor**: Same IP address (192.168.1.100)
- **Target**: Customer data (database, S3, API)
- **Attack Chain**: Reconnaissance → Access → Collection → Exfiltration

#### Recommended Fixes
```python
# IMMEDIATE ACTIONS
1. Rotate AWS credentials in IAM console
2. Revoke all active sessions for compromised key
3. Block IP address 192.168.1.100
4. Disable deprecated /api/v1/export endpoint
5. Force password reset for admin account

# CODE FIXES
# Before (config.py:15-16)
AWS_ACCESS_KEY_ID = "AKIA2E3F4G5H6I7J8K9L"
AWS_SECRET_ACCESS_KEY = "abcdefghijklmnopqrstuvwxyz1234567890ABCD"

# After (config.py:15-16)
import os
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

# CONFIGURATION CHANGES
# .env (add to .gitignore)
AWS_ACCESS_KEY_ID=<new-key>
AWS_SECRET_ACCESS_KEY=<new-secret>

# PREVENTION
- Add pre-commit hook: git-secrets
- Enable AWS CloudTrail monitoring
- Implement rate limiting on admin endpoints
- Remove deprecated API endpoints
```

#### Generated Security Tests
```python
def test_no_aws_credentials_in_code():
    """Verify AWS credentials are not hardcoded"""
    pattern = r'AKIA[0-9A-Z]{16}'
    for file in scan_python_files():
        assert not re.search(pattern, read_file(file))

def test_deprecated_api_disabled():
    """Verify deprecated endpoints return 410 Gone"""
    response = requests.get('http://localhost:5000/api/v1/export')
    assert response.status_code == 410

def test_admin_access_requires_mfa():
    """Verify admin endpoints require MFA"""
    response = requests.post('/api/admin/users', 
                            headers={'Authorization': 'Bearer token'})
    assert response.status_code == 403  # MFA required
```

#### AI Memory Output
```json
{
  "memory_type": "security_prevention_rule",
  "incident_id": "INC-2026-001",
  "incident_pattern": "AWS credentials hardcoded in configuration files leading to unauthorized S3 access and data exfiltration",
  "root_cause": "Developers committing secrets to version control without using environment variables or secrets management",
  "signals_to_watch": [
    "AKIA[0-9A-Z]{16} pattern in Python files",
    "AWS API calls from unusual geographic locations",
    "Large S3 data transfers outside business hours",
    "Database exports exceeding 10,000 rows",
    "Access to deprecated API endpoints"
  ],
  "prevention_rule": "Implement pre-commit hooks to scan for AWS credentials. Use AWS Secrets Manager or environment variables. Enable CloudTrail monitoring with alerts for unusual API activity.",
  "recommended_tests": [
    "test_no_aws_credentials_in_code()",
    "test_environment_variables_required()",
    "test_deprecated_api_disabled()",
    "test_cloudtrail_monitoring_enabled()"
  ],
  "severity_escalation_conditions": [
    "Credentials found in public repository",
    "Evidence of unauthorized AWS API calls in CloudTrail",
    "Large data transfers detected",
    "Multiple attack stages detected within short timeframe"
  ],
  "created_at": "2026-05-15T03:15:00Z",
  "confidence": 0.95
}
```

---

## Scenario 2: Deprecated API Exploitation with Authentication Bypass

### Attack ID
`SCENARIO-002`

### Attack Name
"Legacy Backdoor" - Exploiting Abandoned API Endpoints

### Severity
**Level 4 (High)**

### Attack Timeline

```mermaid
gantt
    title Scenario 2 Attack Timeline
    dateFormat HH:mm
    section Discovery
    API endpoint scanning   :10:00, 30m
    section Exploitation
    Test deprecated API     :10:30, 15m
    Bypass authentication   :10:45, 15m
    section Privilege Escalation
    Enumerate users        :11:00, 20m
    Modify user roles      :11:20, 10m
    section Data Access
    Access sensitive data  :11:30, 30m
```

### Attack Stages

#### Stage 1: Discovery (10:00 - 10:30 UTC)
**Attacker Action**: Automated API endpoint enumeration

**Evidence to Plant**:
- File: `mock_data/repos/ecommerce_app/src/deprecated_api.py`
```python
# TODO: Remove this old API - deprecated since 2024
# WARNING: No authentication required for backward compatibility
@app.route('/api/v1/users', methods=['GET'])
def get_users_v1():
    # Legacy endpoint - DO NOT USE
    return jsonify(User.query.all())

@app.route('/api/v1/admin/roles', methods=['POST'])
def update_roles_v1():
    # DEPRECATED: Weak authorization
    user_id = request.json.get('user_id')
    new_role = request.json.get('role')
    update_user_role(user_id, new_role)
    return jsonify({'status': 'success'})
```

**Expected Detection**:
- Static analyzer finds deprecated API markers
- Comments indicate removal needed
- No authentication decorators present
- Last modified: 2+ years ago

#### Stage 2: Exploitation (10:30 - 11:00 UTC)
**Attacker Action**: Exploit weak authentication in old API

**Evidence to Plant**:
- Log: `mock_data/logs/access_logs/access.log`
```
2026-05-15T10:35:22Z GET /api/v1/users ip=203.0.113.50 status=200 rows=50000
2026-05-15T10:36:15Z GET /api/v1/users ip=203.0.113.50 status=200 rows=50000
2026-05-15T10:37:08Z GET /api/v1/users ip=203.0.113.50 status=200 rows=50000
2026-05-15T10:45:33Z POST /api/v1/admin/roles ip=203.0.113.50 status=200 body={"user_id":123,"role":"admin"}
```

**Expected Detection**:
- Repeated calls to deprecated endpoint
- No authentication headers present
- Privilege escalation attempt
- Rate limiting bypassed on old API

#### Stage 3: Data Access (11:00 - 12:00 UTC)
**Attacker Action**: Use elevated privileges to access sensitive data

**Evidence to Plant**:
- Log: `mock_data/logs/app_logs/application.log`
```
2026-05-15T11:30:45Z INFO User role changed user_id=123 old_role=user new_role=admin
2026-05-15T11:31:12Z INFO Admin access granted user_id=123 ip=203.0.113.50
2026-05-15T11:32:00Z INFO Sensitive data accessed endpoint=/api/admin/customers user_id=123
```

**Expected Detection**:
- Unusual role elevation
- Admin access from previously non-admin user
- Sensitive data access pattern

### Expected System Response

#### Incident Correlation
- Incident ID: `INC-2026-002`
- Title: "Deprecated API Exploitation Leading to Privilege Escalation"
- Severity: Level 4 (High)
- Confidence: 0.88

#### Correlated Findings
1. Deprecated API endpoints in code (Static)
2. Repeated calls to old API (Runtime)
3. Authentication bypass (Runtime)
4. Privilege escalation (Runtime)
5. Unauthorized data access (Runtime)

#### Recommended Fixes
```python
# IMMEDIATE ACTIONS
1. Disable /api/v1/* endpoints immediately
2. Revoke admin role for user_id=123
3. Audit all role changes in last 24 hours
4. Block IP 203.0.113.50

# CODE FIXES
# Remove deprecated endpoints entirely
# deprecated_api.py - DELETE THIS FILE

# Add to main API router
@app.route('/api/v1/<path:path>')
def deprecated_api_handler(path):
    return jsonify({'error': 'This API version is no longer supported'}), 410

# MIGRATION GUIDE
# Old: GET /api/v1/users
# New: GET /api/v2/users (requires authentication)
```

---

## Scenario 3: Multi-Vector Database Attack

### Attack ID
`SCENARIO-003`

### Attack Name
"SQL Injection to Data Breach" - Database Compromise via Multiple Vectors

### Severity
**Level 5 (Critical)**

### Attack Stages

#### Stage 1: SQL Injection Discovery
**Evidence to Plant**:
- File: `mock_data/repos/payment_service/src/database.py`
```python
def get_payment_by_id(payment_id):
    # VULNERABLE: SQL injection
    query = f"SELECT * FROM payments WHERE id = {payment_id}"
    return db.execute(query)

def search_transactions(user_input):
    # VULNERABLE: No input sanitization
    query = f"SELECT * FROM transactions WHERE description LIKE '%{user_input}%'"
    return db.execute(query)
```

#### Stage 2: Credential Discovery
**Evidence to Plant**:
- File: `mock_data/repos/payment_service/src/config.py`
```python
DATABASE_URL = "postgresql://admin:SuperSecret123@db.example.com:5432/payments"
```

#### Stage 3: Direct Database Access
**Evidence to Plant**:
- Log: `mock_data/logs/app_logs/database.log`
```
2026-05-15T14:15:33Z QUERY SELECT * FROM payments WHERE id = 1 OR 1=1-- ip=198.51.100.75
2026-05-15T14:16:12Z QUERY SELECT * FROM users WHERE username = 'admin' AND password = 'x' OR '1'='1'-- ip=198.51.100.75
2026-05-15T14:20:45Z CONNECTION ESTABLISHED user=admin host=198.51.100.75 database=payments
2026-05-15T14:21:00Z QUERY SELECT * FROM payments LIMIT 100000 ip=198.51.100.75
```

### Expected System Response

#### Incident Correlation
- Incident ID: `INC-2026-003`
- Title: "SQL Injection Vulnerability Exploited for Database Breach"
- Severity: Level 5 (Critical)
- Confidence: 0.92

#### Correlated Findings
1. SQL injection vulnerability (Static)
2. Hardcoded database credentials (Static)
3. SQL injection attempts in logs (Runtime)
4. Direct database connection from external IP (Runtime)
5. Large data query (Runtime)

---

## Testing Requirements

### For Each Scenario

1. **Detection Accuracy**
   - System must detect ALL planted vulnerabilities
   - False positive rate < 5%
   - False negative rate = 0% for critical issues

2. **Correlation Accuracy**
   - Related findings must be grouped into single incident
   - Correlation confidence > 0.85
   - Attack chain must be identified correctly

3. **Severity Classification**
   - Severity level must match expected level
   - Escalation conditions must be evaluated
   - Justification must be provided

4. **Remediation Quality**
   - Fixes must be specific and actionable
   - Code examples must be syntactically correct
   - Tests must be executable

5. **AI Memory Generation**
   - Memory must be in correct JSON format
   - Prevention rules must be actionable
   - Signals must be specific and detectable

### Performance Requirements

- Analysis completion time: < 5 minutes per scenario
- Memory usage: < 2GB
- Database queries: < 100 per scenario
- Report generation: < 30 seconds

### Success Criteria

- [ ] All 3 scenarios detected correctly
- [ ] All incidents correlated properly
- [ ] All severity levels assigned correctly
- [ ] All fixes are actionable
- [ ] All tests are executable
- [ ] All AI memory is valid JSON
- [ ] Performance requirements met

## Scenario Execution

### Running Scenarios

```bash
# Run all scenarios
python src/main.py test-scenarios --all

# Run specific scenario
python src/main.py test-scenarios --scenario-id SCENARIO-001

# Run with detailed output
python src/main.py test-scenarios --scenario-id SCENARIO-001 --verbose

# Generate scenario report
python src/main.py test-scenarios --scenario-id SCENARIO-001 --report
```

### Validation

```bash
# Validate scenario detection
python tests/validate_scenarios.py

# Check correlation accuracy
python tests/test_correlation.py --scenario SCENARIO-001

# Verify AI memory format
python tests/validate_ai_memory.py
```

## Future Scenarios

### Planned Additions

1. **Scenario 4**: Insider Threat - Legitimate User Abusing Access
2. **Scenario 5**: Supply Chain Attack - Compromised Dependency
3. **Scenario 6**: Ransomware Preparation - Data Staging
4. **Scenario 7**: API Rate Limit Bypass - DDoS Preparation
5. **Scenario 8**: Container Escape - Privilege Escalation

Each new scenario will follow the same structure and testing requirements.