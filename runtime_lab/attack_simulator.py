from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone

import requests


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def send_attack_event(
    backend_url: str,
    endpoint: str,
    source_ip: str,
    count: int,
    delay: float,
) -> None:
    url = f"{backend_url.rstrip('/')}/api/attack-event"

    for index in range(count):
        payload = {
            "event_type": "deprecated_api_attack",
            "endpoint": endpoint,
            "method": "GET",
            "status": 200,
            "source_ip": source_ip,
            "repo_name": "legacy-backend",
            "file": "runtime/api_gateway",
            "database_table": "users",
            "request_count": index + 1,
            "timestamp": utc_now(),
        }

        response = requests.post(url, json=payload, timeout=30)

        print(
            f"[{index + 1}/{count}] sent attack event "
            f"status={response.status_code} response={response.text}"
        )

        time.sleep(delay)


def main() -> None:
    parser = argparse.ArgumentParser(description="Bob Sentinel real-time attack simulator")

    parser.add_argument(
        "--backend-url",
        default="http://localhost:3000",
        help="Boogle backend URL",
    )

    parser.add_argument(
        "--endpoint",
        default="/api/v1/export-users",
        help="Target endpoint to attack",
    )

    parser.add_argument(
        "--source-ip",
        default="203.0.113.10",
        help="Simulated attacker source IP",
    )

    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of attack events to send",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between events in seconds",
    )

    args = parser.parse_args()

    send_attack_event(
        backend_url=args.backend_url,
        endpoint=args.endpoint,
        source_ip=args.source_ip,
        count=args.count,
        delay=args.delay,
    )


if __name__ == "__main__":
    main()