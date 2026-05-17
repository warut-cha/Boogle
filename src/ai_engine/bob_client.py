from __future__ import annotations

import json
import os
from typing import Any

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

try:
    from ai_engine.bob_prompt_builder import build_bob_prompt
except ImportError:
    from src.ai_engine.bob_prompt_builder import build_bob_prompt


class BobClient:
    """
    IBM Bob client powered by IBM watsonx.ai SDK.

    This class does not do rule-based attack classification.
    It only:
    1. Calls watsonx.ai through ibm-watsonx-ai, or
    2. Returns a valid BobOutput saying Bob is unavailable.
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("WATSONX_API_KEY")
        self.project_id = os.getenv("WATSONX_PROJECT_ID")
        self.url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
        self.model_id = os.getenv("WATSONX_MODEL_ID", "ibm/granite-13b-chat-v2")

    def analyze_incident(
        self,
        incident: dict[str, Any],
        related_memory: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        missing = self._missing_config()

        if missing:
            return self._bob_unavailable_output(
                incident,
                reason=(
                    "IBM Bob is not functional because watsonx.ai configuration "
                    f"is missing: {', '.join(missing)}."
                ),
            )

        try:
            generated_text = self._call_watsonx_sdk(
                incident=incident,
                related_memory=related_memory or [],
            )

            parsed = self._parse_json_response(generated_text)
            return self._ensure_bob_output_shape(parsed, incident)

        except ImportError as error:
            return self._bob_unavailable_output(
                incident,
                reason=(
                    "IBM Bob is not functional because the ibm-watsonx-ai package "
                    f"is not installed or cannot be imported: {error}."
                ),
            )

        except Exception as error:
            return self._bob_unavailable_output(
                incident,
                reason=f"IBM Bob is not functional because watsonx.ai analysis failed: {error}",
            )

    def _missing_config(self) -> list[str]:
        missing: list[str] = []

        if not self.api_key:
            missing.append("WATSONX_API_KEY")

        if not self.project_id:
            missing.append("WATSONX_PROJECT_ID")

        if not self.url:
            missing.append("WATSONX_URL")

        if not self.model_id:
            missing.append("WATSONX_MODEL_ID")

        return missing

    def _call_watsonx_sdk(
        self,
        incident: dict[str, Any],
        related_memory: list[dict[str, Any]],
    ) -> str:
        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference
        from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

        prompt = build_bob_prompt(
            incident=incident,
            related_memory=related_memory,
        )

        credentials = Credentials(
            api_key=self.api_key,
            url=self.url,
        )

        params = {
            GenParams.DECODING_METHOD: "greedy",
            GenParams.MAX_NEW_TOKENS: 1800,
            GenParams.MIN_NEW_TOKENS: 1,
            GenParams.REPETITION_PENALTY: 1.05,
        }

        model = ModelInference(
            model_id=self.model_id,
            credentials=credentials,
            project_id=self.project_id,
            params=params,
        )

        generated_text = model.generate_text(prompt=prompt)

        if isinstance(generated_text, str):
            return generated_text

        if isinstance(generated_text, dict):
            return json.dumps(generated_text)

        return str(generated_text)

    def _parse_json_response(self, response_text: str) -> dict[str, Any]:
        cleaned = response_text.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned.removeprefix("```json").strip()

        if cleaned.startswith("```"):
            cleaned = cleaned.removeprefix("```").strip()

        if cleaned.endswith("```"):
            cleaned = cleaned.removesuffix("```").strip()

        first_brace = cleaned.find("{")
        last_brace = cleaned.rfind("}")

        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            cleaned = cleaned[first_brace : last_brace + 1]

        parsed = json.loads(cleaned)

        if not isinstance(parsed, dict):
            raise ValueError("IBM Bob response must be a JSON object.")

        return parsed

    def _ensure_bob_output_shape(
        self,
        output: dict[str, Any],
        incident: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "attack_type": str(output.get("attack_type", "Unknown attack type")),
            "target": str(output.get("target", "Unknown target")),
            "severity": str(
                output.get("severity", incident.get("severity", "medium"))
            ).lower(),
            "confidence_assessment": str(
                output.get(
                    "confidence_assessment",
                    "IBM Bob did not return a confidence assessment.",
                )
            ),
            "recommended_fixes": self._as_list(output.get("recommended_fixes")),
            "generated_security_tests": self._as_list(
                output.get("generated_security_tests")
            ),
            "incident_report": str(
                output.get(
                    "incident_report",
                    "IBM Bob did not return an incident report.",
                )
            ),
            "ai_memory": self._ensure_ai_memory_shape(output.get("ai_memory")),
            "pr_draft": self._ensure_pr_draft_shape(output.get("pr_draft")),
        }

    def _ensure_ai_memory_shape(self, memory: Any) -> dict[str, Any]:
        if not isinstance(memory, dict):
            memory = {}

        return {
            "memory_type": str(
                memory.get("memory_type", "security_prevention_rule")
            ),
            "incident_pattern": str(memory.get("incident_pattern", "unknown_pattern")),
            "root_cause": str(memory.get("root_cause", "Unknown root cause")),
            "signals_to_watch": self._as_list(memory.get("signals_to_watch")),
            "prevention_rule": str(
                memory.get("prevention_rule", "No prevention rule returned.")
            ),
            "recommended_tests": self._as_list(memory.get("recommended_tests")),
            "severity_escalation_conditions": self._as_list(
                memory.get("severity_escalation_conditions")
            ),
        }

    def _ensure_pr_draft_shape(self, pr_draft: Any) -> dict[str, Any]:
        if not isinstance(pr_draft, dict):
            pr_draft = {}

        return {
            "branch_name": str(
                pr_draft.get("branch_name", "security/bob-analysis-unavailable")
            ),
            "pr_title": str(pr_draft.get("pr_title", "Security analysis unavailable")),
            "pr_description": str(
                pr_draft.get(
                    "pr_description",
                    "IBM Bob did not return a pull request draft.",
                )
            ),
            "files_to_change": self._as_list(pr_draft.get("files_to_change")),
        }

    def _as_list(self, value: Any) -> list[Any]:
        if isinstance(value, list):
            return value

        if value is None:
            return []

        return [value]

    def _bob_unavailable_output(
        self,
        incident: dict[str, Any],
        reason: str,
    ) -> dict[str, Any]:
        incident_id = incident.get("incident_id", "unknown")
        severity = str(incident.get("severity", "medium")).lower()

        return {
            "attack_type": "IBM Bob analysis unavailable",
            "target": "Not analyzed because IBM watsonx.ai is unavailable",
            "severity": severity,
            "confidence_assessment": reason,
            "recommended_fixes": [
                {
                    "type": "config_fix",
                    "description": (
                        "Install ibm-watsonx-ai and configure WATSONX_API_KEY, "
                        "WATSONX_PROJECT_ID, WATSONX_URL, and WATSONX_MODEL_ID."
                    ),
                }
            ],
            "generated_security_tests": [],
            "incident_report": (
                "## IBM Bob Analysis Unavailable\n\n"
                f"Incident `{incident_id}` was detected, but IBM Bob could not analyze it.\n\n"
                f"Reason: {reason}\n\n"
                "No LLM-based attack reasoning was performed."
            ),
            "ai_memory": {
                "memory_type": "security_prevention_rule",
                "incident_pattern": "bob_analysis_unavailable",
                "root_cause": reason,
                "signals_to_watch": [
                    "ibm-watsonx-ai package missing",
                    "WATSONX_API_KEY missing",
                    "WATSONX_PROJECT_ID missing",
                    "watsonx.ai request failure",
                    "invalid watsonx.ai response",
                ],
                "prevention_rule": (
                    "Ensure IBM watsonx.ai SDK and credentials are configured before "
                    "relying on Bob LLM reasoning."
                ),
                "recommended_tests": [],
                "severity_escalation_conditions": [],
            },
            "pr_draft": {
                "branch_name": "security/configure-watsonx",
                "pr_title": "Configure IBM watsonx.ai for Bob reasoning",
                "pr_description": (
                    "IBM Bob analysis could not run because watsonx.ai SDK or "
                    "configuration was unavailable."
                ),
                "files_to_change": [
                    ".env.example",
                    "requirements.txt",
                    "src/ai_engine/bob_client.py",
                ],
            },
        }