# 🎬 Extended Demo Guide - 60 Second Security Simulation

## Overview

The Bob Sentinel dashboard now includes an extended 60-second demo that simulates a realistic, multi-phase security incident with 14 findings and 4 correlated incidents.

## 🚀 Running the Extended Demo

### Quick Start
```bash
# Ensure backend and frontend are running
# Backend: python src/api_server.py
# Frontend: cd frontend && npm run dev

# Open dashboard at http://localhost:5173
# Click "Simulate Attack" button
```

## 📊 Demo Timeline (60 seconds)

### Phase 1: Reconnaissance (0-10s)
**T+0s** - Port scanning detected
- Finding: Exposed PostgreSQL port 5432
- Severity: Low
- Evidence: No firewall rules configured

**T+2s** - Suspicious traffic pattern
- Finding: Unusual traffic from single IP
- Severity: Medium
- Evidence: 150 requests in 30 seconds

**T+4s** - AWS credentials exposed
- Finding: Hardcoded AWS Access Key
- Severity: Critical
- Evidence: Found in frontend code

**T+6s** - SQL injection attempt
- Finding: Malicious query pattern
- Severity: High
- Evidence: ' OR '1'='1 detected

**T+8s** - **INCIDENT #1**: Database exposure
- Title: "Database port exposed without authentication"
- Severity: Medium
- Confidence: 75%

### Phase 2: Credential Discovery (10-25s)
**T+12s** - Deprecated API found
- Finding: Old export endpoint still accessible
- Severity: Medium
- Evidence: Marked for removal 6 months ago

**T+15s** - API key in logs
- Finding: Sensitive data in application logs
- Severity: High
- Evidence: API key logged in plaintext

**T+18s** - Database anomaly
- Finding: Abnormal read spike
- Severity: High
- Evidence: 50,000 rows accessed in 2 minutes

**T+22s** - SSH private key exposed
- Finding: RSA private key in repository
- Severity: Critical
- Evidence: Committed to .github/deploy_key

**T+25s** - **INCIDENT #2**: Multiple credentials exposed
- Title: "Critical: Multiple credentials exposed in codebase"
- Severity: Critical
- Confidence: 95%
- Attack Path: AWS → API Key → SSH Key → Potential Breach

### Phase 3: Active Exploitation (25-42s)
**T+30s** - Brute force attack
- Finding: Failed login attempts
- Severity: High
- Evidence: 500 attempts from single IP

**T+33s** - Unauthorized API access
- Finding: Deprecated endpoint exploited
- Severity: Critical
- Evidence: Using leaked credentials

**T+37s** - Data exfiltration
- Finding: Large data export
- Severity: Critical
- Evidence: 100,000 user records downloaded

**T+42s** - **INCIDENT #3**: Active data breach
- Title: "ACTIVE BREACH: Coordinated attack with data exfiltration"
- Severity: Critical
- Confidence: 98%
- Attack Path: Recon → Creds → Brute Force → API → Database → Exfiltration

### Phase 4: Infrastructure Issues (42-60s)
**T+48s** - Container security issue
- Finding: Container running as root
- Severity: Medium
- Evidence: Privilege escalation risk

**T+52s** - Weak encryption
- Finding: MD5 hash for passwords
- Severity: High
- Evidence: Hardcoded weak encryption key

**T+56s** - Debug mode in production
- Finding: Stack traces exposed
- Severity: Medium
- Evidence: Debug mode enabled

**T+60s** - **INCIDENT #4**: Infrastructure vulnerabilities
- Title: "Critical security posture issues across infrastructure"
- Severity: High
- Confidence: 88%
- Attack Path: Root Container → Weak Crypto → Debug Mode → Elevated Risk

## 📈 Demo Statistics

### Total Events
- **14 Findings** across 3 repositories
- **4 Incidents** with varying severity
- **60 seconds** of continuous monitoring
- **Multiple attack vectors** demonstrated

### Severity Distribution
- **Critical**: 5 findings, 2 incidents
- **High**: 6 findings, 1 incident
- **Medium**: 3 findings, 1 incident
- **Low**: 0 findings, 0 incidents

### Affected Components
- **Repositories**: frontend-app, legacy-backend, infra-config
- **Endpoints**: /api/v1/export-users, /api/v1/login, /api/v1/search
- **Database Tables**: users
- **Files**: 10+ files across repos

## 🎯 What the Demo Demonstrates

### 1. Real-time Detection
- Findings appear as they're detected
- No page refresh needed
- Live counters update automatically

### 2. Incident Correlation
- Multiple findings grouped into incidents
- Confidence scoring based on evidence
- Attack path visualization

### 3. Severity Classification
- Automatic severity assessment
- Color-coded indicators
- Priority-based alerting

### 4. Multi-phase Attacks
- Reconnaissance → Exploitation → Exfiltration
- Coordinated attack patterns
- Time-based correlation

