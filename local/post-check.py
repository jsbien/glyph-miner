import requests
import json

with open("/tmp/uwsgi-wrapper.pid") as f:
    pid = f.read().strip()

url = "http://localhost:9090/api/collections"
headers = {"Content-Type": "application/json"}
data = {"title": f"Debug Collection {pid}"}


response = requests.post(url, headers=headers, data=json.dumps(data))

print("Status Code:", response.status_code)
print("Response Body:")
print(response.text)

if response.status_code != 200:
    exit(1)
