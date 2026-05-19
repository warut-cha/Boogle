**User:**

<task>
can you write a mock_dataset_generate to simulate each incident, every time just randomly genertae one code, i gonna use this to test our system
</task>
<environment_details>
# VSCode Visible Files
../../Downloads/bob_task_may-16-2026_5-54-56-pm.md

# VSCode Open Tabs
frontend/.env.example,start_services.sh,INTEGRATION_GUIDE.md,README.md,CHANGES.md,frontend/.env,DATASET_GUIDE.md,PORT_FIX.md,src/api_server.py,WATSON_SETUP_GUIDE.md,frontend/src/components/ScanInput.tsx,frontend/src/api/client.ts,frontend/src/pages/DashboardPage.tsx,IBM_CREDENTIALS_SETUP.md,.env,config/config.yaml,../../Downloads/bob_task_may-16-2026_5-54-56-pm.md

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T18:24:29.212Z
User time zone: Europe/Stockholm, UTC+2:00

# Current Cost
$0.00

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>


# Current Workspace Directory (/Users/sxy/job_apply/IBM-BOB) Files
.gitignore
ARCHITECTURE.md
ATTACK_SCENARIOS.md
CHANGES.md
DATASET_GUIDE.md
IBM_CREDENTIALS_SETUP.md
IMPLEMENTATION_PLAN.md
INTEGRATION_GUIDE.md
PORT_FIX.md
PROJECT_SUMMARY.md
README.md
requirements.txt
setup.py
start_services.sh
test_incident_output.json
test_pipeline.py
WATSON_SETUP_GUIDE.md
config/
config/config.yaml
contracts/
contracts/bob_input.schema.json
contracts/bob_output.schema.json
contracts/finding.schema.json
contracts/incident.schema.json
contracts/sample_bob_output.json
contracts/sample_findings.json
contracts/sample_incident.json
docs/
docs/dashboard_guide.md
docs/demo_script.md
docs/USER_GUIDE.md
frontend/
frontend/.env.example
frontend/index.html
frontend/package-lock.json
frontend/package.json
frontend/playwright.config.ts
frontend/README.md
frontend/tsconfig.json
frontend/tsconfig.node.json
frontend/vite.config.ts
frontend/e2e/
frontend/e2e/dashboard.spec.ts
frontend/models/
frontend/models/ai_memory.json
frontend/src/
frontend/src/App.tsx
frontend/src/main.tsx
frontend/src/api/
frontend/src/api/client.ts
frontend/src/api/types.ts
frontend/src/components/
frontend/src/components/AttackPathGraph.tsx
frontend/src/components/BobAnalysis.tsx
frontend/src/components/FindingsTable.tsx
frontend/src/components/IncidentDetail.tsx
frontend/src/components/MemoryViewer.tsx
frontend/src/components/OverviewCards.tsx
frontend/src/components/PRDraftViewer.tsx
frontend/src/components/ReportViewer.tsx
frontend/src/components/ScanInput.tsx
frontend/src/pages/
frontend/src/pages/DashboardPage.tsx
frontend/src/test/
frontend/src/test/DashboardPage.test.tsx
frontend/src/test/FindingsTable.test.tsx
frontend/src/test/OverviewCards.test.tsx
frontend/src/test/setup.ts
frontend/test-results/
frontend/test-results/.last-run.json
generated_reports/
generated_reports/.gitkeep
generated_tests/
generated_tests/.gitkeep
mock_data/
mock_data/repos/
mock_data/repos/ecommerce_app/
mock_data/repos/ecommerce_app/api_routes.py
mock_data/repos/ecommerce_app/config.py
mock-repos/
mock-repos/frontend-app/
mock-repos/frontend-app/src/
mock-repos/frontend-app/src/api/
mock-repos/frontend-app/src/api/client.ts
mock-repos/infra-config/
mock-repos/infra-config/docker-compose.yml
mock-repos/infra-config/Dockerfile
mock-repos/infra-config/gateway.yml
mock-repos/infra-config/.github/
mock-repos/legacy-backend/
mock-repos/legacy-backend/database/
mock-repos/legacy-backend/database/mock_db_events.json
mock-repos/legacy-backend/legacy/
mock-repos/legacy-backend/legacy/old_export_api.py
mock-repos/legacy-backend/logs/
mock-repos/legacy-backend/logs/api_logs.json
models/
patterns/
patterns/api_patterns.json
patterns/secret_patterns.json
rust-scanner/
rust-scanner/Cargo.lock
rust-scanner/Cargo.toml
rust-scanner/EXPECTED_OUTPUT.json
rust-scanner/README.md
rust-scanner/TEST_REPORT.md
rust-scanner/test_results.json
rust-scanner/src/
rust-scanner/src/api_scanner.rs
rust-scanner/src/file_walker.rs
rust-scanner/src/infra_scanner.rs
rust-scanner/src/log_scanner.rs
rust-scanner/src/main.rs
rust-scanner/src/models.rs
rust-scanner/src/secret_scanner.rs
src/
src/__init__.py
src/api_server.py
src/main.py
src/ai_engine/
src/ai_engine/__init__.py
src/ai_engine/bob_client.py
src/ai_engine/bob_prompt_builder.py
src/ai_engine/bob_response_parser.py
src/ai_engine/memory_manager.py
src/ai_engine/reasoning_engine.py
src/ai_engine/vector_memory.py
src/analyzers/
src/analyzers/__init__.py
src/analyzers/deprecated_api_detector.py
src/analyzers/runtime_analyzer.py
src/analyzers/static_analyzer.py
src/classifiers/
src/classifiers/__init__.py
src/classifiers/confidence_scorer.py
src/classifiers/severity_classifier.py
src/collectors/
src/collectors/__init__.py
src/collectors/api_collector.py
src/collectors/code_collector.py
src/collectors/log_collector.py
src/correlators/
src/correlators/__init__.py
src/correlators/attack_path_builder.py
src/correlators/incident_correlator.py
src/database/
src/database/__init__.py
src/database/connection.py
src/remediators/
src/remediators/__init__.py
src/remediators/fix_generator.py
src/remediators/pr_draft_generator.py
src/remediators/test_generator.py
src/reporters/
src/reporters/__init__.py
src/reporters/incident_reporter.py
src/scanners/
src/scanners/rust_scanner_client.py
tests/
tests/test_bob_integration.py
tests/test_static_analyzer.py
tests/integration/
tests/integration/test_full_analysis.py
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

I'll help you create a mock dataset generator to simulate incidents. Let me first explore the existing structure to understand what kind of incidents and data formats you're using.

<read_file>
<args>
<file>
<path>contracts/sample_incident.json</path>
</file>
<file>
<path>contracts/incident.schema.json</path>
</file>
<file>
<path>test_incident_output.json</path>
</file>
<file>
<path>mock_data/repos/ecommerce_app/api_routes.py</path>
</file>
<file>
<path>mock-repos/legacy-backend/database/mock_db_events.json</path>
</file>
</args>
</read_file>

---

**User:**

