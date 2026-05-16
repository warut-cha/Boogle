from __future__ import annotations

import argparse
import random
import time

from mock_database import init_db, record_event


def simulate_benign_activity(source_ip: str) -> None:
    record_event(
        actor="normal_user",
        source_ip=source_ip,
        action="login",
        status="success",
        target="auth_service",
        metadata={"note": "normal login"},
    )

    record_event(
        actor="normal_user",
        source_ip=source_ip,
        action="db_query",
        status="success",
        target="user_profile",
        table_name="users",
        rows_returned=1,
        query="SELECT email, role FROM users WHERE id = ?",
        metadata={"note": "normal profile lookup"},
    )


def simulate_bruteforce(source_ip: str, attempts: int = 8) -> None:
    for index in range(attempts):
        record_event(
            actor=f"unknown_actor_{index}",
            source_ip=source_ip,
            action="login",
            status="failure",
            target="auth_service",
            metadata={"attack_simulation": "bruteforce"},
        )
        time.sleep(0.2)


def simulate_deprecated_api_attack(source_ip: str) -> None:
    record_event(
        actor="unknown_actor",
        source_ip=source_ip,
        action="api_request",
        status="success",
        target="legacy_export_service",
        endpoint="/api/v1/export-users",
        metadata={
            "attack_simulation": "deprecated_api_abuse",
            "description": "Suspicious access to abandoned export API",
        },
    )

    time.sleep(0.5)

    record_event(
        actor="unknown_actor",
        source_ip=source_ip,
        action="db_query",
        status="success",
        target="mock_security_db",
        table_name="users",
        rows_returned=50000,
        query="SELECT * FROM users",
        metadata={
            "attack_simulation": "data_exfiltration",
            "description": "Large read from users table",
        },
    )


def simulate_sql_injection_probe(source_ip: str) -> None:
    record_event(
        actor="unknown_actor",
        source_ip=source_ip,
        action="api_request",
        status="blocked",
        target="search_api",
        endpoint="/api/search",
        query="' OR 1=1 --",
        metadata={
            "attack_simulation": "sql_injection_probe",
            "payload": "' OR 1=1 --",
        },
    )


def simulate_full_chain(source_ip: str) -> None:
    simulate_bruteforce(source_ip, attempts=6)
    time.sleep(0.5)
    simulate_deprecated_api_attack(source_ip)
    time.sleep(0.5)
    simulate_sql_injection_probe(source_ip)


def main() -> None:
    parser = argparse.ArgumentParser(description="Safe local attack simulator")
    parser.add_argument(
        "--scenario",
        choices=[
            "benign",
            "bruteforce",
            "deprecated_api",
            "sql_injection",
            "full_chain",
        ],
        default="full_chain",
    )
    parser.add_argument("--source-ip", default="203.0.113.10")
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--delay", type=float, default=3.0)
    args = parser.parse_args()

    init_db(reset=False)

    print(f"Running safe attack simulation: {args.scenario}")

    while True:
        source_ip = args.source_ip

        if args.source_ip == "random":
            source_ip = f"203.0.113.{random.randint(10, 250)}"

        if args.scenario == "benign":
            simulate_benign_activity(source_ip)
        elif args.scenario == "bruteforce":
            simulate_bruteforce(source_ip)
        elif args.scenario == "deprecated_api":
            simulate_deprecated_api_attack(source_ip)
        elif args.scenario == "sql_injection":
            simulate_sql_injection_probe(source_ip)
        elif args.scenario == "full_chain":
            simulate_full_chain(source_ip)

        if not args.loop:
            break

        time.sleep(args.delay)


if __name__ == "__main__":
    main()