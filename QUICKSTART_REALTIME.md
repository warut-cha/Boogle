# ⚡ Quick Start - Real-time Dashboard

Get Bob Sentinel's real-time security dashboard running in 3 minutes!

## 🚀 One-Command Start

```bash
python start_realtime_demo.py
```

That's it! The script will:
- ✅ Check all dependencies
- ✅ Start backend API (port 8000)
- ✅ Start frontend dashboard (port 5173)
- ✅ Open browser automatically

## 📺 What You'll See

### Dashboard Features
1. **Live Connection Status** - Green "Live Updates Active" indicator
2. **Real-time Counters** - Findings and incidents update instantly
3. **Event Log** - Click "Show Event Log" to see SSE messages
4. **Control Buttons**:
   - 🎬 **Simulate Attack** - Demo real-time updates
   - 🗑️ **Clear Data** - Reset dashboard

### Demo Flow
1. Click **"Simulate Attack"** button
2. Watch findings appear one-by-one (every 2 seconds)
3. See incident get created and correlated
4. View attack path visualization update
5. Check event log for SSE messages

## 🎯 Quick Demo Steps

### Step 1: Start the System
```bash
python start_realtime_demo.py
```

### Step 2: Wait for Browser
Dashboard opens automatically at `http://localhost:5173`

### Step 3: Simulate Attack
Click the green **"Simulate Attack"** button in the header

### Step 4: Watch Real-time Updates
- Findings appear in the table (3 findings over 6 seconds)
- Incident gets created automatically
- Attack path graph updates
- Event log shows SSE messages

### Step 5: Explore Features
- Switch between tabs (Overview, Findings, Incidents, Analysis)
- Toggle event log on/off
- Clear data and simulate again

## 🔧 Manual Start (Alternative)

If you prefer to start services separately:

### Terminal 1 - Backend
```bash
python src/api_server.py
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

### Terminal 3 - Open Browser
```bash
# Visit http://localhost:5173
```

## 🧪 Testing Real-time Updates

### Test 1: Connection
```bash
# Should show "Live Updates Active" in green
# Check browser console: "✅ Connected to real-time updates"
```

### Test 2: Simulate Attack
```bash
# Click button or use API:
curl -X POST http://localhost:8000/api/demo/simulate-attack
```

### Test 3: Multiple Clients
1. Open dashboard in 2+ browser tabs
2. Click "Simulate Attack" in one tab
3. All tabs update simultaneously ✨

### Test 4: SSE Stream
```bash
# Watch raw SSE events:
curl -N http://localhost:8000/api/events
```

## 📊 Expected Output

### Backend Console
```
🚀 Bob Sentinel API Server Starting...
📡 Real-time updates available at: http://localhost:8000/api/events
✨ Ready for connections!
```

### Frontend Console (F12)
```
🔌 Connecting to real-time updates...
✅ Connected to real-time updates
📡 Real-time event: {type: 'finding_added', ...}
```

### Dashboard Display
```
┌─────────────────────────────────────┐
│ 🛡️ Bob Sentinel - Real-time        │
│ 📡 Live Updates Active              │
│                                     │
│ [🎬 Simulate Attack] [🗑️ Clear]    │
└─────────────────────────────────────┘

Overview Cards:
├─ 3 Findings
├─ 1 Incident  
└─ Critical Severity
```

## ⚠️ Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
cd frontend && npm install
```

### Port already in use
```bash
# Kill process on port 8000 or 5173
# Windows: taskkill /F /PID <pid>
# Linux/Mac: kill -9 <pid>
```

### Dashboard shows "Disconnected"
1. Check backend is running (port 8000)
2. Refresh browser page
3. Check browser console for errors

### No updates appearing
1. Click "Simulate Attack" button
2. Check backend console for errors
3. Verify SSE connection in Network tab (F12)

## 🎓 Next Steps

After the quick demo:
1. Read [REALTIME_SETUP.md](REALTIME_SETUP.md) for detailed documentation
2. Explore API endpoints at `http://localhost:8000/api/`
3. Customize the dashboard components
4. Integrate with real security scanners

## 🛑 Stopping the System

Press `Ctrl+C` in the terminal running `start_realtime_demo.py`

Or manually stop each service:
- Backend: `Ctrl+C` in backend terminal
- Frontend: `Ctrl+C` in frontend terminal

## 📚 Documentation

- **Full Setup Guide**: [REALTIME_SETUP.md](REALTIME_SETUP.md)
- **API Documentation**: Check `/api/health` endpoint
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)

## 💡 Tips

- **Event Log**: Toggle it on to see all SSE messages in real-time
- **Multiple Tabs**: Open multiple dashboard tabs to see synchronized updates
- **API Testing**: Use `curl` or Postman to test endpoints
- **Browser DevTools**: F12 → Console/Network to debug SSE connection

---

**Ready to see real-time security monitoring in action? Run the demo now!** 🚀