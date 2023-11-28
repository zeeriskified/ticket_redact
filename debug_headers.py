
import base64
import requests
import os

email = os.environ.get("email")  # Replace with actual environment variable name for email
api_token = os.environ.get("ZENDESK_SBX_API_TOKEN")
zendesk_domain = os.environ.get("ZENDESK_SBX_DOMAIN")

# Encode credentials
credentials = base64.b64encode(f'{email}/token:{api_token}'.encode('utf-8')).decode('utf-8')

# Debugging prints
print(f"Encoded credentials: {credentials}")

headers = {
    "Authorization": f"Basic {credentials}",
    "Content-Type": "application/json"
}

# Debugging prints
print(f"URL: https://{zendesk_domain}.zendesk.com/api/v2/tickets.json")
print(f"Headers: {headers}")

response = requests.get(f"https://{zendesk_domain}.zendesk.com/api/v2/tickets.json", headers=headers)

# Debugging output
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
print (email)