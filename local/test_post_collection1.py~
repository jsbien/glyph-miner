import requests
import json

url = "http://localhost:9090/api/collections"

payload = {
    "title": "Debug Collection"
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers, data=json.dumps(payload))

print(f"Status Code: {response.status_code}")
print("Response Body:")
print(response.text)
