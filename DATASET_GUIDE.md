# Bob Sentinel - Dataset Management Guide

## 🎯 Overview

This guide explains how to switch between different datasets and scan different repositories with Bob Sentinel.

---

## 📊 Current Dataset (Mock Data)

By default, the system uses mock data from the `mock-repos/` directory for demonstration purposes.

**Current Mock Repositories:**
```
mock-repos/
├── frontend-app/          # Frontend application with API issues
├── infra-config/          # Infrastructure configuration files
└── legacy-backend/        # Legacy backend with security issues
```

---

## 🔄 How to Switch Datasets

### Option 1: Scan Different Mock Repositories

The system includes additional mock data in `mock_data/repos/`:

```bash
# Via API
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "paths": ["./mock_data/repos/ecommerce_app"],
    "use_mock": false,
    "use_bob": true
  }'
```

### Option 2: Scan Real Repositories

To scan your own repositories:

**1. Via API:**
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "paths": ["/path/to/your/repo"],
    "use_mock": false,
    "use_bob": true
  }'
```

**2. Via CLI:**
```bash
# Activate virtual environment
source venv/bin/activate

# Scan a specific repository
python src/main.py analyze --path /path/to/your/repo --use-bob

# Scan multiple repositories
python src/main.py analyze --path /path/to/repo1 --path /path/to/repo2 --use-bob
```

**3. Via Frontend:**
Currently, the frontend loads data automatically. To scan new repos:
1. Use the API or CLI to run a new scan
2. Refresh the dashboard to see new results

### Option 3: Create Custom Mock Data

Create your own mock repository structure:

```bash
# Create new mock repo
mkdir -p custom-repos/my-app/src

# Add files with security issues (for testing)
cat > custom-repos/my-app/src/config.py << 'EOF'
# Example: Hardcoded credentials
API_KEY = "sk_live_1234567890abcdef"
DATABASE_URL = "postgresql://admin:password123@localhost/mydb"
EOF

# Scan it
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "paths": ["./custom-repos/my-app"],
    "use_mock": false,
    "use_bob": true
  }'
```

---

## 🔧 Backend Configuration for Datasets

### Modify API Server to Use Different Default Data

Edit `src/api_server.py`:

```python
# Line ~100: Change default scan path
if not FINDINGS_CACHE:
    # Change this path to your desired default
    mock_repos_path = Path(__file__).parent.parent / "your-custom-path"
    findings = rust_scanner.scan([str(mock_repos_path)], use_mock=False)
    FINDINGS_CACHE.extend(findings)
```

### Configure Scan Paths in config.yaml

Edit `config/config.yaml`:

```yaml
# Add custom scan paths
analysis:
  default_scan_paths:
    - "./mock-repos"
    - "./custom-repos"
    - "/path/to/production/repos"
  
  static_analysis:
    enabled: true
    scan_patterns:
      - "*.py"
      - "*.js"
      - "*.ts"
      - "*.java"
      - "*.go"
```

---

## 📁 Dataset Structure

### Expected Repository Structure

Bob Sentinel can scan any repository structure, but works best with:

```
your-repo/
├── src/                    # Source code
│   ├── *.py               # Python files
│   ├── *.js               # JavaScript files
│   └── config/            # Configuration files
├── logs/                   # Application logs
│   └── *.log
├── .env                    # Environment variables
├── docker-compose.yml      # Infrastructure configs
└── README.md
```

### What Gets Scanned

**Code Files:**
- Python (`.py`)
- JavaScript/TypeScript (`.js`, `.ts`)
- Java (`.java`)
- Go (`.go`)
- Ruby (`.rb`)
- PHP (`.php`)

**Configuration Files:**
- `.env`, `.env.example`
- `config.yaml`, `config.json`
- `docker-compose.yml`
- `Dockerfile`
- `.yml`, `.yaml` files

**Log Files:**
- `*.log`
- Application logs with timestamps

---

## 🎨 Frontend Dataset Display

### Current Behavior

The frontend automatically displays data from the backend API:

1. On page load, it calls:
   - `GET /api/findings` - Gets all findings
   - `GET /api/incidents` - Gets all incidents
   - `POST /api/incidents/:id/analyze-with-bob` - Gets Bob analysis

2. Data is cached in the backend until server restart

### Refresh Data in Frontend

**Option 1: Automatic Refresh**
The frontend will automatically fetch new data when you:
- Refresh the page (F5)
- Navigate between tabs

**Option 2: Manual API Call**
Run a new scan via API, then refresh the dashboard:
```bash
# Run new scan
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"paths": ["./new-repo"], "use_mock": false}'

