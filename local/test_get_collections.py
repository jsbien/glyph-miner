import requests

url = "http://localhost:9090/api/collections"
response = requests.get(url)

print("Status Code:", response.status_code)
print("Response Body:")
print(response.text)

if response.status_code != 200:
    exit(1)
