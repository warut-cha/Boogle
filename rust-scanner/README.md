# Jeff Rust Scanner

A high-performance security scanner written in Rust for the Jeff DevSecOps platform.

## Features

- **Secret Detection**: Finds hardcoded API keys, passwords, tokens, and credentials
- **API Analysis**: Detects deprecated and legacy API endpoints
- **Infrastructure Scanning**: Identifies security risks in Docker, Kubernetes, and CI/CD configs
- **Log Analysis**: Detects sensitive data exposure in logging statements
- **Multi-Repository Support**: Scan multiple repositories in a single run
- **JSON Output**: Structured output for easy integration with the Python backend

## Prerequisites

- Rust 1.70 or higher
- Cargo (comes with Rust)

### Installing Rust

**Windows:**
```powershell
# Download and run rustup-init.exe from https://rustup.rs/
# Or use winget:
winget install Rustlang.Rustup
```

**Linux/macOS:**
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

## Building

```bash
cd rust-scanner
cargo build --release
```

The compiled binary will be at `target/release/bob-scanner` (or `bob-scanner.exe` on Windows).

## Usage

### Basic Scan

Scan one or more repository paths:

```bash
cargo run --release -- scan --paths ../mock-repos/legacy-backend ../mock-repos/infra-config ../mock-repos/frontend-app
```

Or using the compiled binary:

```bash
./target/release/bob-scanner scan --paths ../mock-repos/legacy-backend ../mock-repos/infra-config
```

### Output

The scanner outputs JSON to stdout. Each finding follows this structure:

```json
{
  "finding_id": "FIND-001",
  "repo_name": "legacy-backend",
  "finding_type": "hardcoded_secret",
  "category": "secret_exposure",
  "severity_hint": "high",
  "source": "rust_scanner",
  "file": "legacy/old_export_api.py",
  "line": 12,
  "endpoint": "/api/v1/export-users",
  "database_table": null,
  "evidence": "Possible API key detected",
  "masked_value": "sk_test_****92fa",
  "timestamp": "2026-05-16T12:00:00Z"
}
```

### Redirecting Output

Save findings to a file:

```bash
cargo run --release -- scan --paths ../mock-repos/legacy-backend > findings.json
```

### Integration with Python Backend

The Python backend can invoke the scanner and parse the JSON output:

```python
import subprocess
import json

result = subprocess.run(
    ['cargo', 'run', '--release', '--', 'scan', '--paths', '../mock-repos/legacy-backend'],
    cwd='rust-scanner',
    capture_output=True,
    text=True
)

findings = json.loads(result.stdout)
```

## Detection Capabilities

### Secret Detection
- API keys (various formats)
- Secret keys
- Access tokens
- Passwords
- Authorization Bearer tokens
- Private keys (RSA, SSH)
- Database URLs with credentials
- AWS credentials

### API Detection
- Deprecated API versions (`/api/v1/`)
- Legacy endpoints (`/legacy/`)
- Export/download/dump endpoints
- Old API routes

### Infrastructure Risks
- Dockerfiles running as root
- Missing USER directives
- Exposed database ports in docker-compose
- Privileged containers
- GitHub Actions secret exposure
- Gateway configs exposing deprecated endpoints
- Insecure HTTP protocols

### Log Exposure
- Logging passwords, secrets, tokens
- Logging user PII (email, SSN, credit cards)
- Logging API keys
- Logging authentication tokens
- Logging database credentials
- Debug logging in production
- Logging request headers/bodies

## Finding Types

- `hardcoded_secret`: Hardcoded credentials in code
- `private_key`: SSH or RSA private keys
- `database_url`: Database connection strings with credentials
- `deprecated_api`: Old or deprecated API endpoints
- `infrastructure_risk`: Security issues in infrastructure configs
- `sensitive_log_exposure`: Sensitive data in logs

## Severity Levels

- `critical`: Immediate action required
- `high`: Should be fixed soon
- `medium`: Should be addressed
- `low`: Minor issue
- `info`: Informational

## Architecture

```
rust-scanner/
├── src/
│   ├── main.rs              # CLI and orchestration
│   ├── models.rs            # Data structures and JSON serialization
│   ├── file_walker.rs       # Recursive file system traversal
│   ├── secret_scanner.rs    # Secret detection patterns
│   ├── api_scanner.rs       # API endpoint analysis
│   ├── infra_scanner.rs     # Infrastructure security checks
│   └── log_scanner.rs       # Log exposure detection
└── Cargo.toml               # Dependencies and build config
```

## Performance

The Rust scanner is designed for speed:
- Parallel file processing (future enhancement)
- Efficient regex matching
- Minimal memory footprint
- Fast startup time

## Error Handling

- Gracefully handles missing paths
- Continues scanning if individual files fail
- Warnings printed to stderr
- JSON output only to stdout

## Development

### Running Tests

```bash
cargo test
```

### Linting

```bash
cargo clippy
```

### Formatting

```bash
cargo fmt
```

## Integration with Jeff

The scanner is the first stage in the Jeff pipeline:

1. **Rust Scanner** → Finds security issues
2. **Python Backend** → Correlates findings into incidents
3. **IBM Bob** → Analyzes and generates fixes
4. **React Dashboard** → Displays results

## License

Part of the Jeff project.