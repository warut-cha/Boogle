# Production Integration Architecture

## Executive Summary

This document outlines the complete integration architecture for the AI-Powered Security Analyst System (Jeff), connecting the frontend dashboard with backend services for production deployment.

## Current State Analysis

### ✅ What's Working
- **Backend Pipeline**: Rust scanner → Python analysis → Bob AI → Report generation
- **Frontend Dashboard**: React/TypeScript SOC-style UI with mock data
- **API Server**: Basic FastAPI with WebSocket support for real-time updates
- **Data Contracts**: JSON schemas defined in `/contracts`

### ❌ Integration Gaps Identified

1. **Incomplete API Coverage**: Missing endpoints for full CRUD operations
2. **Inconsistent Error Handling**: Frontend fallbacks to localStorage without proper retry logic
3. **No State Synchronization**: Frontend and backend can become out of sync
4. **Limited Real-time Features**: WebSocket only broadcasts, no bidirectional communication
5. **No Persistence Layer**: All data stored in memory (lost on restart)
6. **Missing Health Monitoring**: No system health checks or metrics
7. **Incomplete Data Normalization**: Some fields mismatch between layers

## Proposed Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Dashboard   │  │  Real-time   │  │    State     │          │
│  │  Components  │  │  WebSocket   │  │  Management  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                   │
│         └──────────────────┼──────────────────┘                   │
│                            │                                      │
│                    ┌───────▼────────┐                            │
│                    │  API Client    │                            │
│                    │  (axios + WS)  │                            │
│                    └───────┬────────┘                            │
└────────────────────────────┼─────────────────────────────────────┘
                             │ HTTP/WS
┌────────────────────────────▼─────────────────────────────────────┐
│                         API LAYER                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              FastAPI Server (api_server.py)               │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │   │
│  │  │   REST     │  │ WebSocket  │  │   Health   │         │   │
│  │  │ Endpoints  │  │  Manager   │  │   Checks   │         │   │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘         │   │
│  └────────┼───────────────┼───────────────┼────────────────┘   │
└───────────┼───────────────┼───────────────┼────────────────────┘
            │               │               │
┌───────────▼───────────────▼───────────────▼────────────────────┐
│                      BUSINESS LOGIC LAYER                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Analysis   │  │  Correlation │  │  Real-time   │         │
│  │   Pipeline   │  │   Engine     │  │   Detector   │         │
│  │  (main.py)   │  │              │  │              │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼─────────────────┐
│                       DATA LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   In-Memory  │  │   SQLite     │  │    Vector    │         │
│  │    Stores    │  │  (Runtime)   │  │    Memory    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow Architecture

### 1. Initial Scan Flow
```
User → Frontend → POST /api/scan
                    ↓
              API Server validates request
                    ↓
              Triggers Analysis Pipeline
                    ↓
         Rust Scanner → Findings
                    ↓
         Python Correlator → Incidents
                    ↓
         Bob AI → Analysis + Fixes
                    ↓
         Store in memory + Broadcast via WS
                    ↓
         Frontend receives update → UI refresh
```

### 2. Real-time Detection Flow
```
Mock DB Events → Real-time Detector (polling)
                    ↓
              Correlate events → Findings
                    ↓
              Pattern matching → Incidents
                    ↓
              Broadcast via WebSocket
                    ↓
              Frontend receives → Live update
```

### 3. Data Retrieval Flow
```
Frontend → GET /api/incidents
              ↓
         API Server → In-memory store
              ↓
         Return JSON (with fallback to localStorage)
```

## API Endpoints Specification

### Core Endpoints

#### Health & Status
- `GET /api/health` - System health check
- `GET /api/realtime/status` - Real-time detector status

#### Findings
- `GET /api/findings` - List all findings
- `GET /api/findings/{id}` - Get specific finding
- `POST /api/findings` - Create finding (internal)

#### Incidents
- `GET /api/incidents` - List all incidents
- `GET /api/incidents/{id}` - Get specific incident
- `GET /api/incidents/{id}/bob-analysis` - Get Bob analysis
- `POST /api/incidents/{id}/analyze-with-bob` - Trigger Bob analysis

#### Scanning
- `POST /api/scan` - Trigger new security scan
  ```json
  {
    "paths": ["./mock-repos"],
    "use_mock": false,
    "use_bob": true
  }
  ```

#### Real-time
- `POST /api/realtime/start` - Start real-time detection
- `POST /api/realtime/stop` - Stop real-time detection
- `GET /api/updates?since={timestamp}` - Poll for updates

#### Data Management
- `DELETE /api/reset` - Clear all data
- `POST /api/mock-db/init` - Initialize mock database

#### WebSocket
- `WS /ws` - Real-time bidirectional communication
  - Events: `new_finding`, `new_incident`, `scan_completed`, `bob_analysis`

## Frontend Integration Strategy

### 1. API Client Enhancement

**Current Issues:**
- Fallback to localStorage on every error
- No retry logic
- No request queuing
- No optimistic updates

**Proposed Solution:**
```typescript
// Enhanced API client with:
- Automatic retry with exponential backoff
- Request deduplication
- Optimistic updates
- Proper error boundaries
- Connection state management
```

### 2. State Management

**Current Issues:**
- Local state in components
- No global state management
- Data duplication

**Proposed Solution:**
```typescript
// Use React Context + useReducer for:
- Global findings/incidents state
- WebSocket connection state
- Loading/error states
- Cache management
```

### 3. Real-time Integration

**Current Issues:**
- WebSocket connection not properly managed
- No reconnection logic
- No message queuing

