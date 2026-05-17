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

# Node.js 18 or higher (for dashboard)
node --version

# Rust 1.70+ (for high-performance scanner)
rustc --version

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

# Build Rust scanner (high-performance)
cd rust-scanner
cargo build --release
cd ..

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Running the Full System (Dashboard + API)

```bash
# Terminal 1 - Backend API
source venv/bin/activate
python src/api_server.py

# Terminal 2 - Frontend Dashboard
cd frontend
npm run dev

# Terminal 3 - Attack Simulator (For real time attack)
python runtime_lab/attack_simulator.py --backend-url http://localhost:8000 --endpoint /api/v1/export-users --count 5 --delay 1
```

### With IBM Watson Integration
```bash
# Set IBM Watson credentials
export IBM_WATSON_API_KEY="your-api-key"
export IBM_WATSON_URL="your-watson-url"
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
├── src/                    # Python backend
│   ├── collectors/         # Data collection modules
│   ├── analyzers/          # Analysis engines
│   ├── correlators/        # Incident correlation
│   ├── classifiers/        # Severity classification
│   ├── remediators/        # Fix generation
│   ├── ai_engine/          # AI reasoning (IBM watsonx.ai)
│   ├── reporters/          # Report generation
│   ├── database/           # Database operations
│   ├── api_server.py       # FastAPI backend server
│   └── main.py             # CLI entry point
├── frontend/               # React + TanStack Start dashboard
│   ├── src/
│   │   ├── routes/         # TanStack Router pages
│   │   ├── components/     # React components (shadcn/ui)
│   │   └── hooks/          # Custom React hooks
│   ├── package.json        # Node.js dependencies
│   └── vite.config.ts      # Vite configuration
├── rust-scanner/           # High-performance Rust scanner
│   ├── src/                # Rust source code
│   └── Cargo.toml          # Rust dependencies
├── mock_data/              # Test data and scenarios
│   ├── repos/              # Mock vulnerable repositories
│   └── scenarios/          # Attack scenario definitions
├── mock-repos/             # Additional test repositories
├── patterns/               # Detection patterns (JSON)
├── contracts/              # JSON schemas for data contracts
├── config/                 # YAML configuration files
├── generated_reports/      # Output directory for reports
└── runtime_lab/            # Attack simulation tools
```

## 🔧 Configuration

### Main Configuration (`config/config.yaml`)
```yaml
database:
  type: mongodb  # or sqlite
  mongodb:
    host: localhost
    port: 27017
    database: security_analyst

analysis:
  static_analysis:
    enabled: true
    scan_patterns: ["*.py", "*.js", "*.java", "*.go", "*.rb", "*.php", "*.yaml", "*.json", "*.env"]
  
  runtime_analysis:
    enabled: true
    anomaly_threshold: 0.85
    detection_window_minutes: 60
  
  correlation:
    enabled: true
    time_window_minutes: 120
    min_confidence: 0.7

ai_engine:
  local_models:
    enabled: true
    anomaly_detection:
      algorithm: isolation_forest
  
  bob:  # IBM watsonx.ai integration
    enabled: true
    model_id: "ibm/granite-8b-code-instruct"
    project_id: "${WATSONX_PROJECT_ID}"
    api_key: "${WATSONX_API_KEY}"
    url: "${WATSONX_URL}"
    max_tokens: 2000
    temperature: 0.7
  
  vector_memory:
    enabled: true
    storage_path: ./models/vector_memory
    embedding_model: "sentence-transformers/all-MiniLM-L6-v2"

reporting:
  formats: ["markdown", "json", "html"]
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

## 🛠️ Tech Stack

### Backend
- **Python 3.9+**: Core application logic
- **FastAPI**: REST API server with WebSocket support
- **IBM watsonx.ai**: AI-powered security reasoning (Granite models)
- **ChromaDB**: Vector database for AI memory
- **MongoDB/SQLite**: Incident and findings storage
- **scikit-learn**: Machine learning for anomaly detection

### Frontend
- **React 19**: UI framework
- **TanStack Start**: Full-stack React framework with SSR
- **TanStack Router**: Type-safe routing
- **Vite**: Build tool and dev server
- **shadcn/ui**: Component library (Radix UI + Tailwind CSS)
- **Recharts**: Data visualization
- **WebSocket**: Real-time incident updates

### Scanner
- **Rust**: High-performance static code scanner
- **Regex**: Pattern matching for secrets and vulnerabilities
- **Walkdir**: Efficient file system traversal
- **Serde**: JSON serialization

### DevOps & Tools
- **YAML**: Configuration management
- **JSON Schema**: Data contract validation
- **Git**: Version control
- **pytest**: Python testing (optional)

## 🔒 Security Considerations

1. **Sensitive Data Handling**: Never log actual secrets found during analysis
2. **Access Control**: Restrict access to incident reports and AI memory
3. **API Key Management**: Store IBM Watson credentials securely
4. **Database Security**: Use authentication for MongoDB connections
5. **Audit Trail**: Log all analysis operations and report access

## 🛣️ Roadmap

### Phase 1 (Completed ✅)
- [x] Core analysis engines
- [x] Incident correlation
- [x] CLI interface
- [x] Mock data and scenarios
- [x] Rust-based high-performance scanner
- [x] IBM watsonx.ai integration (Bob AI)
- [x] Web dashboard with real-time updates
- [x] WebSocket support for live monitoring
- [x] AI memory system with vector storage

### Phase 2 (In Progress 🚧)
- [x] Interactive dashboard with TanStack Start
- [x] Real-time monitoring with WebSocket
- [ ] CI/CD pipeline integration
- [ ] Automated remediation with PR generation
- [ ] Enhanced attack path visualization

### Phase 3 (Future 🔮)
- [ ] Multi-language support expansion
- [ ] Cloud deployment (AWS, Azure, GCP)
- [ ] SIEM integration
- [ ] Compliance reporting (GDPR, SOC2, ISO27001)
- [ ] Mobile app for incident alerts

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **IBM watsonx.ai** for AI-powered security reasoning
- **IBM Granite models** for code analysis capabilities
- Security research community for attack patterns
- Open source security tools (Bandit, Semgrep)
- **shadcn/ui** for beautiful React components
- **TanStack** ecosystem for modern React development

## 📞 Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Built with ❤️ for security teams everywhere**
