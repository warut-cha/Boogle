# Mock Dataset Generator

## Overview
The `mock_dataset_generator.py` script generates realistic security incident data for testing the BOB (Best-of-Breed) security analysis system. Each execution randomly generates **one complete incident** with associated findings, attack paths, and metadata.

## Features

### 10 Different Incident Types
1. **Credential Leak** - Hardcoded secrets with suspicious access patterns
2. **SQL Injection** - Database injection vulnerabilities with exploitation
3. **Command Injection** - OS command execution vulnerabilities
4. **Data Exfiltration** - Mass data export incidents
5. **Weak Authentication** - Weak auth mechanisms with brute force attempts
6. **Debug Exposure** - Production debug endpoints exposing sensitive data
7. **Path Traversal** - File system access vulnerabilities
8. **CORS Misconfiguration** - Permissive cross-origin policies
9. **Rate Limit Abuse** - Missing rate limiting with abuse patterns
10. **Sensitive Data Logging** - PII/PCI data logged in plaintext

### Generated Data Structure
Each incident includes:
- **Unique IDs** - Incident and finding IDs
- **Severity Levels** - Critical (5), High (4), Medium (3), Low (2)
- **Confidence Scores** - 0.70-0.98 range with reasons and limitations
- **Multiple Findings** - 2-4 correlated findings per incident
- **Attack Paths** - Visual graph data (nodes and edges)
- **Affected Resources** - Repos, files, endpoints, database tables
- **Timestamps** - Realistic time sequences

## Usage

### Basic Usage
Generate one random incident:
```bash
python3 mock_dataset_generator.py
```

### Output
The script outputs:
1. **JSON to stdout** - Full incident data
2. **File saved** - `mock_incident_INC-XXXX.json`
3. **Summary to stderr** - Incident overview

### Example Output
```
✅ Generated incident saved to: mock_incident_INC-3010.json
📊 Incident Type: Path traversal vulnerability in /files/download
🔴 Severity: high (Level 4)
🔍 Findings: 2
📈 Confidence: 0.82
```

### Generate Multiple Incidents
```bash
# Generate 10 random incidents
for i in {1..10}; do
  python3 mock_dataset_generator.py > /dev/null
done

# List generated files
ls -lh mock_incident_*.json
```

### Use in Testing Pipeline
```bash
# Generate incident and pipe to your system
python3 mock_dataset_generator.py | python3 src/main.py --stdin

# Or save and process
python3 mock_dataset_generator.py
python3 src/main.py --input mock_incident_INC-*.json
```

### Integration with API Server
```bash
# Generate and POST to API
INCIDENT=$(python3 mock_dataset_generator.py)
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d "$INCIDENT"
```

## Data Structure

### Incident Schema
```json
{
  "incident_id": "INC-XXXX",
  "title": "Description of the incident",
  "severity": "critical|high|medium|low",
  "severity_level": 1-5,
  "confidence_score": 0.70-0.98,
  "confidence_reasons": ["reason1", "reason2"],
  "confidence_limitations": ["limitation1"],
  "affected_repos": ["repo1", "repo2"],
  "affected_files": ["file1.py"],
  "affected_endpoints": ["/api/endpoint"],
  "affected_database_tables": ["table1"],
  "findings": [...],
  "finding_count": 2-4,
  "correlation_type": "attack_chain|vulnerability_cluster",
  "description": "Detailed description",
  "timestamp": "2026-05-16T18:26:34.300366Z",
  "attack_path": {
    "nodes": [...],
    "edges": [...]
  }
}
```

### Finding Schema
```json
{
  "finding_id": "FIND-XXXX",
  "repo_name": "repository-name",
  "finding_type": "hardcoded_secret|sql_injection|...",
  "category": "secret_exposure|injection_vulnerability|...",
  "severity_hint": "critical|high|medium|low",
  "source": "rust_scanner|python_analyzer|mock_data",
  "file": "path/to/file.py",
  "line": 42,
  "endpoint": "/api/endpoint",
  "database_table": "table_name",
  "evidence": "Description of the finding",
  "masked_value": "sk_test_****92fa",
  "timestamp": "2026-05-16T18:08:34.300058Z"
}
```

## Customization

### Modify Incident Types
Edit the `incident_templates` list in `MockIncidentGenerator.__init__()`:
```python
self.incident_templates = [
    self._generate_credential_leak_incident,
    self._generate_sql_injection_incident,
    # Add your custom generator here
]
```

