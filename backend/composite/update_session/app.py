from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS
import os
import requests
import jwt as pyjwt

app = Flask(__name__)
CORS(app)
api = Api(app, doc="/docs",
    title="Update Session Service",
    version="1.0",
    description="Update Session composite service — updates a session record and its Google Calendar event in one call. Blocked if session is already booked.",
    prefix="/update-session"
)

SESSION_SERVICE_URL = os.environ.get("SESSION_SERVICE_URL", "http://localhost:5003")
TUTOR_SERVICE_URL   = os.environ.get("TUTOR_SERVICE_URL",   "http://localhost:5002")
CALENDAR_SERVICE_URL = os.environ.get("CALENDAR_SERVICE_URL", "http://localhost:5005")

update_session_input = api.model('UpdateSessionInput', {
    'tutorSubjectId': fields.String(required=True, description='The tutor subject UUID'),
    'startTime':      fields.String(required=True, description='New start time in ISO format'),
    'endTime':        fields.String(required=True, description='New end time in ISO format'),
    'durationMins':   fields.Float(required=True,  description='Duration in minutes'),
    'summary':        fields.String(required=True, description='Calendar event title (e.g. "Mathematics (A-Level)")'),
    'timezone':       fields.String(description='Timezone (e.g. Asia/Singapore)', default='UTC'),
})


@api.route("/health")
class Health(Resource):
    def get(self):
        return {"status": "healthy", "service": "update_session"}, 200


@api.route("/<string:session_id>")
class UpdateSession(Resource):
    @api.expect(update_session_input)
    def put(self, session_id):
        """Updates session times/subject and syncs to Google Calendar. Blocked if status is booked."""
        auth_header = request.headers.get("Authorization", "")

        token = auth_header.replace("Bearer ", "")
        try:
            pyjwt.decode(token, options={"verify_signature": False})
        except Exception:
            return {"message": "Invalid authorization token"}, 401

        data = request.get_json()
        tutor_subject_id = data.get("tutorSubjectId")
        start_time       = data.get("startTime")
        end_time         = data.get("endTime")
        duration_mins    = data.get("durationMins")
        summary          = data.get("summary", "Tutor Session")
        timezone         = data.get("timezone", "UTC")

        if not all([tutor_subject_id, start_time, end_time, duration_mins]):
            return {"message": "tutorSubjectId, startTime, endTime and durationMins are required"}, 400

        # 1. Fetch current session — check it exists and is not booked
        session_resp = requests.get(
            f"{SESSION_SERVICE_URL}/session/{session_id}",
            headers={"Authorization": auth_header},
            timeout=5
        )
        if session_resp.status_code == 404:
            return {"message": "Session not found"}, 404
        if session_resp.status_code != 200:
            return {"message": "Failed to retrieve session"}, 500

        session = session_resp.json()
        if session.get("status") == "booked":
            return {"message": "Session cannot be updated once it has been booked"}, 409

        calendar_event_id = session.get("calendarEventId")
        tutor_id          = session.get("tutorId")

        # 2. Update the session record
        update_resp = requests.put(
            f"{SESSION_SERVICE_URL}/session/{session_id}",
            json={
                "tutorSubjectId": tutor_subject_id,
                "startTime":      start_time,
                "endTime":        end_time,
                "durationMins":   duration_mins,
            },
            headers={"Authorization": auth_header},
            timeout=10
        )
        if update_resp.status_code != 200:
            return {"message": "Failed to update session", "error": update_resp.text}, 500

        updated_session = update_resp.json()

        # 3. Sync to Google Calendar if a calendar event is linked
        if not calendar_event_id or not tutor_id:
            return {
                "message": "Session updated but no calendar event linked",
                "session": updated_session
            }, 200

        # Fetch tutor's Clerk user ID for the calendar API
        tutor_resp = requests.get(
            f"{TUTOR_SERVICE_URL}/tutor/{tutor_id}",
            timeout=5
        )
        if tutor_resp.status_code != 200:
            return {
                "message": "Session updated but could not fetch tutor for calendar sync",
                "session": updated_session
            }, 207

        tutor_clerk_id = tutor_resp.json().get("clerkUserId")

        calendar_resp = requests.post(
            f"{CALENDAR_SERVICE_URL}/calendar/reschedule-meeting",
            json={
                "eventId":      calendar_event_id,
                "tutorClerkId": tutor_clerk_id,
                "summary":      summary,
                "start_time":   start_time,
                "end_time":     end_time,
                "timezone":     timezone,
            },
            headers={"Authorization": auth_header},
            timeout=15
        )

        if calendar_resp.status_code != 200:
            return {
                "message": "Session updated but calendar sync failed",
                "session": updated_session,
                "calendarError": calendar_resp.json().get("error")
            }, 207

        return updated_session, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5106, debug=True)
