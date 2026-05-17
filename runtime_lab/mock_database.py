from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "runtime_lab" / "mock_security.db"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(reset: bool = False) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    if reset:
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("DROP TABLE IF EXISTS audit_events")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            role TEXT NOT NULL,
            api_token TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            actor TEXT NOT NULL,
            source_ip TEXT NOT NULL,
            action TEXT NOT NULL,
            target TEXT,
            endpoint TEXT,
            table_name TEXT,
            rows_returned INTEGER DEFAULT 0,
            status TEXT NOT NULL,
            query TEXT,
            metadata_json TEXT
        )
        """
    )

    existing_users = cursor.execute("SELECT COUNT(*) AS count FROM users").fetchone()["count"]

    if existing_users == 0:
        users = [
            ("alice@example.com", "admin", "tok_admin_mock_001"),
            ("bob@example.com", "user", "tok_user_mock_002"),
            ("charlie@example.com", "user", "tok_user_mock_003"),
            ("dana@example.com", "finance", "tok_fin_mock_004"),
        ]

        cursor.executemany(
            "INSERT INTO users (email, role, api_token) VALUES (?, ?, ?)",
            users,
        )

    conn.commit()
    conn.close()


def record_event(
    actor: str,
    source_ip: str,
    action: str,
    status: str,
    target: str | None = None,
    endpoint: str | None = None,
    table_name: str | None = None,
    rows_returned: int = 0,
    query: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO audit_events (
            timestamp,
            actor,
            source_ip,
            action,
            target,
            endpoint,
            table_name,
            rows_returned,
            status,
            query,
            metadata_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            utc_now(),
            actor,
            source_ip,
            action,
            target,
            endpoint,
            table_name,
            rows_returned,
            status,
            query,
            json.dumps(metadata or {}),
        ),
    )

    event_id = int(cursor.lastrowid)
    conn.commit()
    conn.close()
    return event_id


def reset_events() -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM audit_events")
    conn.commit()
    conn.close()


def status() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    users_count = cursor.execute("SELECT COUNT(*) AS count FROM users").fetchone()["count"]
    events_count = cursor.execute("SELECT COUNT(*) AS count FROM audit_events").fetchone()["count"]

    print(
        json.dumps(
            {
                "db_path": str(DB_PATH),
                "users": users_count,
                "audit_events": events_count,
            },
            indent=2,
        )
    )

    conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Mock security database")
    parser.add_argument("--init", action="store_true")
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()

    if args.init:
        init_db(reset=args.reset)
        print(f"Mock database initialized: {DB_PATH}")

    if args.status:
        status()


if __name__ == "__main__":
    main()