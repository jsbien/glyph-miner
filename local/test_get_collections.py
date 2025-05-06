# local/test_get_collections.py
import requests
import sys

url = "http://localhost:9090/api/collections"

try:
    response = requests.get(url)
    print("Status Code:", response.status_code)
    print("Response Body:")
    print(response.json())

    if response.status_code == 200:
        print("✅ GET /collections succeeded")
        sys.exit(0)
    else:
        print("❌ GET /collections returned non-200 status")
        sys.exit(1)
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")
    sys.exit(2)
except ValueError:
    print("❌ Response is not valid JSON")
    print("Raw Response:")
    print(response.text)
    sys.exit(3)