[read_file for 5 files] Result:
<files>
<file><path>contracts/sample_incident.json</path>
<content lines="1-160">
  1 | {
  2 |   "incident_id": "INC-001",
  3 |   "title": "Possible credential leakage through exposed abandoned export API",
  4 |   "severity": "critical",
  5 |   "severity_level": 5,
  6 |   "confidence_score": 0.88,
  7 |   "confidence_reasons": [
  8 |     "Hardcoded API key found in legacy code",
  9 |     "Deprecated export endpoint is still reachable",
 10 |     "Suspicious repeated access detected in logs",
 11 |     "Users table showed abnormal read activity"
 12 |   ],
 13 |   "confidence_limitations": [
 14 |     "No confirmed external exfiltration destination found",
 15 |     "Unable to verify if data was actually exported"
 16 |   ],
 17 |   "affected_repos": [
 18 |     "legacy-backend",
 19 |     "infra-config"
 20 |   ],
 21 |   "affected_files": [
 22 |     "legacy/old_export_api.py",
 23 |     "gateway.yml"
 24 |   ],
 25 |   "affected_endpoints": [
 26 |     "/api/v1/export-users"
 27 |   ],
 28 |   "affected_database_tables": [
 29 |     "users"
 30 |   ],
 31 |   "findings": [
 32 |     {
 33 |       "finding_id": "FIND-001",
 34 |       "repo_name": "legacy-backend",
 35 |       "finding_type": "hardcoded_secret",
 36 |       "category": "secret_exposure",
 37 |       "severity_hint": "high",
 38 |       "source": "rust_scanner",
 39 |       "file": "legacy/old_export_api.py",
 40 |       "line": 12,
 41 |       "endpoint": "/api/v1/export-users",
 42 |       "database_table": null,
 43 |       "evidence": "Possible API key detected: sk_test_****92fa",
 44 |       "masked_value": "sk_test_****92fa",
 45 |       "timestamp": "2026-05-16T12:00:00Z"
 46 |     },
 47 |     {
 48 |       "finding_id": "FIND-002",
 49 |       "repo_name": "legacy-backend",
 50 |       "finding_type": "deprecated_api",
 51 |       "category": "legacy_api",
 52 |       "severity_hint": "medium",
 53 |       "source": "python_analyzer",
 54 |       "file": "legacy/old_export_api.py",
 55 |       "line": 25,
 56 |       "endpoint": "/api/v1/export-users",
 57 |       "database_table": null,
 58 |       "evidence": "Deprecated API endpoint still accessible",
 59 |       "masked_value": null,
 60 |       "timestamp": "2026-05-16T12:01:00Z"
 61 |     },
 62 |     {
 63 |       "finding_id": "FIND-003",
 64 |       "repo_name": "legacy-backend",
 65 |       "finding_type": "runtime_anomaly",
 66 |       "category": "runtime_behavior",
 67 |       "severity_hint": "high",
 68 |       "source": "mock_data",
 69 |       "file": null,
 70 |       "line": null,
 71 |       "endpoint": "/api/v1/export-users",
 72 |       "database_table": null,
 73 |       "evidence": "Repeated access to deprecated endpoint from suspicious IP",
 74 |       "masked_value": null,
 75 |       "timestamp": "2026-05-16T12:05:00Z"
 76 |     },
 77 |     {
 78 |       "finding_id": "FIND-004",
 79 |       "repo_name": "legacy-backend",
 80 |       "finding_type": "database_anomaly",
 81 |       "category": "database_activity",
 82 |       "severity_hint": "high",
 83 |       "source": "mock_data",
 84 |       "file": null,
 85 |       "line": null,
 86 |       "endpoint": null,
 87 |       "database_table": "users",
 88 |       "evidence": "Users table read spike: 10x normal baseline",
 89 |       "masked_value": null,
 90 |       "timestamp": "2026-05-16T12:06:00Z"
 91 |     },
 92 |     {
 93 |       "finding_id": "FIND-005",
 94 |       "repo_name": "infra-config",
 95 |       "finding_type": "infrastructure_risk",
 96 |       "category": "infrastructure",
 97 |       "severity_hint": "medium",
 98 |       "source": "rust_scanner",
 99 |       "file": "gateway.yml",
100 |       "line": 45,
101 |       "endpoint": "/api/v1/export-users",
102 |       "database_table": null,
103 |       "evidence": "Old export endpoint still exposed in gateway config",
104 |       "masked_value": null,
105 |       "timestamp": "2026-05-16T12:02:00Z"
106 |     }
107 |   ],
108 |   "attack_path": {
109 |     "nodes": [
110 |       {
111 |         "id": "secret",
112 |         "label": "Hardcoded API Key",
113 |         "type": "secret"
114 |       },
115 |       {
116 |         "id": "old_api",
117 |         "label": "Abandoned Export API",
118 |         "type": "api"
119 |       },
120 |       {
121 |         "id": "traffic",
122 |         "label": "Suspicious Requests",
123 |         "type": "runtime"
124 |       },
125 |       {
126 |         "id": "db",
127 |         "label": "Users Table Read Spike",
128 |         "type": "database"
129 |       },
130 |       {
131 |         "id": "leak",
132 |         "label": "Possible Data Leak",
133 |         "type": "impact"
134 |       }
135 |     ],
136 |     "edges": [
137 |       {
138 |         "from": "secret",
139 |         "to": "old_api",
140 |         "label": "used by"
141 |       },
142 |       {
143 |         "from": "old_api",
144 |         "to": "traffic",
145 |         "label": "targeted by"
146 |       },
147 |       {
148 |         "from": "traffic",
149 |         "to": "db",
150 |         "label": "accesses"
151 |       },
152 |       {
153 |         "from": "db",
154 |         "to": "leak",
155 |         "label": "may expose"
156 |       }
157 |     ]
158 |   },
159 |   "timestamp": "2026-05-16T12:10:00Z"
160 | }
</content>
</file>
<file><path>contracts/incident.schema.json</path>
<content/><notice>File is empty</notice>
</file>
<file><path>test_incident_output.json</path>
<content lines="1-195">
  1 | {
  2 |   "incident_id": "INC-001",
  3 |   "title": "Possible credential leakage through exposed abandoned export API",
  4 |   "severity": "medium",
  5 |   "severity_level": 3,
  6 |   "affected_repos": [
  7 |     "infra-config",
  8 |     "legacy-backend"
  9 |   ],
 10 |   "affected_files": [
 11 |     "legacy/old_export_api.py",
 12 |     "gateway.yml"
 13 |   ],
 14 |   "affected_endpoints": [
 15 |     "/api/v1/export-users"
 16 |   ],
 17 |   "affected_database_tables": [
 18 |     "users"
 19 |   ],
 20 |   "findings": [
 21 |     {
 22 |       "finding_id": "FIND-001",
 23 |       "repo_name": "legacy-backend",
 24 |       "finding_type": "hardcoded_secret",
 25 |       "category": "secret_exposure",
 26 |       "severity_hint": "high",
 27 |       "source": "rust_scanner",
 28 |       "file": "legacy/old_export_api.py",
 29 |       "line": 12,
 30 |       "endpoint": "/api/v1/export-users",
 31 |       "database_table": null,
 32 |       "evidence": "Hardcoded API key detected in legacy export endpoint",
 33 |       "masked_value": "sk_test_****92fa",
 34 |       "timestamp": "2026-05-16T14:45:24.325969Z"
 35 |     },
 36 |     {
 37 |       "finding_id": "FIND-002",
 38 |       "repo_name": "legacy-backend",
 39 |       "finding_type": "deprecated_api",
 40 |       "category": "legacy_api",
 41 |       "severity_hint": "medium",
 42 |       "source": "rust_scanner",
 43 |       "file": "legacy/old_export_api.py",
 44 |       "line": 8,
 45 |       "endpoint": "/api/v1/export-users",
 46 |       "database_table": null,
 47 |       "evidence": "Deprecated export endpoint still accessible",
 48 |       "masked_value": null,
 49 |       "timestamp": "2026-05-16T14:45:24.325969Z"
 50 |     },
 51 |     {
 52 |       "finding_id": "FIND-003",
 53 |       "repo_name": "legacy-backend",
 54 |       "finding_type": "runtime_anomaly",
 55 |       "category": "runtime_behavior",
 56 |       "severity_hint": "medium",
 57 |       "source": "mock_data",
 58 |       "file": null,
 59 |       "line": null,
 60 |       "endpoint": "/api/v1/export-users",
 61 |       "database_table": null,
 62 |       "evidence": "Repeated suspicious access to deprecated endpoint (47 requests in 10 minutes)",
 63 |       "masked_value": null,
 64 |       "timestamp": "2026-05-16T14:45:24.325969Z"
 65 |     },
 66 |     {
 67 |       "finding_id": "FIND-004",
 68 |       "repo_name": "legacy-backend",
 69 |       "finding_type": "database_anomaly",
 70 |       "category": "database_activity",
 71 |       "severity_hint": "high",
 72 |       "source": "mock_data",
 73 |       "file": null,
 74 |       "line": null,
 75 |       "endpoint": null,
 76 |       "database_table": "users",
 77 |       "evidence": "Abnormal read spike on users table (2,847 rows read in 5 minutes)",
 78 |       "masked_value": null,
 79 |       "timestamp": "2026-05-16T14:45:24.325969Z"
 80 |     },
 81 |     {
 82 |       "finding_id": "FIND-005",
 83 |       "repo_name": "infra-config",
 84 |       "finding_type": "infrastructure_risk",
 85 |       "category": "infrastructure",
 86 |       "severity_hint": "medium",
 87 |       "source": "rust_scanner",
 88 |       "file": "gateway.yml",
 89 |       "line": 23,
 90 |       "endpoint": "/api/v1/export-users",
 91 |       "database_table": null,
 92 |       "evidence": "Gateway configuration still routes to deprecated export endpoint",
 93 |       "masked_value": null,
 94 |       "timestamp": "2026-05-16T14:45:24.325969Z"
 95 |     }
 96 |   ],
 97 |   "finding_count": 5,
 98 |   "correlation_type": "attack_chain",
 99 |   "description": "Detected coordinated attack: Hardcoded API key in abandoned export API with suspicious access patterns and database activity",
100 |   "timestamp": "2026-05-16T14:45:24.326468Z",
101 |   "confidence_score": 0.92,
102 |   "confidence_reasons": [
103 |     "Hardcoded API key found",
104 |     "Deprecated export endpoint is still reachable",
105 |     "Suspicious repeated access detected",
106 |     "Users table showed abnormal read activity",
107 |     "Infrastructure configuration exposes vulnerable endpoint",
108 |     "Multiple attack stages detected in sequence",
109 |     "Multiple repositories affected (2 repos)"
110 |   ],
111 |   "confidence_limitations": [
112 |     "Analysis based on available data only"
113 |   ],
114 |   "attack_path": {
115 |     "nodes": [
116 |       {
117 |         "id": "secret",
118 |         "label": "Hardcoded API Key",
119 |         "type": "secret",
120 |         "findings": [
121 |           "FIND-001"
122 |         ],
123 |         "evidence": [
124 |           "Hardcoded API key detected in legacy export endpoint"
125 |         ],
126 |         "file": "legacy/old_export_api.py",
127 |         "endpoint": "/api/v1/export-users"
128 |       },
129 |       {
130 |         "id": "old_api",
131 |         "label": "Abandoned Export API",
132 |         "type": "api",
133 |         "findings": [
134 |           "FIND-002"
135 |         ],
136 |         "evidence": [
137 |           "Deprecated export endpoint still accessible"
138 |         ],
139 |         "file": "legacy/old_export_api.py",
140 |         "endpoint": "/api/v1/export-users"
141 |       },
142 |       {
143 |         "id": "traffic",
144 |         "label": "Suspicious Requests",
145 |         "type": "runtime",
146 |         "findings": [
147 |           "FIND-003"
148 |         ],
149 |         "evidence": [
150 |           "Repeated suspicious access to deprecated endpoint (47 requests in 10 minutes)"
151 |         ],
152 |         "endpoint": "/api/v1/export-users"
153 |       },
154 |       {
155 |         "id": "db",
156 |         "label": "Users Table Read Spike",
157 |         "type": "database",
158 |         "findings": [
159 |           "FIND-004"
160 |         ],
161 |         "evidence": [
162 |           "Abnormal read spike on users table (2,847 rows read in 5 minutes)"
163 |         ],
164 |         "database_table": "users"
165 |       },
166 |       {
167 |         "id": "leak",
168 |         "label": "Possible Data Leak",
169 |         "type": "impact"
170 |       }
171 |     ],
172 |     "edges": [
173 |       {
174 |         "from": "secret",
175 |         "to": "old_api",
176 |         "label": "used by"
177 |       },
178 |       {
179 |         "from": "old_api",
180 |         "to": "traffic",
181 |         "label": "targeted by"
182 |       },
183 |       {
184 |         "from": "traffic",
185 |         "to": "db",
186 |         "label": "accesses"
187 |       },
188 |       {
189 |         "from": "db",
190 |         "to": "leak",
191 |         "label": "may expose"
192 |       }
193 |     ]
194 |   }
195 | }
</content>
</file>
<file><path>mock_data/repos/ecommerce_app/api_routes.py</path>
<content lines="1-329">
  1 | """
  2 | E-commerce API Routes
  3 | WARNING: This file contains intentional security vulnerabilities for testing purposes
  4 | """
  5 | 
  6 | from flask import Flask, request, jsonify, session
  7 | import sqlite3
  8 | import os
  9 | import subprocess
 10 | 
 11 | app = Flask(__name__)
 12 | app.secret_key = 'insecure-secret-key-123'  # VULNERABILITY: Weak secret key
 13 | 
 14 | # VULNERABILITY: Deprecated API v1 endpoints still active
 15 | @app.route('/api/v1/users', methods=['GET'])
 16 | def get_users_v1():
 17 |     """
 18 |     DEPRECATED: Use /api/v3/users instead
 19 |     This endpoint will be removed on 2024-12-31
 20 |     """
 21 |     # VULNERABILITY: No authentication required
 22 |     conn = sqlite3.connect('ecommerce.db')
 23 |     cursor = conn.cursor()
 24 |     
 25 |     # VULNERABILITY: SQL Injection - user input not sanitized
 26 |     user_id = request.args.get('id', '')
 27 |     query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL INJECTION
 28 |     
 29 |     cursor.execute(query)
 30 |     users = cursor.fetchall()
 31 |     conn.close()
 32 |     
 33 |     # VULNERABILITY: Returns sensitive data including passwords
 34 |     return jsonify({'users': users})
 35 | 
 36 | 
 37 | @app.route('/api/v1/search', methods=['GET'])
 38 | def search_users_v1():
 39 |     """
 40 |     DEPRECATED: Legacy search endpoint
 41 |     """
 42 |     # VULNERABILITY: No authentication
 43 |     search_term = request.args.get('q', '')
 44 |     
 45 |     conn = sqlite3.connect('ecommerce.db')
 46 |     cursor = conn.cursor()
 47 |     
 48 |     # VULNERABILITY: SQL Injection via LIKE clause
 49 |     query = f"SELECT * FROM users WHERE name LIKE '%{search_term}%'"
 50 |     cursor.execute(query)
 51 |     results = cursor.fetchall()
 52 |     conn.close()
 53 |     
 54 |     return jsonify({'results': results})
 55 | 
 56 | 
 57 | @app.route('/api/v1/admin/users', methods=['GET', 'POST', 'DELETE'])
 58 | def admin_users_v1():
 59 |     """
 60 |     DEPRECATED: Admin endpoint without proper authentication
 61 |     """
 62 |     # VULNERABILITY: No authentication check
 63 |     # VULNERABILITY: No authorization check
 64 |     
 65 |     if request.method == 'DELETE':
 66 |         user_id = request.args.get('id')
 67 |         conn = sqlite3.connect('ecommerce.db')
 68 |         cursor = conn.cursor()
 69 |         # VULNERABILITY: SQL Injection
 70 |         cursor.execute(f"DELETE FROM users WHERE id = {user_id}")
 71 |         conn.commit()
 72 |         conn.close()
 73 |         return jsonify({'message': 'User deleted'})
 74 |     
 75 |     return jsonify({'message': 'Admin endpoint'})
 76 | 
 77 | 
 78 | @app.route('/api/v2/payments', methods=['POST'])
 79 | def process_payment_v2():
 80 |     """
 81 |     Payment processing endpoint
 82 |     """
 83 |     # VULNERABILITY: Weak authentication
 84 |     api_key = request.headers.get('X-API-Key')
 85 |     if api_key != 'simple-api-key-123':  # WEAK API KEY
 86 |         return jsonify({'error': 'Unauthorized'}), 401
 87 |     
 88 |     payment_data = request.json
 89 |     
 90 |     # VULNERABILITY: Logs sensitive payment information
 91 |     print(f"Processing payment: {payment_data}")  # LOGS CREDIT CARD DATA
 92 |     app.logger.info(f"Payment details: {payment_data}")  # LOGS TO FILE
 93 |     
 94 |     # VULNERABILITY: No input validation
 95 |     amount = payment_data.get('amount')
 96 |     card_number = payment_data.get('card_number')
 97 |     cvv = payment_data.get('cvv')
 98 |     
 99 |     return jsonify({
100 |         'status': 'success',
101 |         'transaction_id': '12345',
102 |         'card_last_four': card_number[-4:]  # EXPOSES CARD INFO
103 |     })
104 | 
105 | 
106 | @app.route('/api/v3/users/<int:user_id>', methods=['GET'])
107 | def get_user_v3(user_id):
108 |     """
109 |     Current API version - but still has vulnerabilities
110 |     """
111 |     # VULNERABILITY: Weak authentication
112 |     if 'user_id' not in session:
113 |         return jsonify({'error': 'Not authenticated'}), 401
114 |     
115 |     # VULNERABILITY: No authorization check - any authenticated user can access any user's data
116 |     conn = sqlite3.connect('ecommerce.db')
117 |     cursor = conn.cursor()
118 |     cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
119 |     user = cursor.fetchone()
120 |     conn.close()
121 |     
122 |     if user:
123 |         # VULNERABILITY: Returns sensitive data
124 |         return jsonify({
125 |             'id': user[0],
126 |             'username': user[1],
127 |             'email': user[2],
128 |             'password_hash': user[3],  # EXPOSES PASSWORD HASH
129 |             'ssn': user[4],  # EXPOSES SSN
130 |             'credit_card': user[5],  # EXPOSES CREDIT CARD
131 |             'address': user[6]
132 |         })
133 |     
134 |     return jsonify({'error': 'User not found'}), 404
135 | 
136 | 
137 | @app.route('/api/v3/export', methods=['GET'])
138 | def export_data():
139 |     """
140 |     Data export endpoint
141 |     """
142 |     # VULNERABILITY: No rate limiting
143 |     # VULNERABILITY: Weak authentication
144 |     api_key = request.headers.get('Authorization')
145 |     
146 |     if not api_key:
147 |         return jsonify({'error': 'No API key provided'}), 401
148 |     
149 |     # VULNERABILITY: Allows export of all data without proper authorization
150 |     conn = sqlite3.connect('ecommerce.db')
151 |     cursor = conn.cursor()
152 |     
153 |     table = request.args.get('table', 'users')
154 |     # VULNERABILITY: SQL Injection via table name
155 |     cursor.execute(f"SELECT * FROM {table}")  # SQL INJECTION
156 |     data = cursor.fetchall()
157 |     conn.close()
158 |     
159 |     # VULNERABILITY: Logs export activity with sensitive info
160 |     app.logger.info(f"User exported {len(data)} records from {table}")
161 |     
162 |     return jsonify({'data': data, 'count': len(data)})
163 | 
164 | 
165 | @app.route('/api/v3/upload', methods=['POST'])
166 | def upload_file():
167 |     """
168 |     File upload endpoint
169 |     """
170 |     # VULNERABILITY: No authentication
171 |     # VULNERABILITY: No file type validation
172 |     # VULNERABILITY: No file size limit
173 |     
174 |     if 'file' not in request.files:
175 |         return jsonify({'error': 'No file provided'}), 400
176 |     
177 |     file = request.files['file']
178 |     filename = file.filename  # VULNERABILITY: No sanitization
179 |     
180 |     # VULNERABILITY: Path traversal possible
181 |     upload_path = os.path.join('/uploads', filename)
182 |     file.save(upload_path)
183 |     
184 |     return jsonify({'message': 'File uploaded', 'path': upload_path})
185 | 
186 | 
187 | @app.route('/api/v3/execute', methods=['POST'])
188 | def execute_command():
189 |     """
190 |     DANGEROUS: Command execution endpoint
191 |     """
192 |     # VULNERABILITY: Command injection
193 |     # VULNERABILITY: No authentication
194 |     
195 |     command = request.json.get('command', '')
196 |     
197 |     # VULNERABILITY: Direct command execution
198 |     result = subprocess.run(command, shell=True, capture_output=True, text=True)
199 |     
200 |     return jsonify({
201 |         'stdout': result.stdout,
202 |         'stderr': result.stderr,
203 |         'returncode': result.returncode
204 |     })
205 | 
206 | 
207 | @app.route('/api/v3/debug', methods=['GET'])
208 | def debug_info():
209 |     """
210 |     Debug endpoint - should not be in production
211 |     """
212 |     # VULNERABILITY: Debug endpoint exposed in production
213 |     # VULNERABILITY: No authentication
214 |     
215 |     return jsonify({
216 |         'environment': dict(os.environ),  # EXPOSES ALL ENV VARS
217 |         'config': {
218 |             'database': app.config.get('DATABASE_URI'),
219 |             'secret_key': app.config.get('SECRET_KEY'),
220 |             'api_keys': app.config.get('API_KEYS')
221 |         },
222 |         'session': dict(session),  # EXPOSES SESSION DATA
223 |         'headers': dict(request.headers)
224 |     })
225 | 
226 | 
227 | @app.route('/api/v3/logs', methods=['GET'])
228 | def get_logs():
229 |     """
230 |     Log viewing endpoint
231 |     """
232 |     # VULNERABILITY: No authentication
233 |     # VULNERABILITY: Exposes sensitive log data
234 |     
235 |     log_file = request.args.get('file', 'app.log')
236 |     
237 |     # VULNERABILITY: Path traversal
238 |     log_path = f'/var/log/{log_file}'
239 |     
240 |     try:
241 |         with open(log_path, 'r') as f:
242 |             logs = f.read()
243 |         return jsonify({'logs': logs})
244 |     except Exception as e:
245 |         return jsonify({'error': str(e)}), 500
246 | 
247 | 
248 | @app.route('/api/v3/backup', methods=['POST'])
249 | def create_backup():
250 |     """
251 |     Database backup endpoint
252 |     """
253 |     # VULNERABILITY: Weak authentication
254 |     if request.headers.get('X-Admin-Token') != 'admin-token-123':
255 |         return jsonify({'error': 'Unauthorized'}), 401
256 |     
257 |     # VULNERABILITY: Command injection via backup filename
258 |     backup_name = request.json.get('name', 'backup')
259 |     command = f"pg_dump ecommerce_db > /backups/{backup_name}.sql"
260 |     
261 |     os.system(command)  # COMMAND INJECTION
262 |     
263 |     return jsonify({'message': 'Backup created', 'file': f'{backup_name}.sql'})
264 | 
265 | 
266 | @app.route('/api/v1/legacy/auth', methods=['POST'])
267 | def legacy_auth():
268 |     """
269 |     DEPRECATED: Legacy authentication endpoint
270 |     Uses weak authentication mechanism
271 |     """
272 |     # VULNERABILITY: Accepts credentials in GET parameters
273 |     username = request.args.get('username') or request.json.get('username')
274 |     password = request.args.get('password') or request.json.get('password')
275 |     
276 |     # VULNERABILITY: Logs credentials
277 |     app.logger.info(f"Login attempt: {username}:{password}")
278 |     
279 |     # VULNERABILITY: Weak password check
280 |     if username == 'admin' and password == 'admin123':
281 |         session['user_id'] = 1
282 |         session['role'] = 'admin'
283 |         return jsonify({'token': 'simple-jwt-token-12345'})  # WEAK TOKEN
284 |     
285 |     return jsonify({'error': 'Invalid credentials'}), 401
286 | 
287 | 
288 | @app.route('/api/v2/users/password-reset', methods=['POST'])
289 | def password_reset():
290 |     """
291 |     Password reset endpoint
292 |     """
293 |     email = request.json.get('email')
294 |     
295 |     # VULNERABILITY: No rate limiting - allows brute force
296 |     # VULNERABILITY: Reveals if email exists
297 |     
298 |     conn = sqlite3.connect('ecommerce.db')
299 |     cursor = conn.cursor()
300 |     cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
301 |     user = cursor.fetchone()
302 |     conn.close()
303 |     
304 |     if user:
305 |         # VULNERABILITY: Predictable reset token
306 |         reset_token = f"reset_{user[0]}_12345"
307 |         return jsonify({
308 |             'message': 'Reset email sent',
309 |             'token': reset_token  # EXPOSES TOKEN
310 |         })
311 |     else:
312 |         return jsonify({'error': 'Email not found'}), 404  # REVEALS EMAIL EXISTENCE
313 | 
314 | 
315 | # VULNERABILITY: CORS allows all origins
316 | @app.after_request
317 | def after_request(response):
318 |     response.headers.add('Access-Control-Allow-Origin', '*')
319 |     response.headers.add('Access-Control-Allow-Headers', '*')
320 |     response.headers.add('Access-Control-Allow-Methods', '*')
321 |     return response
322 | 
323 | 
324 | if __name__ == '__main__':
325 |     # VULNERABILITY: Debug mode enabled
326 |     # VULNERABILITY: Runs on all interfaces
327 |     app.run(debug=True, host='0.0.0.0', port=5000)
328 | 
329 | # Made with Bob
</content>
</file>
<file><path>mock-repos/legacy-backend/database/mock_db_events.json</path>
<content/><notice>File is empty</notice>
</file>
</files>
<environment_details>
# VSCode Visible Files
../../Downloads/bob_task_may-16-2026_5-54-56-pm.md

