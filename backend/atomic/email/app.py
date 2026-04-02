import os
import base64
import json
from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

app = Flask(__name__)
CORS(app)
api = Api(app, doc="/docs",
    title="Email Service",
    version="1.0",
    description="Email atomic service - REST API version"
)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Paths for credentials
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")
TOKEN_PATH = os.path.join(BASE_DIR, "token.json")

# Global Gmail service instance
gmail_service = None

def init_gmail_service():
    """Initializes the Gmail API service using token.json or credentials.json."""
    global gmail_service
    creds = None
    
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if os.path.exists(CREDENTIALS_PATH):
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            else:
                print(f" [ERROR] '{CREDENTIALS_PATH}' not found. Cannot send emails.")
                return None
        
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    gmail_service = build('gmail', 'v1', credentials=creds)
    return gmail_service

def send_email(recipient, subject, body, reply_to=None):
    """Encodes and sends the email via Gmail API."""
    global gmail_service
    if not gmail_service:
        init_gmail_service()
        if not gmail_service:
            raise Exception("Gmail service not initialized.")

    try:
        message = EmailMessage()
        message.set_content(body)
        message['To'] = recipient
        message['From'] = "TuitionGo <me>"
        message['Subject'] = subject
        
        if reply_to:
            message['Reply-To'] = reply_to

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        raw_message = {'raw': encoded_message}
        
        gmail_service.users().messages().send(userId="me", body=raw_message).execute()
        print(f" [OK] Email sent to: {recipient}")
        return True
    except Exception as error:
        print(f" [ERROR] Failed to send email: {error}")
        raise error

# API Models
email_payload = api.model('EmailRequest', {
    'email': fields.String(required=True, description='Recipient email address'),
    'type': fields.String(required=True, description='Type of email (BOOKING_SUCCESS, CANCELLATION, etc.)'),
    'details': fields.Raw(description='Dynamic data for the email template'),
    'reply_to': fields.String(description='Optional Reply-To email address')
})

@api.route("/send-email")
class EmailSender(Resource):
    @api.expect(email_payload)
    def post(self):
        """Directly send an email based on the payload provided."""
        data = request.json
        recipient = data.get("email")
        email_type = data.get("type")
        details = data.get("details", {})
        reply_to = data.get("reply_to")

        if not recipient or not email_type:
            return {"error": "Missing email or type"}, 400

        # Define templates
        if email_type == "BOOKING_SUCCESS":
            subject = "Booking Confirmed - TuitionGo"
            content = (
                f"Hi {details.get('student_name', 'Student')}!\n\n"
                f"Your booking for {details.get('subject')} with {details.get('tutor_name')} is confirmed.\n"
                f"Date: {details.get('date')}\n"
                f"Time: {details.get('time')}\n"
                f"Meeting Link: {details.get('meeting_link')}\n\n"
                "Good luck with your session!"
            )
        elif email_type == "CANCELLATION":
            subject = "Session Cancelled - TuitionGo"
            content = f"Your session on {details.get('date')} for {details.get('subject')} has been cancelled."
        else:
            subject = "Notification - TuitionGo"
            content = "You have a new update regarding your session."

        try:
            send_email(recipient, subject, content, reply_to)
            return {"message": "Email sent successfully"}, 200
        except Exception as e:
            return {"error": str(e)}, 500

@api.route("/health")
class Health(Resource):
    def get(self):
        return {"status": "healthy", "service": "email", "gmail_connected": gmail_service is not None}, 200

if __name__ == "__main__":
    # Initialize Gmail service once on startup
    init_gmail_service()
    app.run(host="0.0.0.0", port=5006, debug=False)