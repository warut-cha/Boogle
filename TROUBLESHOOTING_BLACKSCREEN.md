# 🔧 Troubleshooting: Dashboard Blackscreen Issue

## Problem Description

The dashboard shows a blackscreen after a few seconds during simulation runs, despite showing initial real-time updates.

## Root Causes Identified

### 1. **React State Update on Unmounted Component**
- Event handlers continue to fire after component unmounts
- Causes React warnings and potential crashes

### 2. **Missing Null Checks**
- Event data might be undefined or null
- Accessing properties on undefined causes crashes

### 3. **Circular Dependencies in useEffect**
- Missing dependencies or incorrect dependency arrays
- Causes infinite re-renders

### 4. **Unhandled Errors in Event Handlers**
- Errors in SSE event processing crash the entire component
- No error boundaries to catch and recover

## ✅ Fixes Applied

### Fix 1: Added Mounted Flag
```typescript
useEffect(() => {
  let mounted = true;

  const handleRealtimeEvent = (event: SSEEvent) => {
    if (!mounted) return; // Prevent updates after unmount
    // ... rest of handler
  };

  return () => {
    mounted = false; // Set flag on cleanup
    unsubscribe();
    realtimeClient.disconnect();
  };
}, []); // Empty dependency array
```

### Fix 2: Added Null Checks
```typescript
case 'finding_added':
  if (event.data) { // Check data exists
    setFindings(prev => [...prev, event.data]);
  }
  break;
```

### Fix 3: Wrapped in Try-Catch
```typescript
const handleRealtimeEvent = (event: SSEEvent) => {
  try {
    // ... event handling logic
  } catch (error) {
    console.error('Error handling real-time event:', error, event);
    // Don't crash, just log
  }
};
```

### Fix 4: Better Error Handling in Client
```typescript
private handleEvent(event: SSEEvent): void {
  try {
    specificListeners.forEach(callback => {
      try {
        callback(event);
      } catch (error) {
        console.error(`Error in listener:`, error);
        // Continue with other listeners
      }
    });
  } catch (error) {
    console.error('Error handling event:', error);
  }
}
```

## 🧪 Testing the Fix

### Step 1: Restart Frontend
```bash
# Stop frontend (Ctrl+C)
cd frontend
npm run dev
```

### Step 2: Clear Browser Cache
```
1. Open DevTools (F12)
2. Right-click refresh button
3. Select "Empty Cache and Hard Reload"
```

### Step 3: Test Simulation
```
1. Open dashboard at http://localhost:5173
2. Open browser console (F12)
3. Click "Simulate Attack"
4. Watch for errors in console
5. Verify dashboard stays responsive
```

### Step 4: Check Console Output

**Good Output:**
```
🔌 Connecting to real-time updates...
✅ Connected to real-time updates
📡 Real-time event: {type: 'finding_added', ...}
📡 Real-time event: {type: 'incident_added', ...}
```

**Bad Output (Fixed):**
```
❌ Error: Cannot read property 'incident_id' of undefined
❌ Warning: Can't perform a React state update on unmounted component
```

## 🔍 Additional Debugging Steps

### 1. Check Backend Logs
```bash
# Backend terminal should show:
127.0.0.1 - - [16/May/2026 16:40:30] "GET /api/events HTTP/1.1" 200 -
127.0.0.1 - - [16/May/2026 16:40:30] "GET /api/findings HTTP/1.1" 200 -
```

### 2. Monitor Network Tab
```
1. Open DevTools → Network tab
2. Filter by "events"
3. Should see persistent connection to /api/events
4. Status should be "200" and "pending" (streaming)
```

### 3. Check Memory Usage
```
1. Open DevTools → Performance tab
2. Record during simulation
3. Check for memory leaks
4. Should see stable memory usage
```

### 4. Test Multiple Tabs
```
1. Open dashboard in 2-3 tabs
2. Trigger simulation in one tab
3. All tabs should update without crashing
```

## 🚨 If Blackscreen Still Occurs

### Emergency Fallback: Use Mock Data Mode

Edit `frontend/src/api/client.ts`:
```typescript
const USE_MOCK_DATA = true; // Change to true
```

This disables SSE and uses static mock data.

### Check for Other Issues

1. **Browser Compatibility**
   - Test in Chrome/Edge (best support)
   - Firefox and Safari may have SSE quirks

2. **Port Conflicts**
   ```bash
   # Check if ports are in use
   netstat -ano | findstr :8000
   netstat -ano | findstr :5173
   ```

3. **CORS Issues**
   - Check browser console for CORS errors
   - Backend should show CORS headers in response

4. **Memory Limits**
   - Close other tabs/applications
   - Restart browser
   - Clear browser cache

## 📊 Performance Monitoring

### Add Performance Logging

Add to `RealtimeDashboardPage.tsx`:
```typescript
useEffect(() => {
  console.log('Component mounted');
  console.log('Findings:', findings.length);
  console.log('Incidents:', incidents.length);
  
  return () => {
    console.log('Component unmounting');
  };
}, [findings, incidents]);
```

### Monitor Event Rate

Add to event handler:
```typescript
let eventCount = 0;
const handleRealtimeEvent = (event: SSEEvent) => {
  eventCount++;
  console.log(`Event #${eventCount}:`, event.type);
  // ... rest of handler
};
```

## 🛠️ Advanced Fixes

### Add Error Boundary

Create `frontend/src/components/ErrorBoundary.tsx`:
```typescript
import React from 'react';

class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('Error boundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '2rem', color: '#f85149' }}>
          <h1>Something went wrong</h1>
          <p>{this.state.error?.message}</p>
          <button onClick={() => window.location.reload()}>
            Reload Dashboard
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

Wrap app in `App.tsx`:
```typescript
import ErrorBoundary from './components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      {/* existing app content */}
    </ErrorBoundary>
  );
}
```

### Add Connection Health Check

Add to `RealtimeDashboardPage.tsx`:
```typescript
useEffect(() => {
  const healthCheck = setInterval(async () => {
    try {
      await realtimeClient.healthCheck();
      console.log('✅ Backend healthy');
    } catch (error) {
      console.error('❌ Backend unhealthy:', error);
      setConnected(false);
    }
  }, 30000); // Every 30 seconds

  return () => clearInterval(healthCheck);
}, []);
```

## 📝 Verification Checklist

After applying fixes, verify:

- [ ] Dashboard loads without errors
- [ ] Connection status shows "Live Updates Active"
- [ ] Simulate Attack button works
- [ ] Findings appear one by one
- [ ] Incident gets created
- [ ] Dashboard stays responsive throughout
- [ ] No errors in browser console
- [ ] No warnings about unmounted components
- [ ] Multiple tabs work simultaneously
- [ ] Event log shows all events
- [ ] Clear Data button works
- [ ] Can run simulation multiple times

## 🎯 Expected Behavior

After fixes:
1. Dashboard loads cleanly
2. Shows "Live Updates Active" in green
3. Simulation runs smoothly for 8-10 seconds
4. All findings and incidents appear
5. Dashboard remains interactive
6. No blackscreen or crashes
7. Can repeat simulation multiple times

## 📞 Still Having Issues?

1. Check all files were saved and frontend restarted
2. Clear browser cache completely
3. Try incognito/private browsing mode
4. Test in different browser
5. Check backend is running without errors
6. Review backend logs for exceptions
7. Test with mock data mode as fallback

---

**Status**: Fixes applied to prevent blackscreen issue. Restart frontend to apply changes.