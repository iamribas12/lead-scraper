import requests
import json

url = "https://nominatim.openstreetmap.org/search"
params = {
    "q": "plumbers in birmingham",
    "format": "json",
    "extratags": 1,
    "addressdetails": 1,
    "limit": 10
}
headers = {"User-Agent": "LeadGenApp/1.0"}
r = requests.get(url, params=params, headers=headers)
print(json.dumps(r.json(), indent=2))
