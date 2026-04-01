from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS
import os
import requests
import jwt as pyjwt
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
EMAIL_SERVICE_URL    = os.environ.get("EMAIL_SERVICE_URL",    "http://localhost:5006")

cancel_input_model = api.model('CancelInput', {
    'session_id': fields.String(required=True, description='The session UUID'),
    'student_id': fields.String(required=True, description='The student UUID'),
})


@api.route("/health")
class Health(Resource):
    def get(self):
        return {"status": "healthy", "service": "cancel_session"}, 200


@api.route("/cancel")
class CancelSession(Resource):

    @api.expect(cancel_input_model)
    @api.response(200, 'Session cancelled successfully')
    @api.response(400, 'Missing required fields')
    @api.response(401, 'Unauthorised')
    @api.response(403, 'Forbidden — not your session')
    @api.response(422, 'Cancellation window has passed (< 2 hours)')
    @api.response(500, 'Internal server error')
    @api.response(502, 'Refund failed')
    def post(self):
        """
        Cancel a booked session.
        Validates the 2-hour window, marks the session cancelled,
        processes the Stripe refund, restores the slot to 'available',
        removes the student from the Google Calendar event, and notifies both via email.
        """
        data = request.get_json()
        session_id = data.get("session_id")
        student_id = data.get("student_id")

        if not session_id or not student_id:
            return {"message": "session_id and student_id are required"}, 400

        auth_header = request.headers.get("Authorization", "")

        # ── Step 1: Extract student Clerk ID from JWT ──────────────────────────
        token = auth_header.replace("Bearer ", "")
        try:
            claims = pyjwt.decode(token, options={"verify_signature": False})
            student_clerk_id = claims.get("sub")
        except Exception:
            return {"message": "Invalid authorization token"}, 401

        if not student_clerk_id:
            return {"message": "Could not identify student from token"}, 401

        # ── Step 2: Fetch session from Session Service ─────────────────────────
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
        start_time_str = session.get("startTime", "")
        try:
            # Step 4a: Normalize the input string to ISO format and ensure it's TZ-aware
            # Supabase strings can be "2026-04-01 10:00:00+00" or "2026-04-01T10:00:00Z"
            clean_time = start_time_str.replace(" ", "T")
            
            # Handle 'Z' suffix by translating to +00:00 for fromisoformat
            if clean_time.endswith("Z"):
                clean_time = clean_time.replace("Z", "+00:00")
            
            # If the string is naive (no + or Z), we assume UTC standard
            dt_parsed = datetime.fromisoformat(clean_time)
            if dt_parsed.tzinfo is None:
                dt_sgt_basis = dt_parsed.replace(tzinfo=timezone.utc)
            else:
                dt_sgt_basis = dt_parsed.astimezone(timezone.utc)
            
            # FINAL ALIGNMENT: 
            # The DB stores SGT time (e.g. 18:00) as a fixed UTC number (18:00Z).
            # SGT 18:00 is actually 10:00 UTC. To get the real absolute UTC, we subtract 8 hours.
            session_start_utc = dt_sgt_basis - timedelta(hours=8)
            
            # Current time in UTC
            now_utc = datetime.now(timezone.utc)
            
            # Calculation
            time_diff = session_start_utc - now_utc
            hours_until = time_diff.total_seconds() / 3600
            
            # Detailed Logging for debugging
            print(f"--- SGT-AWARE CANCELLATION CHECK ---")
            print(f"Raw startTime from DB:     {start_time_str}")
            print(f"Interpreted SGT Time:      {dt_sgt_basis.isoformat()}")
            print(f"Absolute UTC Start Time:   {session_start_utc.isoformat()}")
            print(f"Absolute UTC Now:          {now_utc.isoformat()}")
            print(f"Real Hours until session:  {hours_until:.2f}")
            print(f"------------------------------------")

            # Cancellation window check
            if hours_until < 2:
                # If hours_until is negative, the session has already passed
                total_seconds = max(0, int(time_diff.total_seconds()))
                h = total_seconds // 3600
                m = (total_seconds % 3600) // 60
                
                time_str = f"{h} hour(s) and {m} minute(s)" if h > 0 else f"{m} minute(s)"
                msg = (f"Cancellation must be made at least 2 hours before the session. "
                       f"Session starts in {time_str}.")
                return {
                    "message": msg,
                    "debug": {
                        "raw_start": start_time_str,
                        "session_start_utc": session_start_utc.isoformat(),
                        "now_utc": now_utc.isoformat(),
                        "hours_until": round(hours_until, 2)
                    }
                }, 422
        except Exception as e:
            print(f"ERROR validating time: {str(e)}")
            return {"message": f"Could not validate session time: {str(e)}"}, 500

        # ── Step 5a: Fetch tutor details (Clerk ID for calendar, email for notify) ──
        tutor_id = session.get("tutorId")
        tutor_resp = requests.get(
            f"{TUTOR_SERVICE_URL}/tutor/{tutor_id}",
            timeout=5
        )
        if tutor_resp.status_code != 200:
            return {"message": "Failed to retrieve tutor details"}, 500
        
        tutor_data = tutor_resp.json()
        tutor_clerk_id = tutor_data.get("clerkUserId")
        tutor_email = tutor_data.get("email")
        tutor_name = tutor_data.get("name", "Tutor")

        # ── Step 5b: Fetch student email (calendar removal, notify) ──────────
        student_resp = requests.get(
            f"{STUDENT_SERVICE_URL}/student/by-clerk/{student_clerk_id}",
            headers={"Authorization": auth_header},
            timeout=5
        )
        if student_resp.status_code != 200:
            return {"message": "Failed to retrieve student details"}, 500
        
        student_data = student_resp.json()
        student_email = student_data.get("email")
        student_name = student_data.get("name", "Student")

        # ── Step 6: Mark session as "cancelled" temporarily ────────────────────
        requests.put(
            f"{SESSION_SERVICE_URL}/session/{session_id}",
            json={"status": "cancelled"},
            headers={"Authorization": auth_header},
            timeout=5
        )

        # ── Step 7: Process refund via Payment Service ─────────────────────────
        stripe_session_id = session.get("stripeSessionId")
        refund_status = "skipped"

        if stripe_session_id:
            refund_resp = requests.post(
                f"{PAYMENT_SERVICE_URL}/payment/refund",
                json={"stripe_session_id": stripe_session_id},
                timeout=10
            )
            if refund_resp.status_code not in (200, 201):
                # Roll back session to "booked" if refund fails
                requests.put(
                    f"{SESSION_SERVICE_URL}/session/{session_id}",
                    json={"status": "booked"},
                    headers={"Authorization": auth_header},
                    timeout=5
                )
                return {
                    "message": "Refund failed. Cancellation has been reverted.",
                    "detail": refund_resp.json()
                }, 502
            refund_status = refund_resp.json().get("refund_status", "unknown")

        # ── Step 8: Restore slot — "available" with no student ─────────────────
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

        # ── Step 9: Remove student from Google Calendar event ──────────────────
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

        # ── Step 10: Send email notifications (Second Last Step) ───────────────
        email_notified = False
        try:
            # Format the time for the email as requested
            # Thursday 2 Apr 2026 ⋅ 12am – 1am (Singapore Standard Time)
            end_time_str = session.get("endTime", "")
            
            # Use the already parsed session_start_utc but shift it back to SGT (+8h) for the email display
            # because the user's example 'Thursday 2 Apr' aligns with SGT.
            display_start = session_start_utc + timedelta(hours=8)
            # Parse endTime and shift to SGT as well
            try:
                base_end = datetime.fromisoformat(end_time_str.replace(" ", "T").replace("Z", "+00:00"))
                display_end = base_end.astimezone(timezone.utc) + timedelta(hours=8)
            except:
                display_end = display_start + timedelta(hours=1) # Fallback

            # Format: Thursday 2 Apr 2026 ⋅ 12am – 1am (Singapore Standard Time)
            # %A=Weekday, %d=Day, %b=Abbr Month, %Y=Year, %I%p=12h time with AM/PM
            fmt_date = display_start.strftime("%A %d %b %Y")
            fmt_start_time = display_start.strftime("%I%p").lower().lstrip('0').replace('12am', '12am').replace('12pm', '12pm')
            fmt_end_time = display_end.strftime("%I%p").lower().lstrip('0')
            
            when_string = f"{fmt_date} ⋅ {fmt_start_time} – {fmt_end_time} (Singapore Standard Time)"

            email_body = (
                "This event has been canceled.\n\n"
                "Tuition session cancelled via TuitionGo.\n\n"
                "When\n"
                f"{when_string}\n\n"
                "Organizer\n"
                f"{tutor_name}\n"
                f"{tutor_email}"
            )

            # 10a. Notify Student
            requests.post(
                f"{EMAIL_SERVICE_URL}/email/send",
                json={
                    "to_email": student_email,
                    "subject":  "Canceled: Tuition Session",
                    "body":     email_body,
                    "use_template": False
                },
                timeout=5
            )

            # 10b. Notify Tutor
            requests.post(
                f"{EMAIL_SERVICE_URL}/email/send",
                json={
                    "to_email": tutor_email,
                    "subject":  "Canceled: Tuition Session",
                    "body":     email_body,
                    "use_template": False
                },
                timeout=5
            )
            email_notified = True
        except Exception as e:
            print(f"Non-fatal error sending emails: {str(e)}")

        # ── Step 11: Return success ────────────────────────────────────────────
        return {
            "message": "Session cancelled successfully",
            "session_id": session_id,
            "refund_status": refund_status,
            "calendar_updated": calendar_updated,
            "email_notified": email_notified
        }, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5101, debug=True)
