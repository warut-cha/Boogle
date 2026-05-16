# AI-Powered Security Analyst System

An intelligent automated anomaly detection and data leak prevention system that identifies security risks, correlates attacks, and provides actionable remediation guidance.

## 🎯 Overview

This system serves as an AI-powered security analyst that continuously monitors codebases, logs, database activity, and API traffic to detect:

- **Leaked Secrets**: API keys, SSH keys, database credentials, access tokens
- **Deprecated APIs**: Old unused endpoints and abandoned modules
- **Sensitive Data Exposure**: Credentials in logs, debug mode in production
- **Suspicious Behavior**: Brute force attacks, data exfiltration, privilege escalation
- **Coordinated Attacks**: Multi-vector incidents correlated into unified threats

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Input Sources                             │
│  Code Repos │ Logs │ Database │ API History │ AI Memory     │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                 Analysis Pipeline                            │
│  Static Analysis │ Runtime Detection │ Correlation          │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              AI Reasoning Engine                             │
│  Local ML Models │ Pattern Matching │ IBM Watson (Optional) │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    Outputs                                   │
│  Incident Reports │ Fix Recommendations │ Security Tests    │
└─────────────────────────────────────────────────────────────┘
```

## ✨ Key Features

### 🔍 Multi-Layer Detection
- **Static Analysis**: Scans code for hardcoded secrets, weak configurations
- **Runtime Analysis**: Monitors logs and API traffic for suspicious patterns
- **Behavioral Analysis**: ML-based anomaly detection for unusual activity
- **Correlation Engine**: Groups related findings into unified incidents

### 🎯 Severity Classification
Five-level severity system with intelligent escalation:
- **Level 5 (Critical)**: Active exploitation or data breach in progress
- **Level 4 (High)**: Leaked credentials or exposed sensitive APIs
- **Level 3 (Medium)**: Vulnerable code without active exploitation
- **Level 2 (Low)**: Potential risks without sensitive data involvement
- **Level 1 (Informational)**: Technical debt with no security impact

### 🛠️ Actionable Remediation
- Immediate containment steps
- Specific code fixes with before/after examples
- Configuration changes with exact settings
- Secret rotation procedures
- Generated security tests to prevent regression

### 🧠 AI Memory System
Learns from incidents to prevent future occurrences:
- Stores attack patterns and indicators
- Generates prevention rules
- Provides context for future AI agents
- Enables continuous improvement

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.9 or higher
python --version

# Node.js 16 or higher (for dashboard)
node --version

# MongoDB (optional, SQLite fallback available)
mongod --version
```

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd IBM-BOB

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Running the Full System (Dashboard + API)

**Option 1: Automated Startup (Recommended)**
```bash
# Start both backend API and frontend dashboard
./start_services.sh
```

Then open your browser to:
- 📊 **Dashboard:** http://localhost:5173
- 🔌 **API:** http://localhost:8000
- 💚 **Health Check:** http://localhost:8000/api/health

**Option 2: Manual Startup**
```bash
# Terminal 1 - Backend API
source venv/bin/activate
python src/api_server.py

# Terminal 2 - Frontend Dashboard
cd frontend
npm run dev
```

### CLI Usage (Without Dashboard)
```bash
# Run full security analysis
python src/main.py analyze --path ./mock-repos

# Analyze with Bob AI reasoning
python src/main.py analyze --path ./mock-repos --use-bob

# Generate incident report
python src/main.py report --incident-id INC-2026-001

# View AI memory
python src/main.py memory --list

# Run security tests
python src/main.py test --path ./mock-repos

# Export findings as JSON
python src/main.py export --format json --output findings.json
```

### With IBM Watson Integration
```bash
# Set IBM Watson credentials
export IBM_WATSON_API_KEY="your-api-key"
export IBM_WATSON_URL="your-watson-url"

# Run analysis with Watson
python src/main.py analyze --path ./mock_data/repos --use-ibm-watson
```

## 📊 Example Output

### Executive Summary
```
Security Analysis Report
Generated: 2026-05-15 14:30:00 UTC

Total Incidents Detected: 5
├─ Critical (Level 5): 2
├─ High (Level 4): 2
├─ Medium (Level 3): 1
├─ Low (Level 2): 0
└─ Informational (Level 1): 0

Primary Concerns:
• AWS credentials leaked in configuration files
• Deprecated API endpoints actively exploited
• Suspicious database export activity detected
```

### Incident Details
```
INC-2026-001: AWS Credentials Leaked in Configuration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Severity: Level 5 (Critical)
Type: Credential Leak
Detected: 2026-05-15 14:23:45 UTC

Evidence:
├─ File: ecommerce_app/src/config.py:15
├─ Pattern: AWS Access Key (AKIA...)
└─ Exposure: Committed to Git repository

Correlated Findings:
├─ Unauthorized S3 API calls from 192.168.1.100
├─ Large data export (50,000 rows) at 02:16:15 UTC
└─ Access to deprecated /api/v1/users endpoint

Impact:
• Unauthorized AWS resource access
• Potential customer data breach
• Estimated cost exposure: High

Recommended Fixes:
1. IMMEDIATE: Rotate AWS credentials in IAM console
2. CODE: Move credentials to environment variables
3. PREVENTION: Add pre-commit hook for secret scanning
```

