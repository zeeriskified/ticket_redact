import requests
import os
import base64

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
        return response.json().get('comments', [])
    else:
        print(f"Error fetching comments for ticket {ticket_id}. Status: {response.status_code}, Response: {response.text}")
        return []

def redact_attachment(ticket_id, comment_id, attachment_id):
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    redact_endpoint = f"https://{zendesk_domain}.zendesk.com/api/v2/tickets/{ticket_id}/comments/{comment_id}/attachments/{attachment_id}/redact"
    
    response = requests.put(redact_endpoint, headers=headers)

    if response.status_code == 200:
        log_comment(ticket_id, f"Redacted attachment {attachment_id} in comment {comment_id}.")
    else:
        log_comment(ticket_id, f"Failed to redact attachment {attachment_id} in comment {comment_id}. Status: {response.status_code}, Response: {response.text}")

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
        print(f"Failed to log comment on ticket {ticket_id}. Status: {response.status_code}, Response: {response.text}")

def check_for_attachments_and_redact(ticket_id):
    comments = get_ticket_comments(ticket_id)
    for comment in comments:
        for attachment in comment.get('attachments', []):
            redact_attachment(ticket_id, comment['id'], attachment['id'])

# Specify the ticket ID here
ticket_id = "3863"  # Replace with the actual ticket ID
check_for_attachments_and_redact(ticket_id)
