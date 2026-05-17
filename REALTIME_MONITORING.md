# Real-Time Attack Monitoring

This document explains the real-time monitoring system implemented in Jeff.

## Overview

Jeff now features real-time attack monitoring using WebSocket connections between the frontend and backend. This allows security teams to receive instant notifications when new findings or incidents are detected.

## Architecture

### Backend (FastAPI + WebSocket)

**File:** `src/api_server.py`

The backend implements:
- WebSocket endpoint at `/ws` for real-time connections
- Connection manager to handle multiple clients
- Broadcast functionality to push updates to all connected clients
- Heartbeat mechanism to keep connections alive

**Key Components:**

```python
# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket)

# Notification functions
async def notify_new_finding(finding: Dict[str, Any])
async def notify_new_incident(incident: Dict[str, Any])
async def notify_bob_analysis(incident_id: str, bob_output: Dict[str, Any])
```

### Frontend (React + WebSocket)

**File:** `frontend/src/hooks/useRealtimeMonitoring.ts`

The frontend implements:
- Custom React hook for WebSocket management
- Automatic reconnection on disconnect
- Browser notifications for new findings/incidents
- Heartbeat ping/pong to maintain connection

**File:** `frontend/src/pages/DashboardPage.tsx`

The dashboard integrates:
- Real-time status indicator (connected/disconnected)
- Live notification counter for new findings/incidents
- Toast notifications for real-time alerts
- Automatic data refresh when new items arrive

## Features

### 1. Real-Time Connection Status

The dashboard displays the current WebSocket connection status:
- 🟢 **Connected**: Real-time monitoring is active
- 🔴 **Disconnected**: Connection lost, with reconnect button

### 2. Live Notifications

When new security events occur:
- **In-App Toast**: Slide-in notification with event details
- **Browser Notification**: Desktop notification (requires permission)
- **Counter Badge**: Shows number of new findings/incidents

### 3. Automatic Reconnection

If the connection is lost:
- Automatic reconnection attempt after 5 seconds
- Manual reconnect button available
- Connection state preserved during reconnection

### 4. Event Types

The system monitors and notifies for:
- **new_finding**: New security finding detected
- **new_incident**: New correlated incident created
- **bob_analysis**: AI analysis completed for an incident

## Setup Instructions

### 1. Install Dependencies

Backend (already in requirements.txt):
```bash
pip install fastapi uvicorn websockets
```

Frontend (already in package.json):
```bash
cd frontend
npm install
```

### 2. Start the Backend

```bash
# Start the API server with WebSocket support
python src/api_server.py
```

The server will be available at:
- HTTP API: `http://localhost:8000`
- WebSocket: `ws://localhost:8000/ws`

### 3. Start the Frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at: `http://localhost:5173`

### 4. Enable Browser Notifications

When you first load the dashboard:
1. Browser will request notification permission
2. Click "Allow" to enable desktop notifications
3. You'll receive notifications even when the tab is not active

## Configuration

### Environment Variables

**Frontend** (`frontend/.env`):
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

**Backend** (no additional config needed):
- WebSocket runs on the same port as HTTP API
- CORS is configured for localhost:5173

## Testing Real-Time Monitoring

### Manual Testing

1. **Start both backend and frontend**
2. **Open the dashboard** - you should see "Real-time Monitoring Active"
3. **Trigger a scan** to generate new findings:
   ```bash
   python src/main.py analyze --path ./mock-repos --use-mock
   ```
4. **Watch for notifications** in the dashboard

### Simulating Events

To test without running a full scan, you can manually trigger notifications from the backend:

```python
# In src/api_server.py or a test script
import asyncio

# Simulate new finding
await notify_new_finding({
    "finding_id": "TEST-001",
    "repo_name": "test-repo",
    "finding_type": "test_finding",
    "severity_hint": "high",
    # ... other fields
})

# Simulate new incident
await notify_new_incident({
    "incident_id": "TEST-INC-001",
    "title": "Test Incident",
    "severity": "critical",
    # ... other fields
})
```

## Monitoring Multiple Clients

The WebSocket server supports multiple simultaneous connections:
- Each browser tab creates a separate connection
- All connected clients receive the same updates
- Connection count is logged in the backend

## Troubleshooting

### Connection Issues

**Problem**: WebSocket won't connect

**Solutions**:
1. Check backend is running: `curl http://localhost:8000/api/health`
2. Verify WebSocket URL in browser console
3. Check firewall/antivirus settings
4. Try manual reconnect button

### No Notifications

**Problem**: Not receiving browser notifications

**Solutions**:
1. Check browser notification permissions
2. Ensure notifications aren't blocked for localhost
3. Check browser console for errors
4. Verify WebSocket connection is active

### Disconnections

**Problem**: Frequent disconnections

**Solutions**:
1. Check network stability
2. Verify backend logs for errors
3. Increase heartbeat interval if needed
4. Check for proxy/firewall interference

## Performance Considerations

### Backend

- **Connection Limit**: No hard limit, but monitor memory usage
- **Message Size**: Keep broadcast messages under 1MB
- **Heartbeat**: 30-second interval prevents timeout

### Frontend

- **Memory**: Old notifications are cleared automatically
- **Reconnection**: Exponential backoff prevents server overload
- **Browser Tabs**: Each tab maintains separate connection

## Security Considerations

1. **Authentication**: Currently no auth on WebSocket (add JWT if needed)
2. **CORS**: Restricted to localhost in development
3. **Rate Limiting**: Consider adding for production
4. **Message Validation**: All messages are JSON validated

## Future Enhancements

Potential improvements:
- [ ] Add authentication to WebSocket connections
- [ ] Implement message queuing for offline clients
- [ ] Add filtering options for notification types
- [ ] Support for custom notification sounds
- [ ] Historical event replay on reconnection
- [ ] WebSocket connection pooling
- [ ] Compression for large messages

## API Reference

### WebSocket Messages

**Client → Server:**
```json
{
  "type": "ping"
}
```

**Server → Client:**

Initial data:
```json
{
  "type": "initial_data",
  "data": {
    "findings": [...],
    "incidents": [...],
    "timestamp": "2026-05-16T15:00:00Z"
  }
}
```

New finding:
```json
{
  "type": "new_finding",
  "data": { /* Finding object */ },
  "timestamp": "2026-05-16T15:00:00Z"
}
```

New incident:
```json
{
  "type": "new_incident",
  "data": { /* Incident object */ },
  "timestamp": "2026-05-16T15:00:00Z"
}
```

Bob analysis:
```json
{
  "type": "bob_analysis",
  "data": {
    "incident_id": "INC-001",
    "analysis": { /* BobOutput object */ }
  },
  "timestamp": "2026-05-16T15:00:00Z"
}
```

Heartbeat response:
```json
{
  "type": "pong",
  "timestamp": "2026-05-16T15:00:00Z"
}
```

## Support

For issues or questions:
1. Check backend logs: `python src/api_server.py`
2. Check browser console for frontend errors
3. Review this documentation
4. Check WebSocket connection in browser DevTools (Network tab)

---

**Made with Bob** 🤖