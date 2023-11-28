# Delete old Zendesk tickets that are 3 months or older

import requests
from datetime import datetime, timedelta

# Zendesk API credentials and domain
api_token = "your_api_token"
zendesk_domain = "riskified1644528081"  # Change this to switch between sandbox and production

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
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(f"https://{zendesk_domain}.zendesk.com/api/v2/tickets/{ticket_id}/comments.json", headers=headers)
    if response.status_code == 200:
        return response.json()['comments']
    return []

# Delete tickets
def delete_tickets():
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    tickets = requests.get(f"https://{zendesk_domain}.zendesk.com/api/v2/tickets.json", headers=headers).json()
    for ticket in tickets['tickets']:
        ticket['comments'] = get_ticket_comments(ticket['id'])
        if should_delete_ticket(ticket):
            ticket_id = ticket['id']
            response = requests.delete(f"https://{zendesk_domain}.zendesk.com/api/v2/tickets/{ticket_id}.json", headers=headers)
            if response.status_code == 204:
                print(f"Ticket {ticket_id} deleted successfully.")
            else:
                print(f"Failed to delete ticket {ticket_id}. Status: {response.status_code}")

# Example Usage
delete_tickets()