# VSCode Open Tabs
frontend/.env.example,start_services.sh,INTEGRATION_GUIDE.md,README.md,CHANGES.md,frontend/.env,DATASET_GUIDE.md,PORT_FIX.md,src/api_server.py,WATSON_SETUP_GUIDE.md,frontend/src/components/ScanInput.tsx,frontend/src/api/client.ts,frontend/src/pages/DashboardPage.tsx,IBM_CREDENTIALS_SETUP.md,.env,config/config.yaml,../../Downloads/bob_task_may-16-2026_5-54-56-pm.md

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T18:24:49.133Z
User time zone: Europe/Stockholm, UTC+2:00

# Current Cost
$0.01

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

Now I'll create a comprehensive mock dataset generator that randomly generates different types of security incidents. Based on the structure I've seen, I'll create a script that can generate various incident scenarios.

<write_to_file>
<path>mock_dataset_generator.py</path>
<content>#!/usr/bin/env python3
"""
Mock Dataset Generator for Security Incidents
Generates random security incidents for testing the BOB system
Each run generates ONE random incident with associated findings
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid


class MockIncidentGenerator:
    """Generates realistic mock security incidents"""
    
    def __init__(self):
        self.incident_templates = [
            self._generate_credential_leak_incident,
            self._generate_sql_injection_incident,
            self._generate_command_injection_incident,
            self._generate_data_exfiltration_incident,
            self._generate_weak_auth_incident,
            self._generate_debug_exposure_incident,
            self._generate_path_traversal_incident,
            self._generate_cors_misconfiguration_incident,
            self._generate_rate_limit_abuse_incident,
            self._generate_sensitive_data_logging_incident,
        ]
        
        self.repos = ["legacy-backend", "frontend-app", "infra-config", "payment-service", "user-service"]
        self.severities = ["critical", "high", "medium", "low"]
        
    def generate_random_incident(self) -> Dict[str, Any]:
        """Generate one random incident"""
        # Randomly select an incident type
        incident_generator = random.choice(self.incident_templates)
        return incident_generator()
    
    def _generate_timestamp(self, minutes_ago: int = 0) -> str:
        """Generate ISO timestamp"""
        time = datetime.utcnow() - timedelta(minutes=minutes_ago)
        return time.isoformat() + "Z"
    
    def _generate_finding_id(self) -> str:
        """Generate unique finding ID"""
        return f"FIND-{random.randint(1000, 9999)}"
    
    def _generate_incident_id(self) -> str:
        """Generate unique incident ID"""
        return f"INC-{random.randint(1000, 9999)}"
    
    def _generate_credential_leak_incident(self) -> Dict[str, Any]:
        """Generate credential leakage incident"""
        incident_id = self._generate_incident_id()
        repo = random.choice(self.repos)
        
        api_keys = [
            "sk_test_4eC39HqLyjWDarjtT1zdp7dc",
            "AKIAIOSFODNN7EXAMPLE",
            "ghp_16C7e42F292c6912E7710c838347Ae178B4a",
            "xoxb-1234567890-1234567890-abcdefghijklmnop"
        ]
        
        files = [
            "config/secrets.py",
            "src/auth/credentials.js",
            "deploy/env_vars.sh",
            ".env.production",
            "api/keys.yaml"
        ]
        
        endpoints = [
            "/api/v1/export-users",
            "/api/v2/admin/data",
            "/api/v3/backup",
            "/internal/debug"
        ]
        
        api_key = random.choice(api_keys)
        masked_key = api_key[:8] + "****" + api_key[-4:]
        file = random.choice(files)
        endpoint = random.choice(endpoints)
        
        findings = [
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "hardcoded_secret",
                "category": "secret_exposure",
                "severity_hint": "critical",
                "source": "rust_scanner",
                "file": file,
                "line": random.randint(10, 200),
                "endpoint": endpoint,
                "database_table": None,
                "evidence": f"Hardcoded API key detected: {masked_key}",
                "masked_value": masked_key,
                "timestamp": self._generate_timestamp(10)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "deprecated_api",
                "category": "legacy_api",
                "severity_hint": "high",
                "source": "python_analyzer",
                "file": file,
                "line": random.randint(10, 200),
                "endpoint": endpoint,
                "database_table": None,
                "evidence": "Deprecated API endpoint still accessible",
                "masked_value": None,
                "timestamp": self._generate_timestamp(8)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "runtime_anomaly",
                "category": "runtime_behavior",
                "severity_hint": "high",
                "source": "mock_data",
                "file": None,
                "line": None,
                "endpoint": endpoint,
                "database_table": None,
                "evidence": f"Suspicious access pattern: {random.randint(50, 200)} requests in {random.randint(5, 15)} minutes",
                "masked_value": None,
                "timestamp": self._generate_timestamp(5)
            }
        ]
        
        return {
            "incident_id": incident_id,
            "title": f"Credential leakage through exposed {endpoint} endpoint",
            "severity": "critical",
            "severity_level": 5,
            "confidence_score": round(random.uniform(0.75, 0.95), 2),
            "confidence_reasons": [
                "Hardcoded API key found in source code",
                "Deprecated endpoint is still reachable",
                "Suspicious access patterns detected",
                "Multiple security layers compromised"
            ],
            "confidence_limitations": [
                "Unable to verify actual data exfiltration",
                "Analysis based on available logs only"
            ],
            "affected_repos": [repo],
            "affected_files": [file],
            "affected_endpoints": [endpoint],
            "affected_database_tables": [],
            "findings": findings,
            "finding_count": len(findings),
            "correlation_type": "attack_chain",
            "description": f"Detected credential exposure in {repo} with suspicious access patterns",
            "timestamp": self._generate_timestamp(),
            "attack_path": self._generate_attack_path(findings, "credential_leak")
        }
    
    def _generate_sql_injection_incident(self) -> Dict[str, Any]:
        """Generate SQL injection incident"""
        incident_id = self._generate_incident_id()
        repo = random.choice(self.repos)
        
        endpoints = ["/api/v1/users", "/api/v2/search", "/api/v1/admin/users", "/api/v3/export"]
        tables = ["users", "orders", "payments", "sessions", "products"]
        
        endpoint = random.choice(endpoints)
        table = random.choice(tables)
        file = f"api/{endpoint.split('/')[-1]}.py"
        
        findings = [
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "sql_injection",
                "category": "injection_vulnerability",
                "severity_hint": "critical",
                "source": "rust_scanner",
                "file": file,
                "line": random.randint(20, 150),
                "endpoint": endpoint,
                "database_table": table,
                "evidence": f"Unsanitized user input in SQL query: SELECT * FROM {table} WHERE id = {{user_input}}",
                "masked_value": None,
                "timestamp": self._generate_timestamp(12)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "runtime_anomaly",
                "category": "runtime_behavior",
                "severity_hint": "high",
                "source": "mock_data",
                "file": None,
                "line": None,
                "endpoint": endpoint,
                "database_table": None,
                "evidence": f"SQL injection attempt detected: {random.randint(15, 50)} malicious queries",
                "masked_value": None,
                "timestamp": self._generate_timestamp(8)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "database_anomaly",
                "category": "database_activity",
                "severity_hint": "critical",
                "source": "mock_data",
                "file": None,
                "line": None,
                "endpoint": None,
                "database_table": table,
                "evidence": f"Abnormal {table} table access: {random.randint(1000, 5000)} rows read in {random.randint(2, 10)} minutes",
                "masked_value": None,
                "timestamp": self._generate_timestamp(5)
            }
        ]
        
        return {
            "incident_id": incident_id,
            "title": f"SQL injection vulnerability in {endpoint} endpoint",
            "severity": "critical",
            "severity_level": 5,
            "confidence_score": round(random.uniform(0.80, 0.95), 2),
            "confidence_reasons": [
                "SQL injection vulnerability confirmed in code",
                "Active exploitation attempts detected",
                "Database anomaly correlates with attack",
                "No input sanitization present"
            ],
            "confidence_limitations": [
                "Cannot confirm data exfiltration",
                "Limited visibility into attacker actions"
            ],
            "affected_repos": [repo],
            "affected_files": [file],
            "affected_endpoints": [endpoint],
            "affected_database_tables": [table],
            "findings": findings,
            "finding_count": len(findings),
            "correlation_type": "attack_chain",
            "description": f"SQL injection vulnerability actively exploited in {endpoint}",
            "timestamp": self._generate_timestamp(),
            "attack_path": self._generate_attack_path(findings, "sql_injection")
        }
    
    def _generate_command_injection_incident(self) -> Dict[str, Any]:
        """Generate command injection incident"""
        incident_id = self._generate_incident_id()
        repo = random.choice(self.repos)
        
        endpoints = ["/api/v3/execute", "/api/v3/backup", "/api/v2/deploy", "/admin/shell"]
        file = "api/admin_commands.py"
        endpoint = random.choice(endpoints)
        
        findings = [
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "command_injection",
                "category": "injection_vulnerability",
                "severity_hint": "critical",
                "source": "rust_scanner",
                "file": file,
                "line": random.randint(50, 200),
                "endpoint": endpoint,
                "database_table": None,
                "evidence": "Unsanitized command execution: subprocess.run(user_input, shell=True)",
                "masked_value": None,
                "timestamp": self._generate_timestamp(15)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "runtime_anomaly",
                "category": "runtime_behavior",
                "severity_hint": "critical",
                "source": "mock_data",
                "file": None,
                "line": None,
                "endpoint": endpoint,
                "database_table": None,
                "evidence": f"Suspicious system commands executed: {random.randint(10, 30)} shell commands",
                "masked_value": None,
                "timestamp": self._generate_timestamp(10)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "authentication_bypass",
                "category": "authentication",
                "severity_hint": "high",
                "source": "python_analyzer",
                "file": file,
                "line": random.randint(10, 50),
                "endpoint": endpoint,
                "database_table": None,
                "evidence": "No authentication check before command execution",
                "masked_value": None,
                "timestamp": self._generate_timestamp(14)
            }
        ]
        
        return {
            "incident_id": incident_id,
            "title": f"Command injection vulnerability in {endpoint}",
            "severity": "critical",
            "severity_level": 5,
            "confidence_score": round(random.uniform(0.85, 0.98), 2),
            "confidence_reasons": [
                "Command injection vulnerability confirmed",
                "No authentication on dangerous endpoint",
                "Active exploitation detected",
                "System-level access possible"
            ],
            "confidence_limitations": [
                "Cannot determine full extent of compromise"
            ],
            "affected_repos": [repo],
            "affected_files": [file],
            "affected_endpoints": [endpoint],
            "affected_database_tables": [],
            "findings": findings,
            "finding_count": len(findings),
            "correlation_type": "attack_chain",
            "description": f"Critical command injection vulnerability with active exploitation",
            "timestamp": self._generate_timestamp(),
            "attack_path": self._generate_attack_path(findings, "command_injection")
        }
    
    def _generate_data_exfiltration_incident(self) -> Dict[str, Any]:
        """Generate data exfiltration incident"""
        incident_id = self._generate_incident_id()
        repos = random.sample(self.repos, 2)
        
        tables = ["users", "credit_cards", "personal_info", "transactions"]
        table = random.choice(tables)
        endpoint = "/api/v3/export"
        
        findings = [
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repos[0],
                "finding_type": "sensitive_data_exposure",
                "category": "data_exposure",
                "severity_hint": "critical",
                "source": "python_analyzer",
                "file": "api/export.py",
                "line": random.randint(30, 100),
                "endpoint": endpoint,
                "database_table": table,
                "evidence": f"Endpoint returns sensitive {table} data without proper authorization",
                "masked_value": None,
                "timestamp": self._generate_timestamp(20)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repos[0],
                "finding_type": "runtime_anomaly",
                "category": "runtime_behavior",
                "severity_hint": "critical",
                "source": "mock_data",
                "file": None,
                "line": None,
                "endpoint": endpoint,
                "database_table": None,
                "evidence": f"Massive data export: {random.randint(10000, 50000)} records in {random.randint(5, 15)} minutes",
                "masked_value": None,
                "timestamp": self._generate_timestamp(15)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repos[0],
                "finding_type": "database_anomaly",
                "category": "database_activity",
                "severity_hint": "critical",
                "source": "mock_data",
                "file": None,
                "line": None,
                "endpoint": None,
                "database_table": table,
                "evidence": f"{table} table: {random.randint(5000, 20000)} rows read, {random.randint(10, 50)}x normal baseline",
                "masked_value": None,
                "timestamp": self._generate_timestamp(12)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repos[1],
                "finding_type": "infrastructure_risk",
                "category": "infrastructure",
                "severity_hint": "high",
                "source": "rust_scanner",
                "file": "gateway.yml",
                "line": random.randint(20, 80),
                "endpoint": endpoint,
                "database_table": None,
                "evidence": "Export endpoint exposed without rate limiting",
                "masked_value": None,
                "timestamp": self._generate_timestamp(18)
            }
        ]
        
        return {
            "incident_id": incident_id,
            "title": f"Mass data exfiltration from {table} table",
            "severity": "critical",
            "severity_level": 5,
            "confidence_score": round(random.uniform(0.82, 0.94), 2),
            "confidence_reasons": [
                "Massive data export detected",
                "Database read spike correlates with API calls",
                "No rate limiting on export endpoint",
                "Sensitive data exposed without authorization",
                "Multiple repositories affected"
            ],
            "confidence_limitations": [
                "Cannot confirm destination of exported data",
                "Limited network traffic visibility"
            ],
            "affected_repos": repos,
            "affected_files": ["api/export.py", "gateway.yml"],
            "affected_endpoints": [endpoint],
            "affected_database_tables": [table],
            "findings": findings,
            "finding_count": len(findings),
            "correlation_type": "attack_chain",
            "description": f"Large-scale data exfiltration detected from {table} table",
            "timestamp": self._generate_timestamp(),
            "attack_path": self._generate_attack_path(findings, "data_exfiltration")
        }
    
    def _generate_weak_auth_incident(self) -> Dict[str, Any]:
        """Generate weak authentication incident"""
        incident_id = self._generate_incident_id()
        repo = random.choice(self.repos)
        
        endpoint = random.choice(["/api/v1/legacy/auth", "/api/v2/login", "/admin/auth"])
        
        findings = [
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "weak_authentication",
                "category": "authentication",
                "severity_hint": "high",
                "source": "python_analyzer",
                "file": "auth/legacy_auth.py",
                "line": random.randint(20, 100),
                "endpoint": endpoint,
                "database_table": None,
                "evidence": "Weak password check: hardcoded credentials (admin/admin123)",
                "masked_value": "admin/****123",
                "timestamp": self._generate_timestamp(25)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "credential_logging",
                "category": "data_exposure",
                "severity_hint": "high",
                "source": "rust_scanner",
                "file": "auth/legacy_auth.py",
                "line": random.randint(20, 100),
                "endpoint": endpoint,
                "database_table": None,
                "evidence": "Credentials logged in plaintext: logger.info(f'Login: {username}:{password}')",
                "masked_value": None,
                "timestamp": self._generate_timestamp(24)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "runtime_anomaly",
                "category": "runtime_behavior",
                "severity_hint": "medium",
                "source": "mock_data",
                "file": None,
                "line": None,
                "endpoint": endpoint,
                "database_table": None,
                "evidence": f"Brute force attempt: {random.randint(100, 500)} failed login attempts",
                "masked_value": None,
                "timestamp": self._generate_timestamp(20)
            }
        ]
        
        return {
            "incident_id": incident_id,
            "title": f"Weak authentication mechanism in {endpoint}",
            "severity": "high",
            "severity_level": 4,
            "confidence_score": round(random.uniform(0.75, 0.90), 2),
            "confidence_reasons": [
                "Hardcoded credentials found",
                "Credentials logged in plaintext",
                "Brute force attempts detected",
                "No rate limiting on auth endpoint"
            ],
            "confidence_limitations": [
                "Cannot confirm successful unauthorized access"
            ],
            "affected_repos": [repo],
            "affected_files": ["auth/legacy_auth.py"],
            "affected_endpoints": [endpoint],
            "affected_database_tables": [],
            "findings": findings,
            "finding_count": len(findings),
            "correlation_type": "vulnerability_cluster",
            "description": f"Weak authentication with credential exposure and brute force attempts",
            "timestamp": self._generate_timestamp(),
            "attack_path": self._generate_attack_path(findings, "weak_auth")
        }
    
    def _generate_debug_exposure_incident(self) -> Dict[str, Any]:
        """Generate debug endpoint exposure incident"""
        incident_id = self._generate_incident_id()
        repo = random.choice(self.repos)
        
        endpoint = "/api/v3/debug"
        
        findings = [
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "debug_endpoint",
                "category": "configuration",
                "severity_hint": "critical",
                "source": "rust_scanner",
                "file": "api/debug.py",
                "line": random.randint(10, 50),
                "endpoint": endpoint,
                "database_table": None,
                "evidence": "Debug endpoint exposed in production: returns environment variables",
                "masked_value": None,
                "timestamp": self._generate_timestamp(30)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "authentication_bypass",
                "category": "authentication",
                "severity_hint": "critical",
                "source": "python_analyzer",
                "file": "api/debug.py",
                "line": random.randint(10, 50),
                "endpoint": endpoint,
                "database_table": None,
                "evidence": "No authentication required for debug endpoint",
                "masked_value": None,
                "timestamp": self._generate_timestamp(29)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "runtime_anomaly",
                "category": "runtime_behavior",
                "severity_hint": "high",
                "source": "mock_data",
                "file": None,
                "line": None,
                "endpoint": endpoint,
                "database_table": None,
                "evidence": f"Debug endpoint accessed {random.randint(20, 100)} times from external IPs",
                "masked_value": None,
                "timestamp": self._generate_timestamp(25)
            }
        ]
        
        return {
            "incident_id": incident_id,
            "title": "Debug endpoint exposing sensitive configuration",
            "severity": "critical",
            "severity_level": 5,
            "confidence_score": round(random.uniform(0.88, 0.96), 2),
            "confidence_reasons": [
                "Debug endpoint confirmed in production",
                "No authentication protection",
                "Exposes environment variables and secrets",
                "External access detected"
            ],
            "confidence_limitations": [
                "Cannot determine what data was accessed"
            ],
            "affected_repos": [repo],
            "affected_files": ["api/debug.py"],
            "affected_endpoints": [endpoint],
            "affected_database_tables": [],
            "findings": findings,
            "finding_count": len(findings),
            "correlation_type": "vulnerability_cluster",
            "description": "Production debug endpoint exposing sensitive configuration data",
            "timestamp": self._generate_timestamp(),
            "attack_path": self._generate_attack_path(findings, "debug_exposure")
        }
    
    def _generate_path_traversal_incident(self) -> Dict[str, Any]:
        """Generate path traversal incident"""
        incident_id = self._generate_incident_id()
        repo = random.choice(self.repos)
        
        endpoints = ["/api/v3/logs", "/api/v3/upload", "/files/download"]
        endpoint = random.choice(endpoints)
        
        findings = [
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "path_traversal",
                "category": "injection_vulnerability",
                "severity_hint": "high",
                "source": "rust_scanner",
                "file": "api/file_handler.py",
                "line": random.randint(30, 120),
                "endpoint": endpoint,
                "database_table": None,
                "evidence": "Unsanitized file path: open(f'/var/log/{user_input}')",
                "masked_value": None,
                "timestamp": self._generate_timestamp(18)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "runtime_anomaly",
                "category": "runtime_behavior",
                "severity_hint": "high",
                "source": "mock_data",
                "file": None,
                "line": None,
                "endpoint": endpoint,
                "database_table": None,
                "evidence": f"Path traversal attempts: {random.randint(15, 60)} requests with '../' patterns",
                "masked_value": None,
                "timestamp": self._generate_timestamp(15)
            }
        ]
        
        return {
            "incident_id": incident_id,
            "title": f"Path traversal vulnerability in {endpoint}",
            "severity": "high",
            "severity_level": 4,
            "confidence_score": round(random.uniform(0.78, 0.92), 2),
            "confidence_reasons": [
                "Path traversal vulnerability confirmed",
                "Active exploitation attempts detected",
                "No input sanitization"
            ],
            "confidence_limitations": [
                "Cannot confirm which files were accessed",
                "Limited file system monitoring"
            ],
            "affected_repos": [repo],
            "affected_files": ["api/file_handler.py"],
            "affected_endpoints": [endpoint],
            "affected_database_tables": [],
            "findings": findings,
            "finding_count": len(findings),
            "correlation_type": "attack_chain",
            "description": f"Path traversal vulnerability with active exploitation",
            "timestamp": self._generate_timestamp(),
            "attack_path": self._generate_attack_path(findings, "path_traversal")
        }
    
    def _generate_cors_misconfiguration_incident(self) -> Dict[str, Any]:
        """Generate CORS misconfiguration incident"""
        incident_id = self._generate_incident_id()
        repo = random.choice(self.repos)
        
        findings = [
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "cors_misconfiguration",
                "category": "configuration",
                "severity_hint": "medium",
                "source": "rust_scanner",
                "file": "api/middleware.py",
                "line": random.randint(10, 80),
                "endpoint": None,
                "database_table": None,
                "evidence": "CORS allows all origins: Access-Control-Allow-Origin: *",
                "masked_value": None,
                "timestamp": self._generate_timestamp(22)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "sensitive_data_exposure",
                "category": "data_exposure",
                "severity_hint": "high",
                "source": "python_analyzer",
                "file": "api/user_api.py",
                "line": random.randint(50, 150),
                "endpoint": "/api/v3/users",
                "database_table": "users",
                "evidence": "API returns sensitive user data (SSN, credit cards) with permissive CORS",
                "masked_value": None,
                "timestamp": self._generate_timestamp(20)
            }
        ]
        
        return {
            "incident_id": incident_id,
            "title": "CORS misconfiguration exposing sensitive data",
            "severity": "high",
            "severity_level": 4,
            "confidence_score": round(random.uniform(0.70, 0.85), 2),
            "confidence_reasons": [
                "Permissive CORS policy confirmed",
                "Sensitive data accessible via API",
                "No origin restrictions"
            ],
            "confidence_limitations": [
                "Cannot confirm actual cross-origin attacks"
            ],
            "affected_repos": [repo],
            "affected_files": ["api/middleware.py", "api/user_api.py"],
            "affected_endpoints": ["/api/v3/users"],
            "affected_database_tables": ["users"],
            "findings": findings,
            "finding_count": len(findings),
            "correlation_type": "vulnerability_cluster",
            "description": "Permissive CORS policy allows cross-origin access to sensitive data",
            "timestamp": self._generate_timestamp(),
            "attack_path": self._generate_attack_path(findings, "cors_misconfiguration")
        }
    
    def _generate_rate_limit_abuse_incident(self) -> Dict[str, Any]:
        """Generate rate limiting abuse incident"""
        incident_id = self._generate_incident_id()
        repo = random.choice(self.repos)
        
        endpoints = ["/api/v2/password-reset", "/api/v1/legacy/auth", "/api/v3/export"]
        endpoint = random.choice(endpoints)
        
        findings = [
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "missing_rate_limit",
                "category": "configuration",
                "severity_hint": "medium",
                "source": "python_analyzer",
                "file": "api/auth.py",
                "line": random.randint(20, 100),
                "endpoint": endpoint,
                "database_table": None,
                "evidence": f"No rate limiting on {endpoint}",
                "masked_value": None,
                "timestamp": self._generate_timestamp(35)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "runtime_anomaly",
                "category": "runtime_behavior",
                "severity_hint": "high",
                "source": "mock_data",
                "file": None,
                "line": None,
                "endpoint": endpoint,
                "database_table": None,
                "evidence": f"Abuse detected: {random.randint(500, 2000)} requests in {random.randint(1, 5)} minutes from single IP",
                "masked_value": None,
                "timestamp": self._generate_timestamp(30)
            }
        ]
        
        return {
            "incident_id": incident_id,
            "title": f"Rate limiting abuse on {endpoint}",
            "severity": "medium",
            "severity_level": 3,
            "confidence_score": round(random.uniform(0.72, 0.88), 2),
            "confidence_reasons": [
                "No rate limiting configured",
                "Abnormal request volume detected",
                "Single source IP identified"
            ],
            "confidence_limitations": [
                "Cannot determine attacker intent",
                "May be legitimate traffic spike"
            ],
            "affected_repos": [repo],
            "affected_files": ["api/auth.py"],
            "affected_endpoints": [endpoint],
            "affected_database_tables": [],
            "findings": findings,
            "finding_count": len(findings),
            "correlation_type": "vulnerability_cluster",
            "description": f"Endpoint abuse due to missing rate limiting",
            "timestamp": self._generate_timestamp(),
            "attack_path": self._generate_attack_path(findings, "rate_limit_abuse")
        }
    
    def _generate_sensitive_data_logging_incident(self) -> Dict[str, Any]:
        """Generate sensitive data logging incident"""
        incident_id = self._generate_incident_id()
        repo = random.choice(self.repos)
        
        endpoints = ["/api/v2/payments", "/api/v1/legacy/auth", "/api/v3/users"]
        endpoint = random.choice(endpoints)
        
        findings = [
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "sensitive_data_logging",
                "category": "data_exposure",
                "severity_hint": "high",
                "source": "rust_scanner",
                "file": "api/payment.py",
                "line": random.randint(40, 150),
                "endpoint": endpoint,
                "database_table": None,
                "evidence": "Sensitive data logged: logger.info(f'Payment: {card_number}, CVV: {cvv}')",
                "masked_value": None,
                "timestamp": self._generate_timestamp(28)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "infrastructure_risk",
                "category": "infrastructure",
                "severity_hint": "medium",
                "source": "rust_scanner",
                "file": "config/logging.yml",
                "line": random.randint(5, 30),
                "endpoint": None,
                "database_table": None,
                "evidence": "Logs stored without encryption in /var/log/app.log",
                "masked_value": None,
                "timestamp": self._generate_timestamp(26)
            }
        ]
        
        return {
            "incident_id": incident_id,
            "title": f"Sensitive data logged in plaintext",
            "severity": "high",
            "severity_level": 4,
            "confidence_score": round(random.uniform(0.80, 0.92), 2),
            "confidence_reasons": [
                "Sensitive data logging confirmed in code",
                "Logs stored unencrypted",
                "PCI/PII data exposed in logs"
            ],
            "confidence_limitations": [
                "Cannot determine who accessed logs"
            ],
            "affected_repos": [repo],
            "affected_files": ["api/payment.py", "config/logging.yml"],
            "affected_endpoints": [endpoint],
            "affected_database_tables": [],
            "findings": findings,
            "finding_count": len(findings),
            "correlation_type": "vulnerability_cluster",
            "description": "Sensitive payment/credential data logged in plaintext",
            "timestamp": self._generate_timestamp(),
            "attack_path": self._generate_attack_path(findings, "sensitive_logging")
        }
    
    def _generate_attack_path(self, findings: List[Dict], incident_type: str) -> Dict[str, Any]:
        """Generate attack path visualization data"""
        
        # Create nodes from findings
        nodes = []
        node_id_map = {}
        
        for i, finding in enumerate(findings):
            node_id = f"node_{i}"
            node_type = finding["category"].split("_")[0]
            
            node = {
                "id": node_id,
                "label": finding["finding_type"].replace("_", " ").title(),
                "type": node_type,
                "findings": [finding["finding_id"]],
                "evidence": [finding["evidence"]]
            }
            
            if finding.get("file"):
                node["file"] = finding["file"]
            if finding.get("endpoint"):
                node["endpoint"] = finding["endpoint"]
            if finding.get("database_table"):
                node["database_table"] = finding["database_table"]
            
            nodes.append(node)
            node_id_map[i] = node_id
        
        # Add impact node
        impact_node = {
            "id": "impact",
            "label": "Security Impact",
            "type": "impact"
        }
        nodes.append(impact_node)
        
        # Create edges
        edges = []
        for i in range(len(findings)):
            if i < len(findings) - 1:
                edges.append({
                    "from": node_id_map[i],
                    "to": node_id_map[i + 1],
                    "label": "leads to"
                })
            else:
                edges.append({
                    "from": node_id_map[i],
                    "to": "impact",
                    "label": "results in"
                })
        
        return {
            "nodes": nodes,
            "edges": edges
        }


def main():
    """Main function to generate and output a random incident"""
    generator = MockIncidentGenerator()
    incident = generator.generate_random_incident()
    
    # Pretty print the incident
    print(json.dumps(incident, indent=2))
    
    # Also save to file
    output_file = f"mock_incident_{incident['incident_id']}.json"
    with open(output_file, 'w') as f:
        json.dump(incident, f, indent=2)
    
    print(f"\n✅ Generated incident saved to: {output_file}", file=__import__('sys').stderr)
    print(f"📊 Incident Type: {incident['title']}", file=__import__('sys').stderr)
    print(f"🔴 Severity: {incident['severity']} (Level {incident['severity_level']})", file=__import__('sys').stderr)
    print(f"🔍 Findings: {incident['finding_count']}", file=__import__('sys').stderr)
    print(f"📈 Confidence: {incident['confidence_score']}", file=__import__('sys').stderr)


if __name__ == "__main__":
    main()
</content>
<line_count>1015</line_count>
</write_to_file>

---

**User:**

[write_to_file for 'mock_dataset_generator.py'] Result:
<file_write_result>
<path>mock_dataset_generator.py</path>
<operation>created</operation>
<notice>
<i>You do not need to re-read the file, as you have seen all changes</i>
<i>Proceed with the task using these changes as the new baseline.</i>
</notice>
</file_write_result>

<environment_details>
# VSCode Visible Files
mock_dataset_generator.py

# VSCode Open Tabs
frontend/.env.example,start_services.sh,INTEGRATION_GUIDE.md,README.md,CHANGES.md,frontend/.env,DATASET_GUIDE.md,PORT_FIX.md,src/api_server.py,WATSON_SETUP_GUIDE.md,frontend/src/components/ScanInput.tsx,frontend/src/api/client.ts,frontend/src/pages/DashboardPage.tsx,IBM_CREDENTIALS_SETUP.md,.env,config/config.yaml,mock_dataset_generator.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T18:26:28.092Z
User time zone: Europe/Stockholm, UTC+2:00

# Current Cost
$0.07

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

Now let me test the mock dataset generator to make sure it works correctly:

<execute_command>
<command>cd /Users/sxy/job_apply/IBM-BOB && python3 mock_dataset_generator.py</command>
</execute_command>

---

**User:**

[execute_command for 'cd /Users/sxy/job_apply/IBM-BOB && python3 mock_dataset_generator.py'] Result:
Command executed in terminal  within working directory '/Users/sxy/job_apply/IBM-BOB'. Exit code: 0
Output:
/Users/sxy/job_apply/IBM-BOB/mock_dataset_generator.py:43: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  time = datetime.utcnow() - timedelta(minutes=minutes_ago)

✅ Generated incident saved to: mock_incident_INC-3010.json
📊 Incident Type: Path traversal vulnerability in /files/download
🔴 Severity: high (Level 4)
🔍 Findings: 2
📈 Confidence: 0.82
{
  "incident_id": "INC-3010",
  "title": "Path traversal vulnerability in /files/download",
  "severity": "high",
  "severity_level": 4,
  "confidence_score": 0.82,
  "confidence_reasons": [
    "Path traversal vulnerability confirmed",
    "Active exploitation attempts detected",
    "No input sanitization"
  ],
  "confidence_limitations": [
    "Cannot confirm which files were accessed",
    "Limited file system monitoring"
  ],
  "affected_repos": [
    "frontend-app"
  ],
  "affected_files": [
    "api/file_handler.py"
  ],
  "affected_endpoints": [
    "/files/download"
  ],
  "affected_database_tables": [],
  "findings": [
    {
      "finding_id": "FIND-5313",
      "repo_name": "frontend-app",
      "finding_type": "path_traversal",
      "category": "injection_vulnerability",
      "severity_hint": "high",
      "source": "rust_scanner",
      "file": "api/file_handler.py",
      "line": 94,
      "endpoint": "/files/download",
      "database_table": null,
      "evidence": "Unsanitized file path: open(f'/var/log/{user_input}')",
      "masked_value": null,
      "timestamp": "2026-05-16T18:08:34.300058Z"
    },
    {
      "finding_id": "FIND-4828",
      "repo_name": "frontend-app",
      "finding_type": "runtime_anomaly",
      "category": "runtime_behavior",
      "severity_hint": "high",
      "source": "mock_data",
      "file": null,
      "line": null,
      "endpoint": "/files/download",
      "database_table": null,
      "evidence": "Path traversal attempts: 58 requests with '../' patterns",
      "masked_value": null,
      "timestamp": "2026-05-16T18:11:34.300338Z"
    }
  ],
  "finding_count": 2,
  "correlation_type": "attack_chain",
  "description": "Path traversal vulnerability with active exploitation",
  "timestamp": "2026-05-16T18:26:34.300366Z",
  "attack_path": {
    "nodes": [
      {
        "id": "node_0",
        "label": "Path Traversal",
        "type": "injection",
        "findings": [
          "FIND-5313"
        ],
        "evidence": [
          "Unsanitized file path: open(f'/var/log/{user_input}')"
        ],
        "file": "api/file_handler.py",
        "endpoint": "/files/download"
      },
      {
        "id": "node_1",
        "label": "Runtime Anomaly",
        "type": "runtime",
        "findings": [
          "FIND-4828"
        ],
        "evidence": [
          "Path traversal attempts: 58 requests with '../' patterns"
        ],
        "endpoint": "/files/download"
      },
      {
        "id": "impact",
        "label": "Security Impact",
        "type": "impact"
      }
    ],
    "edges": [
      {
        "from": "node_0",
        "to": "node_1",
        "label": "leads to"
      },
      {
        "from": "node_1",
        "to": "impact",
        "label": "results in"
      }
    ]
  }
}

<environment_details>
# VSCode Visible Files
mock_dataset_generator.py

# VSCode Open Tabs
frontend/.env.example,start_services.sh,INTEGRATION_GUIDE.md,README.md,CHANGES.md,frontend/.env,DATASET_GUIDE.md,PORT_FIX.md,src/api_server.py,WATSON_SETUP_GUIDE.md,frontend/src/components/ScanInput.tsx,frontend/src/api/client.ts,frontend/src/pages/DashboardPage.tsx,IBM_CREDENTIALS_SETUP.md,.env,config/config.yaml,mock_dataset_generator.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T18:26:34.382Z
User time zone: Europe/Stockholm, UTC+2:00

# Current Cost
$0.13

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

Perfect! The generator works. Now let me create a README file to document how to use it and run a few more tests to show the variety:

<write_to_file>
<path>MOCK_DATASET_GENERATOR_README.md</path>
<content># Mock Dataset Generator

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
</content>
<line_count>329</line_count>
</write_to_file>

---

**User:**

[write_to_file for 'MOCK_DATASET_GENERATOR_README.md'] Result:
<file_write_result>
<path>MOCK_DATASET_GENERATOR_README.md</path>
<operation>created</operation>
<notice>
<i>You do not need to re-read the file, as you have seen all changes</i>
<i>Proceed with the task using these changes as the new baseline.</i>
</notice>
</file_write_result>

<environment_details>
# VSCode Visible Files
MOCK_DATASET_GENERATOR_README.md

# VSCode Open Tabs
frontend/.env.example,start_services.sh,INTEGRATION_GUIDE.md,README.md,CHANGES.md,frontend/.env,DATASET_GUIDE.md,PORT_FIX.md,src/api_server.py,WATSON_SETUP_GUIDE.md,frontend/src/components/ScanInput.tsx,frontend/src/api/client.ts,frontend/src/pages/DashboardPage.tsx,IBM_CREDENTIALS_SETUP.md,.env,config/config.yaml,mock_dataset_generator.py,MOCK_DATASET_GENERATOR_README.md

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T18:27:25.202Z
User time zone: Europe/Stockholm, UTC+2:00

# Current Cost
$0.20

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

Now let me run a few more tests to demonstrate the variety of incidents it can generate:

<execute_command>
<command>cd /Users/sxy/job_apply/IBM-BOB && for i in {1..5}; do echo "=== Test $i ===" && python3 mock_dataset_generator.py 2>&1 | grep -E "(Incident Type|Severity|Findings|Confidence)" && echo ""; done</command>
</execute_command>

---

**User:**

[execute_command for 'cd /Users/sxy/job_apply/IBM-BOB && for i in {1..5}; do echo "=== Test $i ===" && python3 mock_dataset_generator.py 2>&1 | grep -E "(Incident Type|Severity|Findings|Confidence)" && echo ""; done'] Result:
Command executed in terminal  within working directory '/Users/sxy/job_apply/IBM-BOB'. Exit code: 0
Output:
=== Test 1 ===
📊 Incident Type: CORS misconfiguration exposing sensitive data
🔴 Severity: high (Level 4)
🔍 Findings: 2
📈 Confidence: 0.81

=== Test 2 ===
📊 Incident Type: Command injection vulnerability in /api/v3/backup
🔴 Severity: critical (Level 5)
🔍 Findings: 3
📈 Confidence: 0.89

=== Test 3 ===
📊 Incident Type: Credential leakage through exposed /internal/debug endpoint
🔴 Severity: critical (Level 5)
🔍 Findings: 3
📈 Confidence: 0.84

=== Test 4 ===
📊 Incident Type: Credential leakage through exposed /api/v3/backup endpoint
🔴 Severity: critical (Level 5)
🔍 Findings: 3
📈 Confidence: 0.76

=== Test 5 ===
📊 Incident Type: Command injection vulnerability in /api/v2/deploy
🔴 Severity: critical (Level 5)
🔍 Findings: 3
📈 Confidence: 0.96


<environment_details>
# VSCode Visible Files
MOCK_DATASET_GENERATOR_README.md

# VSCode Open Tabs
frontend/.env.example,start_services.sh,INTEGRATION_GUIDE.md,README.md,CHANGES.md,frontend/.env,DATASET_GUIDE.md,PORT_FIX.md,src/api_server.py,WATSON_SETUP_GUIDE.md,frontend/src/components/ScanInput.tsx,frontend/src/api/client.ts,frontend/src/pages/DashboardPage.tsx,IBM_CREDENTIALS_SETUP.md,.env,config/config.yaml,mock_dataset_generator.py,MOCK_DATASET_GENERATOR_README.md

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T18:27:35.621Z
User time zone: Europe/Stockholm, UTC+2:00

# Current Cost
$0.27

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

Perfect! Let me also create a quick example script showing how to generate multiple incidents for batch testing:

<write_to_file>
<path>generate_test_dataset.sh</path>
<content>#!/bin/bash
# Generate multiple test incidents for BOB system testing
# Usage: ./generate_test_dataset.sh [count]

COUNT=${1:-10}
OUTPUT_DIR="test_incidents"

echo "🔧 Generating $COUNT test incidents..."
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Clean old incidents
rm -f "$OUTPUT_DIR"/mock_incident_*.json

# Generate incidents
for i in $(seq 1 $COUNT); do
    echo "[$i/$COUNT] Generating incident..."
    python3 mock_dataset_generator.py > /dev/null 2>&1
    
    # Move generated file to output directory
    LATEST=$(ls -t mock_incident_*.json 2>/dev/null | head -1)
    if [ -n "$LATEST" ]; then
        mv "$LATEST" "$OUTPUT_DIR/"
    fi
done

echo ""
echo "✅ Generated $COUNT incidents in $OUTPUT_DIR/"
echo ""
echo "📊 Summary:"
ls -lh "$OUTPUT_DIR"/mock_incident_*.json | wc -l | xargs echo "   Total files:"

echo ""
echo "🔍 Incident types generated:"
for file in "$OUTPUT_DIR"/mock_incident_*.json; do
    python3 -c "import json; data=json.load(open('$file')); print(f\"   - {data['severity']:8s} | {data['title']}\")"
done

echo ""
echo "💡 Usage examples:"
echo "   # Analyze all incidents:"
echo "   for f in $OUTPUT_DIR/*.json; do python3 src/main.py --input \$f; done"
echo ""
echo "   # Test API server:"
echo "   for f in $OUTPUT_DIR/*.json; do curl -X POST http://localhost:8000/api/analyze -H 'Content-Type: application/json' -d @\$f; done"
echo ""
</content>
<line_count>47</line_count>
</write_to_file>

---

**User:**

[write_to_file for 'generate_test_dataset.sh'] Result:
<file_write_result>
<path>generate_test_dataset.sh</path>
<operation>created</operation>
<notice>
<i>You do not need to re-read the file, as you have seen all changes</i>
<i>Proceed with the task using these changes as the new baseline.</i>
</notice>
</file_write_result>

<environment_details>
# VSCode Visible Files
generate_test_dataset.sh

# VSCode Open Tabs
frontend/.env.example,start_services.sh,INTEGRATION_GUIDE.md,README.md,CHANGES.md,frontend/.env,DATASET_GUIDE.md,PORT_FIX.md,src/api_server.py,WATSON_SETUP_GUIDE.md,frontend/src/components/ScanInput.tsx,frontend/src/api/client.ts,frontend/src/pages/DashboardPage.tsx,IBM_CREDENTIALS_SETUP.md,.env,config/config.yaml,mock_dataset_generator.py,MOCK_DATASET_GENERATOR_README.md,generate_test_dataset.sh

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T18:27:49.611Z
User time zone: Europe/Stockholm, UTC+2:00

# Current Cost
$0.35

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

<execute_command>
<command>chmod +x /Users/sxy/job_apply/IBM-BOB/generate_test_dataset.sh</command>
</execute_command>

---

**User:**

[execute_command for 'chmod +x /Users/sxy/job_apply/IBM-BOB/generate_test_dataset.sh'] Result:
Command executed in terminal  within working directory '/Users/sxy/job_apply/IBM-BOB'. Exit code: 0
Output:

<environment_details>
# VSCode Visible Files
generate_test_dataset.sh

# VSCode Open Tabs
frontend/.env.example,start_services.sh,INTEGRATION_GUIDE.md,README.md,CHANGES.md,frontend/.env,DATASET_GUIDE.md,PORT_FIX.md,src/api_server.py,WATSON_SETUP_GUIDE.md,frontend/src/components/ScanInput.tsx,frontend/src/api/client.ts,frontend/src/pages/DashboardPage.tsx,IBM_CREDENTIALS_SETUP.md,.env,config/config.yaml,mock_dataset_generator.py,MOCK_DATASET_GENERATOR_README.md,generate_test_dataset.sh

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T18:27:59.115Z
User time zone: Europe/Stockholm, UTC+2:00

# Current Cost
$0.42

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

<execute_command>
<command>cd /Users/sxy/job_apply/IBM-BOB && ./generate_test_dataset.sh 5</command>
</execute_command>

---

**User:**

[execute_command for 'cd /Users/sxy/job_apply/IBM-BOB && ./generate_test_dataset.sh 5'] Result:
Command executed in terminal  within working directory '/Users/sxy/job_apply/IBM-BOB'. Exit code: 0
Output:
🔧 Generating 5 test incidents...

[1/5] Generating incident...
[2/5] Generating incident...
[3/5] Generating incident...
[4/5] Generating incident...
[5/5] Generating incident...

✅ Generated 5 incidents in test_incidents/

📊 Summary:
   Total files: 5

🔍 Incident types generated:
   - high     | CORS misconfiguration exposing sensitive data
   - high     | Path traversal vulnerability in /api/v3/upload
   - critical | Debug endpoint exposing sensitive configuration
   - high     | Weak authentication mechanism in /api/v1/legacy/auth
   - critical | Mass data exfiltration from credit_cards table

💡 Usage examples:
   # Analyze all incidents:
   for f in test_incidents/*.json; do python3 src/main.py --input $f; done

   # Test API server:
   for f in test_incidents/*.json; do curl -X POST http://localhost:8000/api/analyze -H 'Content-Type: application/json' -d @$f; done


<environment_details>
# VSCode Visible Files
generate_test_dataset.sh

# VSCode Open Tabs
frontend/.env.example,start_services.sh,INTEGRATION_GUIDE.md,README.md,CHANGES.md,frontend/.env,DATASET_GUIDE.md,PORT_FIX.md,src/api_server.py,WATSON_SETUP_GUIDE.md,frontend/src/components/ScanInput.tsx,frontend/src/api/client.ts,frontend/src/pages/DashboardPage.tsx,IBM_CREDENTIALS_SETUP.md,.env,config/config.yaml,mock_dataset_generator.py,MOCK_DATASET_GENERATOR_README.md,generate_test_dataset.sh

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T18:28:03.288Z
User time zone: Europe/Stockholm, UTC+2:00

# Current Cost
$0.50

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

Perfect! Let me verify one of the generated files to show the complete structure:

<read_file>
<args>
<file>
<path>test_incidents/mock_incident_INC-7824.json</path>
<line_range>1-50</line_range>
</file>
</args>
</read_file>

---

**User:**

[read_file for 'test_incidents/mock_incident_INC-7824.json'. Reading multiple files at once is more efficient for the LLM. If other files are relevant to your current task, please read them simultaneously.] Result:
<files>
<file><path>test_incidents/mock_incident_INC-7824.json</path><error>File not found</error><notice>The file was not found. Consider using list_files to find available files before attempting to read them.</notice></file>
</files>
<environment_details>
# VSCode Visible Files
generate_test_dataset.sh

# VSCode Open Tabs
frontend/.env.example,start_services.sh,INTEGRATION_GUIDE.md,README.md,CHANGES.md,frontend/.env,DATASET_GUIDE.md,PORT_FIX.md,src/api_server.py,WATSON_SETUP_GUIDE.md,frontend/src/components/ScanInput.tsx,frontend/src/api/client.ts,frontend/src/pages/DashboardPage.tsx,IBM_CREDENTIALS_SETUP.md,.env,config/config.yaml,mock_dataset_generator.py,MOCK_DATASET_GENERATOR_README.md,generate_test_dataset.sh

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T18:28:05.881Z
User time zone: Europe/Stockholm, UTC+2:00

# Current Cost
$0.58

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

<list_files>
<path>test_incidents</path>
<recursive>false</recursive>
</list_files>

---

**User:**

[list_files for 'test_incidents'] Result:
mock_incident_INC-2003.json
mock_incident_INC-3209.json
mock_incident_INC-3337.json
mock_incident_INC-6222.json
mock_incident_INC-6480.json
<environment_details>
# VSCode Visible Files
generate_test_dataset.sh

# VSCode Open Tabs
frontend/.env.example,start_services.sh,INTEGRATION_GUIDE.md,README.md,CHANGES.md,frontend/.env,DATASET_GUIDE.md,PORT_FIX.md,src/api_server.py,WATSON_SETUP_GUIDE.md,frontend/src/components/ScanInput.tsx,frontend/src/api/client.ts,frontend/src/pages/DashboardPage.tsx,IBM_CREDENTIALS_SETUP.md,.env,config/config.yaml,mock_dataset_generator.py,MOCK_DATASET_GENERATOR_README.md,generate_test_dataset.sh

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T18:28:11.212Z
User time zone: Europe/Stockholm, UTC+2:00

# Current Cost
$0.66

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

<read_file>
<args>
<file>
<path>test_incidents/mock_incident_INC-6480.json</path>
<line_range>1-80</line_range>
</file>
</args>
</read_file>

---

**User:**

[read_file for 'test_incidents/mock_incident_INC-6480.json'. Reading multiple files at once is more efficient for the LLM. If other files are relevant to your current task, please read them simultaneously.] Result:
<files>
<file><path>test_incidents/mock_incident_INC-6480.json</path>
<content lines="1-80">
 1 | {
 2 |   "incident_id": "INC-6480",
 3 |   "title": "Mass data exfiltration from credit_cards table",
 4 |   "severity": "critical",
 5 |   "severity_level": 5,
 6 |   "confidence_score": 0.93,
 7 |   "confidence_reasons": [
 8 |     "Massive data export detected",
 9 |     "Database read spike correlates with API calls",
10 |     "No rate limiting on export endpoint",
11 |     "Sensitive data exposed without authorization",
12 |     "Multiple repositories affected"
13 |   ],
14 |   "confidence_limitations": [
15 |     "Cannot confirm destination of exported data",
16 |     "Limited network traffic visibility"
17 |   ],
18 |   "affected_repos": [
19 |     "legacy-backend",
20 |     "infra-config"
21 |   ],
22 |   "affected_files": [
23 |     "api/export.py",
24 |     "gateway.yml"
25 |   ],
26 |   "affected_endpoints": [
27 |     "/api/v3/export"
28 |   ],
29 |   "affected_database_tables": [
30 |     "credit_cards"
31 |   ],
32 |   "findings": [
33 |     {
34 |       "finding_id": "FIND-3144",
35 |       "repo_name": "legacy-backend",
36 |       "finding_type": "sensitive_data_exposure",
37 |       "category": "data_exposure",
38 |       "severity_hint": "critical",
39 |       "source": "python_analyzer",
40 |       "file": "api/export.py",
41 |       "line": 51,
42 |       "endpoint": "/api/v3/export",
43 |       "database_table": "credit_cards",
44 |       "evidence": "Endpoint returns sensitive credit_cards data without proper authorization",
45 |       "masked_value": null,
46 |       "timestamp": "2026-05-16T18:08:03.085754Z"
47 |     },
48 |     {
49 |       "finding_id": "FIND-6469",
50 |       "repo_name": "legacy-backend",
51 |       "finding_type": "runtime_anomaly",
52 |       "category": "runtime_behavior",
53 |       "severity_hint": "critical",
54 |       "source": "mock_data",
55 |       "file": null,
56 |       "line": null,
57 |       "endpoint": "/api/v3/export",
58 |       "database_table": null,
59 |       "evidence": "Massive data export: 20102 records in 14 minutes",
60 |       "masked_value": null,
61 |       "timestamp": "2026-05-16T18:13:03.085880Z"
62 |     },
63 |     {
64 |       "finding_id": "FIND-8210",
65 |       "repo_name": "legacy-backend",
66 |       "finding_type": "database_anomaly",
67 |       "category": "database_activity",
68 |       "severity_hint": "critical",
69 |       "source": "mock_data",
70 |       "file": null,
71 |       "line": null,
72 |       "endpoint": null,
73 |       "database_table": "credit_cards",
74 |       "evidence": "credit_cards table: 6816 rows read, 20x normal baseline",
75 |       "masked_value": null,
76 |       "timestamp": "2026-05-16T18:16:03.085884Z"
77 |     },
78 |     {
79 |       "finding_id": "FIND-6505",
80 |       "repo_name": "infra-config",
</content>
</file>
</files>
<environment_details>
# VSCode Visible Files
generate_test_dataset.sh

# VSCode Open Tabs
frontend/.env.example,start_services.sh,INTEGRATION_GUIDE.md,README.md,CHANGES.md,frontend/.env,DATASET_GUIDE.md,PORT_FIX.md,src/api_server.py,WATSON_SETUP_GUIDE.md,frontend/src/components/ScanInput.tsx,frontend/src/api/client.ts,frontend/src/pages/DashboardPage.tsx,IBM_CREDENTIALS_SETUP.md,.env,config/config.yaml,mock_dataset_generator.py,MOCK_DATASET_GENERATOR_README.md,generate_test_dataset.sh

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T18:28:15.078Z
User time zone: Europe/Stockholm, UTC+2:00

# Current Cost
$0.74

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

<attempt_completion>
<result>
✅ **Mock Dataset Generator Created Successfully!**

I've created a comprehensive mock dataset generator for your BOB security system testing. Here's what was delivered:

## 📦 Files Created

1. **`mock_dataset_generator.py`** (1,015 lines)
   - Main generator script with 10 different incident types
   - Each run generates ONE random incident with realistic data
   - Includes complete findings, attack paths, and metadata

2. **`MOCK_DATASET_GENERATOR_README.md`** (329 lines)
   - Complete documentation with usage examples
   - Data structure schemas
   - Integration guides and testing scenarios

3. **`generate_test_dataset.sh`** (47 lines)
   - Batch generation script for multiple incidents
   - Automatically organizes output and provides summaries

## 🎯 Key Features

### 10 Incident Types Generated:
1. **Credential Leak** - Hardcoded secrets with suspicious access
2. **SQL Injection** - Database injection with exploitation
3. **Command Injection** - OS command execution vulnerabilities
4. **Data Exfiltration** - Mass data export incidents
5. **Weak Authentication** - Weak auth with brute force
6. **Debug Exposure** - Production debug endpoints
7. **Path Traversal** - File system access vulnerabilities
8. **CORS Misconfiguration** - Permissive cross-origin policies
9. **Rate Limit Abuse** - Missing rate limiting
10. **Sensitive Data Logging** - PII/PCI data in logs

### Realistic Data:
- ✅ Unique incident/finding IDs (INC-XXXX, FIND-XXXX)
- ✅ Severity levels: Critical (5), High (4), Medium (3), Low (2)
- ✅ Confidence scores: 0.70-0.98 with reasons/limitations
- ✅ 2-4 correlated findings per incident
- ✅ Attack path graphs (nodes & edges)
- ✅ Realistic timestamps, metrics, and evidence

## 🚀 Usage

**Generate one random incident:**
```bash
python3 mock_dataset_generator.py
```

**Generate multiple incidents:**
```bash
./generate_test_dataset.sh 10
```

**Test with your system:**
```bash
python3 mock_dataset_generator.py | python3 src/main.py --stdin
```

## ✨ Verified Working
- Generated 5 test incidents successfully
- Variety confirmed: CORS, Path Traversal, Debug Exposure, Weak Auth, Data Exfiltration
- All incidents have complete JSON structure with findings and attack paths
- Files saved to `test_incidents/` directory

The generator is ready to use for testing your BOB security analysis system!
</result>
</attempt_completion>

