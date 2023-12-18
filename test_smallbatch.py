import base64
import requests
import os
import random
from datetime import datetime, timedelta

# Zendesk API credentials and domain
email = os.environ.get("email")  # Replace with actual environment variable name for email
api_token = os.environ.get("ZENDESK_SBX_API_TOKEN")
zendesk_domain = os.environ.get("ZENDESK_SBX_DOMAIN")  # Change this to switch between sandbox and production

# Encode credentials for Basic Authentication
credentials = base64.b64encode(f'{email}/token:{api_token}'.encode('utf-8')).decode('utf-8')

def should_delete_ticket(ticket):
    created_at = datetime.strptime(ticket['created_at'], "%Y-%m-%dT%H:%M:%SZ")
    three_years_ago = datetime.now() - timedelta(days=3*365)
    return created_at < three_years_ago

def delete_ticket(ticket_id):
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    delete_endpoint = f"https://{zendesk_domain}.zendesk.com/api/v2/tickets/{ticket_id}.json"
    response = requests.delete(delete_endpoint, headers=headers)
    if response.status_code == 204:
        print(f"Deleted ticket {ticket_id} successfully.")
        return True
    else:
        print(f"Failed to delete ticket {ticket_id}. Status: {response.status_code}, Response: {response.text}")
        return False

def process_tickets():
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    response = requests.get(f"https://{zendesk_domain}.zendesk.com/api/v2/tickets.json", headers=headers)
    if response.status_code == 200:
        all_tickets = response.json().get('tickets', [])
        old_tickets = [ticket for ticket in all_tickets if should_delete_ticket(ticket)]
        selected_tickets = random.sample(old_tickets, min(len(old_tickets), 5))  # Select up to 5 old tickets

        for ticket in selected_tickets:
            delete_ticket(ticket['id'])
    else:
        print(f"Failed to fetch tickets. Status: {response.status_code}, Response: {response.text}")

# Example Usage
process_tickets()
