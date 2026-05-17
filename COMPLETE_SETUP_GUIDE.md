# 🚀 Complete Setup Guide: Rust Scanner + Backend + Frontend + Real-Time Monitoring

This guide shows you how to run the complete Jeff system with all components working together.

## System Architecture

```
┌─────────────────┐
│  Rust Scanner   │ ──┐
│  (Findings)     │   │
└─────────────────┘   │
                      ▼
┌─────────────────┐   ┌──────────────────┐   ┌─────────────────┐
│   Frontend      │◄──│  Backend API     │◄──│  Bob AI         │
│   Dashboard     │   │  + WebSocket     │   │  (watsonx.ai)   │
│   (React)       │   │  (FastAPI)       │   │  or Mock        │
└─────────────────┘   └──────────────────┘   └─────────────────┘
        ▲                      │
        │                      │
        └──────────────────────┘
           Real-time Updates
```

## Prerequisites

### Required
- **Python 3.8+** - For backend
- **Node.js 16+** - For frontend
- **Rust & Cargo** - For scanner (optional, can use mock data)

### Optional (for real AI)
- **IBM Cloud Account** - For watsonx.ai
- **WATSONX_API_KEY** - IBM Cloud API key
- **WATSONX_PROJECT_ID** - watsonx.ai project ID

## Quick Start (5 Minutes)

### Step 1: Install Dependencies

```bash
# Backend dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend
npm install
cd ..
```

### Step 2: Start Backend Server

```bash
# Terminal 1: Start the API server with WebSocket support
python src/api_server.py
```

You should see:
```
🚀 Starting Jeff API Server
API will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs
```

### Step 3: Start Frontend

```bash
# Terminal 2: Start the React frontend
cd frontend
npm run dev
```

You should see:
```
VITE ready in XXX ms
➜  Local:   http://localhost:5173/
```

### Step 4: Open Dashboard

Open your browser to: **http://localhost:5173**

You should see:
- ✅ "Real-time Monitoring Active" (green indicator)
- 🔍 "Run Security Scan" button

### Step 5: Trigger a Scan

Click the **"Run Security Scan"** button in the dashboard!

Watch as:
1. 🔍 Scan starts
2. 📊 Findings appear in real-time
3. 🚨 Incidents are correlated
4. 🤖 Bob AI analyzes and generates fixes
5. 🔔 Notifications pop up for each event

## Detailed Setup

### Backend Configuration

The backend automatically detects if you have IBM watsonx.ai credentials:

**Without API Key (Demo Mode):**
```bash
# Just run the server - it will use intelligent mock responses
python src/api_server.py
```

**With IBM watsonx.ai (Real AI):**
```bash
# Set environment variables
export WATSONX_API_KEY="your-ibm-cloud-api-key"
export WATSONX_PROJECT_ID="your-project-id"
export WATSONX_URL="https://us-south.ml.cloud.ibm.com"

# Run the server
python src/api_server.py
```

### Frontend Configuration

Create `frontend/.env` (optional):
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

### Rust Scanner Configuration

**Option 1: Use Mock Data (Recommended for Demo)**
- No Rust installation needed
- Click "Run Security Scan" - it uses pre-configured findings
- Perfect for demonstrations

**Option 2: Use Real Rust Scanner**
```bash
# Build the Rust scanner
cd rust-scanner
cargo build --release
cd ..

# The backend will automatically use it
```

## How to Use

### 1. Real-Time Monitoring

The dashboard automatically connects via WebSocket:
- **Green indicator** = Connected and monitoring
- **Red indicator** = Disconnected (click Reconnect)

### 2. Trigger Scans

**From Dashboard:**
- Click "🔍 Run Security Scan" button
- Watch real-time updates appear

**From Command Line:**
```bash
# Using the main CLI
python src/main.py analyze --path ./mock-repos --use-mock --use-bob

# Or trigger via API
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"paths": ["./mock-repos"], "use_mock": true, "use_bob": true}'
```

### 3. View Results

**Real-Time Notifications:**
- Browser notifications (allow when prompted)
- In-app toast notifications
- Live counter of new findings/incidents

**Dashboard Tabs:**
- **Overview** - Summary cards and recent findings
- **Findings** - All security findings
- **Incident Analysis** - Correlated incidents with attack paths
- **Bob AI Analysis** - AI-generated fixes, tests, and reports

## Features Demonstrated

### ✅ Rust Scanner Integration
- Scans code for secrets, APIs, infrastructure issues
- Outputs findings in standardized JSON format
- Integrates with Python backend

### ✅ Real-Time Monitoring
- WebSocket connection for instant updates
- No polling - push-based notifications
- Multiple clients supported

