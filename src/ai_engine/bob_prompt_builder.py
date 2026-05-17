from __future__ import annotations

import json
from typing import Any


def build_bob_prompt(
    incident: dict[str, Any],
    related_memory: list[dict[str, Any]] | None = None,
) -> str:
    related_memory = related_memory or []

    return f"""
You are IBM Bob, powered by IBM watsonx.ai, acting as the reasoning engine for Bob Sentinel.

Bob Sentinel is an agentic DevSecOps security assistant.
The scanner/backend already detected and correlated evidence.
Your job is to analyze the incident and return structured security reasoning.

Important rules:
- Return valid JSON only.
- Do not wrap the JSON in markdown.
- Do not invent evidence that is not present.
- Do not expose real secrets.
- Use only the incident, findings, attack path, confidence reasons, and memory provided.
- All severity values must be lowercase: info, low, medium, high, critical.
- The output must match the exact schema below.

Incident JSON:
{json.dumps(incident, indent=2)}

Related AI memory:
{json.dumps(related_memory, indent=2)}

Return JSON in this exact shape:

{{
  "attack_type": "",
  "target": "",
  "severity": "critical",
  "confidence_assessment": "",
  "recommended_fixes": [
    {{
      "type": "immediate_action",
      "description": ""
    }}
  ],
  "generated_security_tests": [
    {{
      "file": "",
      "name": "",
      "purpose": "",
      "code": ""
    }}
  ],
  "incident_report": "",
  "ai_memory": {{
    "memory_type": "security_prevention_rule",
    "incident_pattern": "",
    "root_cause": "",
    "signals_to_watch": [],
    "prevention_rule": "",
    "recommended_tests": [],
    "severity_escalation_conditions": []
  }},
  "pr_draft": {{
    "branch_name": "",
    "pr_title": "",
    "pr_description": "",
    "files_to_change": []
  }}
}}
""".strip()