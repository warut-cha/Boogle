# Security Analyst System - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage Examples](#usage-examples)
5. [Understanding Results](#understanding-results)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Getting Started

The Security Analyst System is an AI-powered tool that automatically detects security vulnerabilities, correlates related findings into incidents, and provides actionable remediation guidance.

### Key Features
- **Multi-layer Detection**: Static code analysis, runtime behavior analysis, and deprecated API detection
- **Intelligent Correlation**: Groups related findings into unified incidents
- **5-Level Severity Classification**: From Informational to Critical
- **Actionable Remediation**: Specific code fixes with before/after examples
- **AI Learning**: Continuous improvement through incident memory
- **Professional Reporting**: Markdown, JSON, and HTML formats

## Installation

### Prerequisites
- Python 3.9 or higher
- MongoDB (optional, SQLite is default)
- Git

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd security-analyst
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Initialize System
```bash
python src/main.py init
```

This will:
- Set up the database schema
- Load detection patterns
- Initialize AI models
- Create output directories

## Configuration

### Main Configuration File
Edit `config/config.yaml` to customize the system:

```yaml
# Database Configuration
database:
  type: mongodb  # or sqlite
  mongodb:
    host: localhost
    port: 27017
    database: security_analyst

# Analysis Settings
analysis:
  static_analysis:
    enabled: true
    scan_patterns:
      - "*.py"
      - "*.js"
      - "*.java"
  
  runtime_analysis:
    enabled: true
    anomaly_threshold: 0.85
  
  correlation:
    time_window_minutes: 120
    min_confidence: 0.7

# AI Engine
ai_engine:
  local_models:
    enabled: true
  ibm_watson:
    enabled: false
    api_key: "${IBM_WATSON_API_KEY}"
```

### Environment Variables
Create a `.env` file for sensitive configuration:

```bash
IBM_WATSON_API_KEY=your_api_key_here
IBM_WATSON_URL=your_watson_url_here
DATABASE_PASSWORD=your_db_password
```

## Usage Examples

### Basic Analysis

Analyze a single repository:
```bash
python src/main.py analyze --path /path/to/repository
```

Output:
```
🔍 Security Analysis Started
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 Scanning: /path/to/repository
   ├─ Files scanned: 45
   ├─ Secrets found: 3
   └─ Deprecated APIs: 2

📊 Analysis Complete
   ├─ Total findings: 12
   ├─ Incidents created: 3
   └─ Severity distribution:
      ├─ Critical (5): 2
      ├─ High (4): 1
      └─ Medium (3): 0

⚠️  CRITICAL INCIDENT DETECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INC-2026-001: AWS Credentials Leaked in Configuration
Severity: Level 5 (Critical)
Confidence: 0.95

Evidence:
├─ AWS Access Key in config.py:15
├─ Unauthorized S3 API calls detected
└─ Large data export (50,000 rows)

Immediate Actions Required:
1. Rotate AWS credentials in IAM console
2. Revoke all active sessions
3. Block IP address 192.168.1.100

📄 Full report: ./output/INC-2026-001.md
```

### Advanced Analysis with IBM Watson

```bash
python src/main.py analyze \
  --path /path/to/repository \
  --use-ibm-watson \
  --output ./reports \
  --format markdown json html \
  --severity-threshold 3
```

Options:
- `--use-ibm-watson`: Enable IBM Watson AI analysis
- `--output`: Specify output directory
- `--format`: Report formats (markdown, json, html)
- `--severity-threshold`: Minimum severity to report (1-5)

### Generate Specific Report

```bash
python src/main.py report --incident-id INC-2026-001 --format markdown
```

### View AI Memory

List all learned prevention rules:
```bash
python src/main.py memory --list
```

Search for specific patterns:
```bash
python src/main.py memory --pattern "SQL injection"
```

Export memory:
```bash
python src/main.py memory --export ./memory_backup.json
```

### Run Security Tests

Test for specific vulnerabilities:
```bash
python src/main.py test --path /path/to/code --test-type secrets deprecated-api auth
```

Test all:
```bash
python src/main.py test --path /path/to/code --test-type all
```

### Test Attack Scenarios

Run predefined attack scenarios:
```bash
python src/main.py test-scenarios --all
```

Run specific scenario:
```bash
python src/main.py test-scenarios --scenario-id SCENARIO-001
```

### Export Findings

Export to JSON:
```bash
python src/main.py export --format json --output findings.json --severity 4
```

### Check System Status

```bash
python src/main.py status
```

Output:
```
System Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Database: 🟢 Connected
AI Engine: 🟢 Enabled
IBM Watson: 🔴 Disabled

Statistics:
  Total Incidents: 15
  AI Memory Entries: 23
  Last Analysis: 2026-05-15 14:30:00
```

## Understanding Results

### Severity Levels

| Level | Name | Description | Action Required |
|-------|------|-------------|-----------------|
| 5 | Critical | Active exploitation or data breach | Immediate (within 1 hour) |
| 4 | High | Leaked credentials or exposed APIs | Urgent (within 24 hours) |
| 3 | Medium | Vulnerable code without exploitation | High priority (within 1 week) |
| 2 | Low | Potential risk, no sensitive data | Medium priority (within 1 month) |
| 1 | Informational | Technical debt, no security impact | Low priority (next quarter) |

### Incident Types

**Attack Chain**: Multiple related attacks forming a coordinated sequence
- Example: Credential theft → API access → Data exfiltration

**Temporal Correlation**: Multiple events from same source within time window
- Example: Rapid requests from same IP address

**Credential Correlation**: Multiple instances of same credential type
- Example: AWS keys found in multiple files

**Target Correlation**: Multiple vulnerabilities in same resource
- Example: 3+ issues in same file or endpoint

### Reading Reports

#### Markdown Report Structure
```markdown
# Security Incident Report: INC-2026-001

## AWS Credentials Leaked in Configuration

### Incident Details
- Severity: 🔴 Level 5 (Critical)
- Confidence: 0.95
- Findings: 3

### Description
Multiple AWS credentials found in source code with evidence of unauthorized usage.

### Findings
1. AWS Access Key in config.py:15
2. AWS Secret Key in config.py:16
3. Unauthorized S3 access in logs

### Recommended Actions
#### Immediate Containment
1. Rotate AWS credentials in IAM console
2. Revoke all active sessions
3. Enable CloudTrail monitoring

#### Code Fixes
**File**: config.py
**Line**: 15
**Before**: `AWS_ACCESS_KEY_ID = 'AKIAIOSFODNN7EXAMPLE'`
**After**: `AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')`

#### Prevention
1. Add pre-commit hooks for secret detection
2. Use AWS Secrets Manager
3. Implement secret rotation policy
```

### AI Memory Format

```json
{
  "memory_type": "security_prevention_rule",
  "incident_pattern": "AWS credentials leaked in configuration files",
  "root_cause": "Hardcoded credentials without proper secret management",
  "signals_to_watch": [
    "High-entropy strings in config files",
    "AWS key patterns (AKIA*)",
    "Unauthorized AWS API calls"
  ],
  "prevention_rule": "Use environment variables or AWS Secrets Manager, implement pre-commit hooks",
  "recommended_tests": [
    "test_no_hardcoded_aws_keys",
    "test_secrets_from_environment"
  ],
  "severity_escalation_conditions": [
    "Credentials actively used in logs",
    "Multiple AWS services accessed"
  ]
}
```

## Best Practices

### 1. Regular Scanning
Run analysis on every commit or at least daily:
```bash
# In CI/CD pipeline
python src/main.py analyze --path . --severity-threshold 4
```

### 2. Prioritize Critical Incidents
Always address Level 5 (Critical) and Level 4 (High) incidents immediately.

### 3. Review AI Memory
Periodically review learned patterns:
```bash
python src/main.py memory --list | grep "critical"
```

### 4. Integrate with CI/CD
Add to your pipeline:
```yaml
# .github/workflows/security.yml
- name: Security Analysis
  run: |
    python src/main.py analyze --path . --severity-threshold 3
    if [ $? -ne 0 ]; then exit 1; fi
```

### 5. Rotate Credentials Immediately
When credentials are detected:
1. Rotate in the service (AWS, GitHub, etc.)
2. Update environment variables
3. Revoke old credentials
4. Monitor for unauthorized usage

### 6. Use Environment Variables
Never hardcode secrets:
```python
# ❌ Bad
API_KEY = "sk_live_abc123"

# ✅ Good
API_KEY = os.getenv('API_KEY')
```

### 7. Implement Pre-commit Hooks
Prevent secrets from being committed:
```bash
# .git/hooks/pre-commit
python src/main.py test --path . --test-type secrets
```

## Troubleshooting

### Issue: No findings detected
**Solution**: 
- Check that scan patterns match your file types
- Verify files are not in exclude patterns
- Ensure patterns files are loaded correctly

### Issue: Too many false positives
**Solution**:
- Adjust confidence thresholds in config.yaml
- Add false positive patterns to exclusions
- Review and update detection patterns

### Issue: Database connection failed
**Solution**:
```bash
# For MongoDB
mongod --dbpath ./data/db

# Or use SQLite
# Edit config.yaml: database.type = "sqlite"
```

### Issue: IBM Watson not working
**Solution**:
- Verify API key is set: `echo $IBM_WATSON_API_KEY`
- Check Watson service is active
- Review Watson URL configuration

### Issue: Reports not generating
**Solution**:
- Check output directory permissions
- Verify disk space available
- Review logs: `cat logs/security_analyst.log`

### Issue: Memory usage too high
**Solution**:
- Reduce max_file_size_mb in config
- Limit scan patterns
- Process repositories in batches

## Support

For issues and questions:
- Check logs: `./logs/security_analyst.log`
- Review documentation: `./docs/`
- Run diagnostics: `python src/main.py status`

## Next Steps

1. Run your first analysis
2. Review the generated reports
3. Implement recommended fixes
4. Set up automated scanning
5. Monitor AI memory growth
6. Integrate with your CI/CD pipeline

Happy securing! 🔒