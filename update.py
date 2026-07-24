#!/usr/bin/env python3
"""Generate a Cloudflare preferred-domain feed from VPS789's daily Top 20."""
from __future__ import annotations

import json
import os
import tempfile
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
    selected: list[dict] = []
    seen: set[str] = set()
    for item in fetch():
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

    # Keep this file strictly IP/domain:port#label. Some EdgeTunnel aggregators
    # treat comments and metadata lines as malformed API data.
    content = "\n".join(
        f"{str(item['ip']).strip().lower()}:443#CF-MOBILE-0LOSS-{item.get('ydLatency', '?')}ms"
        for item in selected
    ) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=".") as tmp:
        tmp.write(content)
        temp_name = tmp.name
    os.replace(temp_name, OUT)
    print(f"published {len(selected)} domains")


if __name__ == "__main__":
    main()
