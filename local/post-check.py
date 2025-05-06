#!/usr/bin/env python3

import sys
import requests

if len(sys.argv) != 2:
    print("Usage: post-check.py <url>")
    sys.exit(2)

url = sys.argv[1]
print(f"📡 Sending POST to {url}")
response = requests.post(url, json={"test": "data"})

print(f"🔎 Status Code: {response.status_code}")
print(f"📬 Response Body:\n{response.text}")

if response.status_code == 200 and '"status": "ok"' in response.text:
    sys.exit(0)
else:
    print("❌ Unexpected response.")
    sys.exit(1)
