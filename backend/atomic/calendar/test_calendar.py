import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5005"

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check: {response.status_code}")
    print(response.json())

def test_create_meeting():
    start_time = (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z"
    end_time = (datetime.utcnow() + timedelta(hours=2)).isoformat() + "Z"
    
    payload = {
        "summary": "Test Tutor Session",
        "description": "Verification of Google Meet integration",
        "start_time": start_time,
        "end_time": end_time,
        "attendees": ["test@example.com"]
    }
    
    print(f"Creating meeting with payload: {json.dumps(payload, indent=2)}")
    response = requests.post(f"{BASE_URL}/create-meeting", json=payload)
    
    print(f"Create Meeting Response: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    try:
        test_health()
        print("-" * 20)
        test_create_meeting()
    except Exception as e:
        print(f"Error connecting to service: {e}")
        print("Note: Ensure the calendar service is running at http://localhost:5005")
