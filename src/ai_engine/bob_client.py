from __future__ import annotations

import json
import os
from typing import Any
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenChatParamsMetaNames as ChatParams
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
    def _extract_chat_content(self, response: Any) -> str:
        if isinstance(response, str):
            return response

        if not isinstance(response, dict):
            return str(response)

        choices = response.get("choices")

        if isinstance(choices, list) and choices:
            first_choice = choices[0]

            if isinstance(first_choice, dict):
                message = first_choice.get("message")

                if isinstance(message, dict):
                    content = message.get("content")

                    if isinstance(content, str):
                        return content

                    if isinstance(content, list):
                        parts: list[str] = []

                        for item in content:
                            if isinstance(item, dict):
                                text = item.get("text")
                                if isinstance(text, str):
                                    parts.append(text)

                        return "\n".join(parts)

        output = response.get("output")
        if isinstance(output, str):
            return output

        generated_text = response.get("generated_text")
        if isinstance(generated_text, str):
            return generated_text

        return json.dumps(response)

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

        prompt = build_bob_prompt(
            incident=incident,
            related_memory=related_memory,
        )

        credentials = Credentials(
            api_key=self.api_key,
            url=self.url,
        )

        model = ModelInference(
            model_id=self.model_id,
            credentials=credentials,
            project_id=self.project_id,
        )

        params = {
            ChatParams.MAX_TOKENS: 1800,
            ChatParams.TEMPERATURE: 0.2,
            ChatParams.TOP_P: 0.9,
            ChatParams.TIME_LIMIT: 60000,
        }

        response = model.chat(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are IBM Bob, a cybersecurity reasoning assistant. "
                        "Return valid JSON only. Do not wrap the JSON in markdown."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            params=params,
        )

        return self._extract_chat_content(response)

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
        }