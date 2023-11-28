import base64
import requests
import random
import os
from datetime import datetime, timedelta

# Zendesk API credentials and domain
email = os.environ.get("email")  # Replace with actual environment variable name for email
api_token = os.environ.get("ZENDESK_SBX_API_TOKEN")
zendesk_domain = os.environ.get("ZENDESK_SBX_DOMAIN")# Change this to switch between sandbox and production



# Encode credentials for Basic Authentication
# credentials = base64.b64encode(f'{email}/token:{api_token}'.encode('utf-8')).decode('utf-8')
credentials = base64.b64encode(f'{email}/token:{api_token}'.encode('utf-8')).decode('utf-8')
print(f"Encoded credentials: {credentials}")  # Debugging print


# Define your criteria for deletion
def should_delete_ticket(ticket):
    created_at = datetime.strptime(ticket['created_at'], "%Y-%m-%dT%H:%M:%SZ")
    three_months_ago = datetime.now() - timedelta(days=90)

    # Check if the ticket is older than 3 months and has attachments
    if created_at < three_months_ago:
        for comment in ticket['comments']:
            if comment['attachments']:
                return True
    return False

# Fetch ticket comments with attachments info
def get_ticket_comments(ticket_id):
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    response = requests.get(f"https://{zendesk_domain}.zendesk.com/api/v2/tickets/{ticket_id}/comments.json", headers=headers)
    if response.status_code == 200:
        return response.json()['comments']
    return []

# Function to randomly select 3 tickets for deletion
def select_random_tickets(tickets, num=3):
    if len(tickets) > num:
        return random.sample(tickets, num)
    return tickets

# Temporary hardcoded domain for debugging
zendesk_domain = "riskified1644528081"  # Replace with your actual Zendesk subdomain

# Delete tickets

def delete_tickets():
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }

    response = requests.get(f"https://{zendesk_domain}.zendesk.com/api/v2/tickets.json", headers=headers)
    print(f"Attempting to fetch tickets from: https://{zendesk_domain}.zendesk.com/api/v2/tickets.json")  # Debugging print

    # response = requests.get(f"https://{zendesk_domain}.zendesk.com/api/v2/tickets.json", headers=headers)

    if response.status_code == 200:
        print("Fetched tickets successfully.")
        all_tickets = response.json()['tickets']
        print(f"Total tickets fetched: {len(all_tickets)}")
        
        selected_tickets = select_random_tickets(all_tickets, 3)
        print(f"Total tickets selected for deletion: {len(selected_tickets)}")

        for ticket in selected_tickets:
            ticket_id = ticket['id']
            ticket_subject = ticket['subject']
            ticket['comments'] = get_ticket_comments(ticket_id)
            if should_delete_ticket(ticket):
                delete_response = requests.delete(f"https://{zendesk_domain}.zendesk.com/api/v2/tickets/{ticket_id}.json", headers=headers)
                if delete_response.status_code == 204:
                    print(f"Ticket {ticket_id} - '{ticket_subject}' deleted successfully.")
                else:
                    print(f"Failed to delete ticket {ticket_id} - '{ticket_subject}'. Status: {delete_response.status_code}")
            else:
                print(f"Ticket {ticket_id} - '{ticket_subject}' does not meet deletion criteria.")
    else:
        print(f"Failed to fetch tickets. Status: {response.status_code}, Message: {response.text}")



# Example Usage
delete_tickets()