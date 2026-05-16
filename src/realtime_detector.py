from __future__ import annotations

import asyncio
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


class RealtimeAttackDetector:
    def __init__(
        self,
        db_path: Path,
        findings_store: list[dict[str, Any]],
        incidents_store: list[dict[str, Any]],
        ws_manager: Any,
        poll_interval_seconds: float = 1.0,
    ) -> None:
        self.db_path = db_path
        self.findings_store = findings_store
        self.incidents_store = incidents_store
        self.ws_manager = ws_manager
        self.poll_interval_seconds = poll_interval_seconds

        self.last_event_id = 0
        self.running = False
        self.task: asyncio.Task | None = None
        self.event_buffer: list[dict[str, Any]] = []
        self.seen_incident_keys: set[str] = set()

    async def start(self) -> None:
        if self.running:
            return

        self.running = True
        self.task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        self.running = False

        if self.task:
            self.task.cancel()
            self.task = None

    def status(self) -> dict[str, Any]:
        return {
            "running": self.running,
            "last_event_id": self.last_event_id,
            "db_path": str(self.db_path),
            "buffered_events": len(self.event_buffer),
        }

    async def _run_loop(self) -> None:
        while self.running:
            try:
                new_events = self._load_new_events()

                if new_events:
                    self.event_buffer.extend(new_events)
                    self.event_buffer = self.event_buffer[-200:]

                    for event in new_events:
                        finding = self._event_to_finding(event)
                        if finding:
                            self.findings_store.append(finding)
                            await self.ws_manager.broadcast(
                                {
                                    "type": "new_finding",
                                    "finding": finding,
                                }
                            )

                    incidents = self._correlate_events()

                    for incident in incidents:
                        self.incidents_store.append(incident)
                        await self.ws_manager.broadcast(
                            {
                                "type": "new_incident",
                                "incident": incident,
                            }
                        )

            except Exception as error:
                print(f"[RealtimeAttackDetector] Error: {error}")

            await asyncio.sleep(self.poll_interval_seconds)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _load_new_events(self) -> list[dict[str, Any]]:
        if not self.db_path.exists():
            return []

        conn = self._connect()
        rows = conn.execute(
            """
            SELECT *
            FROM audit_events
            WHERE id > ?
            ORDER BY id ASC
            """,
            (self.last_event_id,),
        ).fetchall()
        conn.close()

        events: list[dict[str, Any]] = []

        for row in rows:
            event = dict(row)

            try:
                event["metadata"] = json.loads(event.get("metadata_json") or "{}")
            except Exception:
                event["metadata"] = {}

            events.append(event)
            self.last_event_id = max(self.last_event_id, int(event["id"]))

        return events

    def _event_to_finding(self, event: dict[str, Any]) -> dict[str, Any] | None:
        action = str(event.get("action") or "")
        status = str(event.get("status") or "")
        endpoint = event.get("endpoint")
        table_name = event.get("table_name")
        rows_returned = int(event.get("rows_returned") or 0)
        query = str(event.get("query") or "")
        source_ip = str(event.get("source_ip") or "unknown")

        if action == "login" and status == "failure":
            return self._finding(
                event=event,
                finding_type="runtime_anomaly",
                category="runtime_behavior",
                severity_hint="medium",
                evidence=f"Failed login attempt from {source_ip}",
            )

        if endpoint and "/api/v1" in endpoint:
            return self._finding(
                event=event,
                finding_type="deprecated_api",
                category="legacy_api",
                severity_hint="high",
                evidence=f"Deprecated endpoint accessed: {endpoint}",
            )

        if table_name == "users" and rows_returned >= 1000:
            return self._finding(
                event=event,
                finding_type="database_anomaly",
                category="database_activity",
                severity_hint="critical",
                evidence=f"Large read from users table: {rows_returned} rows",
            )

        if " OR 1=1" in query.upper() or "DROP TABLE" in query.upper() or "--" in query:
            return self._finding(
                event=event,
                finding_type="runtime_anomaly",
                category="runtime_behavior",
                severity_hint="high",
                evidence="SQL injection-like query pattern detected",
            )

        return None

    def _finding(
        self,
        event: dict[str, Any],
        finding_type: str,
        category: str,
        severity_hint: str,
        evidence: str,
    ) -> dict[str, Any]:
        return {
            "finding_id": f"FIND-RT-{uuid4().hex[:10]}",
            "repo_name": "runtime-mock-db",
            "finding_type": finding_type,
            "category": category,
            "severity_hint": severity_hint,
            "source": "python_analyzer",
            "file": None,
            "line": None,
            "endpoint": event.get("endpoint"),
            "database_table": event.get("table_name"),
            "evidence": evidence,
            "masked_value": None,
            "timestamp": self._now(),
            "event_id": event.get("id"),
            "source_ip": event.get("source_ip"),
            "actor": event.get("actor"),
            "action": event.get("action"),
        }

    def _correlate_events(self) -> list[dict[str, Any]]:
        incidents: list[dict[str, Any]] = []

        events_by_ip: dict[str, list[dict[str, Any]]] = {}

        for event in self.event_buffer:
            source_ip = str(event.get("source_ip") or "unknown")
            events_by_ip.setdefault(source_ip, []).append(event)

        for source_ip, events in events_by_ip.items():
            failed_logins = [
                event
                for event in events
                if event.get("action") == "login" and event.get("status") == "failure"
            ]

            deprecated_api_events = [
                event
                for event in events
                if event.get("endpoint") and "/api/v1" in str(event.get("endpoint"))
            ]

            large_user_reads = [
                event
                for event in events
                if event.get("table_name") == "users"
                and int(event.get("rows_returned") or 0) >= 1000
            ]

            injection_events = [
                event
                for event in events
                if " OR 1=1" in str(event.get("query") or "").upper()
                or "--" in str(event.get("query") or "")
            ]

            if len(failed_logins) >= 5:
                incident_key = f"bruteforce:{source_ip}:{failed_logins[-1].get('id')}"

                if incident_key not in self.seen_incident_keys:
                    self.seen_incident_keys.add(incident_key)
                    incidents.append(
                        self._build_incident(
                            title="Possible brute force attack against authentication service",
                            severity="high",
                            severity_level=4,
                            confidence_score=0.82,
                            confidence_reasons=[
                                f"{len(failed_logins)} failed login attempts from the same source IP",
                            ],
                            confidence_limitations=[
                                "No confirmed successful login after brute force attempt",
                            ],
                            affected_endpoints=[],
                            affected_tables=[],
                            event_group=failed_logins,
                            source_ip=source_ip,
                            attack_path={
                                "nodes": [
                                    {
                                        "id": "failed_logins",
                                        "label": "Repeated Failed Logins",
                                        "type": "runtime",
                                    },
                                    {
                                        "id": "auth",
                                        "label": "Authentication Service",
                                        "type": "api",
                                    },
                                    {
                                        "id": "impact",
                                        "label": "Possible Account Takeover Attempt",
                                        "type": "impact",
                                    },
                                ],
                                "edges": [
                                    {
                                        "from": "failed_logins",
                                        "to": "auth",
                                        "label": "targets",
                                    },
                                    {
                                        "from": "auth",
                                        "to": "impact",
                                        "label": "may lead to",
                                    },
                                ],
                            },
                        )
                    )

            if deprecated_api_events and large_user_reads:
                incident_key = f"deprecated-api-exfil:{source_ip}:{large_user_reads[-1].get('id')}"

                if incident_key not in self.seen_incident_keys:
                    self.seen_incident_keys.add(incident_key)
                    incidents.append(
                        self._build_incident(
                            title="Possible data exfiltration through abandoned export API",
                            severity="critical",
                            severity_level=5,
                            confidence_score=0.91,
                            confidence_reasons=[
                                "Deprecated API endpoint was accessed",
                                "Large read from users table detected",
                                "Both events came from the same source IP",
                            ],
                            confidence_limitations=[
                                "This is a mock local simulation, not confirmed external breach",
                            ],
                            affected_endpoints=list(
                                {
                                    str(event.get("endpoint"))
                                    for event in deprecated_api_events
                                    if event.get("endpoint")
                                }
                            ),
                            affected_tables=["users"],
                            event_group=deprecated_api_events + large_user_reads,
                            source_ip=source_ip,
                            attack_path={
                                "nodes": [
                                    {
                                        "id": "old_api",
                                        "label": "Abandoned Export API",
                                        "type": "api",
                                    },
                                    {
                                        "id": "traffic",
                                        "label": "Suspicious Requests",
                                        "type": "runtime",
                                    },
                                    {
                                        "id": "db",
                                        "label": "Users Table Read Spike",
                                        "type": "database",
                                    },
                                    {
                                        "id": "leak",
                                        "label": "Possible Data Leak",
                                        "type": "impact",
                                    },
                                ],
                                "edges": [
                                    {
                                        "from": "old_api",
                                        "to": "traffic",
                                        "label": "targeted by",
                                    },
                                    {
                                        "from": "traffic",
                                        "to": "db",
                                        "label": "accesses",
                                    },
                                    {
                                        "from": "db",
                                        "to": "leak",
                                        "label": "may expose",
                                    },
                                ],
                            },
                        )
                    )

            if injection_events:
                incident_key = f"injection:{source_ip}:{injection_events[-1].get('id')}"

                if incident_key not in self.seen_incident_keys:
                    self.seen_incident_keys.add(incident_key)
                    incidents.append(
                        self._build_incident(
                            title="Possible SQL injection probe detected",
                            severity="high",
                            severity_level=4,
                            confidence_score=0.78,
                            confidence_reasons=[
                                "SQL injection-like query pattern detected",
                            ],
                            confidence_limitations=[
                                "Request was blocked in simulation",
                            ],
                            affected_endpoints=list(
                                {
                                    str(event.get("endpoint"))
                                    for event in injection_events
                                    if event.get("endpoint")
                                }
                            ),
                            affected_tables=[],
                            event_group=injection_events,
                            source_ip=source_ip,
                            attack_path={
                                "nodes": [
                                    {
                                        "id": "payload",
                                        "label": "Injection Payload",
                                        "type": "runtime",
                                    },
                                    {
                                        "id": "api",
                                        "label": "Search API",
                                        "type": "api",
                                    },
                                    {
                                        "id": "impact",
                                        "label": "Possible Query Manipulation",
                                        "type": "impact",
                                    },
                                ],
                                "edges": [
                                    {
                                        "from": "payload",
                                        "to": "api",
                                        "label": "sent to",
                                    },
                                    {
                                        "from": "api",
                                        "to": "impact",
                                        "label": "may cause",
                                    },
                                ],
                            },
                        )
                    )

        return incidents

    def _build_incident(
        self,
        title: str,
        severity: str,
        severity_level: int,
        confidence_score: float,
        confidence_reasons: list[str],
        confidence_limitations: list[str],
        affected_endpoints: list[str],
        affected_tables: list[str],
        event_group: list[dict[str, Any]],
        source_ip: str,
        attack_path: dict[str, Any],
    ) -> dict[str, Any]:
        related_findings = [
            finding
            for finding in self.findings_store
            if finding.get("event_id") in {event.get("id") for event in event_group}
        ]

        return {
            "incident_id": f"INC-RT-{uuid4().hex[:10]}",
            "title": title,
            "severity": severity,
            "severity_level": severity_level,
            "confidence_score": confidence_score,
            "confidence_reasons": confidence_reasons,
            "confidence_limitations": confidence_limitations,
            "affected_repos": ["runtime-mock-db"],
            "affected_files": [],
            "affected_endpoints": affected_endpoints,
            "affected_database_tables": affected_tables,
            "findings": related_findings,
            "attack_path": attack_path,
            "related_memory": [],
            "timestamp": self._now(),
            "source_ip": source_ip,
            "event_ids": [event.get("id") for event in event_group],
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()