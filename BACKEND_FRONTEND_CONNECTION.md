# Connecting Frontend to Backend and Rust Scanner

## Current State vs. Full Integration

### Current State (Working Now)
```
Frontend (Mock Mode) ← Static JSON files
Python Backend ← Mock findings (--use-mock flag)
```

### Full Integration (What You Want)
```
Frontend ← HTTP API ← Python Backend ← Rust Scanner
```

---

## Option 1: Use Real Rust Scanner (Keep Frontend in Mock Mode)

This is the **easiest next step** - just remove the `--use-mock` flag:

### Step 1: Build Rust Scanner

```bash
cd rust-scanner
cargo build --release
cd ..
```

### Step 2: Run Analysis with Real Rust Scanner

```bash
# Instead of --use-mock, let it use the real Rust scanner
python src/main.py analyze --path ./mock-repos --use-bob

# Or scan your actual repositories
python src/main.py analyze --path /path/to/your/repos --use-bob
```

**What happens:**
1. Python calls: `cargo run -- scan --path ./mock-repos`
2. Rust scanner analyzes the code
3. Returns JSON findings to Python
4. Python processes them through the full pipeline
5. Generates reports, tests, and PR drafts

**Frontend:** Still uses mock data (no changes needed yet)

---

## Option 2: Connect Frontend to Backend via API

This requires creating a REST API server.

### Step 1: Create API Server

Create `src/api_server.py`:

```python
#!/usr/bin/env python3
"""
FastAPI server for Jeff
Provides REST API for frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
from typing import List, Dict, Any

app = FastAPI(title="Jeff API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data storage (in-memory for now)
findings_db: List[Dict[str, Any]] = []
incidents_db: List[Dict[str, Any]] = []
bob_outputs_db: Dict[str, Dict[str, Any]] = {}

@app.get("/")
def root():
    return {"message": "Jeff API", "version": "1.0.0"}

@app.get("/api/findings")
def get_findings():
    """Get all findings"""
    return findings_db

@app.get("/api/incidents")
def get_incidents():
    """Get all incidents"""
    return incidents_db

@app.get("/api/incidents/{incident_id}")
def get_incident(incident_id: str):
    """Get specific incident"""
    incident = next((i for i in incidents_db if i["incident_id"] == incident_id), None)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@app.get("/api/incidents/{incident_id}/bob-analysis")
def get_bob_analysis(incident_id: str):
    """Get Bob analysis for incident"""
    if incident_id not in bob_outputs_db:
        raise HTTPException(status_code=404, detail="Bob analysis not found")
    return bob_outputs_db[incident_id]

@app.post("/api/scan")
async def trigger_scan(paths: List[str]):
    """Trigger a new scan"""
    # This would call the main analysis pipeline
    # For now, return success
    return {"status": "scan_started", "paths": paths}

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "findings_count": len(findings_db),
        "incidents_count": len(incidents_db)
    }

# Load data from files on startup
@app.on_event("startup")
def load_data():
    """Load existing analysis results"""
    global findings_db, incidents_db, bob_outputs_db
    
    # Load from output directory if exists
    output_dir = Path("./output")
    if output_dir.exists():
        # Load findings
        findings_file = output_dir / "findings.json"
        if findings_file.exists():
            with open(findings_file, 'r', encoding='utf-8') as f:
                findings_db = json.load(f)
        
        # Load incidents
        incidents_file = output_dir / "incidents.json"
        if incidents_file.exists():
            with open(incidents_file, 'r', encoding='utf-8') as f:
                incidents_db = json.load(f)
        
        # Load Bob outputs
        bob_file = output_dir / "bob_outputs.json"
        if bob_file.exists():
            with open(bob_file, 'r', encoding='utf-8') as f:
                bob_outputs_db = json.load(f)
    
    print(f"Loaded {len(findings_db)} findings, {len(incidents_db)} incidents")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Step 2: Install FastAPI

```bash
pip install fastapi uvicorn
```

### Step 3: Update Backend to Save API Data

Modify `src/main.py` to save data in API-friendly format:

```python
# Add this after generating reports (around line 150)

# Save data for API server
api_output_dir = Path(output) / "api"
api_output_dir.mkdir(parents=True, exist_ok=True)

# Save findings
with open(api_output_dir / "findings.json", 'w', encoding='utf-8') as f:
    json.dump(findings, f, indent=2)

# Save incidents
with open(api_output_dir / "incidents.json", 'w', encoding='utf-8') as f:
    json.dump(incidents, f, indent=2)