# Refresh browser to see new data
```

---

## 🔍 Example: Scanning Different Datasets

### Example 1: Scan E-commerce App
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "paths": ["./mock_data/repos/ecommerce_app"],
    "use_mock": false,
    "use_bob": true
  }'
```

### Example 2: Scan Multiple Repos
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "paths": [
      "./mock-repos/frontend-app",
      "./mock-repos/legacy-backend",
      "./mock-repos/infra-config"
    ],
    "use_mock": false,
    "use_bob": true
  }'
```

### Example 3: Scan Production Code
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "paths": ["/home/user/projects/my-production-app"],
    "use_mock": false,
    "use_bob": true
  }'
```

---

## 💾 Persistent Storage (Future Enhancement)

Currently, data is stored in-memory and lost on server restart.

**To add persistent storage:**

1. **Enable MongoDB** in `config/config.yaml`:
```yaml
database:
  type: mongodb
  mongodb:
    host: localhost
    port: 27017
    database: bob_sentinel
```

2. **Modify API Server** to use database:
```python
# In src/api_server.py
# Replace in-memory caches with database queries
findings = db_manager.get_findings()
incidents = db_manager.get_incidents()
```

---

## 🧪 Testing with Different Datasets

### Create Test Dataset

```bash
# Create test repository
mkdir -p test-repos/vulnerable-app/src

# Add vulnerable code
cat > test-repos/vulnerable-app/src/app.py << 'EOF'
import os

# Hardcoded secret (will be detected)
API_KEY = "sk_test_EXAMPLE_FAKE_KEY_FOR_TESTING"

# SQL injection vulnerability (will be detected)
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)

# Deprecated API (will be detected)
@app.route('/api/v1/users')
def old_api():
    return "This endpoint is deprecated"
EOF

# Scan it
python src/main.py analyze --path ./test-repos/vulnerable-app --use-bob
```

---

## 📊 Dataset Statistics

View statistics about current dataset:

```bash
# Via API
curl http://localhost:8000/api/stats

# Response:
{
  "findings_count": 15,
  "incidents_count": 3,
  "bob_analysis_count": 3,
  "memory_entries": 5,
  "last_analysis": "2026-05-16T14:00:00Z"
}
```

---

## 🔄 Reset Dataset

To clear current data and start fresh:

**Option 1: Restart Server**
```bash
# Stop server (Ctrl+C)
# Start again
python src/api_server.py
```

**Option 2: Clear Cache via API** (if implemented)
```bash
curl -X DELETE http://localhost:8000/api/cache
```

---

## 📝 Summary

**Current Setup:**
- ✅ Uses mock data from `mock-repos/` by default
- ✅ Can scan any repository via API or CLI
- ✅ Data cached in-memory (lost on restart)
- ✅ Frontend displays whatever backend provides

**To Switch Datasets:**
1. Use `POST /api/analyze` with different paths
2. Or use CLI: `python src/main.py analyze --path /your/path`
3. Refresh frontend to see new data

**For Production:**
- Enable MongoDB for persistent storage
- Configure default scan paths in config.yaml
- Add scheduled scans for continuous monitoring

---

**Made with ❤️ by Bob**