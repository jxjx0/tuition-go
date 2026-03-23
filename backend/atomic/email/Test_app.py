from app import get_gmail_service, send_email
def test_single_email():
    print("--- Starting Email Test ---")
    # 1. Initialize the Gmail service
    # This might open a browser for login if token.json is missing
    service = get_gmail_service()
    if not service:
        print("Failed to initialize Gmail service. Check your credentials.json")
        return

    # 2. Define test details
    recipient = "fr.suwibowo.2024@computing.smu.edu.sg"  # <--- CHANGE THIS to your email
    subject = "Manual Test - TuitionGo"
    body = "This is a direct test of the send_email function."

    # 3. Send the email
    print(f"Attempting to send email to {recipient}...")
    send_email(service, recipient, subject, body)
    print("--- Test Complete ---")

if __name__ == "__main__":
    test_single_email()