# Save Bob outputs
bob_outputs = {}
for incident in incidents:
    if 'bob_analysis' in incident:
        bob_outputs[incident['incident_id']] = incident['bob_analysis']

with open(api_output_dir / "bob_outputs.json", 'w', encoding='utf-8') as f:
    json.dump(bob_outputs, f, indent=2)
```

### Step 4: Update Frontend to Use Real API

Edit `frontend/src/api/client.ts`:

```typescript
// Change this line:
const USE_MOCK_DATA = true;

// To:
const USE_MOCK_DATA = false;
```

### Step 5: Run Everything

**Terminal 1 - Run Analysis:**
```bash
python src/main.py analyze --path ./mock-repos --use-bob --output ./output
```

**Terminal 2 - Start API Server:**
```bash
python src/api_server.py
# API runs on http://localhost:8000
```

**Terminal 3 - Start Frontend:**
```bash
cd frontend
npm run dev
# Frontend runs on http://localhost:5173
```

**Terminal 4 - Test API:**
```bash
# Check API health
curl http://localhost:8000/api/health

# Get findings
curl http://localhost:8000/api/findings

# Get incidents
curl http://localhost:8000/api/incidents
```

---

## Option 3: Full Real-Time Integration

For a complete real-time system:

### Architecture

```
User → Frontend → API Server → Analysis Pipeline → Rust Scanner
                      ↓
                  WebSocket (real-time updates)
                      ↓
                  Frontend (live progress)
```

### Implementation Steps

1. **Add WebSocket support to API server**
2. **Make analysis pipeline async**
3. **Stream progress updates to frontend**
4. **Add job queue for multiple scans**

This is more complex and better suited for production deployment.

---

## Quick Connection Test

### Test 1: Rust Scanner → Python

```bash
# Test Rust scanner directly
cd rust-scanner
cargo run -- scan --path ../mock-repos/legacy-backend

# Should output JSON findings
```

### Test 2: Python → Rust Scanner

```bash
# Test Python calling Rust
python -c "
from src.scanners.rust_scanner_client import RustScannerClient
scanner = RustScannerClient()
findings = scanner.scan(['./mock-repos'], use_mock=False)
print(f'Found {len(findings)} findings')
"
```

### Test 3: Frontend → Backend (Mock)

```bash
# Start frontend
cd frontend
npm run dev

# Open http://localhost:5173
# Should see mock data
```

### Test 4: Frontend → Backend (API)

```bash
# Terminal 1: Start API
python src/api_server.py

# Terminal 2: Start frontend with API mode
cd frontend
# Edit src/api/client.ts: USE_MOCK_DATA = false
npm run dev

# Open http://localhost:5173
# Should fetch from API
```

---

## Recommended Approach for Hackathon

**For fastest demo:**

1. ✅ **Use mock mode** (already working)
   - Frontend shows mock data
   - Backend generates reports
   - No API needed

2. ✅ **Add real Rust scanner** (5 minutes)
   ```bash
   python src/main.py analyze --path ./mock-repos --use-bob
   # Remove --use-mock flag
   ```

3. ⏭️ **Add API later** (if time permits)
   - Create `api_server.py`
   - Update frontend to `USE_MOCK_DATA = false`

**For production:**

1. Build full API server with FastAPI
2. Add authentication
3. Add database (PostgreSQL)
4. Add job queue (Celery/Redis)
5. Add WebSocket for real-time updates
6. Deploy with Docker

---

## Current Working Flow

**What works RIGHT NOW:**

```bash
# 1. Run analysis (generates all files)
python src/main.py analyze --path ./mock-repos --use-mock --use-bob

# 2. View generated files
cat output/INC-001_report.md
cat generated_tests/test_export_api_security.py
cat generated_reports/PR_DRAFT_security-fix-inc-001_INC-001.md

# 3. View frontend (mock mode)
cd frontend && npm run dev
# Open http://localhost:5173
```

**This demonstrates the full pipeline without needing API integration!**

---

## Summary

| Connection | Status | How to Enable |
|------------|--------|---------------|
| Python → Rust Scanner | ✅ Working | Remove `--use-mock` flag |
| Python → Bob AI | ✅ Working | Use `--use-bob` flag |
| Python → Generated Files | ✅ Working | Automatic |
| Frontend → Mock Data | ✅ Working | Default mode |
| Frontend → API → Python | ⏭️ Optional | Create `api_server.py` |
| Real-time Updates | ⏭️ Future | Add WebSocket |

**For the hackathon demo, the current setup (mock mode) is sufficient to show all features!**

The backend already connects to Rust scanner - just remove the `--use-mock` flag to use it.