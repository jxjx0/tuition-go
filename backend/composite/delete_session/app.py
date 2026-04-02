from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS
import os
import requests
import jwt as pyjwt

app = Flask(__name__)
CORS(app)
api = Api(app, doc="/docs",
    title="Delete Session Service",
    version="1.0",
    description="Delete Session composite service — deletes a session record and its Google Calendar event. Blocked if session is already booked.",
    prefix="/delete-session"
)

SESSION_SERVICE_URL  = os.environ.get("SESSION_SERVICE_URL",  "http://localhost:5003")
TUTOR_SERVICE_URL    = os.environ.get("TUTOR_SERVICE_URL",    "http://localhost:5002")
CALENDAR_SERVICE_URL = os.environ.get("CALENDAR_SERVICE_URL", "http://localhost:5005")


@api.route("/health")
class Health(Resource):
    def get(self):
        return {"status": "healthy", "service": "delete_session"}, 200


@api.route("/<string:session_id>")
class DeleteSession(Resource):
    def delete(self, session_id):
        """Deletes a session record and its Google Calendar event. Blocked if status is booked."""
        auth_header = request.headers.get("Authorization", "")

        token = auth_header.replace("Bearer ", "")
        try:
            pyjwt.decode(token, options={"verify_signature": False})
        except Exception:
            return {"message": "Invalid authorization token"}, 401

        # 1. Fetch session — check it exists and is not booked
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
            return {"message": "Session cannot be deleted once it has been booked. Use cancel instead."}, 409

        calendar_event_id = session.get("calendarEventId")
        tutor_id          = session.get("tutorId")

        # 2. Hard-delete the session record
        delete_resp = requests.delete(
            f"{SESSION_SERVICE_URL}/session/{session_id}",
            headers={"Authorization": auth_header},
            timeout=5
        )
        if delete_resp.status_code not in (200, 204):
            return {"message": "Failed to delete session", "error": delete_resp.text}, 500

        # 3. Delete the Google Calendar event if one is linked
        if not calendar_event_id or not tutor_id:
            return {"message": "Session deleted (no calendar event linked)"}, 200

        tutor_resp = requests.get(
            f"{TUTOR_SERVICE_URL}/tutor/{tutor_id}",
            timeout=5
        )
        if tutor_resp.status_code != 200:
            return {
                "message": "Session deleted but could not fetch tutor for calendar cleanup",
            }, 207

        tutor_clerk_id = tutor_resp.json().get("clerkUserId")

        calendar_resp = requests.post(
            f"{CALENDAR_SERVICE_URL}/calendar/delete-meeting",
            json={
                "eventId":      calendar_event_id,
                "tutorClerkId": tutor_clerk_id,
            },
            headers={"Authorization": auth_header},
            timeout=15
        )

        if calendar_resp.status_code != 200:
            return {
                "message": "Session deleted but calendar event cleanup failed",
                "calendarError": calendar_resp.json().get("error")
            }, 207

        return {"message": "Session and calendar event deleted successfully"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5107, debug=True)
