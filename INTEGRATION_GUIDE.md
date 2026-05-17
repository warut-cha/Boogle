# Jeff Integration Guide

## Overview

This guide explains how all components of Jeff work together to provide end-to-end security analysis.

## Architecture Flow

```
┌─────────────────┐
│  Rust Scanner   │ ──> Finds security issues in code/infra/logs
└────────┬────────┘
         │ JSON findings
         ▼
┌─────────────────┐
│ Python Backend  │ ──> Correlates findings into incidents
│  - Correlator   │     Calculates confidence scores
│  - Classifier   │     Builds attack paths
│  - Scorer       │     Retrieves similar past incidents
└────────┬────────┘
         │ Incident JSON
         ▼
┌─────────────────┐
│  IBM Bob AI     │ ──> Explains attack
│  Reasoning      │     Generates fixes
│                 │     Creates security tests
│                 │     Drafts PR
│                 │     Learns patterns
└────────┬────────┘
         │ Bob Output JSON
         ▼
┌─────────────────┐
│ React Dashboard │ ──> Displays findings
│  TypeScript     │     Shows attack path
│                 │     Presents Bob analysis
│                 │     Visualizes memory
└─────────────────┘
```

## Data Flow

### 1. Rust Scanner → Python Backend

**Command:**
```bash
cargo run -- scan --path ../mock-repos/legacy-backend ../mock-repos/infra-config
```

**Output:** JSON array of findings
```json
[
  {
    "finding_id": "FIND-001",
    "repo_name": "legacy-backend",
    "finding_type": "hardcoded_secret",
    "category": "secret_exposure",
    "severity_hint": "high",
    "source": "rust_scanner",
    "file": "legacy/old_export_api.py",
    "line": 12,
    "endpoint": "/api/v1/export-users",
    "database_table": null,
    "evidence": "Hardcoded API key detected",
    "masked_value": "sk_test_****92fa",
    "timestamp": "2026-05-16T12:00:00Z"
  }
]
```

**Python Integration:**
```python
from scanners.rust_scanner_client import RustScannerClient

scanner = RustScannerClient()
findings = scanner.scan(paths=['./mock-repos'], use_mock=False)
```

### 2. Python Backend → Incident Correlation

**Process:**
1. Normalize findings using `src/utils/normalizers.py`
2. Correlate related findings into incidents
3. Calculate confidence scores
4. Build attack paths
5. Retrieve similar past incidents from memory

**Output:** Incident JSON
```json
{
  "incident_id": "INC-001",
  "title": "Credential leakage through exposed API",
  "severity": "critical",
  "severity_level": 5,
  "confidence_score": 0.88,
  "confidence_reasons": ["Hardcoded key found", "Suspicious access detected"],
  "confidence_limitations": ["No confirmed exfiltration"],
  "affected_repos": ["legacy-backend"],
  "affected_files": ["legacy/old_export_api.py"],
  "affected_endpoints": ["/api/v1/export-users"],
  "affected_database_tables": ["users"],
  "findings": [...],
  "attack_path": {
    "nodes": [...],
    "edges": [...]
  },
  "related_memory": [...]
}
```

### 3. IBM Bob AI Analysis

**Input:** Incident + Attack Path + Related Memory

**Process:**
1. Build Bob input with context
2. Call Bob reasoning engine
3. Generate comprehensive analysis

**Output:** Bob Output JSON
```json
{
  "attack_type": "Credential leakage and API abuse",
  "target": "User export endpoint",
  "severity": "critical",
  "confidence_assessment": "High confidence (0.88)...",
  "recommended_fixes": [
    {
      "type": "immediate_action",
      "description": "Rotate exposed API key immediately"
    },
    {
      "type": "code_fix",
      "description": "Move API key to environment variable"
    }
  ],
  "generated_security_tests": [
    {
      "file": "tests/test_export_api_security.py",
      "name": "test_export_endpoint_requires_admin",
      "purpose": "Ensure only admin users can access export",
      "code": "def test_export_endpoint_requires_admin(...):\n    ..."
    }
  ],
  "incident_report": "## Incident Report...",
  "ai_memory": {
    "memory_type": "security_prevention_rule",
    "incident_pattern": "hardcoded_secret_in_abandoned_api",
    "root_cause": "Legacy API with static credentials",
    "signals_to_watch": [...],
    "prevention_rule": "Flag abandoned APIs with credentials",
    "recommended_tests": [...]
  },
  "pr_draft": {
    "branch_name": "security/fix-inc-001",
    "pr_title": "Security: Fix credential leakage",
    "pr_description": "## Security Fix...",
    "files_to_change": [...]
  }
}
```

### 4. Generated Artifacts

**Security Tests:** Saved to `generated_tests/`
- `test_export_api_security.py`
- `test_secrets_detection.py`
- `test_database_access_controls.py`
- `run_security_tests.py` (test suite runner)

**PR Drafts:** Saved to `generated_reports/`
- `PR_DRAFT_security-fix-inc-001_INC-001.md`
- `GIT_COMMANDS_security-fix-inc-001_INC-001.sh`

**Incident Reports:** Saved to `generated_reports/`
- `INC-001_report.md`
- `INC-001_report.json`

### 5. Frontend Display

**API Client:** `frontend/src/api/client.ts`
```typescript
// Fetch incidents
const incidents = await apiClient.getIncidents();

// Fetch Bob analysis for specific incident
const bobOutput = await apiClient.getBobAnalysis(incidentId);
```

