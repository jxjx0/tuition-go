from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS
import os
import json
import requests
import jwt as pyjwt
import pika
from datetime import datetime, timezone, timedelta

app = Flask(__name__)
CORS(app)
api = Api(app, doc="/docs",
    title="Process Booking Service",
    version="1.0",
    description="Process Booking composite service",
    prefix="/process-booking"
)

SESSION_SERVICE_URL  = os.environ.get("SESSION_SERVICE_URL",  "http://localhost:5003")
TUTOR_SERVICE_URL    = os.environ.get("TUTOR_SERVICE_URL",    "http://localhost:5002")
STUDENT_SERVICE_URL  = os.environ.get("STUDENT_SERVICE_URL",  "http://localhost:5001")
CALENDAR_SERVICE_URL = os.environ.get("CALENDAR_SERVICE_URL", "http://localhost:5005")
PAYMENT_SERVICE_URL  = os.environ.get("PAYMENT_SERVICE_URL",  "http://localhost:5007")
RABBITMQ_HOST        = os.environ.get("RABBITMQ_HOST",        "localhost")


def publish_email(routing_key, payload):
    """Fire-and-forget publish to tuitiongo.email exchange."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.exchange_declare(exchange="tuitiongo.email", exchange_type="direct", durable=True)
    channel.basic_publish(
        exchange="tuitiongo.email",
        routing_key=routing_key,
        body=json.dumps(payload),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()


def _extract_clerk_id(auth_header):
    """Decode JWT and return the 'sub' claim (Clerk user ID), or raise ValueError."""
    token = auth_header.replace("Bearer ", "")
    try:
        claims = pyjwt.decode(token, options={"verify_signature": False})
    except Exception:
        raise ValueError("Invalid authorization token")
    clerk_id = claims.get("sub")
    if not clerk_id:
        raise ValueError("Could not identify student from token")
    return clerk_id


def _format_booking_time(start_time_str, end_time_str):
    """
    Parse Supabase startTime/endTime (SGT wall-clock stored as UTC) and return
    a (date_str, time_str) tuple in SGT for the BOOKING_SUCCESS email template.

    e.g. ("Saturday 05 Apr 2026", "9:30am – 10:30am (Singapore Standard Time)")
    """
    def _parse_sgt(s):
        clean = s.replace(" ", "T").replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        # DB stores SGT wall-clock as a UTC number — no real offset shift needed for display
        return dt

    def _fmt_time(dt):
        fmt = "%I:%M%p" if dt.minute != 0 else "%I%p"
        return dt.strftime(fmt).lower().lstrip("0") or "12am"

    try:
        display_start = _parse_sgt(start_time_str)
        date_str = display_start.strftime("%A %d %b %Y")

        try:
            display_end = _parse_sgt(end_time_str)
        except Exception:
            display_end = display_start + timedelta(hours=1)

        time_str = f"{_fmt_time(display_start)} – {_fmt_time(display_end)} (Singapore Standard Time)"
        return date_str, time_str
    except Exception:
        return start_time_str, end_time_str


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

        # ── Step 1: Verify payment and extract booking context from Stripe metadata (PAYMENT ATOMIC SERVICE) ──
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

        # ── Step 2: Extract student Clerk ID from JWT ──────────────────────────
        try:
            student_clerk_id = _extract_clerk_id(auth_header)
        except ValueError as e:
            return {"message": str(e)}, 401

        # ── Step 3: Fetch session (SESSION ATOMIC SERVICE) ──────────────────────────────────────────────
        session_resp = requests.get(
            f"{SESSION_SERVICE_URL}/session/{session_id}",
            headers={"Authorization": auth_header},
            timeout=5
        )
        if session_resp.status_code != 200:
            return {"message": "Failed to retrieve session"}, 500

        session = session_resp.json()
        tutor_id          = session.get("tutorId")
        calendar_event_id = session.get("calendarEventId")
        tutor_subject_id  = session.get("tutorSubjectId")
        start_time        = session.get("startTime")
        end_time          = session.get("endTime")

        # ── Step 4: Fetch tutor details and resolve subject name (TUTOR ATOMIC SERVICE) ───────────────
        tutor_resp = requests.get(f"{TUTOR_SERVICE_URL}/tutor/{tutor_id}", timeout=5)
        if tutor_resp.status_code != 200:
            return {"message": "Failed to retrieve tutor details"}, 500

        tutor_data     = tutor_resp.json()
        tutor_name     = tutor_data.get("name", "Tutor")
        tutor_clerk_id = tutor_data.get("clerkUserId")
        tutor_email    = tutor_data.get("email")

        matching     = next((s for s in tutor_data.get("subjects", []) if s.get("tutorSubjectId") == tutor_subject_id), None)
        subject_name = matching.get("subject", "Tutoring Session") if matching else "Tutoring Session"

        # ── Step 5: Fetch student details  (STUDENT ATOMIC SERVICE) ─────────────────────────────────────
        student_resp = requests.get(
            f"{STUDENT_SERVICE_URL}/student/by-clerk/{student_clerk_id}",
            headers={"Authorization": auth_header},
            timeout=5
        )
        if student_resp.status_code != 200:
            return {"message": "Failed to retrieve student details"}, 500

        student_data  = student_resp.json()
        student_email = student_data.get("email")
        student_name  = student_data.get("name", "Student")

        if not student_email:
            return {"message": "Student email not found"}, 500

        # ── Step 6: Update session — booked, assign student + stripe ref (SESSION ATOMIC SERVICE) ───────
        update_resp = requests.put(
            f"{SESSION_SERVICE_URL}/session/{session_id}",
            json={"status": "booked", "studentId": student_id, "stripeSessionId": stripe_session_id},
            headers={"Authorization": auth_header},
            timeout=5
        )
        if update_resp.status_code != 200:
            return {"message": "Failed to update session status"}, 500

        # ── Step 7: Add student to tutor's Google Calendar event (CALENDAR ATOMIC SERVICE) ───────────────
        base_response = {
            "sessionId":    session_id,
            "student_email": student_email,
            "student_name": student_name,
            "tutor_name":   tutor_name,
            "amount_paid":  payment_data.get("amount_total", 0),
            "start_time":   start_time,
            "end_time":     end_time,
            "subject":      subject_name,
            "status":       "booked"
        }

        meeting_link = None
        calendar_updated = False
        calendar_error = None

        if calendar_event_id and tutor_clerk_id:
            calendar_resp = requests.post(
                f"{CALENDAR_SERVICE_URL}/calendar/update-meeting",
                json={
                    "eventId":      calendar_event_id,
                    "tutorClerkId": tutor_clerk_id,
                    "studentEmail": student_email
                },
                headers={"Authorization": auth_header},
                timeout=10
            )
            if calendar_resp.status_code == 200:
                meeting_link = calendar_resp.json().get("hangoutLink")
                calendar_updated = True
            else:
                calendar_error = calendar_resp.json().get("error")

        # ── Step 8: Send booking confirmation emails (EMAIL ATOMIC SERVICE) ───────────────────────────
        email_notified = False
        email_error = None
        try:
            print(f"[EMAIL] start_time={start_time!r} end_time={end_time!r}")
            print(f"[EMAIL] student_email={student_email!r} tutor_email={tutor_email!r}")

            date_str, time_str = _format_booking_time(start_time, end_time)
            print(f"[EMAIL] formatted date={date_str!r} time={time_str!r}")

            email_details = {
                "student_name": student_name,
                "tutor_name":   tutor_name,
                "subject":      subject_name,
                "date":         date_str,
                "time":         time_str,
                "meeting_link": meeting_link or "To be confirmed"
            }

            publish_email("notification.email", {"email": student_email, "type": "BOOKING_SUCCESS", "details": email_details})
            print(f"[EMAIL] Published to student: {student_email}")

            publish_email("notification.email", {"email": tutor_email, "type": "BOOKING_SUCCESS", "details": email_details})
            print(f"[EMAIL] Published to tutor: {tutor_email}")

            email_notified = True
        except Exception as e:
            email_error = str(e)
            print(f"[EMAIL ERROR] {email_error}")

        return {**base_response, "message": "Booking confirmed", "meetingLink": meeting_link, "calendar_updated": calendar_updated, "calendar_error": calendar_error, "email_notified": email_notified, "email_error": email_error}, 200


@api.route("/booking-details/<string:stripe_session_id>")
class BookingDetails(Resource):
    def get(self, stripe_session_id):
        """Fetch session details for payment failed/success page using Stripe session ID."""
        auth_header = request.headers.get("Authorization", "")

        # 1. Retrieve Stripe session to get metadata
        payment_resp = requests.get(
            f"{PAYMENT_SERVICE_URL}/payment/stripe-session/{stripe_session_id}",
            headers={"Authorization": auth_header},
            timeout=10
        )
        if payment_resp.status_code != 200:
            return {"message": "Failed to retrieve Stripe session"}, 404

        payment_data = payment_resp.json()
        session_id = payment_data.get("session_id")
        student_id = payment_data.get("student_id")

        if not session_id:
            return {"message": "No session found for this Stripe session"}, 404

        # 2. Fetch session details
        session_resp = requests.get(
            f"{SESSION_SERVICE_URL}/session/{session_id}",
            headers={"Authorization": auth_header},
            timeout=5
        )
        if session_resp.status_code != 200:
            return {"message": "Failed to retrieve session"}, 500

        session          = session_resp.json()
        tutor_id         = session.get("tutorId")
        tutor_subject_id = session.get("tutorSubjectId")

        # 3. Fetch tutor details + subject name
        tutor_resp = requests.get(
            f"{TUTOR_SERVICE_URL}/tutor/{tutor_id}",
            headers={"Authorization": auth_header},
            timeout=5
        )
        if tutor_resp.status_code != 200:
            return {"message": "Failed to retrieve tutor details"}, 500

        tutor_data   = tutor_resp.json()
        tutor_name   = tutor_data.get("name", "Tutor")
        matching     = next((s for s in tutor_data.get("subjects", []) if s.get("tutorSubjectId") == tutor_subject_id), None)
        subject_name = matching.get("subject", "Tutoring Session") if matching else "Tutoring Session"

        return {
            "sessionId":   session_id,
            "studentId":   student_id,
            "tutor_name":  tutor_name,
            "subject":     subject_name,
            "amount_paid": payment_data.get("amount_total", 0),
            "start_time":  session.get("startTime"),
            "end_time":    session.get("endTime"),
            "status":      session.get("status"),
        }, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5104, debug=True)
