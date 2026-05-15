# Implementation Plan: AI-Powered Security Analyst System

## Project Structure

```
security-analyst/
├── src/
│   ├── __init__.py
│   ├── main.py                          # CLI entry point
│   ├── config.py                        # Configuration management
│   │
│   ├── collectors/                      # Data collection modules
│   │   ├── __init__.py
│   │   ├── base_collector.py           # Abstract base class
│   │   ├── code_collector.py           # Source code scanner
│   │   ├── log_collector.py            # Log file parser
│   │   ├── db_collector.py             # Database activity monitor
│   │   └── api_collector.py            # API request history
│   │
│   ├── analyzers/                       # Analysis engines
│   │   ├── __init__.py
│   │   ├── static_analyzer.py          # Static code analysis
│   │   ├── secret_detector.py          # Secret pattern matching
│   │   ├── deprecated_api_detector.py  # Old API detection
│   │   ├── runtime_analyzer.py         # Runtime behavior analysis
│   │   └── anomaly_detector.py         # ML-based anomaly detection
│   │
│   ├── correlators/                     # Incident correlation
│   │   ├── __init__.py
│   │   ├── incident_correlator.py      # Main correlation logic
│   │   └── attack_chain_detector.py    # Attack sequence detection
│   │
│   ├── classifiers/                     # Severity classification
│   │   ├── __init__.py
│   │   ├── severity_classifier.py      # 5-level severity system
│   │   └── risk_scorer.py              # Risk calculation
│   │
│   ├── remediators/                     # Fix generation
│   │   ├── __init__.py
│   │   ├── fix_generator.py            # Remediation recommendations
│   │   └── test_generator.py           # Security test creation
│   │
│   ├── ai_engine/                       # AI reasoning components
│   │   ├── __init__.py
│   │   ├── reasoning_engine.py         # Main AI logic
│   │   ├── ibm_watson_client.py        # IBM Watson integration
│   │   ├── memory_manager.py           # AI memory storage
│   │   └── pattern_library.py          # Known attack patterns
│   │
│   ├── reporters/                       # Report generation
│   │   ├── __init__.py
│   │   ├── incident_reporter.py        # Incident documentation
│   │   └── report_formatter.py         # Output formatting
│   │
│   ├── database/                        # Database operations
│   │   ├── __init__.py
│   │   ├── mongodb_client.py           # MongoDB operations
│   │   ├── sqlite_client.py            # SQLite fallback
│   │   └── models.py                   # Data models
│   │
│   └── utils/                           # Utility functions
│       ├── __init__.py
│       ├── file_utils.py               # File operations
│       ├── log_parser.py               # Log parsing utilities
│       └── validators.py               # Input validation
│
├── mock_data/                           # Test data and scenarios
│   ├── repos/                           # Mock vulnerable repositories
│   │   ├── ecommerce_app/
│   │   ├── payment_service/
│   │   └── user_service/
│   ├── logs/                            # Sample log files
│   │   ├── app_logs/
│   │   ├── access_logs/
│   │   └── security_logs/
│   └── scenarios/                       # Attack scenario definitions
│       ├── scenario_1_credential_theft.json
│       ├── scenario_2_deprecated_api.json
│       └── scenario_3_database_attack.json
│
├── patterns/                            # Detection patterns
│   ├── secret_patterns.json            # Secret detection regex
│   ├── api_patterns.json               # API vulnerability patterns
│   └── attack_patterns.json            # Known attack signatures
│
├── templates/                           # Report templates
│   ├── incident_report.md              # Markdown template
│   ├── incident_report.html            # HTML template
│   └── fix_templates.json              # Fix recommendation templates
│
├── models/                              # ML models
│   ├── anomaly_detector.pkl            # Trained anomaly model
│   └── baseline_models.pkl             # Baseline behavior models
│
├── tests/                               # Test suite
│   ├── __init__.py
│   ├── test_collectors.py
│   ├── test_analyzers.py
│   ├── test_correlators.py
│   ├── test_classifiers.py
│   ├── test_remediators.py
│   ├── test_ai_engine.py
│   └── test_integration.py
│
├── docs/                                # Documentation
│   ├── API.md                           # API documentation
│   ├── USAGE.md                         # Usage guide
│   └── EXAMPLES.md                      # Example scenarios
│
├── config/                              # Configuration files
│   ├── config.yaml                      # Main configuration
│   ├── patterns.yaml                    # Pattern definitions
│   └── severity_rules.yaml             # Severity classification rules
│
├── logs/                                # Application logs
│   └── .gitkeep
│
├── output/                              # Generated reports
│   └── .gitkeep
│
├── requirements.txt                     # Python dependencies
├── setup.py                             # Package setup
├── README.md                            # Project overview
├── ARCHITECTURE.md                      # Architecture documentation
├── IMPLEMENTATION_PLAN.md              # This file
└── .gitignore                          # Git ignore rules
```

