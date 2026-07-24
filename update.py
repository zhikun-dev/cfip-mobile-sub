#!/usr/bin/env python3
"""Generate a Cloudflare preferred-domain feed from VPS789's daily Top 20.

Only China Mobile candidates whose measured packet loss is exactly 0% are
published. The list is intentionally a discovery feed: domains remain domains
so EdgeTunnel can resolve them at connection time.
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

API = "https://vps789.com/openApi/cfIpTop20"
OUT = Path("cf-mobile.txt")


def fetch() -> list[dict]:
    request = Request(API, headers={"User-Agent": "cfip-mobile-sub/1.0"})
    with urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if payload.get("code") != 0 or not isinstance(payload.get("data", {}).get("good"), list):
        raise RuntimeError(f"unexpected VPS789 response: {payload!r}")
    return payload["data"]["good"]


def main() -> None:
    candidates = fetch()
    selected: list[dict] = []
    seen: set[str] = set()
    for item in candidates:
        domain = str(item.get("ip", "")).strip().lower()
        try:
            loss = float(item.get("ydPkgLostRate"))
        except (TypeError, ValueError):
            continue
        if domain and loss == 0 and domain not in seen:
            selected.append(item)
            seen.add(domain)

    if not selected:
        raise RuntimeError("zero Mobile-loss candidates is empty; preserving last feed")

    sample_time = str(selected[0].get("createdTime", "unknown"))
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# VPS789 CF daily Top20 — China Mobile loss 0%",
        f"# source sample: {sample_time}; generated: {generated}",
        "# connection address only; preserve your EdgeTunnel domain as SNI/Host.",
    ]
    for item in selected:
        domain = str(item["ip"]).strip().lower()
        latency = item.get("ydLatency", "?")
        lines.append(f"{domain}:443#CF-MOBILE-0LOSS-{latency}ms")
    content = "\n".join(lines) + "\n"

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=".") as tmp:
        tmp.write(content)
        tmp_name = tmp.name
    os.replace(tmp_name, OUT)
    print(f"published {len(selected)} domains")


if __name__ == "__main__":
    main()
