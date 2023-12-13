import base64
import requests
import os
from datetime import datetime, timedelta

# Zendesk API credentials and domain
email = os.environ.get("email")
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
        print(f"Comments fetched for ticket {ticket_id}")
        return response.json().get('comments', [])
    else:
        print(f"Failed to fetch comments for ticket {ticket_id}. Status: {response.status_code}")
        return []

def redact_comment(ticket_id, comment_id):
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    redact_endpoint = f"https://{zendesk_domain}.zendesk.com/api/v2/tickets/{ticket_id}/comments/{comment_id}/redact.json"
    data = {"text": "This comment has been redacted due to containing sensitive information."}

    response = requests.put(redact_endpoint, json=data, headers=headers)
    if response.status_code == 200:
        print(f"Comment {comment_id} on ticket {ticket_id} redacted successfully.")
        log_comment(ticket_id, f"Redacted comment {comment_id} successfully.")
    else:
        print(f"Failed to redact comment {comment_id} on ticket {ticket_id}. Status: {response.status_code}")
        log_comment(ticket_id, f"Failed to redact comment {comment_id}. Status: {response.status_code}")

def log_comment(ticket_id, text):
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    data = {
        "ticket": {
            "comment": {
                "body": text,
                "public": False
            }
        }
    }
    response = requests.put(f"https://{zendesk_domain}.zendesk.com/api/v2/tickets/{ticket_id}.json", headers=headers, json=data)
    if response.status_code != 200:
        print(f"Failed to log comment on ticket {ticket_id}. Status: {response.status_code}")

def process_all_tickets():
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    response = requests.get(f"https://{zendesk_domain}.zendesk.com/api/v2/tickets.json", headers=headers)
    if response.status_code == 200:
        tickets = response.json()['tickets']
        print(f"Processing {len(tickets)} tickets")
        for ticket in tickets:
            comments = get_ticket_comments(ticket['id'])
            for comment in comments:
                if comment['attachments']:
                    redact_comment(ticket['id'], comment['id'])
    else:
        print(f"Failed to fetch tickets. Status: {response.status_code}")

# Run the script
process_all_tickets()