**Proposed Solution:**
```typescript
// Enhanced WebSocket hook:
- Auto-reconnect with backoff
- Message queue for offline mode
- Connection health monitoring
- Heartbeat/ping-pong
```

## Backend Enhancements

### 1. API Server Improvements

**Add:**
- Request validation with Pydantic models
- Proper error responses with status codes
- Rate limiting
- CORS configuration per environment
- Request logging and metrics

### 2. Data Persistence

**Current:** In-memory only (data lost on restart)

**Proposed:**
```python
# Add optional SQLite persistence:
- Store findings/incidents to DB
- Load on startup
- Keep in-memory cache for performance
- Periodic sync to disk
```

### 3. Analysis Pipeline Integration

**Current:** Separate CLI tool

**Proposed:**
```python
# Make analysis pipeline async:
- Background task execution
- Progress tracking
- Cancellation support
- Result streaming
```

## Data Contract Standardization

### Field Naming Convention
- **Use snake_case** for all JSON fields (Python/backend standard)
- Frontend TypeScript types mirror backend exactly
- No camelCase conversion needed

### Required Fields Validation
```typescript
// All entities must have:
- id field (finding_id, incident_id)
- timestamp (ISO 8601 UTC)
- source/origin tracking
```

### Normalization Layer
```typescript
// Frontend normalizers handle:
- Missing optional fields → defaults
- Old format → new format
- Type coercion
- Validation
```

## Error Handling Strategy

### Backend Error Responses
```json
{
  "error": {
    "code": "SCAN_FAILED",
    "message": "Rust scanner execution failed",
    "details": "...",
    "timestamp": "2026-05-17T09:00:00Z"
  }
}
```

### Frontend Error Handling
```typescript
// Three-tier fallback:
1. Try API request
2. On failure, use cached data (localStorage)
3. On no cache, show error UI with retry
```

## Real-time Communication Protocol

### WebSocket Message Format
```json
{
  "type": "new_finding" | "new_incident" | "scan_completed" | "bob_analysis" | "reset",
  "timestamp": "2026-05-17T09:00:00Z",
  "data": { ... }
}
```

### Client-side Handling
```typescript
// Message types:
- new_finding → Add to findings list
- new_incident → Add to incidents list
- scan_completed → Refresh all data
- bob_analysis → Update incident with analysis
- reset → Clear all local data
```

## Performance Optimization

### Backend
- In-memory caching for frequent queries
- Lazy loading of Bob analysis
- Pagination for large result sets
- Background task queue for heavy operations

### Frontend
- Virtual scrolling for large tables
- Lazy loading of incident details
- Debounced search/filter
- Memoized components
- Code splitting

## Security Considerations

### API Security
- CORS whitelist for allowed origins
- WebSocket origin validation
- Input sanitization
- Rate limiting per endpoint

### Data Security
- No sensitive data in localStorage
- Masked secrets in UI
- Secure WebSocket (WSS in production)

## Deployment Architecture

### Development
```
Frontend: http://localhost:5173 (Vite dev server)
Backend: http://localhost:8000 (Uvicorn)
WebSocket: ws://localhost:8000/ws
```

### Production
```
Frontend: https://jeff.example.com (Static hosting)
Backend: https://api.jeff.example.com (Containerized)
WebSocket: wss://api.jeff.example.com/ws
Database: SQLite → PostgreSQL
```

## Testing Strategy

### Integration Tests
```python
# Test full flow:
1. POST /api/scan → Verify findings created
2. GET /api/incidents → Verify incidents returned
3. WebSocket → Verify real-time updates
4. POST /api/incidents/{id}/analyze-with-bob → Verify analysis
```

### Frontend Tests
```typescript
// Test components with:
- Mock API responses
- Mock WebSocket messages
- Error scenarios
- Loading states
```

## Migration Path

### Phase 1: Stabilize Current Integration ✅
- Fix API endpoint inconsistencies
- Add proper error handling
- Improve WebSocket reliability

### Phase 2: Add Persistence
- SQLite for development
- PostgreSQL for production
- Migration scripts

### Phase 3: Production Hardening
- Add authentication
- Add monitoring/logging
- Add rate limiting
- Add health checks

### Phase 4: Scale
- Add job queue (Celery/Redis)
- Add caching layer (Redis)
- Horizontal scaling support

## Monitoring & Observability

### Metrics to Track
- API response times
- WebSocket connection count
- Scan completion rate
- Error rates by endpoint
- Memory usage
- Active incidents count

### Logging
```python
# Structured logging:
- Request/response logs
- Error logs with stack traces
- Audit logs for data changes
- Performance logs
```

## Configuration Management

### Environment Variables
```bash
# Backend
JEFF_API_HOST=0.0.0.0
JEFF_API_PORT=8000
JEFF_DB_PATH=./data/jeff.db
JEFF_LOG_LEVEL=INFO
BOB_API_KEY=xxx

# Frontend
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_ENABLE_MOCK=false
```

## Success Criteria

### Integration Complete When:
- ✅ Frontend can trigger scans via API
- ✅ Real-time updates work reliably
- ✅ All data flows end-to-end
- ✅ Error handling is robust
- ✅ No data loss on refresh
- ✅ WebSocket reconnects automatically
- ✅ All tests pass
- ✅ Documentation is complete

## Next Steps

1. **Immediate**: Fix critical integration issues
2. **Short-term**: Add persistence and improve reliability
3. **Medium-term**: Production hardening
4. **Long-term**: Scale and optimize

---

*Document Version: 1.0*
*Last Updated: 2026-05-17*
*Status: Implementation Ready*