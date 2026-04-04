import os
import base64
import json
import threading
import pika
from flask import Flask, jsonify
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
    description=(
        "Email worker service. Sends transactional emails via Gmail API. "
        "Emails are triggered by publishing messages to the **tuitiongo.email** RabbitMQ exchange "
        "(routing key: `notification.email`). "
        "Supported `type` values: `BOOKING_SUCCESS`, `BOOKING_TUTOR`, `CANCELLATION_STUDENT`, `CANCELLATION_TUTOR`."
    ),
    prefix="/email"
)

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
        elif email_type == "BOOKING_TUTOR":
            subject = "New Booking Received - TuitionGo"
            content = (
                f"Hi {details.get('tutor_name', 'Tutor')}!\n\n"
                f"You have a new booking from {details.get('student_name')} for {details.get('subject')}.\n"
                f"Date: {details.get('date')}\n"
                f"Time: {details.get('time')}\n"
                f"Meeting Link: {details.get('meeting_link')}\n\n"
                "Please be ready for the session!"
            )
        elif email_type == "CANCELLATION_STUDENT":
            subject = "Session Cancelled - TuitionGo"
            content = (
                f"Hi {details.get('student_name', 'Student')}!\n\n"
                f"Your session for {details.get('subject')} with {details.get('tutor_name')} has been cancelled.\n\n"
                f"When: {details.get('date')}\n\n"
                "If you paid for this session, your refund will be processed shortly.\n\n"
                "We hope to see you book again soon!"
            )
        elif email_type == "CANCELLATION_TUTOR":
            subject = "Booking Cancelled - TuitionGo"
            content = (
                f"Hi {details.get('tutor_name', 'Tutor')}!\n\n"
                f"{details.get('student_name')} has cancelled their booking for {details.get('subject')}.\n\n"
                f"When: {details.get('date')}\n\n"
                "The slot has been restored and is available for new bookings."
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

health_response_model = api.model('EmailHealthResponse', {
    'status': fields.String(description='Service status', example='healthy'),
    'service': fields.String(description='Service name', example='email-worker'),
    'gmail_connected': fields.Boolean(description='Whether the Gmail API service is initialised', example=True),
})


@api.route("/health")
class Health(Resource):
    @api.response(200, 'Service is healthy', health_response_model)
    def get(self):
        """
        Health check. Also reports whether the Gmail API service is connected.

        **RabbitMQ message format** (publish to exchange `tuitiongo.email`, routing key `notification.email`):
        ```json
        {
          "email": "recipient@example.com",
          "type": "BOOKING_SUCCESS",
          "details": {
            "student_name": "Alice Tan",
            "tutor_name": "Mr John Lim",
            "subject": "Mathematics",
            "date": "Saturday 05 Apr 2026",
            "time": "10am – 11am (Singapore Standard Time)",
            "meeting_link": "https://meet.google.com/abc-defg-hij"
          }
        }
        ```

        **Supported `type` values:**
        - `BOOKING_SUCCESS` — sent to student on successful booking
        - `BOOKING_TUTOR` — sent to tutor on new booking
        - `CANCELLATION_STUDENT` — sent to student on cancellation
        - `CANCELLATION_TUTOR` — sent to tutor on cancellation
        """
        return jsonify({
            "status": "healthy",
            "service": "email-worker",
            "gmail_connected": gmail_service is not None
        })

if __name__ == "__main__":
    # Initialize Gmail service once on startup
    init_gmail_service()
    
    # Start RabbitMQ consumer in a background thread
    consumer_thread = threading.Thread(target=start_rabbitmq_consumer, daemon=True)
    consumer_thread.start()
    
    # Run simple Flask server for health checks
    app.run(host="0.0.0.0", port=5006, debug=False)
