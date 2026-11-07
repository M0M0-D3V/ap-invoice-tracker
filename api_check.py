import requests

r = requests.get("http://localhost:8000/vendors", timeout=5)

print(r.status_code)
print(r.json())