### ✅ Bob AI Analysis
- Analyzes security incidents
- Generates remediation plans
- Creates security tests
- Writes PR drafts
- **Works without API key** (uses intelligent mocks)

### ✅ Attack Path Visualization
- Shows how findings correlate
- Visual graph of attack chain
- Confidence scoring

### ✅ Incident Correlation
- Groups related findings
- Temporal correlation
- Target-based correlation
- Attack chain detection

## Testing the System

### Test 1: Basic Scan
```bash
# Click "Run Security Scan" in dashboard
# Watch for:
# - 5 findings appear one by one
# - 1 incident created
# - Bob AI analysis completes
# - Notifications for each event
```

### Test 2: Multiple Clients
```bash
# Open dashboard in 2 browser tabs
# Trigger scan from one tab
# Watch both tabs receive updates simultaneously
```

### Test 3: Reconnection
```bash
# Stop the backend (Ctrl+C)
# Dashboard shows "Disconnected"
# Restart backend
# Click "Reconnect" or wait 5 seconds
# Connection restored automatically
```

## API Endpoints

### REST API

```bash
# Health check
GET http://localhost:8000/api/health

# Get all findings
GET http://localhost:8000/api/findings

# Get all incidents
GET http://localhost:8000/api/incidents

# Get specific incident
GET http://localhost:8000/api/incidents/{incident_id}

# Get Bob analysis
GET http://localhost:8000/api/incidents/{incident_id}/bob-analysis

# Trigger scan
POST http://localhost:8000/api/scan
Body: {"paths": ["./mock-repos"], "use_mock": true, "use_bob": true}
```

### WebSocket

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

// Receive messages
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Update:', update.type, update.data);
};
```

## Troubleshooting

### Backend Won't Start

**Problem:** `ModuleNotFoundError`
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Problem:** Port 8000 already in use
```bash
# Solution: Kill the process or use different port
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

### Frontend Won't Connect

**Problem:** WebSocket connection failed
```bash
# Check backend is running
curl http://localhost:8000/api/health

# Check WebSocket URL in browser console
# Should be: ws://localhost:8000/ws
```

**Problem:** CORS errors
```bash
# Backend CORS is configured for localhost:5173
# Make sure frontend is running on that port
```

### No Notifications

**Problem:** Browser notifications not showing
```bash
# Solution: Allow notifications when prompted
# Or check browser settings:
# Chrome: Settings > Privacy > Site Settings > Notifications
# Allow for localhost:5173
```

### Scan Not Working

**Problem:** Scan button does nothing
```bash
# Check browser console for errors
# Check backend logs
# Verify backend is running: curl http://localhost:8000/api/health
```

## Performance Tips

### For Demos
- Use mock data (`use_mock: true`) - instant results
- Mock Bob AI - no API calls needed
- Perfect for presentations

### For Production
- Use real Rust scanner for accurate findings
- Configure IBM watsonx.ai for real AI analysis
- Add authentication to WebSocket
- Implement rate limiting

## IBM watsonx.ai Setup (Optional)

To use real AI instead of mocks:

### 1. Create IBM Cloud Account
Visit: https://cloud.ibm.com

### 2. Create watsonx.ai Instance
1. Go to IBM Cloud Catalog
2. Search for "watsonx.ai"
3. Create a service instance
4. Note your Project ID

### 3. Get API Key
1. Go to IBM Cloud > Manage > Access (IAM)
2. Create an API key
3. Save it securely

### 4. Configure Environment
```bash
export WATSONX_API_KEY="your-api-key-here"
export WATSONX_PROJECT_ID="your-project-id-here"
export WATSONX_URL="https://us-south.ml.cloud.ibm.com"
```

### 5. Restart Backend
```bash
python src/api_server.py
```

You'll see: "🤖 Bob AI: Connected to IBM watsonx.ai"

## Demo Script

Perfect 5-minute demo:

```
1. [0:00] Show dashboard - "Real-time monitoring active"
2. [0:30] Click "Run Security Scan"
3. [1:00] Watch findings appear in real-time
4. [2:00] Show incident correlation
5. [3:00] Show Bob AI analysis with fixes
6. [4:00] Show generated security tests
7. [4:30] Show PR draft
8. [5:00] Highlight real-time notifications
```

## Next Steps

- ✅ System is running
- ✅ Real-time monitoring active
- ✅ Rust scanner integrated
- ✅ Bob AI analyzing incidents

**Try it now:**
1. Open http://localhost:5173
2. Click "🔍 Run Security Scan"
3. Watch the magic happen! ✨

## Support

- Check logs in terminal windows
- Visit http://localhost:8000/docs for API documentation
- Review REALTIME_MONITORING.md for WebSocket details
- Check BACKEND_FRONTEND_CONNECTION.md for integration info

---

**Made with Bob** 🤖 | IBM Hack 2026