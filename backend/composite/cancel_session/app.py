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
    title="Cancel Session Service",
    version="1.0",
    description="Cancel Session composite service",
    prefix="/cancel-session"
)

SESSION_SERVICE_URL  = os.environ.get("SESSION_SERVICE_URL",  "http://localhost:5003")
TUTOR_SERVICE_URL    = os.environ.get("TUTOR_SERVICE_URL",    "http://localhost:5002")
STUDENT_SERVICE_URL  = os.environ.get("STUDENT_SERVICE_URL",  "http://localhost:5001")
PAYMENT_SERVICE_URL  = os.environ.get("PAYMENT_SERVICE_URL",  "http://localhost:5007")
CALENDAR_SERVICE_URL = os.environ.get("CALENDAR_SERVICE_URL", "http://localhost:5005")
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


def _parse_session_start_utc(start_time_str):
    """
    Parse a Supabase startTime string into an absolute UTC datetime.

    Supabase stores SGT times as fixed UTC offsets (e.g. 18:00+00 meaning
    18:00 SGT, not 18:00 UTC). We subtract 8 hours to get the real UTC instant.
    """
    clean = start_time_str.replace(" ", "T")
    if clean.endswith("Z"):
        clean = clean.replace("Z", "+00:00")
    dt = datetime.fromisoformat(clean)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    # DB stores SGT wall-clock as a UTC number — subtract 8 h for real UTC
    return dt - timedelta(hours=8)


def _format_email_when(session_start_utc, end_time_str):
    """
    Return a human-readable session time string in SGT, e.g.
    "Thursday 02 Apr 2026 ⋅ 6pm – 7pm (Singapore Standard Time)"
    """
    display_start = session_start_utc + timedelta(hours=8)
    try:
        base_end = datetime.fromisoformat(end_time_str.replace(" ", "T").replace("Z", "+00:00"))
        display_end = base_end.astimezone(timezone.utc)
    except Exception:
        display_end = display_start + timedelta(hours=1)

    def _fmt_time(dt):
        fmt = "%I:%M%p" if dt.minute != 0 else "%I%p"
        return dt.strftime(fmt).lower().lstrip("0") or "12am"

    fmt_date       = display_start.strftime("%A %d %b %Y")
    fmt_start_time = _fmt_time(display_start)
    fmt_end_time   = _fmt_time(display_end)
    return f"{fmt_date} ⋅ {fmt_start_time} – {fmt_end_time} (Singapore Standard Time)"


cancel_input_model = api.model('CancelInput', {
    'session_id': fields.String(required=True, description='The session UUID', example='a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'),
    'student_id': fields.String(required=True, description='The student UUID', example='b5eebc99-9c0b-4ef8-bb6d-6bb9bd380a22'),
})

cancel_success_model = api.model('CancelSessionResponse', {
    'message': fields.String(example='Session cancelled successfully'),
    'session_id': fields.String(example='a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'),
    'refund_status': fields.String(description='Stripe refund status or "skipped" if no payment was made', example='succeeded'),
    'calendar_updated': fields.Boolean(example=True),
    'email_notified': fields.Boolean(example=True),
})

cancel_error_model = api.model('CancelSessionError', {
    'message': fields.String(description='Error message', example='You are not authorised to cancel this session'),
})


@api.route("/health")
class Health(Resource):
    @api.response(200, 'Service is healthy')
    def get(self):
        """Health check."""
        return {"status": "healthy", "service": "cancel_session"}, 200


