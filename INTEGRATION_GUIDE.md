# Bob Sentinel - Frontend-Backend Integration Guide

## 🎯 Overview

This guide explains how the Bob Sentinel frontend dashboard connects to the backend API server.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React + Vite)                  │
│                    http://localhost:5173                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Dashboard UI Components                              │  │
│  │  - OverviewCards                                      │  │
│  │  - FindingsTable                                      │  │
│  │  - IncidentDetail                                     │  │
│  │  - BobAnalysis                                        │  │
│  │  - AttackPathGraph                                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Client (axios)                                   │  │
│  │  - getFindings()                                      │  │
│  │  - getIncidents()                                     │  │
│  │  - getBobAnalysis()                                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                   Backend API (Flask)                        │
│                   http://localhost:8000                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  REST API Endpoints                                   │  │
│  │  GET  /api/health                                     │  │
│  │  GET  /api/findings                                   │  │
│  │  GET  /api/incidents                                  │  │
│  │  GET  /api/incidents/:id                              │  │
│  │  POST /api/incidents/:id/analyze-with-bob             │  │
│  │  POST /api/analyze                                    │  │
│  │  GET  /api/memory                                     │  │
│  │  GET  /api/stats                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Analysis Pipeline                                    │  │
│  │  - RustScannerClient                                  │  │
│  │  - IncidentCorrelator                                 │  │
│  │  - SeverityClassifier                                 │  │
│  │  - ConfidenceScorer                                   │  │
│  │  - AttackPathBuilder                                  │  │
│  │  - ReasoningEngine (IBM Bob)                          │  │
│  │  - MemoryManager                                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)

```bash
# Start both frontend and backend with one command
./start_services.sh
```

This will:
1. Check dependencies
2. Start backend API on port 8000
3. Start frontend dashboard on port 5173
4. Open your browser automatically

### Option 2: Manual Startup

**Terminal 1 - Backend API:**
```bash
# Activate virtual environment
source venv/bin/activate  # or: source .venv/bin/activate

# Start API server
python src/api_server.py
```

**Terminal 2 - Frontend Dashboard:**
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

## 📡 API Endpoints

### Health Check
```http
GET /api/health
```
Returns API status and version information.

### Get All Findings
```http
GET /api/findings
```
Returns array of security findings from all scans.

**Response:**
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
    "evidence": "Possible API key detected",
    "timestamp": "2026-05-16T12:00:00Z"
  }
]
```

### Get All Incidents
```http
GET /api/incidents
```
Returns array of correlated security incidents.

**Response:**
```json
[
  {
    "incident_id": "INC-001",
    "title": "Possible credential leakage through exposed abandoned export API",
    "severity": "critical",
    "severity_level": 5,
    "confidence_score": 0.88,
    "confidence_reasons": [...],
    "affected_repos": ["legacy-backend"],
    "findings": [...],
    "attack_path": {...}
  }
]
```

### Get Specific Incident
```http
GET /api/incidents/:incident_id
```
Returns detailed information about a specific incident.

### Analyze with Bob AI
```http
POST /api/incidents/:incident_id/analyze-with-bob
```
Runs IBM Bob AI analysis on an incident.

**Response:**
```json
{
  "attack_type": "Credential leakage and abandoned API abuse",
  "target": "User export endpoint and users database table",
  "severity": "critical",
  "confidence_assessment": "High confidence (88%)...",
  "recommended_fixes": [...],
  "generated_security_tests": [...],
  "incident_report": "...",
  "ai_memory": {...},
  "pr_draft": {...}
}
```

### Run New Analysis
```http
POST /api/analyze
Content-Type: application/json

{
  "paths": ["/path/to/scan"],
  "use_mock": true,
  "use_bob": true
}
```

### Get AI Memory
```http
GET /api/memory
```
Returns all AI memory entries (learned security patterns).

### Get Statistics
```http
GET /api/stats
```
Returns system statistics.

## 🔧 Configuration

### Backend Configuration

**File:** `config/config.yaml`

Key settings:
```yaml
database:
  type: mongodb  # or sqlite
  host: localhost
  port: 27017

ai_engine:
  local_models:
    enabled: true
  bob:
    enabled: true
```

### Frontend Configuration

**File:** `frontend/.env`

```env
VITE_API_BASE_URL=http://localhost:8000
```

**File:** `frontend/src/api/client.ts`

```typescript
// Toggle between mock and real API
const USE_MOCK_DATA = false;  // false = use real backend
```

## 🔄 Data Flow

1. **User opens dashboard** → Frontend loads
2. **Dashboard requests data** → `apiClient.getFindings()`
3. **API receives request** → `/api/findings`
4. **Backend scans repos** → RustScannerClient
5. **Findings returned** → JSON response
6. **Dashboard displays** → FindingsTable component

## 🐛 Troubleshooting

### Frontend can't connect to backend

**Problem:** Network error or CORS issues

**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/api/health

# Check CORS is enabled in src/api_server.py
# Should see: CORS(app)
```

### Backend returns empty data

**Problem:** No findings or incidents in cache

**Solution:**
```bash
# Run a scan first
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"paths": ["./mock-repos"], "use_mock": true}'
```

### Mock data still showing

**Problem:** `USE_MOCK_DATA = true` in client.ts

**Solution:**
```typescript
// frontend/src/api/client.ts
const USE_MOCK_DATA = false;  // Change to false
```

### Port already in use

**Problem:** Port 8000 or 5173 is occupied

**Solution:**
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or change port in api_server.py
app.run(host='0.0.0.0', port=8001, debug=True)
```

## 🧪 Testing the Integration

### 1. Health Check
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Bob Sentinel API",
  "version": "1.0.0"
}
```

### 2. Get Findings
```bash
curl http://localhost:8000/api/findings
```

### 3. Get Incidents
```bash
curl http://localhost:8000/api/incidents
```

### 4. Run Bob Analysis
```bash
curl -X POST http://localhost:8000/api/incidents/INC-001/analyze-with-bob
```

## 📊 Monitoring

### Backend Logs
```bash
# Watch API server logs
tail -f logs/security_analyst.log
```

### Frontend Console
Open browser DevTools (F12) → Console tab to see:
- API requests
- Response data
- Error messages

## 🔒 Security Considerations

1. **CORS:** Enabled for development, restrict in production
2. **API Keys:** Store in environment variables, not in code
3. **Rate Limiting:** Add rate limiting for production
4. **Authentication:** Add JWT or OAuth for production
5. **HTTPS:** Use HTTPS in production

## 📚 Additional Resources

- [Backend API Documentation](docs/API.md)
- [Frontend Component Guide](frontend/README.md)
- [Architecture Overview](ARCHITECTURE.md)
- [User Guide](docs/USER_GUIDE.md)

## 🤝 Contributing

When adding new API endpoints:

1. Add endpoint to `src/api_server.py`
2. Add corresponding method to `frontend/src/api/client.ts`
3. Update TypeScript types in `frontend/src/api/types.ts`
4. Update this documentation

## 📞 Support

For issues or questions:
- Check troubleshooting section above
- Review logs in `logs/` directory
- Open an issue on GitHub

---

**Made with ❤️ by Bob**