## 🧪 Mock Data & Testing

The system includes comprehensive mock data for testing:

### Mock Repositories
- **ecommerce_app**: E-commerce application with leaked API keys
- **payment_service**: Payment processing with SQL injection vulnerability
- **user_service**: User management with exposed SSH keys

### Attack Scenarios
1. **Coordinated Credential Theft**: Multi-stage attack using leaked AWS credentials
2. **Deprecated API Exploitation**: Bypassing authentication via old endpoints
3. **Database Attack**: SQL injection leading to data exfiltration

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test suite
pytest tests/test_analyzers.py

# Run integration tests
pytest tests/test_integration.py -v

# Test attack scenarios
python src/main.py test-scenario --scenario-id SCENARIO-001
```

## 📁 Project Structure

```
security-analyst/
├── src/                    # Source code
│   ├── collectors/         # Data collection modules
│   ├── analyzers/          # Analysis engines
│   ├── correlators/        # Incident correlation
│   ├── classifiers/        # Severity classification
│   ├── remediators/        # Fix generation
│   ├── ai_engine/          # AI reasoning components
│   ├── reporters/          # Report generation
│   └── database/           # Database operations
├── mock_data/              # Test data and scenarios
│   ├── repos/              # Mock vulnerable repositories
│   ├── logs/               # Sample log files
│   └── scenarios/          # Attack scenario definitions
├── patterns/               # Detection patterns
├── templates/              # Report templates
├── models/                 # ML models
├── tests/                  # Test suite
├── docs/                   # Documentation
└── config/                 # Configuration files
```

## 🔧 Configuration

### Main Configuration (`config/config.yaml`)
```yaml
database:
  type: mongodb  # or sqlite
  host: localhost
  port: 27017
  name: security_analyst

analysis:
  static_analysis:
    enabled: true
    scan_patterns: ["*.py", "*.js", "*.java", "*.env"]
  
  runtime_analysis:
    enabled: true
    anomaly_threshold: 0.85
    time_window_minutes: 60
  
  correlation:
    enabled: true
    time_window_minutes: 120
    min_confidence: 0.7

ai_engine:
  local_models:
    enabled: true
    model_path: "./models"
  
  ibm_watson:
    enabled: false
    api_key: "${IBM_WATSON_API_KEY}"
    url: "${IBM_WATSON_URL}"

reporting:
  output_format: "markdown"  # or html, json
  include_code_snippets: true
  max_snippet_lines: 20
```

### Secret Patterns (`patterns/secret_patterns.json`)
```json
{
  "aws_access_key": "AKIA[0-9A-Z]{16}",
  "aws_secret_key": "[A-Za-z0-9/+=]{40}",
  "stripe_key": "sk_(live|test)_[0-9a-zA-Z]{24,}",
  "github_token": "ghp_[0-9a-zA-Z]{36}",
  "ssh_private_key": "-----BEGIN (RSA|OPENSSH) PRIVATE KEY-----"
}
```

## 🤖 AI Memory Format

The system generates structured memory for future prevention:

```json
{
  "memory_type": "security_prevention_rule",
  "incident_pattern": "AWS credentials hardcoded in Python configuration files",
  "root_cause": "Developers committing secrets to version control",
  "signals_to_watch": [
    "AKIA[0-9A-Z]{16} pattern in .py files",
    "AWS_SECRET_ACCESS_KEY in plain text"
  ],
  "prevention_rule": "Scan all Python files for AWS credential patterns before commit",
  "recommended_tests": [
    "test_no_aws_credentials_in_code()",
    "test_environment_variables_required()"
  ],
  "severity_escalation_conditions": [
    "Credentials found in public repository",
    "Evidence of unauthorized AWS API calls"
  ]
}
```

## 📚 Documentation

- [Architecture](ARCHITECTURE.md) - System architecture and design
- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Detailed implementation guide
- [API Documentation](docs/API.md) - API reference
- [Usage Guide](docs/USAGE.md) - Comprehensive usage examples
- [Examples](docs/EXAMPLES.md) - Real-world scenarios

## 🔒 Security Considerations

1. **Sensitive Data Handling**: Never log actual secrets found during analysis
2. **Access Control**: Restrict access to incident reports and AI memory
3. **API Key Management**: Store IBM Watson credentials securely
4. **Database Security**: Use authentication for MongoDB connections
5. **Audit Trail**: Log all analysis operations and report access

## 🛣️ Roadmap

### Phase 1 (Current)
- [x] Core analysis engines
- [x] Incident correlation
- [x] CLI interface
- [x] Mock data and scenarios

### Phase 2 (Planned)
- [ ] Web dashboard for visualization
- [ ] Real-time monitoring with webhooks
- [ ] CI/CD pipeline integration
- [ ] Automated remediation with PR generation

### Phase 3 (Future)
- [ ] Multi-language support (Java, Go, Ruby)
- [ ] Cloud deployment (AWS, Azure, GCP)
- [ ] SIEM integration
- [ ] Compliance reporting (GDPR, SOC2, ISO27001)

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- IBM Watson for AI capabilities
- Security research community for attack patterns
- Open source security tools (Bandit, Semgrep)

## 📞 Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Built with ❤️ for security teams everywhere**