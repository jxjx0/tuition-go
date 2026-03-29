from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS
import os
import requests
import jwt as pyjwt

app = Flask(__name__)
CORS(app)
api = Api(app, doc="/docs",
    title="Book Session Service",
    version="1.0",
    description="Book Session composite service",
    prefix="/book-session"
)

SESSION_SERVICE_URL = os.environ.get("SESSION_SERVICE_URL", "http://localhost:5003")
TUTOR_SERVICE_URL = os.environ.get("TUTOR_SERVICE_URL", "http://localhost:5002")
PAYMENT_SERVICE_URL = os.environ.get("PAYMENT_SERVICE_URL", "http://localhost:5007")
STUDENT_SERVICE_URL = os.environ.get("STUDENT_SERVICE_URL", "http://localhost:5001")
CALENDAR_SERVICE_URL = os.environ.get("CALENDAR_SERVICE_URL", "http://localhost:5005")

checkout_input = api.model('CheckoutInput', {
    'session_id': fields.String(required=True, description='The session UUID to book'),
    'student_id': fields.String(required=True, description='The student UUID who is booking')
})


@api.route("/health")
class Health(Resource):
    def get(self):
        return {"status": "healthy", "service": "book_session"}, 200


@api.route("/checkout")
class Checkout(Resource):
    @api.expect(checkout_input)
    def post(self):
        """Create a Stripe checkout session for booking a tuition session."""
        data = request.get_json()
        session_id = data.get("session_id")
        student_id = data.get("student_id")
        if not session_id or not student_id:
            return {"message": "session_id and student_id are required"}, 400

        # 1. Fetch session from session atomic service
        session_resp = requests.get(
            f"{SESSION_SERVICE_URL}/session/{session_id}",
            timeout=5
        )
        if session_resp.status_code == 404:
            return {"message": "Session not found"}, 404
        if session_resp.status_code != 200:
            return {"message": "Failed to retrieve session"}, 500

        session = session_resp.json()
        tutor_id = session.get("tutorId")
        tutor_subject_id = session.get("tutorSubjectId")
        duration_mins = session.get("durationMins", 0)
        start_time = session.get("startTime", "")

        # 2. Fetch tutor subjects from tutor atomic service
        subjects_resp = requests.get(
            f"{TUTOR_SERVICE_URL}/tutor/{tutor_id}/subjects",
            timeout=5
        )
        if subjects_resp.status_code != 200:
            return {"message": "Failed to retrieve tutor subjects"}, 500

        subjects = subjects_resp.json()
        matching = next(
            (s for s in subjects if s.get("tutorSubjectId") == tutor_subject_id),
            None
        )
        if not matching:
            return {"message": "Tutor subject not found"}, 404

        hourly_rate = matching.get("hourlyRate", 0)
        subject_name = matching.get("subject", "Tuition")
        academic_level = matching.get("academicLevel", "")

        # 3. Fetch tutor name from tutor atomic service
        tutor_resp = requests.get(
            f"{TUTOR_SERVICE_URL}/tutor/{tutor_id}",
            timeout=5
        )
        tutor_name = "Tutor"
        if tutor_resp.status_code == 200:
            tutor_name = tutor_resp.json().get("name", "Tutor")

        # 4. Calculate price server-side
        total_price = round(hourly_rate * (duration_mins / 60.0), 2)
        amount_cents = int(total_price * 100)

        # 5. Call payment atomic service
        payment_resp = requests.post(
            f"{PAYMENT_SERVICE_URL}/payment/create-checkout-session",
            json={
                "title": f"{subject_name} ({academic_level})",
                "description": f"{int(duration_mins)} min session",
                "amount": amount_cents,
                "tutor_name": tutor_name,
                "subject": subject_name,
                "lesson_date": start_time,
                "session_id": session_id,
                "student_id": student_id,
                "tutor_id": tutor_id,
            },
            timeout=10
        )
        if payment_resp.status_code != 200:
            return {"message": "Failed to create checkout session"}, 500

        return payment_resp.json(), 200


process_booking_input = api.model('ProcessBookingInput', {
    'session_id':        fields.String(required=True, description='The session UUID'),
    'student_id':        fields.String(required=True, description='The student UUID'),
    'tutor_id':          fields.String(required=True, description='The tutor UUID'),
    'amount_total':      fields.Integer(description='Amount paid in cents'),
    'stripe_session_id': fields.String(description='Stripe checkout session ID'),
})


@api.route("/process-booking")
class ProcessBooking(Resource):
    @api.expect(process_booking_input)
    def post(self):
        """Called after successful Stripe payment to complete the booking."""
        data = request.get_json()
        session_id = data.get("session_id")
        if not session_id:
            return {"message": "session_id is required"}, 400

        auth_header = request.headers.get("Authorization", "")

        # 1. Extract student's Clerk user ID from their JWT
        token = auth_header.replace("Bearer ", "")
        try:
            claims = pyjwt.decode(token, options={"verify_signature": False})
            student_clerk_id = claims.get("sub")
        except Exception:
            return {"message": "Invalid authorization token"}, 401

        if not student_clerk_id:
            return {"message": "Could not identify student from token"}, 401

        # 2. Fetch session to get tutorId and calendarEventId
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

        # 2b. Fetch tutor to get their Clerk user ID
        tutor_resp = requests.get(
            f"{TUTOR_SERVICE_URL}/tutor/{tutor_id}",
            timeout=5
        )
        if tutor_resp.status_code != 200:
            return {"message": "Failed to retrieve tutor details"}, 500

        tutor_clerk_id = tutor_resp.json().get("clerkUserId")

        # 3. Fetch student email using their Clerk ID
        student_resp = requests.get(
            f"{STUDENT_SERVICE_URL}/student/by-clerk/{student_clerk_id}",
            headers={"Authorization": auth_header},
            timeout=5
        )
        if student_resp.status_code != 200:
            return {"message": "Failed to retrieve student details"}, 500

        student_email = student_resp.json().get("email")
        if not student_email:
            return {"message": "Student email not found"}, 500

        # 4. Update session status to booked and assign student
        student_id = data.get("student_id")
        update_resp = requests.put(
            f"{SESSION_SERVICE_URL}/session/{session_id}",
            json={"status": "booked", "studentId": student_id},
            headers={"Authorization": auth_header},
            timeout=5
        )
        if update_resp.status_code != 200:
            return {"message": "Failed to update session status"}, 500

        # 5. Update tutor's Google Calendar event with student as attendee
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
                    "session_id": session_id,
                    "calendarError": calendar_resp.json().get("error")
                }, 207
        else:
            return {
                "message": "Booking confirmed but no calendar event linked to this session",
                "session_id": session_id
            }, 200

        return {
            "message": "Booking confirmed and calendar updated",
            "session_id": session_id,
            "student_email": student_email
        }, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5100, debug=True)
