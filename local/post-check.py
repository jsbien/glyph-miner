#!/usr/bin/env python3
import requests
import json

url = "http://localhost:9090/api/collections"
headers = {"Content-Type": "application/json"}
data = {"title": "Debug Collection"}

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    try:
        print("Response JSON:")
        print(response.json())
    except json.JSONDecodeError:
        print("Response is not valid JSON.")
        print("Raw response:")
        print(response.text)
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
