import requests
import os
import sys
import pika
import json

# Add current directory to path so it can find app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import init_gmail_service, send_email

# --- CONFIGURATION ---
# Change this to your own email to see the result!
TEST_RECIPIENT = "fabreyns@gmail.com" 
HEALTH_URL = "http://127.0.0.1:5006/health"
RABBITMQ_HOST = "localhost" # Change to 'rabbitmq' if running inside docker
QUEUE_NAME = "email_queue"

def test_internal_functions():
    """Tests the Gmail logic directly without using the web server."""
    print("\n--- [1] Testing Internal Functions (Verification) ---")
    
    # Initialize
    service = init_gmail_service()
    if not service:
        print(" [FAIL] Could not initialize Gmail service. check credentials.json")
        return False

    try:
        print(f" [INFO] Sending direct email to {TEST_RECIPIENT}...")
        send_email(
            recipient=TEST_RECIPIENT,
            subject="TuitionGo",
            body="If you see this, the Gmail Token and send_email function are working perfectly!",
            reply_to="support@tuitiongo.com"
        )
        print(" [SUCCESS] Function test passed.")
        return True
    except Exception as e:
        print(f" [FAIL] Function test failed: {e}")
        return False

def test_health_check():
    """Tests the health check endpoint."""
    print("\n--- [2] Testing Health Check Endpoint ---")
    try:
        response = requests.get(HEALTH_URL, timeout=10)
        if response.status_code == 200:
            print(f" [SUCCESS] Health Check: {response.json()}")
        else:
            print(f" [FAIL] Health check returned status {response.status_code}")
    except Exception as e:
        print(f" [FAIL] Could not connect to health check: {e}")

def test_rabbitmq_publisher():
    """Tests the RabbitMQ consumer by publishing a message to the queue."""
    print("\n--- [3] Testing RabbitMQ Publisher (Async Integration) ---")
    
    payload = {
        "email": TEST_RECIPIENT,
        "type": "BOOKING_SUCCESS",
        "reply_to": "tutor_contact@example.com",
        "details": {
            "student_name": "Test Student (RabbitMQ)",
            "tutor_name": "Prof. Rabbit",
            "subject": "Messaging Queues 101",
            "date": "2024-12-26",
            "time": "11:00 AM",
            "meeting_link": "https://meet.google.com/rabbitmq-link"
        }
    }

    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        
        print(f" [INFO] Publishing message to {QUEUE_NAME}...")
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=json.dumps(payload),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )
        print(" [SUCCESS] Message published. Check the email service logs for delivery confirmation.")
        connection.close()
    except Exception as e:
        print(f" [FAIL] RabbitMQ Publisher failed: {e}")
        print(" [HINT] Is RabbitMQ running? Check your docker containers.")

if __name__ == "__main__":
    print("TuitionGo Email Service Test Suite (Worker Version)")
    print("==================================================")
    
    # 1. Test the internal logic first (does not need the server)
    test_internal_functions()
    
    # 2. Test the Health Check
    test_health_check()

    # 3. Test RabbitMQ
    test_rabbitmq_publisher()
