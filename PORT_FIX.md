# Port Issue Fix

## Problem

Frontend is running on port **3001** instead of the expected port **5173**.

## Why This Happens

Vite (the frontend build tool) automatically finds an available port if the default port is in use. Port 5173 might be occupied by another process.

---

## Solutions

### Solution 1: Access Frontend on Port 3001 (Quick Fix)

Since your frontend is running on port 3001, simply access it there:

**Open in browser:**
```
http://localhost:3001
```

The backend API is correctly running on port 8000, so everything should work fine.

---

### Solution 2: Free Up Port 5173

If you want to use port 5173 specifically:

**On macOS/Linux:**
```bash
# Find process using port 5173
lsof -ti:5173

# Kill the process
lsof -ti:5173 | xargs kill -9

# Restart frontend
cd frontend
npm run dev
```

**On Windows:**
```cmd
# Find process using port 5173
netstat -ano | findstr :5173

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Restart frontend
cd frontend
npm run dev
```

---

### Solution 3: Configure Specific Port

Force Vite to use a specific port:

**Edit `frontend/vite.config.ts`:**
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,  // Fail if port is not available
    host: true
  }
})
```

Then restart:
```bash
cd frontend
npm run dev
```

---

### Solution 4: Update Documentation to Use Port 3001

If port 3001 works fine for you, update the frontend .env:

**Edit `frontend/.env`:**
```env
VITE_API_BASE_URL=http://localhost:8000
# Note: Frontend will run on whatever port Vite assigns (3001 in your case)
```

---

## Current Status

Based on your logs:
- ✅ **Backend API:** Running on port 8000 (correct)
- ✅ **Frontend:** Running on port 3001 (working, just different port)
- ✅ **API Calls:** Working correctly (200 responses)
- ✅ **Integration:** Fully functional

**Action Required:**
Just open **http://localhost:3001** instead of http://localhost:5173

---

## Verify Everything Works

1. **Open frontend:**
   ```
   http://localhost:3001
   ```

2. **Check API health:**
   ```bash
   curl http://localhost:8000/api/health
   ```

3. **Check browser console (F12):**
   - Should see successful API calls
   - No CORS errors
   - Data loading correctly

---

## Update Start Script (Optional)

If you want the script to show the correct port, edit `start_services.sh`:

```bash
# After starting frontend, detect actual port
echo ""
echo "✨ Bob Sentinel is running!"
echo ""
echo "📊 Dashboard: Check terminal output above for actual port (usually 3001 or 5173)"
echo "🔌 API: http://localhost:8000"
```

---

## Summary

**Your system is working correctly!** The only difference is the port number.

- Frontend: http://localhost:3001 ✅
- Backend: http://localhost:8000 ✅
- Integration: Working ✅

Just use port 3001 to access the dashboard.

---

**Made with ❤️ by Bob**