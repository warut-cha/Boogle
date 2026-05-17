from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


class AIMemoryStore:
    def __init__(self, path: str | Path = "data/ai_memory.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if not self.path.exists():
            self._write_data({"version": 1, "memories": []})

    def list_memories(self) -> list[dict[str, Any]]:
        data = self._read_data()
        memories = data.get("memories", [])

        if not isinstance(memories, list):
            return []

        return memories

    def clear(self) -> None:
        self._write_data({"version": 1, "memories": []})

    def find_related_memories(
        self,
        incident: dict[str, Any],
        limit: int = 5,
        min_score: float = 0.08,
    ) -> list[dict[str, Any]]:
        memories = self.list_memories()

        if not memories:
            return []

        incident_tokens = self._tokens_from_incident(incident)

        scored: list[tuple[float, dict[str, Any]]] = []

        for memory in memories:
            memory_tokens = self._tokens_from_memory(memory)
            score = self._similarity_score(incident_tokens, memory_tokens)

            if score >= min_score:
                memory_copy = dict(memory)
                memory_copy["similarity_score"] = round(score, 3)
                scored.append((score, memory_copy))

        scored.sort(key=lambda item: item[0], reverse=True)

        return [memory for _, memory in scored[:limit]]

    def save_from_bob_output(
        self,
        bob_output: dict[str, Any],
        incident: dict[str, Any],
    ) -> dict[str, Any] | None:
        if not isinstance(bob_output, dict):
            return None

        attack_type = str(bob_output.get("attack_type", "")).lower()

        # Do not store failed/unavailable Bob output as useful AI memory.
        if "unavailable" in attack_type or "not functional" in attack_type:
            return None

        ai_memory = bob_output.get("ai_memory")

        if not isinstance(ai_memory, dict):
            return None

        memory_entry = self._normalize_memory_entry(
            ai_memory=ai_memory,
            bob_output=bob_output,
            incident=incident,
        )

        memories = self.list_memories()

        existing_index = self._find_existing_memory_index(memories, memory_entry)

        if existing_index is not None:
            existing = memories[existing_index]
            memories[existing_index] = self._merge_memory(existing, memory_entry)
            saved = memories[existing_index]
        else:
            memories.append(memory_entry)
            saved = memory_entry

        self._write_data({"version": 1, "memories": memories})

        return saved

    def _normalize_memory_entry(
        self,
        ai_memory: dict[str, Any],
        bob_output: dict[str, Any],
        incident: dict[str, Any],
    ) -> dict[str, Any]:
        now = self._utc_now()

        return {
            "memory_id": ai_memory.get("memory_id") or f"MEM-{uuid4().hex[:10]}",
            "memory_type": str(
                ai_memory.get("memory_type", "security_prevention_rule")
            ),
            "incident_pattern": str(
                ai_memory.get("incident_pattern", "unknown_pattern")
            ),
            "root_cause": str(ai_memory.get("root_cause", "Unknown root cause")),
            "signals_to_watch": self._as_string_list(
                ai_memory.get("signals_to_watch")
            ),
            "prevention_rule": str(
                ai_memory.get("prevention_rule", "No prevention rule provided.")
            ),
            "recommended_tests": self._as_string_list(
                ai_memory.get("recommended_tests")
            ),
            "severity_escalation_conditions": self._as_string_list(
                ai_memory.get("severity_escalation_conditions")
            ),
            "source_incident_ids": [str(incident.get("incident_id", "unknown"))],
            "source_attack_type": str(bob_output.get("attack_type", "unknown")),
            "source_target": str(bob_output.get("target", "unknown")),
            "source_severity": str(
                bob_output.get("severity", incident.get("severity", "medium"))
            ).lower(),
            "created_at": now,
            "last_seen_at": now,
            "times_seen": 1,
        }

    def _find_existing_memory_index(
        self,
        memories: list[dict[str, Any]],
        new_memory: dict[str, Any],
    ) -> int | None:
        new_pattern = self._normalize_key(new_memory.get("incident_pattern"))
        new_rule = self._normalize_key(new_memory.get("prevention_rule"))

        for index, memory in enumerate(memories):
            existing_pattern = self._normalize_key(memory.get("incident_pattern"))
            existing_rule = self._normalize_key(memory.get("prevention_rule"))

            if existing_pattern == new_pattern and existing_rule == new_rule:
                return index

        return None

    def _merge_memory(
        self,
        existing: dict[str, Any],
        new_memory: dict[str, Any],
    ) -> dict[str, Any]:
        source_ids = set(self._as_string_list(existing.get("source_incident_ids")))
        source_ids.update(self._as_string_list(new_memory.get("source_incident_ids")))

        return {
            **existing,
            "root_cause": new_memory.get("root_cause") or existing.get("root_cause"),
            "signals_to_watch": self._merge_lists(
                existing.get("signals_to_watch"),
                new_memory.get("signals_to_watch"),
            ),
            "recommended_tests": self._merge_lists(
                existing.get("recommended_tests"),
                new_memory.get("recommended_tests"),
            ),
            "severity_escalation_conditions": self._merge_lists(
                existing.get("severity_escalation_conditions"),
                new_memory.get("severity_escalation_conditions"),
            ),
            "source_incident_ids": sorted(source_ids),
            "last_seen_at": self._utc_now(),
            "times_seen": int(existing.get("times_seen", 1)) + 1,
        }

    def _tokens_from_incident(self, incident: dict[str, Any]) -> set[str]:
        parts: list[str] = []

        parts.append(str(incident.get("title", "")))
        parts.append(str(incident.get("severity", "")))

        parts.extend(self._as_string_list(incident.get("confidence_reasons")))
        parts.extend(self._as_string_list(incident.get("affected_repos")))
        parts.extend(self._as_string_list(incident.get("affected_files")))
        parts.extend(self._as_string_list(incident.get("affected_endpoints")))
        parts.extend(self._as_string_list(incident.get("affected_database_tables")))

        for finding in incident.get("findings", []):
            if not isinstance(finding, dict):
                continue

            parts.append(str(finding.get("finding_type", "")))
            parts.append(str(finding.get("category", "")))
            parts.append(str(finding.get("endpoint", "")))
            parts.append(str(finding.get("database_table", "")))
            parts.append(str(finding.get("evidence", "")))
            parts.append(str(finding.get("event_type", "")))
            parts.append(str(finding.get("action", "")))
            parts.append(str(finding.get("status", "")))

            metadata = finding.get("metadata", {})
            if isinstance(metadata, dict):
                parts.append(json.dumps(metadata, sort_keys=True))

        attack_path = incident.get("attack_path", {})
        if isinstance(attack_path, dict):
            for node in attack_path.get("nodes", []):
                if isinstance(node, dict):
                    parts.append(str(node.get("label", "")))
                    parts.append(str(node.get("type", "")))

            for edge in attack_path.get("edges", []):
                if isinstance(edge, dict):
                    parts.append(str(edge.get("label", "")))

        return self._tokenize(" ".join(parts))

    def _tokens_from_memory(self, memory: dict[str, Any]) -> set[str]:
        parts: list[str] = []

        parts.append(str(memory.get("memory_type", "")))
        parts.append(str(memory.get("incident_pattern", "")))
        parts.append(str(memory.get("root_cause", "")))
        parts.append(str(memory.get("prevention_rule", "")))
        parts.append(str(memory.get("source_attack_type", "")))
        parts.append(str(memory.get("source_target", "")))

        parts.extend(self._as_string_list(memory.get("signals_to_watch")))
        parts.extend(self._as_string_list(memory.get("recommended_tests")))
        parts.extend(self._as_string_list(memory.get("severity_escalation_conditions")))

        return self._tokenize(" ".join(parts))

    def _similarity_score(self, left: set[str], right: set[str]) -> float:
        if not left or not right:
            return 0.0

        intersection = left.intersection(right)
        union = left.union(right)

        return len(intersection) / len(union)

    def _tokenize(self, text: str) -> set[str]:
        tokens = re.findall(r"[a-zA-Z0-9_/\-]+", text.lower())

        stop_words = {
            "the",
            "and",
            "or",
            "to",
            "from",
            "with",
            "for",
            "this",
            "that",
            "was",
            "were",
            "are",
            "is",
            "in",
            "on",
            "of",
            "a",
            "an",
        }

        return {
            token
            for token in tokens
            if len(token) >= 3 and token not in stop_words
        }

    def _normalize_key(self, value: Any) -> str:
        return " ".join(sorted(self._tokenize(str(value or ""))))

    def _merge_lists(self, left: Any, right: Any) -> list[str]:
        merged: list[str] = []

        for item in self._as_string_list(left) + self._as_string_list(right):
            if item not in merged:
                merged.append(item)

        return merged

    def _as_string_list(self, value: Any) -> list[str]:
        if value is None:
            return []

        if isinstance(value, list):
            return [str(item) for item in value if item is not None]

        return [str(value)]

    def _read_data(self) -> dict[str, Any]:
        try:
            with self.path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, dict):
                return data

            return {"version": 1, "memories": []}
        except Exception:
            return {"version": 1, "memories": []}

    def _write_data(self, data: dict[str, Any]) -> None:
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat()