from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS
import os
import requests
import jwt as pyjwt

app = Flask(__name__)
CORS(app)
api = Api(app, doc="/docs",
    title="Create Session Service",
    version="1.0",
    description="Create Session composite service — creates a session record and Google Calendar event in one call",
    prefix="/create-session"
)

SESSION_SERVICE_URL = os.environ.get("SESSION_SERVICE_URL", "http://localhost:5003")
CALENDAR_SERVICE_URL = os.environ.get("CALENDAR_SERVICE_URL", "http://localhost:5005")

create_session_input = api.model('CreateSessionInput', {
    'tutorId':        fields.String(required=True, description='The tutor UUID'),
    'tutorSubjectId': fields.String(required=True, description='The tutor subject UUID'),
    'startTime':      fields.String(required=True, description='Start time in ISO format (e.g. 2027-03-03T10:00:00)'),
    'endTime':        fields.String(required=True, description='End time in ISO format'),
    'durationMins':   fields.Float(required=True, description='Duration in minutes'),
    'summary':        fields.String(required=True, description='Calendar event title (e.g. "Mathematics (A-Level)")'),
    'timezone':       fields.String(description='Timezone (e.g. Asia/Singapore)', default='UTC'),
})


@api.route("/health")
class Health(Resource):
    def get(self):
        return {"status": "healthy", "service": "create_session"}, 200


@api.route("/create-session")
class CreateSession(Resource):
    @api.expect(create_session_input)
    def post(self):
        """Creates a session record and a Google Calendar event, then links them together."""
        auth_header = request.headers.get("Authorization", "")

        # Verify the caller is authenticated
        token = auth_header.replace("Bearer ", "")
        try:
            pyjwt.decode(token, options={"verify_signature": False})
        except Exception:
            return {"message": "Invalid authorization token"}, 401

        data = request.get_json()
        tutor_id        = data.get("tutorId")
        tutor_subject_id = data.get("tutorSubjectId")
        start_time      = data.get("startTime")
        end_time        = data.get("endTime")
        duration_mins   = data.get("durationMins")
        summary         = data.get("summary", "Tutor Session")
        timezone        = data.get("timezone", "UTC")

        if not all([tutor_id, tutor_subject_id, start_time, end_time, duration_mins]):
            return {"message": "tutorId, tutorSubjectId, startTime, endTime and durationMins are required"}, 400

        # 1. Create the session record
        session_resp = requests.post(
            f"{SESSION_SERVICE_URL}/session/session",
            json={
                "tutorId":        tutor_id,
                "tutorSubjectId": tutor_subject_id,
                "startTime":      start_time,
                "endTime":        end_time,
                "durationMins":   duration_mins,
                "status":         "available",
            },
            headers={"Authorization": auth_header},
            timeout=10
        )

        if session_resp.status_code == 409:
            return {"message": "Tutor has an overlapping session at this time."}, 409
        if session_resp.status_code != 201:
            return {"message": "Failed to create session", "error": session_resp.text}, 500

        session = session_resp.json()
        session_id = session.get("sessionId")

        # 2. Create the Google Calendar event using the tutor's JWT
        calendar_resp = requests.post(
            f"{CALENDAR_SERVICE_URL}/calendar/create-meeting",
            json={
                "summary":     summary,
                "description": "Tuition session created via TuitionGo.",
                "start_time":  start_time,
                "end_time":    end_time,
                "timezone":    timezone,
                "attendees":   [],
            },
            headers={"Authorization": auth_header},
            timeout=15
        )

        if calendar_resp.status_code != 201:
            # Non-fatal — session is created, calendar event failed
            return {
                "message": "Session created but calendar event failed",
                "session": session,
                "calendarError": calendar_resp.json().get("error")
            }, 207

        calendar_data = calendar_resp.json()
        event_id     = calendar_data.get("eventId")
        meeting_link = calendar_data.get("hangoutLink")

        # 3. Patch the session with the calendar event ID and meeting link
        update_resp = requests.put(
            f"{SESSION_SERVICE_URL}/session/{session_id}",
            json={
                "calendarEventId": event_id,
                "meetingLink":     meeting_link,
            },
            headers={"Authorization": auth_header},
            timeout=10
        )

        if update_resp.status_code != 200:
            return {
                "message": "Session and calendar created but failed to link them",
                "session": session,
                "calendarEventId": event_id,
                "meetingLink": meeting_link,
            }, 207

        return update_resp.json(), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5105, debug=True)
