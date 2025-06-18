import requests
from fake_headers import Headers


headers = Headers(os="mac", headers=True).generate()
response = requests.get("https://direct.mit.edu", timeout=5, headers=headers)
print(response.status_code)