### 5. Diverse Finding Types
- Secret exposure (credentials, keys)
- Infrastructure risks (ports, containers)
- Runtime anomalies (traffic, access)
- Database issues (queries, exports)
- Legacy code problems (deprecated APIs)

## 🔍 Dashboard Features Showcased

### Overview Cards
- Total findings counter (updates to 14)
- Incidents counter (updates to 4)
- Severity distribution
- Confidence scores
- Affected repositories

### Findings Table
- Real-time finding additions
- Severity color coding
- File locations and line numbers
- Evidence descriptions
- Timestamp tracking

### Incident Details
- Incident correlation
- Confidence assessment
- Affected assets
- Attack path graphs
- Related findings

### Event Log
- All SSE messages visible
- Event types and timestamps
- Progress indicators
- Demo completion status

## 🎬 Demo Scenarios

### Scenario 1: Security Audit
**Use Case**: Demonstrating comprehensive security scanning

**What to Show**:
1. Start demo
2. Point out diverse finding types
3. Highlight severity distribution
4. Show incident correlation

### Scenario 2: Active Breach Response
**Use Case**: Incident response workflow

**What to Show**:
1. Watch Phase 3 (T+25-42s)
2. Show attack path visualization
3. Highlight confidence scoring
4. Demonstrate real-time alerting

### Scenario 3: Infrastructure Review
**Use Case**: DevOps security assessment

**What to Show**:
1. Focus on Phase 4 (T+42-60s)
2. Container security issues
3. Configuration problems
4. Production best practices

## 📝 Talking Points for Demos

### For Security Teams
- "Watch how Bob correlates 14 separate findings into 4 actionable incidents"
- "Notice the confidence scoring - 98% confidence on the active breach"
- "See the attack path visualization showing the full exploit chain"

### For DevOps Teams
- "All findings include exact file locations and line numbers"
- "Infrastructure misconfigurations detected automatically"
- "Container security issues flagged in real-time"

### For Management
- "60 seconds of monitoring detected a critical data breach"
- "System identified 5 critical issues requiring immediate action"
- "Automated correlation reduced alert fatigue from 14 to 4 incidents"

## 🔄 Comparing to Short Demo

### Short Demo (10 seconds)
- 3 findings
- 1 incident
- Single attack vector
- Basic demonstration

### Extended Demo (60 seconds)
- 14 findings
- 4 incidents
- Multiple attack vectors
- Production-realistic scenario
- Full attack lifecycle
- Infrastructure + application issues

## 🛠️ Customizing the Demo

### Adjusting Timing
Edit `src/api_server.py`, line ~270:
```python
{
    "type": "finding",
    "delay": 2,  # Change delay in seconds
    "data": { ... }
}
```

### Adding New Findings
Add to the `demo_events` array:
```python
{
    "type": "finding",
    "delay": 3,
    "data": {
        "finding_id": f"FIND-{int(timestamp_base)}-015",
        "repo_name": "your-repo",
        "finding_type": "your_type",
        # ... rest of finding data
    }
}
```

### Creating New Incidents
Add incident events:
```python
{
    "type": "incident",
    "delay": 5,
    "data": {
        "incident_id": f"INC-{int(timestamp_base)}-005",
        "title": "Your incident title",
        # ... rest of incident data
    }
}
```

## 🧪 Testing the Extended Demo

### Verification Checklist
- [ ] All 14 findings appear
- [ ] All 4 incidents are created
- [ ] Demo runs for ~60 seconds
- [ ] No errors in console
- [ ] Dashboard stays responsive
- [ ] Counters update correctly
- [ ] Event log shows all events
- [ ] Can run demo multiple times

### Performance Check
- Memory usage stays stable
- No memory leaks
- SSE connection remains active
- Multiple tabs work simultaneously

## 📊 Expected Console Output

```
🔌 Connecting to real-time updates...
✅ Connected to real-time updates
📡 Real-time event: {type: 'connected', ...}
📡 Real-time event: {type: 'finding_added', ...} (x14)
📡 Real-time event: {type: 'incident_added', ...} (x4)
📡 Real-time event: {type: 'demo_progress', ...} (x18)
📡 Real-time event: {type: 'demo_complete', ...}
```

## 🎓 Learning Outcomes

After watching the extended demo, viewers will understand:
1. How real-time security monitoring works
2. The importance of incident correlation
3. How attack chains are visualized
4. The value of confidence scoring
5. Multi-phase attack patterns
6. Infrastructure security issues
7. The speed of automated detection

## 🚀 Next Steps

After the demo:
1. Explore individual findings in detail
2. Review attack path visualizations
3. Check incident confidence assessments
4. View generated security tests
5. Read incident reports
6. Examine AI memory patterns

## 📞 Support

For demo-related questions:
- Check console for errors
- Verify backend is running
- Ensure frontend is on latest version
- Clear browser cache if issues occur

---

**The extended demo provides a production-realistic view of Bob Sentinel's capabilities in a 60-second showcase!** 🎬