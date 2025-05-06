import requests
import json

url = "http://localhost:9090/api/collections"
headers = {"Content-Type": "application/json"}
data = {"title": "Debug Collection"}

response = requests.post(url, headers=headers, data=json.dumps(data))

print("Status Code:", response.status_code)
print("Response Body:")
print(response.text)

if response.status_code != 200:
    exit(1)
