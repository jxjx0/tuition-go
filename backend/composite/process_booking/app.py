from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS
import os
import requests
import jwt as pyjwt

app = Flask(__name__)
CORS(app)
api = Api(app, doc="/docs",
    title="Process Booking Service",
    version="1.0",
    description="Process Booking composite service",
    prefix="/process-booking"
)

SESSION_SERVICE_URL = os.environ.get("SESSION_SERVICE_URL", "http://localhost:5003")
TUTOR_SERVICE_URL = os.environ.get("TUTOR_SERVICE_URL", "http://localhost:5002")
STUDENT_SERVICE_URL = os.environ.get("STUDENT_SERVICE_URL", "http://localhost:5001")
CALENDAR_SERVICE_URL = os.environ.get("CALENDAR_SERVICE_URL", "http://localhost:5005")
PAYMENT_SERVICE_URL = os.environ.get("PAYMENT_SERVICE_URL", "http://localhost:5007")

process_booking_input = api.model('ProcessBookingInput', {
    'stripe_session_id': fields.String(required=True, description='Stripe checkout session ID'),
})


@api.route("/health")
class Health(Resource):
    def get(self):
        return {"status": "healthy", "service": "process_booking"}, 200


@api.route("/process-booking")
class ProcessBooking(Resource):
    @api.expect(process_booking_input)
    def post(self):
        """Called after successful Stripe payment to complete the booking."""
        data = request.get_json()
        stripe_session_id = data.get("stripe_session_id")
        if not stripe_session_id:
            return {"message": "stripe_session_id is required"}, 400

        auth_header = request.headers.get("Authorization", "")

        # 1. Verify payment and extract booking context from Stripe metadata
        payment_resp = requests.post(
            f"{PAYMENT_SERVICE_URL}/payment/verify",
            json={"stripe_session_id": stripe_session_id},
            timeout=10
        )
        if payment_resp.status_code == 402:
            return {"message": "Payment not completed"}, 402
        if payment_resp.status_code != 200:
            return {"message": "Failed to verify payment"}, 500

        payment_data = payment_resp.json()
        session_id = payment_data.get("session_id")
        student_id = payment_data.get("student_id")

        if not session_id or not student_id:
            return {"message": "Missing booking context in payment metadata"}, 500

        # 2. Extract student's Clerk user ID from their JWT
        token = auth_header.replace("Bearer ", "")
        try:
            claims = pyjwt.decode(token, options={"verify_signature": False})
            student_clerk_id = claims.get("sub")
        except Exception:
            return {"message": "Invalid authorization token"}, 401

        if not student_clerk_id:
            return {"message": "Could not identify student from token"}, 401

        # 3. Fetch session to get tutorId and calendarEventId
        session_resp = requests.get(
            f"{SESSION_SERVICE_URL}/session/{session_id}",
            headers={"Authorization": auth_header},
            timeout=5
        )
        if session_resp.status_code != 200:
            return {"message": "Failed to retrieve session"}, 500

        session = session_resp.json()
        tutor_id = session.get("tutorId")
        calendar_event_id = session.get("calendarEventId")
        tutor_subject_id = session.get("tutorSubjectId")
        start_time = session.get("startTime")

        # 4. Fetch tutor to get their name and Clerk user ID
        tutor_resp = requests.get(
            f"{TUTOR_SERVICE_URL}/tutor/{tutor_id}",
            timeout=5
        )
        if tutor_resp.status_code != 200:
            return {"message": "Failed to retrieve tutor details"}, 500

        tutor_name = tutor_resp.json().get("name", "Tutor")
        tutor_clerk_id = tutor_resp.json().get("clerkUserId")

        # 5. Fetch tutor subjects to get subject name
        subjects_resp = requests.get(
            f"{TUTOR_SERVICE_URL}/tutor/{tutor_id}/subjects",
            timeout=5
        )
        subject_name = "Tutoring Session"
        if subjects_resp.status_code == 200:
            subjects = subjects_resp.json()
            matching = next(
                (s for s in subjects if s.get("tutorSubjectId") == tutor_subject_id),
                None
            )
            if matching:
                subject_name = matching.get("subject", "Tutoring Session")

        # 6. Fetch student email and name using their Clerk ID
        student_resp = requests.get(
            f"{STUDENT_SERVICE_URL}/student/by-clerk/{student_clerk_id}",
            headers={"Authorization": auth_header},
            timeout=5
        )
        if student_resp.status_code != 200:
            return {"message": "Failed to retrieve student details"}, 500

        student_email = student_resp.json().get("email")
        student_name = student_resp.json().get("name", "Student")
        if not student_email:
            return {"message": "Student email not found"}, 500

        # 7. Update session status to booked, assign student, and store Stripe session ID for future refunds
        student_id = data.get("student_id")
        stripe_session_id = data.get("stripe_session_id")
        update_payload = {"status": "booked", "studentId": student_id}
        if stripe_session_id:
            update_payload["stripeSessionId"] = stripe_session_id

        update_resp = requests.put(
            f"{SESSION_SERVICE_URL}/session/{session_id}",
            json=update_payload,
            headers={"Authorization": auth_header},
            timeout=5
        )
        if update_resp.status_code != 200:
            return {"message": "Failed to update session status"}, 500

        # 8. Update tutor's Google Calendar event with student as attendee
        if calendar_event_id and tutor_clerk_id:
            calendar_resp = requests.post(
                f"{CALENDAR_SERVICE_URL}/calendar/update-meeting",
                json={
                    "eventId": calendar_event_id,
                    "tutorClerkId": tutor_clerk_id,
                    "studentEmail": student_email
                },
                headers={"Authorization": auth_header},
                timeout=10
            )
            if calendar_resp.status_code != 200:
                # Non-fatal — session is booked, calendar update failed
                return {
                    "message": "Booking confirmed but calendar update failed",
                    "sessionId": session_id,
                    "student_email": student_email,
                    "student_name": student_name,
                    "tutor_name": tutor_name,
                    "amount_paid": payment_data.get("amount_total", 0),
                    "start_time": start_time,
                    "end_time": session.get("endTime"),
                    "subject": subject_name,
                    "status": "booked",
                    "calendarError": calendar_resp.json().get("error")
                }, 207
        else:
            return {
                "message": "Booking confirmed but no calendar event linked to this session",
                "sessionId": session_id,
                "student_email": student_email,
                "student_name": student_name,
                "tutor_name": tutor_name,
                "amount_paid": payment_data.get("amount_total", 0),
                "start_time": start_time,
                "end_time": session.get("endTime"),
                "subject": subject_name,
                "status": "booked"
            }, 200

        return {
            "message": "Booking confirmed and calendar updated",
            "session_id": session_id,
            "student_id": student_id,
            "tutor_id":   tutor_id,
            "amount_total": data.get("amount_total"),
            "stripe_session_id": stripe_session_id,
            "student_email": student_email
        }, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5104, debug=True)
