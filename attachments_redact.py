import base64
import requests
import os
from datetime import datetime, timedelta

# Zendesk API credentials and domain
email = os.environ.get("email")  # Replace with actual environment variable name for email
api_token = os.environ.get("ZENDESK_SBX_API_TOKEN")
zendesk_domain = os.environ.get("ZENDESK_SBX_DOMAIN")

# Encode credentials for Basic Authentication
credentials = base64.b64encode(f'{email}/token:{api_token}'.encode('utf-8')).decode('utf-8')

def get_ticket_comments(ticket_id):
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    response = requests.get(f"https://{zendesk_domain}.zendesk.com/api/v2/tickets/{ticket_id}/comments.json", headers=headers)
    if response.status_code == 200:
        return response.json()['comments']
    return []

def redact_ticket_comments(ticket_id):
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    comments = get_ticket_comments(ticket_id)
    for comment in comments:
        if comment['attachments']:
            redact_endpoint = f"https://{zendesk_domain}.zendesk.com/api/v2/tickets/{ticket_id}/comments/{comment['id']}/redact.json"
            data = {"text": "This comment has been redacted due to age and content."}

            # Enhanced logging for debugging
            print(f"Attempting to redact comment {comment['id']} on ticket {ticket_id}")
            print(f"Redact endpoint: {redact_endpoint}")
            print(f"Data being sent: {data}")
            print(f"Headers: {headers}")

            response = requests.put(redact_endpoint, json=data, headers=headers)
            print(f"Redaction response status: {response.status_code}")
            print(f"Redaction response body: {response.text}")

            if response.status_code == 200:
                print(f"Comment {comment['id']} on ticket {ticket_id} redacted successfully.")
            else:
                print(f"Failed to redact comment {comment['id']} on ticket {ticket_id}.")

def should_redact_attachment(ticket):
    created_at = datetime.strptime(ticket['created_at'], "%Y-%m-%dT%H:%M:%SZ")
    three_months_ago = datetime.now() - timedelta(days=90)
    return created_at <= three_months_ago  # Check if the ticket is older than or equal to 3 months

def process_tickets():
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    response = requests.get(f"https://{zendesk_domain}.zendesk.com/api/v2/tickets.json", headers=headers)
    if response.status_code == 200:
        all_tickets = response.json()['tickets']
        for ticket in all_tickets:
            if should_redact_attachment(ticket):
                redact_ticket_comments(ticket['id'])

# Example Usage
process_tickets()