@api.route("/cancel")
class CancelSession(Resource):

    @api.expect(cancel_input_model)
    @api.response(200, 'Session cancelled successfully', cancel_success_model)
    @api.response(400, 'Missing required fields', cancel_error_model)
    @api.response(401, 'Invalid or missing Bearer JWT', cancel_error_model)
    @api.response(403, 'Forbidden — not the student who booked this session', cancel_error_model)
    @api.response(422, 'Cancellation window has passed — must cancel at least 2 hours before session', cancel_error_model)
    @api.response(500, 'Internal server error', cancel_error_model)
    @api.response(502, 'Stripe refund failed — session NOT cancelled', cancel_error_model)
    def post(self):
        """
        Cancel a booked session. Requires student Bearer JWT.

        **Business rules:**
        - Student must be the one who booked the session
        - Cancellation must be made at least **2 hours** before the session start time
        - Full Stripe refund is processed before the slot is restored

        **Flow:**
        1. Extract student Clerk ID from JWT
        2. Fetch and validate session (Session Service)
        3. Verify student ownership
        4. Validate 2-hour cancellation window
        5. Fetch tutor and student details (Tutor + Student Services)
        6. Process Stripe refund (Payment Service)
        7. Restore session to `available`, clear studentId and stripeSessionId (Session Service)
        8. Remove student from Google Calendar event (Calendar Service)
        9. Send cancellation emails to both parties via RabbitMQ (Email Service)
        """
        data = request.get_json()
        session_id = data.get("session_id")
        student_id = data.get("student_id")

        if not session_id or not student_id:
            return {"message": "session_id and student_id are required"}, 400

        auth_header = request.headers.get("Authorization", "")

        # ── Step 1: Extract student Clerk ID from JWT ──────────────────────────
        try:
            student_clerk_id = _extract_clerk_id(auth_header)
        except ValueError as e:
            return {"message": str(e)}, 401

        # ── Step 2: Fetch session (SESSION ATOMIC SERVICE)
        session_resp = requests.get(
            f"{SESSION_SERVICE_URL}/session/{session_id}",
            headers={"Authorization": auth_header},
            timeout=5
        )
        if session_resp.status_code != 200:
            return {"message": "Failed to retrieve session"}, 500

        session = session_resp.json()

        # ── Step 3: Verify the student owns this session ───────────────────────
        if session.get("studentId") != student_id:
            return {"message": "You are not authorised to cancel this session"}, 403

        # ── Step 4: Validate 2-hour cancellation window ────────────────────────
        try:
            session_start_utc = _parse_session_start_utc(session.get("startTime", ""))
            now_utc = datetime.now(timezone.utc)
            hours_until = (session_start_utc - now_utc).total_seconds() / 3600

            if hours_until < 2:
                time_diff = session_start_utc - now_utc
                total_seconds = max(0, int(time_diff.total_seconds()))
                h, m = total_seconds // 3600, (total_seconds % 3600) // 60
                time_str = f"{h} hour(s) and {m} minute(s)" if h > 0 else f"{m} minute(s)"
                return {
                    "message": (
                        f"Cancellation must be made at least 2 hours before the session. "
                        f"Session starts in {time_str}."
                    ),
                    "debug": {
                        "session_start_utc": session_start_utc.isoformat(),
                        "now_utc": now_utc.isoformat(),
                        "hours_until": round(hours_until, 2)
                    }
                }, 422
        except Exception as e:
            return {"message": f"Could not validate session time: {str(e)}"}, 500

        # Step 5a: Fetch tutor details (TUTOR ATOMIC SERVICE)
        tutor_id = session.get("tutorId")
        tutor_resp = requests.get(f"{TUTOR_SERVICE_URL}/tutor/{tutor_id}", timeout=5)
        if tutor_resp.status_code != 200:
            return {"message": "Failed to retrieve tutor details"}, 500

        tutor_data = tutor_resp.json()
        tutor_clerk_id = tutor_data.get("clerkUserId")
        tutor_email    = tutor_data.get("email")
        tutor_name     = tutor_data.get("name", "Tutor")

        tutor_subject_id = session.get("tutorSubjectId")
        matching     = next((s for s in tutor_data.get("subjects", []) if s.get("tutorSubjectId") == tutor_subject_id), None)
        subject_name = matching.get("subject", "Tuition Session") if matching else "Tuition Session"

        # Step 5b: Fetch student details (STUDENT ATOMIC SERVICE)
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

        # Step 6: Process refund (PAYMENT ATOMIC SERVICE)
        stripe_session_id = session.get("stripeSessionId")
        refund_status = "skipped"

        if stripe_session_id:
            refund_resp = requests.post(
                f"{PAYMENT_SERVICE_URL}/payment/refund",
                json={"stripe_session_id": stripe_session_id},
                timeout=10
            )
            if refund_resp.status_code not in (200, 201):
                return {
                    "message": "Refund failed. Session has not been cancelled.",
                    "detail": refund_resp.json()
                }, 502
            refund_status = refund_resp.json().get("refund_status", "unknown")

        # Step 7: Restore slot — "available", clear student + payment refs (SESSSION ATOMIC SERVICE)
        restore_resp = requests.put(
            f"{SESSION_SERVICE_URL}/session/{session_id}",
            json={"status": "available", "studentId": None, "stripeSessionId": None},
            headers={"Authorization": auth_header},
            timeout=5
        )
        if restore_resp.status_code != 200:
            return {
                "message": "Refund processed but failed to restore session to available",
                "refund_status": refund_status
            }, 207

        # Step 8: Remove student from Google Calendar event (CALENDAR ATOMIC SERVICE)
        calendar_event_id = session.get("calendarEventId")
        calendar_updated = False
        if calendar_event_id and tutor_clerk_id and student_email:
            calendar_resp = requests.post(
                f"{CALENDAR_SERVICE_URL}/calendar/cancel-meeting",
                json={
                    "eventId":      calendar_event_id,
                    "tutorClerkId": tutor_clerk_id,
                    "studentEmail": student_email,
                },
                headers={"Authorization": auth_header},
                timeout=10
            )
            if calendar_resp.status_code == 200:
                calendar_updated = True

        # Step 9: Send email for cancellation (EMAIL ATOMIC SERVICE)
        email_notified = False
        try:
            when_string = _format_email_when(session_start_utc, session.get("endTime", ""))
            email_details = {
                "student_name": student_name,
                "subject":      subject_name,
                "tutor_name":   tutor_name,
                "tutor_email":  tutor_email,
                "date":         when_string
            }
            publish_email("notification.email", {"email": student_email, "type": "CANCELLATION_STUDENT", "details": email_details})
            publish_email("notification.email", {"email": tutor_email,   "type": "CANCELLATION_TUTOR",  "details": email_details})
            email_notified = True
        except Exception as e:
            print(f"Non-fatal error sending emails: {str(e)}")

        # Step 10: Return success ────────────────────────────────────────────
        return {
            "message": "Session cancelled successfully",
            "session_id": session_id,
            "refund_status": refund_status,
            "calendar_updated": calendar_updated,
            "email_notified": email_notified
        }, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5101, debug=True)
