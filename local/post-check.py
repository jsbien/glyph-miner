#!/usr/bin/env python3
import requests
import sys

if len(sys.argv) != 2:
    print("Usage: post-check.py <API endpoint>")
    sys.exit(1)

url = sys.argv[1]
payload = {"title": "Debug Collection (post-check.py)"}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    print(response.text)
    response.raise_for_status()
    sys.exit(0)
except requests.RequestException as e:
    print(f"Request failed: {e}")
    sys.exit(1)
