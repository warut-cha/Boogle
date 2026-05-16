# 🚀 Bob Sentinel Real-time Dashboard Setup Guide

This guide explains how to set up and run the Bob Sentinel real-time security dashboard with live updates using Server-Sent Events (SSE).

## 📋 Overview

The real-time system consists of three main components:

1. **Flask Backend API** (`src/api_server.py`) - REST API with SSE support
2. **React Frontend Dashboard** (`frontend/`) - Real-time UI with live updates
3. **Event Broadcasting System** - Pushes updates from backend to frontend

## 🎯 Features

- ✅ **Real-time Updates** - See findings and incidents appear instantly
- ✅ **Server-Sent Events (SSE)** - Efficient one-way communication from server to client
- ✅ **Live Event Log** - Monitor all real-time events in the dashboard
- ✅ **Attack Simulation** - Demo mode to showcase real-time capabilities
- ✅ **Auto-reconnection** - Automatically reconnects if connection is lost
- ✅ **Multiple Clients** - Support for multiple dashboard instances

## 🔧 Prerequisites

### Backend Requirements
- Python 3.9+
- Flask and Flask-CORS (already in requirements.txt)

### Frontend Requirements
- Node.js 18+
- npm or yarn

## 📦 Installation

### 1. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Flask (REST API framework)
- Flask-CORS (Cross-origin resource sharing)
- All other project dependencies

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

This installs:
- React 18
- TypeScript
- Vite (build tool)
- Axios (HTTP client)
- Other UI dependencies

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)

Use the provided startup script to launch both backend and frontend:

```bash
python start_realtime_demo.py
```

This will:
1. Check all dependencies
2. Start the Flask backend on `http://localhost:8000`
3. Start the Vite frontend on `http://localhost:5173`
4. Open the dashboard in your browser
5. Display connection status and instructions

### Option 2: Manual Startup

#### Terminal 1 - Start Backend

```bash
python src/api_server.py
```

Expected output:
```
🚀 Bob Sentinel API Server Starting...
📡 Real-time updates available at: http://localhost:8000/api/events
🌐 Dashboard API at: http://localhost:8000/api/

Endpoints:
  GET  /api/health
  GET  /api/findings
  GET  /api/incidents
  GET  /api/events (SSE)
  POST /api/scan
  POST /api/demo/simulate-attack
  POST /api/clear

✨ Ready for connections!
```

#### Terminal 2 - Start Frontend

```bash
cd frontend
npm run dev
```

Expected output:
```
  VITE v5.0.8  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

#### Terminal 3 - Open Dashboard

```bash
# Open in browser
open http://localhost:5173
# or visit manually
```

## 🎭 Demo: Simulating Real-time Attacks

Once the dashboard is running, you can simulate a real-time attack scenario:

### Method 1: Dashboard Button

1. Click the **"Simulate Attack"** button in the dashboard header
2. Watch as findings appear one by one (2-second intervals)
3. See the incident get created and correlated
4. Observe the event log showing SSE messages

### Method 2: API Call

```bash
curl -X POST http://localhost:8000/api/demo/simulate-attack
```

### Method 3: Python Script

```python
import requests

response = requests.post('http://localhost:8000/api/demo/simulate-attack')
print(response.json())
```

## 📡 Real-time Event Flow

```
┌─────────────────┐
│  Flask Backend  │
│  (Port 8000)    │
└────────┬────────┘
         │
         │ SSE Stream (/api/events)
         │
         ▼
┌─────────────────┐
│ Event Broadcaster│
│  (In-memory)    │
└────────┬────────┘
         │
         │ Broadcasts to all connected clients
         │
         ▼
┌─────────────────┐
│ React Dashboard │
│  (Port 5173)    │
└─────────────────┘
```

## 🔌 API Endpoints

### REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check and system status |
| GET | `/api/findings` | Get all security findings |
| GET | `/api/incidents` | Get all correlated incidents |
| GET | `/api/incidents/:id` | Get specific incident details |
| POST | `/api/incidents/:id/analyze-with-bob` | Trigger Bob AI analysis |
| POST | `/api/scan` | Trigger new security scan |
| POST | `/api/demo/simulate-attack` | Simulate attack for demo |
| POST | `/api/clear` | Clear all findings and incidents |

### SSE Endpoint

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/events` | Server-Sent Events stream for real-time updates |

## 📨 SSE Event Types

The backend emits the following event types:

| Event Type | Description | Data |
|------------|-------------|------|
| `connected` | Client connected to SSE stream | Connection message |
| `heartbeat` | Keep-alive ping (every 30s) | Timestamp |
| `finding_added` | New security finding detected | Finding object |
| `incident_added` | New incident created | Incident object |
| `incident_updated` | Incident updated (e.g., Bob analysis) | Updated incident |
| `data_cleared` | All data cleared | Empty object |
| `scan_complete` | Security scan finished | Counts |
| `scan_error` | Scan failed | Error message |
| `demo_progress` | Demo simulation progress | Step info |
| `demo_complete` | Demo simulation finished | Summary |