## Implementation Phases

### Phase 1: Foundation Setup (Steps 1-4)

#### Step 1: Project Structure and Dependencies
**Files to Create**:
- `requirements.txt` - Python dependencies
- `setup.py` - Package configuration
- `README.md` - Project overview
- `.gitignore` - Git ignore rules
- `config/config.yaml` - Main configuration

**Dependencies**:
```
flask==3.0.0
pymongo==4.6.0
python-dotenv==1.0.0
pyyaml==6.0.1
pandas==2.1.4
numpy==1.26.2
scikit-learn==1.3.2
regex==2023.12.25
bandit==1.7.6
semgrep==1.52.0
click==8.1.7
colorama==0.4.6
tabulate==0.9.0
jinja2==3.1.2
requests==2.31.0
ibm-watson==7.0.1
python-dateutil==2.8.2
```

#### Step 2: Mock Vulnerable Repositories
**Files to Create**:
- `mock_data/repos/ecommerce_app/src/config.py` - Hardcoded credentials
- `mock_data/repos/ecommerce_app/src/api_keys.py` - Exposed API keys
- `mock_data/repos/ecommerce_app/src/auth.py` - Weak authentication
- `mock_data/repos/ecommerce_app/src/deprecated_api.py` - Old endpoints
- `mock_data/repos/payment_service/src/stripe_handler.py` - Leaked Stripe key
- `mock_data/repos/payment_service/src/database.py` - SQL injection
- `mock_data/repos/user_service/src/ssh_keys/id_rsa` - Private SSH key
- `mock_data/repos/user_service/src/jwt_handler.py` - Weak JWT secret

**Vulnerabilities to Include**:
- AWS credentials: `AKIA...` format
- Database passwords in connection strings
- Stripe API keys: `sk_live_...` format
- SSH private keys with BEGIN RSA PRIVATE KEY
- JWT secrets shorter than 32 characters
- Debug mode enabled: `DEBUG = True`
- SQL injection vulnerabilities
- Hardcoded admin passwords

#### Step 3: Mock Logs with Attack Patterns
**Files to Create**:
- `mock_data/logs/app_logs/application.log` - Normal + suspicious activity
- `mock_data/logs/access_logs/access.log` - HTTP requests with attacks
- `mock_data/logs/security_logs/auth.log` - Failed login attempts

**Log Patterns to Include**:
- Brute force: 10+ failed logins in 60 seconds
- Data exfiltration: Large database exports (50k+ rows)
- Deprecated API calls: Requests to `/api/v1/*` endpoints
- Suspicious timing: Activity at 2-4 AM
- Geographic anomalies: Access from unusual countries
- Privilege escalation: User role changes
- SQL injection attempts in query parameters

#### Step 4: Mock Database Setup
**Collections to Create**:
- `incidents` - Detected security incidents
- `api_requests` - Historical API calls
- `db_queries` - Database query logs
- `ai_memory` - Prevention rules and patterns
- `users` - Mock user data
- `audit_logs` - System audit trail

**Sample Data**:
- 1000+ API requests with 5% suspicious
- 50+ database queries with 10% anomalous
- 20+ users with various privilege levels
- 10+ previous incidents for AI learning

### Phase 2: Core Analysis Engines (Steps 5-7)

#### Step 5: Static Code Analysis
**Files to Create**:
- `src/analyzers/static_analyzer.py`
- `src/analyzers/secret_detector.py`
- `patterns/secret_patterns.json`

**Detection Capabilities**:
```python
# Secret patterns to detect
patterns = {
    "aws_access_key": r"AKIA[0-9A-Z]{16}",
    "aws_secret_key": r"[A-Za-z0-9/+=]{40}",
    "stripe_key": r"sk_(live|test)_[0-9a-zA-Z]{24,}",
    "github_token": r"ghp_[0-9a-zA-Z]{36}",
    "jwt_secret": r"(jwt|JWT).*['\"]([a-zA-Z0-9]{8,})['\"]",
    "db_password": r"(password|passwd|pwd).*['\"]([^'\"]{8,})['\"]",
    "ssh_private_key": r"-----BEGIN (RSA|OPENSSH) PRIVATE KEY-----",
    "google_api_key": r"AIza[0-9A-Za-z\\-_]{35}",
    "slack_token": r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,}",
}
```

