import requests
import json

from datetime import datetime
timestamp = datetime.now().isoformat()


    
url = "http://localhost:9090/api/collections"
headers = {"Content-Type": "application/json"}
data = {"title": f"Debug Collection {timestamp}"}


response = requests.post(url, headers=headers, data=json.dumps(data))

print("Status Code:", response.status_code)
print("Response Body:")
print(response.text)

if response.status_code != 200:
    exit(1)
