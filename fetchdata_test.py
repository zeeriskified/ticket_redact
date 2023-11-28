import base64
import requests
import os

# Zendesk API credentials and domain
email = "zee.perez-canals@riskified.com" 
api_token = os.environ.get('ZENDESK_SBX_API_TOKEN')
zendesk_domain = os.environ.get('ZENDESK_SBX_DOMAIN')  # Ensure this is set in your environment variables

# Encode credentials
credentials = base64.b64encode(f'{email}/token:{api_token}'.encode('utf-8')).decode('utf-8')

# Set the headers for Basic Authentication
headers = {
    "Authorization": f"Basic {credentials}"
}

# Example: Fetch tickets using Basic Auth
response = requests.get(f"https://{zendesk_domain}.zendesk.com/api/v2/tickets.json", headers=headers)

if response.status_code == 200:
    print("Tickets fetched successfully.")
    # Process the fetched data...
else:
    print(f"Failed to fetch tickets. Status: {response.status_code}, Message: {response.text}")


# # Function to fetch tickets
# def fetch_tickets():
#     headers = {
#         "Authorization": f"Basic {api_token}",
#         "Content-Type": "application/json"
#     }
#     response = requests.get(f"https://{zendesk_domain}.zendesk.com/api/v2/tickets.json", headers=headers)
    
#     if response.status_code == 200:
#         tickets = response.json()['tickets']
#         for ticket in tickets:
#             print(f"Ticket ID: {ticket['id']}, Subject: {ticket['subject']}")
#     else:
#         print(f"Failed to fetch tickets. Status: {response.status_code}, Message: {response.text}")

# # Execute the function
# fetch_tickets()