### Add Custom Repositories
Modify the `repos` list:
```python
self.repos = ["legacy-backend", "frontend-app", "your-repo"]
```

### Adjust Severity Distribution
Modify severity selection in each generator function:
```python
severity = random.choice(["critical", "high"])  # Only critical/high
```

## Testing Scenarios

### Test Different Incident Types
```bash
# Generate 10 incidents to see variety
for i in {1..10}; do
  python3 mock_dataset_generator.py 2>&1 | grep "Incident Type"
done
```

### Test Severity Distribution
```bash
# Check severity distribution
for i in {1..20}; do
  python3 mock_dataset_generator.py 2>&1 | grep "Severity"
done | sort | uniq -c
```

### Test with BOB System
```bash
# Generate and analyze
python3 mock_dataset_generator.py > test_incident.json
python3 test_pipeline.py --incident test_incident.json
```

## Realistic Data Features

### Randomization
- **Incident IDs**: INC-1000 to INC-9999
- **Finding IDs**: FIND-1000 to FIND-9999
- **Timestamps**: Realistic time sequences (older findings → newer incidents)
- **Confidence Scores**: Varied based on incident type
- **Request Counts**: Realistic ranges for anomalies
- **Database Metrics**: Realistic row counts and multipliers

### Correlation Types
- **attack_chain**: Sequential attack stages (e.g., secret → API → traffic → DB → leak)
- **vulnerability_cluster**: Related vulnerabilities (e.g., weak auth + credential logging)

### Evidence Patterns
- Masked secrets (e.g., `sk_test_****92fa`)
- Specific code patterns (e.g., `subprocess.run(user_input, shell=True)`)
- Quantified anomalies (e.g., "47 requests in 10 minutes")
- Database metrics (e.g., "2,847 rows read, 10x baseline")

## Troubleshooting

### Deprecation Warning
If you see a datetime warning, it's harmless and doesn't affect functionality:
```
DeprecationWarning: datetime.datetime.utcnow() is deprecated
```

### No Output File
Check write permissions in the current directory:
```bash
ls -la mock_incident_*.json
```

### JSON Parse Errors
Validate generated JSON:
```bash
python3 mock_dataset_generator.py | python3 -m json.tool
```

## Examples

### Example 1: Credential Leak
```json
{
  "incident_id": "INC-2341",
  "title": "Credential leakage through exposed /api/v1/export-users endpoint",
  "severity": "critical",
  "severity_level": 5,
  "findings": [
    {
      "finding_type": "hardcoded_secret",
      "evidence": "Hardcoded API key detected: sk_test_****92fa"
    },
    {
      "finding_type": "deprecated_api",
      "evidence": "Deprecated API endpoint still accessible"
    },
    {
      "finding_type": "runtime_anomaly",
      "evidence": "Suspicious access pattern: 127 requests in 8 minutes"
    }
  ]
}
```

### Example 2: SQL Injection
```json
{
  "incident_id": "INC-5678",
  "title": "SQL injection vulnerability in /api/v1/users endpoint",
  "severity": "critical",
  "severity_level": 5,
  "findings": [
    {
      "finding_type": "sql_injection",
      "evidence": "Unsanitized user input in SQL query"
    },
    {
      "finding_type": "runtime_anomaly",
      "evidence": "SQL injection attempt detected: 32 malicious queries"
    },
    {
      "finding_type": "database_anomaly",
      "evidence": "Abnormal users table access: 3,421 rows read"
    }
  ]
}
```

## Integration Points

### With BOB Pipeline
```python
from mock_dataset_generator import MockIncidentGenerator

generator = MockIncidentGenerator()
incident = generator.generate_random_incident()

# Feed to your analysis pipeline
analyze_incident(incident)
```

### With Test Suite
```python
import pytest
from mock_dataset_generator import MockIncidentGenerator

@pytest.fixture
def random_incident():
    generator = MockIncidentGenerator()
    return generator.generate_random_incident()

def test_incident_analysis(random_incident):
    result = analyze(random_incident)
    assert result.severity in ["critical", "high", "medium", "low"]
```

## License
Part of the IBM-BOB security analysis system.

---
**Note**: This generator creates synthetic data for testing purposes only. Do not use in production security monitoring.