## 🎨 Frontend Components

### Real-time Client (`frontend/src/api/realtime-client.ts`)

```typescript
import { realtimeClient } from './api/realtime-client';

// Connect to SSE
realtimeClient.connect();

// Subscribe to events
const unsubscribe = realtimeClient.on('finding_added', (event) => {
  console.log('New finding:', event.data);
});

// Trigger actions
await realtimeClient.simulateAttack();
await realtimeClient.clearData();

// Cleanup
unsubscribe();
realtimeClient.disconnect();
```

### Dashboard Features

1. **Connection Status Indicator** - Shows live/disconnected state
2. **Event Log Viewer** - Toggle to see all SSE messages
3. **Real-time Counters** - Findings and incidents update live
4. **Simulate Attack Button** - Trigger demo scenario
5. **Clear Data Button** - Reset dashboard state

## 🔍 Monitoring & Debugging

### Backend Logs

The Flask server logs all events to console:

```
📡 Real-time event: {'type': 'finding_added', 'data': {...}}
✅ Scan complete: {'findings_count': 5, 'incidents_count': 1}
```

### Frontend Console

Open browser DevTools (F12) to see:

```javascript
🔌 Connecting to real-time updates...
✅ Connected to real-time updates
📡 Real-time event: {type: 'finding_added', data: {...}}
```

### Event Log in Dashboard

Click "Show Event Log" button to see all SSE messages in real-time.

## 🐛 Troubleshooting

### Backend won't start

**Problem:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
pip install -r requirements.txt
```

### Frontend won't start

**Problem:** `Cannot find module 'react'`

**Solution:**
```bash
cd frontend
npm install
```

### SSE connection fails

**Problem:** Dashboard shows "Disconnected"

**Solutions:**
1. Check backend is running on port 8000
2. Check CORS is enabled (Flask-CORS installed)
3. Check browser console for errors
4. Try refreshing the page

### Port already in use

**Problem:** `Address already in use: 8000`

**Solution:**
```bash
# Find and kill process using port 8000
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### No events appearing

**Problem:** Dashboard connected but no updates

**Solutions:**
1. Click "Simulate Attack" to trigger demo
2. Check backend logs for errors
3. Verify EventSource is supported in browser
4. Check network tab for SSE connection

## 🧪 Testing the System

### 1. Connection Test

```bash
# Test SSE endpoint directly
curl -N http://localhost:8000/api/events
```

Expected output:
```
data: {"type": "connected", "message": "Real-time updates enabled"}

data: {"type": "heartbeat", "timestamp": "2026-05-16T14:00:00Z"}
```

### 2. Simulate Attack Test

```bash
# Trigger simulation
curl -X POST http://localhost:8000/api/demo/simulate-attack

# Watch events in dashboard or via curl
curl -N http://localhost:8000/api/events
```

### 3. Multiple Clients Test

1. Open dashboard in multiple browser tabs
2. Click "Simulate Attack" in one tab
3. Verify all tabs receive updates simultaneously

## 📊 Performance Considerations

- **SSE Connection Limit:** Browsers typically allow 6 SSE connections per domain
- **Memory Usage:** Event broadcaster stores all findings/incidents in memory
- **Reconnection:** Client auto-reconnects with exponential backoff (max 5 attempts)
- **Heartbeat:** Server sends heartbeat every 30 seconds to keep connection alive

## 🔐 Security Notes

- SSE endpoint is open (no authentication) - add auth for production
- CORS is enabled for all origins - restrict in production
- Events are broadcast to all connected clients - implement per-user filtering if needed

## 🚀 Production Deployment

For production use:

1. **Add Authentication:**
   ```python
   @app.route('/api/events')
   @require_auth
   def sse_events():
       # ...
   ```

2. **Use Production WSGI Server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -k gevent src.api_server:app
   ```

3. **Configure CORS Properly:**
   ```python
   CORS(app, resources={r"/api/*": {"origins": "https://yourdomain.com"}})
   ```

4. **Add Rate Limiting:**
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app, key_func=get_remote_address)
   ```

5. **Use Redis for Event Broadcasting:**
   ```python
   # For multi-process/multi-server deployments
   import redis
   r = redis.Redis()
   ```

## 📚 Additional Resources

- [Server-Sent Events Specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)
- [EventSource API](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review backend logs in terminal
3. Check browser console for frontend errors
4. Open an issue on GitHub

---

**Built with ❤️ by the Bob Sentinel Team**