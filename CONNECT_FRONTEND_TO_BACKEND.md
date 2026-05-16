# How to Connect Frontend to Real Backend

## Current Status
- ❌ Frontend shows MOCK data (hardcoded in `frontend/src/api/client.ts`)
- ✅ Backend works and generates real data
- ✅ API server created (`src/api_server.py`)

## Goal
- ✅ Frontend fetches REAL data from backend via API

---

## Step-by-Step Connection Guide

### Step 1: Install FastAPI (if not already installed)

```bash
pip install fastapi uvicorn
```

### Step 2: Run Backend Analysis to Generate Data

```bash
# This creates the JSON files that the API will serve
python src/main.py analyze --path ./mock-repos --use-mock --use-bob --output ./output
```

**What this does:**
- Scans repositories
- Generates incidents
- Runs Bob AI analysis
- **Saves 3 JSON files in `output/` directory:**
  - `findings.json`
  - `incidents.json`
  - `bob_outputs.json`

**Verify the files exist:**
```bash
ls output/
# Should see: findings.json, incidents.json, bob_outputs.json
```

### Step 3: Start the API Server

Open a **NEW terminal** and run:

```bash
python src/api_server.py
```

**You should see:**
```
🚀 Starting Jeff API Server
============================================================
API will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs
Health check: http://localhost:8000/api/health
============================================================

INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     ✓ Loaded 5 findings
INFO:     ✓ Loaded 1 incidents
INFO:     ✓ Loaded 1 Bob analyses
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Test the API (Optional but Recommended)

Open another terminal and test:

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test findings endpoint
curl http://localhost:8000/api/findings

# Test incidents endpoint
curl http://localhost:8000/api/incidents
```

**Expected output:**
- Health: `{"status":"healthy","findings_count":5,"incidents_count":1,"bob_analyses_count":1}`
- Findings: JSON array with 5 findings
- Incidents: JSON array with 1 incident

### Step 5: Switch Frontend from Mock to Real API

Edit `frontend/src/api/client.ts`:

**Find this line (around line 7):**
```typescript
const USE_MOCK_DATA = true;
```

**Change it to:**
```typescript
const USE_MOCK_DATA = false;
```

**Save the file.**

### Step 6: Start Frontend

Open another terminal:

```bash
cd frontend
npm run dev
```

**Open browser:** http://localhost:5173

### Step 7: Verify Real Connection

**In the browser, you should now see:**
- Real data from your backend analysis
- The incident title: "Possible credential leakage through exposed abandoned export API"
- 5 findings in the findings table
- Attack path graph with nodes
- Bob analysis with recommended fixes

**To confirm it's real data (not mock):**
1. Check browser developer tools (F12)
2. Go to Network tab
3. Refresh the page
4. You should see API calls to `localhost:8000/api/findings`, etc.

---

## Troubleshooting

### Problem: "Failed to fetch" errors in frontend

**Solution:** Make sure API server is running on port 8000

```bash
# Check if API is running
curl http://localhost:8000/api/health
```

### Problem: API returns empty data

**Solution:** Run backend analysis first to generate data

```bash
python src/main.py analyze --path ./mock-repos --use-mock --use-bob --output ./output
```

### Problem: CORS errors in browser

**Solution:** API server already has CORS enabled. Make sure you're using `localhost:5173` (not `127.0.0.1`)

### Problem: API server won't start

**Solution:** Install FastAPI

```bash
pip install fastapi uvicorn
```

---

## Complete Working Setup

**Terminal 1 - API Server:**
```bash
python src/api_server.py
# Keep running
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Keep running
```

**Browser:**
- Open http://localhost:5173
- Should show real backend data

---

## How to Verify It's Working

### Visual Confirmation

**Mock Mode (old):**
- Shows generic mock incident
- Always same data

**Real Mode (new):**
- Shows "Possible credential leakage through exposed abandoned export API"
- Shows 5 specific findings
- Shows real attack path
- Shows Bob's actual analysis

### Technical Confirmation

**Browser Developer Tools (F12):**
1. Open Network tab
2. Refresh page
3. Should see requests to:
   - `http://localhost:8000/api/findings`
   - `http://localhost:8000/api/incidents`
   - `http://localhost:8000/api/incidents/INC-001/bob-analysis`

### API Direct Test

```bash
# Should return real data
curl http://localhost:8000/api/incidents | jq '.[0].title'
# Output: "Possible credential leakage through exposed abandoned export API"
```

---

## Data Flow Verification

**Complete flow:**
```
1. python src/main.py analyze → generates output/*.json
2. python src/api_server.py → loads output/*.json, serves via HTTP
3. frontend (USE_MOCK_DATA=false) → fetches from http://localhost:8000
4. Browser shows real backend data
```

**Files involved:**
- `output/findings.json` ← Backend writes
- `output/incidents.json` ← Backend writes  
- `output/bob_outputs.json` ← Backend writes
- `src/api_server.py` ← Reads files, serves HTTP API
- `frontend/src/api/client.ts` ← Fetches from API (when USE_MOCK_DATA=false)

---

## Quick Test Script

Save this as `test_connection.py`:

```python
#!/usr/bin/env python3
import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    try:
        # Test health
        response = requests.get(f"{base_url}/api/health")
        health = response.json()
        print(f"✓ API Health: {health}")
        
        # Test findings
        response = requests.get(f"{base_url}/api/findings")
        findings = response.json()
        print(f"✓ Findings: {len(findings)} items")
        
        # Test incidents
        response = requests.get(f"{base_url}/api/incidents")
        incidents = response.json()
        print(f"✓ Incidents: {len(incidents)} items")
        
        if incidents:
            incident_id = incidents[0]["incident_id"]
            print(f"✓ First incident: {incident_id}")
            
            # Test Bob analysis
            response = requests.get(f"{base_url}/api/incidents/{incident_id}/bob-analysis")
            bob = response.json()
            print(f"✓ Bob analysis: {bob.get('attack_type', 'N/A')}")
        
        print("\n🎉 All API endpoints working!")
        
    except requests.exceptions.ConnectionError:
        print("❌ API server not running. Start with: python src/api_server.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api()
```

Run with: `python test_connection.py`

---

## Summary

**To connect frontend to real backend:**

1. ✅ **Generate data:** `python src/main.py analyze --path ./mock-repos --use-mock --use-bob --output ./output`
2. ✅ **Start API:** `python src/api_server.py`
3. ✅ **Switch frontend:** Change `USE_MOCK_DATA = false` in `frontend/src/api/client.ts`
4. ✅ **Start frontend:** `cd frontend && npm run dev`
5. ✅ **Open browser:** http://localhost:5173

**You'll know it's working when:**
- Browser shows real incident data
- Network tab shows API calls to localhost:8000
- Data changes when you re-run the backend analysis

**The frontend is now connected to the real backend!** 🎉