**Analysis Steps**:
1. Recursively scan all files in repository
2. Apply regex patterns to detect secrets
3. Check for debug mode in config files
4. Identify sensitive data in comments
5. Detect weak cryptographic implementations
6. Flag hardcoded credentials in connection strings

#### Step 6: Deprecated API Detection
**Files to Create**:
- `src/analyzers/deprecated_api_detector.py`
- `patterns/api_patterns.json`

**Detection Logic**:
```python
# Identify deprecated APIs
deprecated_indicators = [
    "api/v1/",           # Old version endpoints
    "@deprecated",       # Decorator markers
    "# TODO: remove",    # Removal comments
    "# DEPRECATED",      # Explicit deprecation
    "legacy_",           # Legacy function prefix
    "_old",              # Old function suffix
]

# Check for unused modules
unused_indicators = [
    "No imports found",
    "Last modified > 365 days ago",
    "No function calls detected",
    "Marked as abandoned in comments",
]
```

#### Step 7: Runtime Anomaly Detection
**Files to Create**:
- `src/analyzers/runtime_analyzer.py`
- `src/analyzers/anomaly_detector.py`
- `models/anomaly_detector.pkl`

**Anomaly Detection Features**:
```python
# Features for ML model
features = [
    "request_frequency",      # Requests per minute
    "failed_auth_rate",       # Failed login percentage
    "data_volume",            # Bytes transferred
    "unique_endpoints",       # Number of different endpoints
    "time_of_day",           # Hour of access (0-23)
    "geographic_distance",    # Distance from usual location
    "privilege_level",        # User permission level
    "query_complexity",       # Database query complexity
]

# Anomaly thresholds
thresholds = {
    "request_frequency": 100,  # requests/min
    "failed_auth_rate": 0.3,   # 30% failure rate
    "data_volume": 10_000_000, # 10MB
    "off_hours_access": True,  # 2-4 AM
}
```

### Phase 3: Correlation and Classification (Steps 8-9)

#### Step 8: Incident Correlation
**Files to Create**:
- `src/correlators/incident_correlator.py`
- `src/correlators/attack_chain_detector.py`

**Correlation Rules**:
```python
# Temporal correlation
time_window = 120  # minutes

# Credential correlation
def correlate_by_credential(findings):
    # Group findings using same API key/password
    credential_groups = {}
    for finding in findings:
        cred = extract_credential(finding)
        if cred:
            credential_groups.setdefault(cred, []).append(finding)
    return credential_groups

# Target correlation
def correlate_by_target(findings):
    # Group findings targeting same resource
    target_groups = {}
    for finding in findings:
        target = finding.get("target")  # DB table, endpoint, etc.
        if target:
            target_groups.setdefault(target, []).append(finding)
    return target_groups

# Attack chain detection
attack_chains = [
    ["secret_leak", "api_abuse", "data_exfiltration"],
    ["deprecated_api", "auth_bypass", "privilege_escalation"],
    ["sql_injection", "db_access", "data_export"],
]
```

#### Step 9: Severity Classification
**Files to Create**:
- `src/classifiers/severity_classifier.py`
- `src/classifiers/risk_scorer.py`
- `config/severity_rules.yaml`

**Classification Logic**:
```python
def classify_severity(incident):
    score = 0
    
    # Base severity by type
    type_scores = {
        "secret_leak": 4,
        "sql_injection": 4,
        "weak_auth": 3,
        "deprecated_api": 2,
        "unused_code": 1,
    }
    score += type_scores.get(incident.type, 1)
    
    # Escalation factors
    if incident.has_active_exploitation:
        score += 1
    if incident.involves_sensitive_data:
        score += 1
    if incident.has_public_exposure:
        score += 1
    
    # Cap at 5
    return min(score, 5)
```

### Phase 4: Remediation and Reporting (Steps 10-13)

#### Step 10: Remediation Generator
**Files to Create**:
- `src/remediators/fix_generator.py`
- `templates/fix_templates.json`

