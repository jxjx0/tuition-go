import requests
import os
import sys

# Add current directory to path so it can find app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import init_gmail_service, send_email

# --- CONFIGURATION ---
# Change this to your own email to see the result!
TEST_RECIPIENT = "fabreyns@gmail.com" 
API_URL = "http://127.0.0.1:5006/send-email"

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

def test_rest_api():
    """Tests the REST API endpoint. The Flask app MUST be running for this."""
    print("\n--- [2] Testing REST API Endpoint (Integration) ---")
    
    payload = {
        "email": TEST_RECIPIENT,
        "type": "BOOKING_SUCCESS",
        "reply_to": "tutor_contact@example.com",
        "details": {
            "student_name": "Test Student",
            "tutor_name": "Prof. Matrix",
            "subject": "Advanced Microservices",
            "date": "2024-12-25",
            "time": "10:00 AM",
            "meeting_link": "https://meet.google.com/test-link"
        }
    }

    try:
        print(f" [INFO] Sending POST request to {API_URL}...")
        response = requests.post(API_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f" [SUCCESS] API Response: {response.json()}")
        else:
            print(f" [FAIL] API returned status {response.status_code}: {response.text}")
            print(" [HINT] Is the Flask app running? Run 'python app.py' in another terminal.")
            
    except requests.exceptions.ConnectionError:
        print(" [FAIL] Could not connect to the server.")
        print("        ERROR: The server at http://127.0.0.1:5006 is not responding.")
        print("        ACTION: Open a new terminal and run 'python app.py' first.")
    except Exception as e:
        print(f" [ERROR] Unexpected error: {e}")

if __name__ == "__main__":
    print("TuitionGo Email Service Test Suite")
    print("==================================")
    
    # 1. Test the internal logic first (does not need the server)
    test_internal_functions()
    
    # 2. Test the API (NEEDS the server to be running in another terminal)
    test_rest_api()
