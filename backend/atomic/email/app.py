import os
import base64
import json
import threading
import pika
from flask import Flask, jsonify
from flask_cors import CORS
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

app = Flask(__name__)
CORS(app)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Paths for credentials
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")
TOKEN_PATH = os.path.join(BASE_DIR, "token.json")

# RabbitMQ configuration
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
QUEUE_NAME = "email_queue"

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

def process_email_message(ch, method, properties, body):
    """Processes a message from RabbitMQ."""
    try:
        data = json.loads(body)
        recipient = data.get("email")
        email_type = data.get("type")
        details = data.get("details", {})
        reply_to = data.get("reply_to")

        if not recipient or not email_type:
            print(" [ERROR] Missing email or type in RabbitMQ message")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

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
            subject = "Canceled: Tuition Session - TuitionGo"
            content = (
                "This event has been canceled.\n\n"
                "Tuition session cancelled via TuitionGo.\n\n"
                "When\n"
                f"{details.get('date')}\n\n"
                "Organizer\n"
                f"{details.get('tutor_name')}\n"
                f"{details.get('tutor_email')}"
            )
        else:
            subject = "Notification - TuitionGo"
            content = "You have a new update regarding your session."

        send_email(recipient, subject, content, reply_to)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f" [OK] Processed email for: {recipient}")
    except Exception as e:
        print(f" [ERROR] Failed to process RabbitMQ message: {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

def start_rabbitmq_consumer():
    """Starts the RabbitMQ consumer with automatic reconnection on failure."""
    import time
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            channel.exchange_declare(exchange="tuitiongo.email", exchange_type="direct", durable=True)
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            channel.queue_bind(queue=QUEUE_NAME, exchange="tuitiongo.email", routing_key="notification.email")
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_email_message)

            print(f" [*] Waiting for messages in {QUEUE_NAME}. To exit press CTRL+C")
            channel.start_consuming()
        except Exception as e:
            print(f" [ERROR] RabbitMQ consumer error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "email-worker", 
        "gmail_connected": gmail_service is not None
    }), 200

if __name__ == "__main__":
    # Initialize Gmail service once on startup
    init_gmail_service()
    
    # Start RabbitMQ consumer in a background thread
    consumer_thread = threading.Thread(target=start_rabbitmq_consumer, daemon=True)
    consumer_thread.start()
    
    # Run simple Flask server for health checks
    app.run(host="0.0.0.0", port=5006, debug=False)