**Components:**
- `FindingsTable` - Shows all findings
- `IncidentDetail` - Displays incident information
- `AttackPathGraph` - Visualizes attack chain
- `BobAnalysis` - Shows AI reasoning and fixes
- `MemoryViewer` - Displays learned patterns
- `PRDraftViewer` - Shows generated PR

## Setup Instructions

### 1. Install Dependencies

**Rust Scanner:**
```bash
cd rust-scanner
cargo build --release
```

**Python Backend:**
```bash
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 2. Verify Integration

Run the integration check script:
```bash
python scripts/integration_check.py
```

This verifies:
- ✓ Rust scanner builds
- ✓ Contract files are valid JSON
- ✓ Python backend files exist
- ✓ Frontend builds successfully
- ✓ Data structures match across components

### 3. Run End-to-End Test

**Option A: CLI Mode (Recommended for Hackathon)**

```bash
# Run full analysis with mock data
python src/main.py analyze --path ./mock-repos --use-mock --use-bob

# Check outputs
ls generated_tests/      # Security tests
ls generated_reports/    # PR drafts and reports
```

**Option B: API Mode (Future)**

```bash
# Start backend API
python src/api_server.py

# Start frontend dev server
cd frontend
npm run dev

# Open browser to http://localhost:5173
```

## Key Integration Points

### 1. Rust ↔ Python

**File:** `src/scanners/rust_scanner_client.py`

**Critical:** Both must use `--path` flag (not `--paths`)

```python
cmd = ["cargo", "run", "--", "scan", "--path"] + paths
```

### 2. Python ↔ Contracts

**Files:** `contracts/*.json`

**Critical:** All JSON must match schemas

Use normalizers to handle old/new formats:
```python
from utils.normalizers import normalize_finding, normalize_incident

normalized_finding = normalize_finding(raw_finding)
```

### 3. Python ↔ Frontend

**Files:** 
- Backend: `src/main.py`, incident JSON output
- Frontend: `frontend/src/api/types.ts`

**Critical:** Field names must match (use snake_case)

```typescript
// TypeScript types match Python JSON
export type Finding = {
  finding_id: string;
  finding_type: string;
  severity_hint: string;
  // ...
}
```

### 4. Bob Output → Generated Files

**Files:**
- `src/remediators/test_generator.py`
- `src/remediators/pr_draft_generator.py`

**Critical:** Bob output must include:
- `generated_security_tests[]`
- `pr_draft{}`

These are automatically saved when `--use-bob` flag is used.

## Troubleshooting

### Rust Scanner Issues

**Problem:** `cargo check` fails
```bash
cd rust-scanner
cargo clean
cargo check
```

**Problem:** Python can't call Rust scanner
- Verify `--path` flag (not `--paths`)
- Check Cargo.toml has correct binary name

### Contract Issues

**Problem:** JSON parsing errors
```bash
# Validate JSON
python -m json.tool contracts/sample_findings.json
```

**Problem:** Missing fields
- Use normalizers: `from utils.normalizers import normalize_finding`
- Check contract schemas

### Frontend Issues

**Problem:** TypeScript errors
```bash
cd frontend
npm run build
```

**Problem:** Types don't match backend
- Ensure `frontend/src/api/types.ts` matches Python JSON
- Use snake_case for all fields

### Integration Issues

**Problem:** Data not flowing end-to-end
```bash
# Run integration check
python scripts/integration_check.py

# Check each step
python src/main.py analyze --path ./mock-repos --use-mock --use-bob
```

## Testing the Full Flow

### Quick Test (5 minutes)

```bash
# 1. Verify Rust scanner
cd rust-scanner && cargo check && cd ..

# 2. Run integration check
python scripts/integration_check.py

# 3. Run analysis with mock data
python src/main.py analyze --path ./mock-repos --use-mock --use-bob

# 4. Check outputs
ls generated_tests/
ls generated_reports/

# 5. Build frontend
cd frontend && npm run build && cd ..
```

### Full Demo (10 minutes)

```bash
# 1. Run backend analysis
python src/main.py analyze \
  --path ./mock-repos \
  --use-mock \
  --use-bob \
  --output ./output \
  --format markdown json

# 2. Start frontend
cd frontend
npm run dev

# 3. Open browser to http://localhost:5173

# 4. Verify dashboard shows:
#    - Findings table
#    - Incident details
#    - Attack path graph
#    - Bob analysis
#    - Generated tests
#    - PR draft
```

## Success Criteria

✅ **Integration is working when:**

1. Rust scanner outputs valid JSON findings
2. Python backend creates incidents with attack paths
3. Bob generates fixes, tests, and PR drafts
4. Generated tests are saved to `generated_tests/`
5. PR drafts are saved to `generated_reports/`
6. Frontend builds without TypeScript errors
7. Dashboard displays all incident information
8. Integration check script passes all tests

## Next Steps

After integration is verified:

1. **Add Real Bob API:** Replace mock Bob with actual IBM watsonx.ai API
2. **Add Backend API:** Create FastAPI endpoints for frontend
3. **Add Database:** Store incidents and memory persistently
4. **Add Authentication:** Secure the dashboard
5. **Add CI/CD:** Automate testing and deployment

---

*Generated for IBM Jeff Hackathon*