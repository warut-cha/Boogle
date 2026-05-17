# Jeff - Quick Start Guide

## Prerequisites

Make sure you have installed:
- Python 3.9+ with pip
- Rust and Cargo (for scanner)
- Node.js and npm (for frontend)

## Step-by-Step Instructions

### 1. Verify Integration (30 seconds)

```bash
# Run the integration check
python scripts/integration_check.py
```

You should see all green checkmarks ✓

---

### 2. Run Backend Analysis (2 minutes)

This will analyze the mock repositories and generate security reports:

```bash
# Run analysis with mock data and Bob AI
python src/main.py analyze --path ./mock-repos --use-mock --use-bob
```

**What this does:**
- Scans mock repositories for security issues
- Correlates findings into incidents
- Calculates confidence scores
- Builds attack paths
- Runs IBM Bob AI reasoning
- Generates security tests
- Creates PR drafts
- Generates incident reports

**Expected output:**
```
🔍 Jeff Security Analysis Started
✓ Found 5 security findings
✓ Created 1 incidents
✓ Classified severity
✓ Calculated confidence scores
✓ Built attack paths
✓ Running IBM Bob AI reasoning...
✓ Generated 5 security tests
✓ Generated 1 PR drafts
✓ Generated reports
✓ Updated AI memory

📊 Analysis Summary
Total Incidents: 1
Critical (Level 5): 1

Reports generated:
  📄 ./output/INC-001_report.md
  📄 ./output/INC-001_report.json
```

---

### 3. Check Generated Files

**Security Tests:**
```bash
# View generated tests
ls generated_tests/

# You should see:
# - test_export_api_security.py
# - test_secrets_detection.py
# - test_database_access_controls.py
# - test_api_rate_limiting.py
# - test_environment_variables.py
# - run_security_tests.py
# - README.md
```

**PR Drafts:**
```bash
# View generated PR drafts
ls generated_reports/

# You should see:
# - PR_DRAFT_security-fix-inc-001_INC-001.md
# - GIT_COMMANDS_security-fix-inc-001_INC-001.sh
```

**Incident Reports:**
```bash
# View incident reports
ls output/

# You should see:
# - INC-001_report.md
# - INC-001_report.json
```

---

### 4. Run Frontend Dashboard (Optional)

If you have npm installed:

```bash
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

Then open your browser to: **http://localhost:5173**

**What you'll see:**
- Overview cards with incident statistics
- Findings table with all security issues
- Incident details with severity and confidence
- Attack path visualization (interactive graph)
- Bob AI analysis with recommended fixes
- Generated security tests
- PR draft preview
- AI memory patterns

---

## Quick Demo Script

For a complete demo, run these commands in order:

```bash
# 1. Verify everything is set up
python scripts/integration_check.py

# 2. Run security analysis
python src/main.py analyze --path ./mock-repos --use-mock --use-bob

# 3. View the incident report
cat output/INC-001_report.md

# 4. View generated tests
cat generated_tests/test_export_api_security.py

# 5. View PR draft
cat generated_reports/PR_DRAFT_security-fix-inc-001_INC-001.md

# 6. (Optional) Start frontend
cd frontend && npm run dev
```

---

## Understanding the Output

### Incident Report Structure

The generated incident report includes:

1. **Executive Summary** - High-level overview
2. **Attack Path Analysis** - Step-by-step attack chain
3. **Confidence Assessment** - Why we're confident this is real
4. **Technical Details** - Affected systems and files
5. **Findings** - Individual security issues
6. **Recommended Actions** - Immediate, short-term, and long-term fixes
7. **Impact Assessment** - Business and data risk
8. **Prevention Measures** - How to avoid similar issues

### Generated Security Tests

Bob automatically creates tests for:
- Authentication and authorization
- Secret detection
- Database access controls
- API rate limiting
- Environment variable validation

These tests can be added to your CI/CD pipeline.

### PR Draft

The PR draft includes:
- Security fix description
- List of changes made
- Testing checklist
- Security checklist
- Deployment notes
- Git commands to create the PR

---

## Troubleshooting

### "Module not found" errors

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### "cargo: command not found"

The Rust scanner is optional. The system will use mock data if Rust is not installed.

To install Rust:
```bash
# Visit: https://rustup.rs/
# Or use mock mode: --use-mock flag (already included in examples above)
```

### "npm: command not found"

The frontend is optional for backend analysis. You can still:
- Run the backend analysis
- View generated reports in `output/`
- View generated tests in `generated_tests/`
- View PR drafts in `generated_reports/`

To install Node.js:
```bash
# Visit: https://nodejs.org/
```

### Integration check fails

```bash
# Re-run with verbose output
python scripts/integration_check.py

# Check which component failed and refer to INTEGRATION_GUIDE.md
```

---

## What's Next?

After running the quick start:

1. **Review the generated incident report** in `output/INC-001_report.md`
2. **Check the security tests** in `generated_tests/`
3. **Read the PR draft** in `generated_reports/`
4. **Explore the frontend** (if npm is available)
5. **Read the full integration guide** in `INTEGRATION_GUIDE.md`

---

## Command Reference

```bash
# Verify integration
python scripts/integration_check.py

# Run analysis (mock mode)
python src/main.py analyze --path ./mock-repos --use-mock --use-bob

# Run analysis (real Rust scanner)
python src/main.py analyze --path ./mock-repos --use-bob

# Run analysis without Bob AI
python src/main.py analyze --path ./mock-repos --use-mock

# View help
python src/main.py --help
python src/main.py analyze --help

# Frontend commands
cd frontend
npm install          # First time only
npm run dev          # Development server
npm run build        # Production build
npm run preview      # Preview production build
```

---

## Demo Scenario

The mock data simulates a real security incident:

**Scenario:** Credential leakage through exposed abandoned export API

**Attack Chain:**
1. Hardcoded API key found in legacy code
2. Deprecated export endpoint still accessible
3. Suspicious repeated access detected
4. Database read spike on users table
5. Possible data exfiltration

**Bob's Analysis:**
- Severity: CRITICAL
- Confidence: 88%
- 6 recommended fixes
- 5 generated security tests
- Complete PR draft with git commands

This demonstrates how Jeff can detect, analyze, and help remediate complex security incidents.

---

**Ready to start? Run:** `python scripts/integration_check.py`