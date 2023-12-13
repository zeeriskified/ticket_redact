import requests
import base64
import os


# Zendesk API credentials and domain
email = os.environ.get("email")  # Replace with actual environment variable name for email
api_token = os.environ.get("ZENDESK_SBX_API_TOKEN")
zendesk_domain = os.environ.get("ZENDESK_SBX_DOMAIN")


# Encode credentials for Basic Authentication
credentials = base64.b64encode(f'{email}/token:{api_token}'.encode('utf-8')).decode('utf-8')

def upload_attachment(file_path):
    headers = {
        "Authorization": f"Basic {credentials}"
    }
    files = {
        'file': open(file_path, 'rb')
    }
    response = requests.post(f"https://{zendesk_domain}.zendesk.com/api/v2/uploads.json?filename={os.path.basename(file_path)}", 
                             headers=headers, files=files)
    if response.status_code == 201:
        return response.json()['upload']['token']
    else:
        print(f"Failed to upload attachment. Status: {response.status_code}, Response: {response.text}")
        return None

def create_ticket_with_attachment(attachment_token):
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    data = {
        "ticket": {
            "subject": "Test with Attachment Zee test",
            "comment": {
                "body": "This is a test ticket with an attachment for Zee.",
                "uploads": [attachment_token]
            }
        }
    }
    response = requests.post(f"https://{zendesk_domain}.zendesk.com/api/v2/tickets.json", 
                             headers=headers, json=data)
    if response.status_code == 201:
        print("Ticket created successfully.")
    else:
        print(f"Failed to create ticket. Status: {response.status_code}, Response: {response.text}")

def generate_tickets(batch_size=5):
    file_path = "/Users/zeeperezcanals/Desktop/test.jpg"  # Update this with the path to your attachment file
    for _ in range(batch_size):
        attachment_token = upload_attachment(file_path)
        if attachment_token:
            create_ticket_with_attachment(attachment_token)

# Example usage
generate_tickets()