**Fix Templates**:
```json
{
  "secret_leak": {
    "immediate_actions": [
      "Rotate the exposed credential immediately",
      "Revoke API key in provider console",
      "Check access logs for unauthorized usage"
    ],
    "code_fix": {
      "before": "API_KEY = 'sk_live_abc123'",
      "after": "API_KEY = os.environ.get('API_KEY')"
    },
    "prevention": [
      "Use environment variables for secrets",
      "Add .env to .gitignore",
      "Implement pre-commit hooks for secret scanning"
    ]
  }
}
```

#### Step 11: Security Test Generator
**Files to Create**:
- `src/remediators/test_generator.py`

**Test Templates**:
```python
# Generated test example
def test_no_hardcoded_secrets():
    """Verify no secrets are hardcoded in repository"""
    secret_patterns = load_patterns()
    for file in scan_repository():
        content = read_file(file)
        for pattern_name, pattern in secret_patterns.items():
            matches = re.findall(pattern, content)
            assert len(matches) == 0, f"Found {pattern_name} in {file}"

def test_deprecated_endpoints_disabled():
    """Verify deprecated endpoints return 410 Gone"""
    deprecated_endpoints = ["/api/v1/users", "/api/v1/products"]
    for endpoint in deprecated_endpoints:
        response = requests.get(f"http://localhost:5000{endpoint}")
        assert response.status_code == 410, f"{endpoint} should return 410"
```

#### Step 12: Incident Report Generator
**Files to Create**:
- `src/reporters/incident_reporter.py`
- `src/reporters/report_formatter.py`
- `templates/incident_report.md`
- `templates/incident_report.html`

**Report Structure**:
```markdown
# Security Incident Report

## Executive Summary
- Total Incidents: 5
- Critical: 2
- High: 2
- Medium: 1
- Primary Concerns: Credential leaks, deprecated API exploitation

## Incident Details

### INC-2026-001: AWS Credentials Leaked in Configuration
**Severity**: Level 5 (Critical)
**Type**: Credential Leak
**Detected**: 2026-05-15 14:23:45 UTC

**Evidence**:
- File: `ecommerce_app/src/config.py:15`
- Pattern: AWS Access Key (AKIA...)
- Exposure: Committed to Git repository

**Impact**:
- Unauthorized AWS resource access possible
- Potential data breach via S3 buckets
- Estimated cost exposure: High

**Recommended Fixes**:
1. Immediate: Rotate AWS credentials in IAM console
2. Code: Move credentials to environment variables
3. Prevention: Add pre-commit hook for secret scanning
```

#### Step 13: AI Memory System
**Files to Create**:
- `src/ai_engine/memory_manager.py`
- `src/database/models.py` (AI memory schema)

**Memory Format**:
```json
{
  "memory_type": "security_prevention_rule",
  "incident_id": "INC-2026-001",
  "incident_pattern": "AWS credentials hardcoded in Python configuration files",
  "root_cause": "Developers directly committing secrets to version control without using environment variables",
  "signals_to_watch": [
    "AKIA[0-9A-Z]{16} pattern in .py files",
    "AWS_SECRET_ACCESS_KEY in plain text",
    "boto3 client initialization with hardcoded credentials"
  ],
  "prevention_rule": "Scan all Python files for AWS credential patterns before commit. Enforce environment variable usage for all API keys and secrets.",
  "recommended_tests": [
    "test_no_aws_credentials_in_code()",
    "test_environment_variables_required()"
  ],
  "severity_escalation_conditions": [
    "Credentials found in public repository",
    "Evidence of unauthorized AWS API calls in CloudTrail"
  ],
  "created_at": "2026-05-15T14:30:00Z",
  "confidence": 0.95
}
```

### Phase 5: AI Engine and Interface (Steps 14-15)

#### Step 14: CLI Interface
**Files to Create**:
- `src/main.py`
- `src/cli/commands.py`

**CLI Commands**:
```python
@click.group()
def cli():
    """AI-Powered Security Analyst CLI"""
    pass

@cli.command()
@click.option('--path', required=True, help='Path to analyze')
@click.option('--use-ibm-watson', is_flag=True, help='Enable IBM Watson')
def analyze(path, use_ibm_watson):
    """Run security analysis on repository"""
    pass

@cli.command()
@click.option('--incident-id', required=True)
def report(incident_id):
    """Generate incident report"""
    pass

@cli.command()
@click.option('--list', is_flag=True)
def memory(list):
    """View AI memory"""
    pass

@cli.command()
@click.option('--path', required=True)
def test(path):
    """Run security tests"""
    pass
```

