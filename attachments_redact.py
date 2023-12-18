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
    return response.json().get('comments', []) if response.status_code == 200 else []

def redact_attachment(ticket_id, comment_id, attachment_id):
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    redact_endpoint = f"https://{zendesk_domain}.zendesk.com/api/v2/tickets/{ticket_id}/comments/{comment_id}/attachments/{attachment_id}/redact"
    
    response = requests.put(redact_endpoint, headers=headers)

    log_message = f"Redacted attachment {attachment_id} in comment {comment_id} of ticket {ticket_id} successfully." if response.status_code == 200 else f"Failed to redact attachment {attachment_id} in comment {comment_id} of ticket {ticket_id}. Status: {response.status_code}, Response: {response.text}"
    print(log_message)
    log_comment(ticket_id, log_message)

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
    requests.put(f"https://{zendesk_domain}.zendesk.com/api/v2/tickets/{ticket_id}.json", headers=headers, json=data)

def should_redact_attachment(ticket, comment):
    created_at = datetime.strptime(ticket['created_at'], "%Y-%m-%dT%H:%M:%SZ")
    three_months_ago = datetime.now() - timedelta(days=90)
    return created_at <= three_months_ago and any(comment.get('attachments', []))

def process_tickets():
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    response = requests.get(f"https://{zendesk_domain}.zendesk.com/api/v2/tickets.json", headers=headers)
    if response.status_code == 200:
        all_tickets = response.json().get('tickets', [])
        for ticket in all_tickets:
            comments = get_ticket_comments(ticket['id'])
            for comment in comments:
                if should_redact_attachment(ticket, comment):
                    for attachment in comment['attachments']:
                        redact_attachment(ticket['id'], comment['id'], attachment['id'])
    else:
        print(f"Failed to fetch tickets. Status: {response.status_code}, Response: {response.text}")

# Example Usage
process_tickets()
