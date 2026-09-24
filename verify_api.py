#!/usr/bin/env python3
"""Verify the production health endpoint and opportunity catalogue contract."""

import json
import sys
import urllib.request


BASE_URL = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "https://globalpathways-gglc.onrender.com"


def get(path):
    request = urllib.request.Request(BASE_URL + path, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"{path}: HTTP {response.status}")
        return json.loads(response.read().decode("utf-8"))


health = get("/api/health/")
records = get("/api/opportunities/")
scholarships = get("/api/opportunities/?category=scholarship")

assert health.get("status") == "ok", health
assert len(records) == 104, len(records)
assert len(scholarships) == 37, len(scholarships)
assert all(item.get("category") == "scholarship" for item in scholarships)
assert len({item["slug"] for item in records}) == len(records)
assert all(item.get("title") and item.get("deadline") for item in records)

print(f"base_url={BASE_URL}")
print(f"health={health.get('service')}:{health.get('status')}")
print(f"total={len(records)}")
print(f"scholarships={len(scholarships)}")
print("unique_slugs=yes")
print("verification=passed")