#### Step 15: Hybrid AI Reasoning Engine
**Files to Create**:
- `src/ai_engine/reasoning_engine.py`
- `src/ai_engine/ibm_watson_client.py`
- `src/ai_engine/pattern_library.py`

**AI Engine Architecture**:
```python
class ReasoningEngine:
    def __init__(self, use_ibm_watson=False):
        self.local_analyzer = LocalAnalyzer()
        self.pattern_matcher = PatternMatcher()
        self.ibm_client = IBMWatsonClient() if use_ibm_watson else None
        self.memory = MemoryManager()
    
    def analyze_incident(self, findings):
        # Local analysis
        local_result = self.local_analyzer.analyze(findings)
        
        # Pattern matching
        patterns = self.pattern_matcher.match(findings)
        
        # IBM Watson (optional)
        if self.ibm_client:
            watson_result = self.ibm_client.analyze(findings)
            return self.merge_results(local_result, patterns, watson_result)
        
        return self.merge_results(local_result, patterns)
    
    def learn_from_incident(self, incident):
        # Generate AI memory
        memory = self.generate_memory(incident)
        self.memory.store(memory)
```

### Phase 6: Documentation and Testing (Steps 16-17)

#### Step 16: Documentation
**Files to Create**:
- `docs/API.md` - API documentation
- `docs/USAGE.md` - Usage guide
- `docs/EXAMPLES.md` - Example scenarios

#### Step 17: Attack Scenarios
**Files to Create**:
- `mock_data/scenarios/scenario_1_credential_theft.json`
- `mock_data/scenarios/scenario_2_deprecated_api.json`
- `mock_data/scenarios/scenario_3_database_attack.json`

**Scenario Format**:
```json
{
  "scenario_id": "SCENARIO-001",
  "name": "Coordinated Credential Theft and Data Exfiltration",
  "description": "Multi-stage attack using leaked AWS credentials",
  "attack_timeline": [
    {
      "timestamp": "2026-05-15T02:00:00Z",
      "action": "Attacker discovers leaked AWS key in config.py",
      "evidence_file": "mock_data/repos/ecommerce_app/src/config.py"
    },
    {
      "timestamp": "2026-05-15T02:15:00Z",
      "action": "Unauthorized S3 API calls detected",
      "evidence_file": "mock_data/logs/access_logs/aws_cloudtrail.log"
    }
  ],
  "expected_detections": [
    {
      "type": "secret_leak",
      "severity": 5,
      "file": "ecommerce_app/src/config.py",
      "line": 15
    }
  ],
  "expected_correlation": true,
  "expected_incident_count": 1
}
```

## Implementation Order

1. **Day 1-2**: Foundation (Steps 1-4)
   - Set up project structure
   - Create mock vulnerable repositories
   - Generate mock logs and database

2. **Day 3-5**: Core Analysis (Steps 5-7)
   - Implement static analysis engine
   - Build deprecated API detector
   - Create runtime anomaly detector

3. **Day 6-7**: Correlation (Steps 8-9)
   - Implement incident correlator
   - Build severity classifier

4. **Day 8-9**: Remediation (Steps 10-11)
   - Create fix generator
   - Build test generator

5. **Day 10-11**: Reporting (Steps 12-13)
   - Implement report generator
   - Build AI memory system

6. **Day 12-13**: Interface (Steps 14-15)
   - Create CLI interface
   - Implement AI reasoning engine

7. **Day 14**: Documentation (Step 16)
   - Write comprehensive docs

8. **Day 15**: Testing (Step 17)
   - Create attack scenarios
   - Run integration tests

## Success Criteria

- [ ] System detects all intentional vulnerabilities in mock repos
- [ ] Incident correlation groups related findings correctly
- [ ] Severity classification matches expected levels
- [ ] Generated fixes are specific and actionable
- [ ] Security tests prevent regression
- [ ] AI memory enables future prevention
- [ ] CLI interface is intuitive and functional
- [ ] All coordinated attack scenarios are detected
- [ ] Reports are professional and comprehensive
- [ ] IBM Watson integration works (when enabled)

## Next Steps

After reviewing this plan, we can proceed to implementation by switching to Code mode. The implementation will follow the phases outlined above, creating each component systematically.