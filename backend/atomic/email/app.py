import os
import base64
import json
import threading
import pika
from flask import Flask
from flask_restx import Api, Resource
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
    description="Email atomic service - Message Consumer"
)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Determine the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")
TOKEN_PATH = os.path.join(BASE_DIR, "token.json")

def get_gmail_service():
    """Initializes the Gmail API service using token.json or credentials.json."""
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
                print(f"Error: '{CREDENTIALS_PATH}' not found.")
                return None
        
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def send_email(service, recipient, subject, body):
    """Encodes and sends the email via Gmail API."""
    try:
        message = EmailMessage()
        message.set_content(body)
        message['To'] = recipient
        message['From'] = 'me'
        message['Subject'] = subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        raw_message = {'raw': encoded_message}
        
        service.users().messages().send(userId="me", body=raw_message).execute()
        print(f" [OK] Email sent to: {recipient}")
    except Exception as error:
        print(f" [ERROR] Failed to send email: {error}")

def callback(ch, method, properties, body):
    """Callback for RabbitMQ consumer."""
    try:
        payload = json.loads(body)
        print(f" [x] Received: {payload}")

        email_type = payload.get("type")
        recipient = payload.get("email")
        details = payload.get("details", {})

        if email_type == "BOOKING_SUCCESS":
            subject = "Booking Confirmed - TuitionGo"
            content = f"Hi! Your booking for {details.get('subject')} with {details.get('tutor')} is confirmed."
        elif email_type == "CANCELLATION":
            subject = "Session Cancelled - TuitionGo"
            content = f"Your session on {details.get('date')} has been cancelled."
        else:
            subject = "Notification - TuitionGo"
            content = "You have a new update regarding your session."

        service = get_gmail_service()
        if service:
            send_email(service, recipient, subject, content)
        else:
            print(" [ERROR] Gmail service not initialized.")

    except Exception as e:
        print(f" [ERROR] Message processing failed: {e}")

def run_consumer():
    """Starts the RabbitMQ consumer in a background thread."""
    rabbit_host = os.environ.get("RABBITMQ_HOST", "localhost")
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host))
        channel = connection.channel()
        channel.queue_declare(queue='email_queue', durable=True)
        channel.basic_consume(queue='email_queue', on_message_callback=callback, auto_ack=True)
        print(' [*] Email Consumer started. Waiting for messages...')
        channel.start_consuming()
    except Exception as e:
        print(f" [ERROR] RabbitMQ Connection failed: {e}")

@api.route("/health")
class Health(Resource):
    def get(self):
        return {"status": "healthy", "service": "email"}, 200

if __name__ == "__main__":
    # Start consumer thread
    consumer_thread = threading.Thread(target=run_consumer, daemon=True)
    consumer_thread.start()
    
    # Start Flask app
    app.run(host="0.0.0.0", port=5006, debug=False) # debug=False to avoid starting thread twice
