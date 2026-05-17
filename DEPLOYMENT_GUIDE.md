# Deployment and Testing Guide

## Overview

This guide provides step-by-step instructions for deploying and testing the fully integrated AI-Powered Security Analyst System (Jeff).

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Backend Deployment](#backend-deployment)
4. [Frontend Deployment](#frontend-deployment)
5. [Testing](#testing)
6. [Production Deployment](#production-deployment)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Python 3.9+** with pip
- **Node.js 18+** with npm
- **Rust 1.70+** with Cargo
- **Git**

### Optional (for production)

- **Docker** and Docker Compose
- **PostgreSQL** (for persistent storage)
- **Redis** (for caching and job queue)
- **Nginx** (for reverse proxy)

---

## Environment Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd IBM-BOB
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install additional dependencies for API server
pip install fastapi uvicorn[standard] websockets pydantic
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env
```

### 4. Rust Scanner Setup

```bash
cd rust-scanner

# Build release version
cargo build --release

# Verify build
cargo test
```

---

## Backend Deployment

### Development Mode

#### Option 1: Run API Server Only

```bash
# From project root
python -m uvicorn src.api_server:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

#### Option 2: Run Full Analysis Pipeline

```bash
# Run analysis with mock data
python src/main.py analyze --path ./mock-repos --use-mock --use-bob

# Run analysis with real Rust scanner
python src/main.py analyze --path ./mock-repos --use-bob

# Run analysis on your own repositories
python src/main.py analyze --path /path/to/your/repos --use-bob
```

### Production Mode

#### Using Gunicorn (Recommended)

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn src.api_server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

#### Using Docker

```bash
# Build Docker image
docker build -t jeff-backend -f Dockerfile.backend .

# Run container
docker run -d \
  --name jeff-backend \
  -p 8000:8000 \
  -e JEFF_API_HOST=0.0.0.0 \
  -e JEFF_API_PORT=8000 \
  jeff-backend
```

---

## Frontend Deployment

### Development Mode

```bash
cd frontend

# Start development server
npm run dev
```

The frontend will be available at: `http://localhost:5173`

### Production Build

```bash
cd frontend

# Build for production
npm run build

# Preview production build
npm run preview
```

### Deploy to Static Hosting

#### Option 1: Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
cd frontend
npm run build
netlify deploy --prod --dir=dist
```

#### Option 2: Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel --prod
```

#### Option 3: Nginx

```bash
# Build frontend
cd frontend
npm run build

# Copy to nginx directory
sudo cp -r dist/* /var/www/jeff-frontend/

# Configure nginx (see nginx.conf example below)
```

---

## Testing

### Backend Tests

#### Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/integration/test_api_integration.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

#### Integration Tests

```bash
# Test full analysis pipeline
python test_pipeline.py

# Test API endpoints
pytest tests/integration/test_api_integration.py -v

# Test real-time detection
python scripts/test_realtime.py
```

#### Manual API Testing

```bash
# Health check
curl http://localhost:8000/api/health

# Get findings
curl http://localhost:8000/api/findings

# Get incidents
curl http://localhost:8000/api/incidents

# Trigger scan
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"paths": ["./mock-repos"], "use_mock": true, "use_bob": true}'

# Get metrics
curl http://localhost:8000/api/metrics
```

### Frontend Tests

#### Unit Tests

```bash
cd frontend

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch
```

#### E2E Tests

```bash
cd frontend

# Run Playwright tests
npm run test:e2e

# Run in UI mode
npm run test:e2e:ui

# Generate test report
npm run test:e2e:report
```

### Integration Testing

#### Full Stack Test

```bash
# Terminal 1: Start backend
python -m uvicorn src.api_server:app --reload

# Terminal 2: Start frontend
cd frontend && npm run dev

# Terminal 3: Run integration tests
python scripts/integration_check.py
```

#### WebSocket Testing

```bash
# Start backend
python -m uvicorn src.api_server:app --reload

# In another terminal, test WebSocket
python scripts/test_realtime.py
```

---

## Production Deployment

### Architecture

```
┌─────────────┐
│   Nginx     │ ──> Reverse Proxy & SSL
└──────┬──────┘
       │
       ├──> Frontend (Static Files)
       │
       └──> Backend API (Gunicorn + Uvicorn)
              │
              ├──> PostgreSQL (Data)
              ├──> Redis (Cache)
              └──> Rust Scanner
```

### Docker Compose Deployment

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - JEFF_API_HOST=0.0.0.0
      - JEFF_API_PORT=8000
      - JEFF_DB_PATH=/data/jeff.db
      - BOB_API_KEY=${BOB_API_KEY}
    volumes:
      - ./data:/data
      - ./mock-repos:/app/mock-repos
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    environment:
      - VITE_API_BASE_URL=http://backend:8000
      - VITE_WS_URL=ws://backend:8000/ws
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
```

Deploy:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Variables

#### Backend (.env)

```bash
# API Configuration
JEFF_API_HOST=0.0.0.0
JEFF_API_PORT=8000
JEFF_LOG_LEVEL=INFO

# Database
JEFF_DB_PATH=./data/jeff.db

# Bob AI
BOB_API_KEY=your_api_key_here
BOB_API_URL=https://api.watsonx.ai

# Real-time Detection
JEFF_REALTIME_ENABLED=true
JEFF_REALTIME_POLL_INTERVAL=1.0

# CORS
JEFF_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

#### Frontend (.env)

```bash
# API Configuration
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_WS_URL=wss://api.yourdomain.com/ws

# Feature Flags
VITE_ENABLE_MOCK=false
VITE_ENABLE_REALTIME=true
```

### Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Frontend
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket
        location /ws {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

---

## Monitoring and Logging

### Backend Logging

Logs are written to stdout/stderr. Configure log aggregation:

```bash
# View logs
docker-compose logs -f backend

# Save logs to file
docker-compose logs backend > backend.log
```

### Health Checks

```bash
# Check backend health
curl https://api.yourdomain.com/api/health

# Check metrics
curl https://api.yourdomain.com/api/metrics

# Check real-time detector
curl https://api.yourdomain.com/api/realtime/status
```

### Monitoring Tools

- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **Sentry**: Error tracking
- **DataDog**: Full-stack monitoring

---

## Troubleshooting

### Backend Issues

#### API Server Won't Start

```bash
# Check if port is in use
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Kill process on port
# Windows:
scripts/kill_port_8000.ps1
# Linux/Mac:
kill -9 $(lsof -t -i:8000)
```

#### Database Errors

```bash
# Reset database
python -c "from runtime_lab.mock_database import init_db; init_db(reset=True)"

# Check database file
ls -la runtime_lab/mock_events.db
```

#### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

### Frontend Issues

#### Build Failures

```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf .vite
```

#### API Connection Issues

```bash
# Check API URL in browser console
# Verify CORS headers
curl -I http://localhost:8000/api/health

# Test WebSocket connection
# Open browser console and run:
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onopen = () => console.log('Connected');
ws.onerror = (e) => console.error('Error:', e);
```

### Integration Issues

#### WebSocket Not Connecting

1. Check backend is running
2. Verify WebSocket URL in frontend
3. Check browser console for errors
4. Verify CORS configuration

#### Data Not Syncing

1. Check API endpoints are responding
2. Verify data normalization
3. Check browser localStorage
4. Clear cache and refresh

---

## Performance Optimization

### Backend

```bash
# Use multiple workers
gunicorn src.api_server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker

# Enable caching
# Add Redis for caching frequent queries
```

### Frontend

```bash
# Enable production optimizations
npm run build

# Analyze bundle size
npm run build -- --analyze

# Enable compression in nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

---

## Security Checklist

- [ ] Change default API keys
- [ ] Enable HTTPS/WSS in production
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable authentication
- [ ] Sanitize user inputs
- [ ] Keep dependencies updated
- [ ] Use environment variables for secrets
- [ ] Enable security headers
- [ ] Set up monitoring and alerts

---

## Support

For issues and questions:

1. Check this guide
2. Review logs
3. Check GitHub issues
4. Contact support team

---

*Last Updated: 2026-05-17*
*Version: 1.0.0*