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
    title="Complete Session Service",
    version="1.0",
    description="Complete Session composite service",
    prefix="/complete-session"
)

SESSION_SERVICE_URL = os.environ.get("SESSION_SERVICE_URL", "http://localhost:5003")
TUTOR_SERVICE_URL   = os.environ.get("TUTOR_SERVICE_URL",   "http://localhost:5002")
STUDENT_SERVICE_URL = os.environ.get("STUDENT_SERVICE_URL", "http://localhost:5001")
RABBITMQ_HOST       = os.environ.get("RABBITMQ_HOST",       "localhost")


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
        raise ValueError("Could not identify tutor from token")
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


complete_input_model = api.model('CompleteSessionInput', {
    'session_id': fields.String(required=True, description='The session UUID', example='a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'),
    'tutor_id':   fields.String(required=True, description='The tutor UUID',   example='c3eebc99-9c0b-4ef8-bb6d-6bb9bd380a33'),
})

complete_success_model = api.model('CompleteSessionResponse', {
    'message':       fields.String(example='Session marked as completed successfully'),
    'session_id':    fields.String(example='a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'),
    'email_notified': fields.Boolean(example=True),
})

complete_error_model = api.model('CompleteSessionError', {
    'message': fields.String(description='Error message', example='You are not authorised to complete this session'),
})


@api.route("/health")
class Health(Resource):
    @api.response(200, 'Service is healthy')
    def get(self):
        """Health check."""
        return {"status": "healthy", "service": "complete_session"}, 200


@api.route("/complete")
class CompleteSession(Resource):

    @api.expect(complete_input_model)
    @api.response(200, 'Session completed successfully', complete_success_model)
    @api.response(400, 'Missing required fields', complete_error_model)
    @api.response(401, 'Invalid or missing Bearer JWT', complete_error_model)
    @api.response(403, 'Forbidden — not the tutor who owns this session', complete_error_model)
    @api.response(422, 'Session cannot be completed before it has ended', complete_error_model)
    @api.response(500, 'Internal server error', complete_error_model)
    def post(self):
        """
        Mark a booked session as completed. Requires tutor Bearer JWT.

        **Business rules:**
        - Caller must be the tutor who owns the session (verified via JWT)
        - Session end time must have already passed
        - Sends a review-request email to the student after completion

        **Flow:**
        1. Extract tutor Clerk ID from JWT
        2. Fetch tutor details (Tutor Service) and verify JWT matches
        3. Call session atomic service to mark session as completed
        4. Fetch student details (Student Service)
        5. Send review-request email to student via RabbitMQ (Email Service)
        """
        data = request.get_json() or {}
        session_id = data.get("session_id")
        tutor_id   = data.get("tutor_id")

        if not session_id or not tutor_id:
            return {"message": "session_id and tutor_id are required"}, 400

        auth_header = request.headers.get("Authorization", "")

        # ── Step 1: Extract tutor Clerk ID from JWT ────────────────────────────
        try:
            tutor_clerk_id = _extract_clerk_id(auth_header)
        except ValueError as e:
            return {"message": str(e)}, 401

        # ── Step 2: Fetch tutor and verify JWT identity (TUTOR ATOMIC SERVICE) ────────────────────────
        tutor_resp = requests.get(f"{TUTOR_SERVICE_URL}/tutor/{tutor_id}", timeout=5)
        if tutor_resp.status_code != 200:
            return {"message": "Failed to retrieve tutor details"}, 500

        tutor_data = tutor_resp.json()
        if tutor_data.get("clerkUserId") != tutor_clerk_id:
            return {"message": "You are not authorised to complete this session"}, 403

        tutor_name = tutor_data.get("name", "Tutor")

        # ── Step 3: Mark session as completed (SESSION ATOMIC SERVICE) ─────────
        complete_resp = requests.post(
            f"{SESSION_SERVICE_URL}/session/{session_id}/complete",
            json={"tutorId": tutor_id},
            headers={"Authorization": auth_header},
            timeout=5
        )
        if complete_resp.status_code != 200:
            return complete_resp.json(), complete_resp.status_code

        session = complete_resp.json()

        # ── Step 4: Fetch student details (STUDENT ATOMIC SERVICE) ────────────
        student_id = session.get("studentId")
        if not student_id:
            return {"message": "Session has no associated student"}, 500

        student_resp = requests.get(
            f"{STUDENT_SERVICE_URL}/student/{student_id}",
            headers={"Authorization": auth_header},
            timeout=5
        )
        if student_resp.status_code != 200:
            return {"message": "Failed to retrieve student details"}, 500

        student_data  = student_resp.json()
        student_email = student_data.get("email")
        student_name  = student_data.get("name", "Student")

        # Resolve subject name from tutor's subjects list
        tutor_subject_id = session.get("tutorSubjectId")
        matching     = next((s for s in tutor_data.get("subjects", []) if s.get("tutorSubjectId") == tutor_subject_id), None)
        subject_name = matching.get("subject", "Tuition Session") if matching else "Tuition Session"

        # ── Step 5: Send review-request email to student (EMAIL ATOMIC SERVICE) ───────
        email_notified = False
        try:
            session_start_utc = _parse_session_start_utc(session.get("startTime", ""))
            when_string = _format_email_when(session_start_utc, session.get("endTime", ""))
            email_details = {
                "student_name": student_name,
                "tutor_name":   tutor_name,
                "subject":      subject_name,
                "date":         when_string,
            }
            publish_email("notification.email", {
                "email":   student_email,
                "type":    "SESSION_COMPLETE_STUDENT",
                "details": email_details
            })
            email_notified = True
        except Exception as e:
            print(f"Non-fatal error sending email: {str(e)}")

        # ── Step 6: Return success ─────────────────────────────────────────────
        return {
            "message":        "Session marked as completed successfully",
            "session_id":     session_id,
            "email_notified": email_notified,
        }, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5108, debug=True)
