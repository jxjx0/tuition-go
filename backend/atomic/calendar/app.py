import os
import uuid
import jwt as pyjwt
import requests as http_requests
from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

load_dotenv()

CLERK_SECRET_KEY = os.environ.get("CLERK_SECRET_KEY", "")

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.readonly"
]

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["Content-Type", "Authorization"]}})
api = Api(app, doc="/docs",
    title="Calendar Service",
    version="1.0",
    description="Calendar atomic service",
    prefix="/calendar"
)

meeting_model = api.model('MeetingRequest', {
    'summary': fields.String(required=True, description='Meeting title'),
    'description': fields.String(description='Meeting description'),
    'start_time': fields.String(required=True, description='Start time in ISO format (e.g. 2024-05-28T09:00:00)'),
    'end_time': fields.String(required=True, description='End time in ISO format'),
    'timezone': fields.String(description='Timezone (e.g. Asia/Singapore)', default='UTC'),
    'attendees': fields.List(fields.String, description='List of attendee emails')
})

update_meeting_model = api.model('UpdateMeetingRequest', {
    'eventId': fields.String(required=True, description='Google Calendar event ID to update'),
    'tutorClerkId': fields.String(required=True, description='Clerk user ID of the tutor (user_xxx)'),
    'studentEmail': fields.String(required=True, description='Student email to add as attendee'),
})

delete_meeting_model = api.model('DeleteMeetingRequest', {
    'eventId':      fields.String(required=True, description='Google Calendar event ID to delete'),
    'tutorClerkId': fields.String(required=True, description='Clerk user ID of the tutor (user_xxx)'),
})

cancel_meeting_model = api.model('CancelMeetingRequest', {
    'eventId':      fields.String(required=True, description='Google Calendar event ID to update'),
    'tutorClerkId': fields.String(required=True, description='Clerk user ID of the tutor (user_xxx)'),
    'studentEmail': fields.String(required=True, description='Student email to remove as attendee'),
})

reschedule_meeting_model = api.model('RescheduleMeetingRequest', {
    'eventId':      fields.String(required=True, description='Google Calendar event ID to reschedule'),
    'tutorClerkId': fields.String(required=True, description='Clerk user ID of the tutor (user_xxx)'),
    'summary':      fields.String(description='New event title'),
    'start_time':   fields.String(required=True, description='New start time in ISO format'),
    'end_time':     fields.String(required=True, description='New end time in ISO format'),
    'timezone':     fields.String(description='Timezone (e.g. Asia/Singapore)', default='UTC'),
})


def get_google_token_for_user(clerk_user_id: str) -> str:
    """Fetches the user's Google OAuth token from Clerk's Backend API."""
    url = f"https://api.clerk.com/v1/users/{clerk_user_id}/oauth_access_tokens/google"
    resp = http_requests.get(url, headers={"Authorization": f"Bearer {CLERK_SECRET_KEY}"})
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise Exception("No Google OAuth token found for this user. Have they signed in with Google via Clerk?")
    return data[0]["token"]


def get_calendar_service(clerk_user_id: str):
    """Builds a Google Calendar API service using a Clerk user's OAuth token."""
    logger.info(f"Fetching Google token from Clerk for user {clerk_user_id}...")
    token = get_google_token_for_user(clerk_user_id)
    creds = Credentials(token=token)
    return build("calendar", "v3", credentials=creds)


@api.route("/health")
class Health(Resource):
    def get(self):
        return {"status": "healthy", "service": "calendar"}, 200


@api.route("/create-meeting")
class CreateMeeting(Resource):
    @api.expect(meeting_model)
    def post(self):
        """Creates a Google Calendar event with a Google Meet link."""
        # Extract Clerk user ID from the JWT — Kong already validated the signature
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "")
        try:
            claims = pyjwt.decode(token, options={"verify_signature": False})
            clerk_user_id = claims.get("sub")
        except Exception:
            return {"error": "Invalid authorization token"}, 401

        if not clerk_user_id:
            return {"error": "Could not identify user from token"}, 401

        data = request.json
        summary = data.get('summary', 'Tutor Session')
        description = data.get('description', 'Generated by Tuition-Go')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        timezone = data.get('timezone', 'UTC')
        attendee_emails = data.get('attendees', [])

        if not start_time or not end_time:
            return {"error": "start_time and end_time are required"}, 400

        try:
            service = get_calendar_service(clerk_user_id=clerk_user_id)
        except Exception as e:
            logger.error(f"Failed to get calendar service: {e}")
            return {"error": str(e)}, 401

        try:
            final_attendees = [{'email': email} for email in attendee_emails]

            try:
                primary_calendar = service.calendars().get(calendarId='primary').execute()
                user_email = primary_calendar.get('id')
                if user_email:
                    host_added = False
                    for att in final_attendees:
                        if att['email'].lower() == user_email.lower():
                            att['responseStatus'] = 'accepted'
                            host_added = True
                            break
                    if not host_added:
                        final_attendees.append({'email': user_email, 'responseStatus': 'accepted'})
            except Exception as ident_err:
                logger.warning(f"Could not establish host identity: {ident_err}")

            event = {
                'summary': summary,
                'description': description,
                'start': {'dateTime': start_time, 'timeZone': timezone},
                'end': {'dateTime': end_time, 'timeZone': timezone},
                'attendees': final_attendees,
                'conferenceData': {
                    'createRequest': {
                        'requestId': str(uuid.uuid4()),
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                },
            }

            event = service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1
            ).execute()
            logger.info("Event created successfully!")

            return {
                "message": "Meeting created successfully",
                "htmlLink": event.get('htmlLink'),
                "hangoutLink": event.get('hangoutLink'),
                "eventId": event.get('id')
            }, 201

        except HttpError as error:
            logger.error(f"HTTP Error: {error}")
            return {"error": f"An error occurred: {error}"}, 500
        except Exception as e:
            logger.exception("General Error occurred during meeting creation")
            return {"error": str(e)}, 500


@api.route("/update-meeting")
class UpdateMeeting(Resource):
    @api.expect(update_meeting_model)
    def post(self):
        """Adds a student as attendee to an existing tutor calendar event."""
        data = request.json
        event_id = data.get('eventId')
        tutor_clerk_id = data.get('tutorClerkId')
        student_email = data.get('studentEmail')

        if not event_id or not tutor_clerk_id or not student_email:
            return {"error": "eventId, tutorClerkId and studentEmail are required"}, 400

        # Use the TUTOR's Google token — the student made the HTTP request
        # but we update the tutor's calendar
        try:
            service = get_calendar_service(clerk_user_id=tutor_clerk_id)
        except Exception as e:
            logger.error(f"Failed to get tutor calendar service: {e}")
            return {"error": str(e)}, 401

        try:
            # Fetch the existing event from tutor's calendar
            event = service.events().get(calendarId='primary', eventId=event_id).execute()

            # Add student to attendees if not already present
            attendees = event.get('attendees', [])
            already_added = any(a.get('email', '').lower() == student_email.lower() for a in attendees)
            if not already_added:
                attendees.append({'email': student_email})
                event['attendees'] = attendees

            # Update event title to reflect booking
            event['summary'] = event.get('summary', 'Tutor Session').replace('(Pending)', '(Booked)')

            updated_event = service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event,
                sendUpdates='all'  # emails invite to student automatically
            ).execute()

            logger.info(f"Event {event_id} updated with student {student_email}")
            return {
                "message": "Meeting updated successfully",
                "eventId": updated_event.get('id'),
                "hangoutLink": updated_event.get('hangoutLink')
            }, 200

        except HttpError as error:
            logger.error(f"HTTP Error updating event: {error}")
            return {"error": f"An error occurred: {error}"}, 500
        except Exception as e:
            logger.exception("General error updating meeting")
            return {"error": str(e)}, 500


@api.route("/cancel-meeting")
class CancelMeeting(Resource):
    @api.expect(cancel_meeting_model)
    def post(self):
        """Removes a student as attendee from an existing tutor calendar event and marks it as Pending."""
        data = request.json
        event_id = data.get('eventId')
        tutor_clerk_id = data.get('tutorClerkId')
        student_email = data.get('studentEmail')

        if not event_id or not tutor_clerk_id or not student_email:
            return {"error": "eventId, tutorClerkId and studentEmail are required"}, 400

        try:
            service = get_calendar_service(clerk_user_id=tutor_clerk_id)
        except Exception as e:
            logger.error(f"Failed to get tutor calendar service: {e}")
            return {"error": str(e)}, 401

        try:
            # Fetch current event from tutor's calendar
            event = service.events().get(calendarId='primary', eventId=event_id).execute()

            # Remove student from attendees list
            attendees = event.get('attendees', [])
            attendees = [a for a in attendees if a.get('email', '').lower() != student_email.lower()]
            event['attendees'] = attendees

            # Revert title back to Pending so tutor knows the slot is free
            event['summary'] = event.get('summary', 'Tutor Session').replace('(Booked)', '(Pending)')

            updated_event = service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event,
                sendUpdates='all'  # automatically emails cancellation notice to student
            ).execute()

            logger.info(f"Event {event_id}: student {student_email} removed from attendees")
            return {
                "message": "Student removed from calendar event successfully",
                "eventId": updated_event.get('id'),
            }, 200

        except HttpError as error:
            logger.error(f"HTTP Error cancelling event: {error}")
            return {"error": f"An error occurred: {error}"}, 500
        except Exception as e:
            logger.exception("General error cancelling meeting")
            return {"error": str(e)}, 500


@api.route("/cancel-meeting")
class CancelMeeting(Resource):
    @api.expect(cancel_meeting_model)
    def post(self):
        """Removes a student attendee from an existing tutor calendar event (on cancellation)."""
        data = request.json
        event_id       = data.get('eventId')
        tutor_clerk_id = data.get('tutorClerkId')
        student_email  = data.get('studentEmail')

        if not event_id or not tutor_clerk_id or not student_email:
            return {"error": "eventId, tutorClerkId and studentEmail are required"}, 400

        try:
            service = get_calendar_service(clerk_user_id=tutor_clerk_id)
        except Exception as e:
            logger.error(f"Failed to get tutor calendar service: {e}")
            return {"error": str(e)}, 401

        try:
            # Fetch current event from tutor's calendar
            event = service.events().get(calendarId='primary', eventId=event_id).execute()

            # Remove student from attendees list
            attendees = event.get('attendees', [])
            attendees = [a for a in attendees if a.get('email', '').lower() != student_email.lower()]
            event['attendees'] = attendees

            # Revert title back to indicate the slot is free again
            event['summary'] = event.get('summary', 'Tutor Session').replace('(Booked)', '(Available)')

            updated_event = service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event,
                sendUpdates='all'  # automatically sends cancellation notice to student
            ).execute()

            logger.info(f"Event {event_id}: student {student_email} removed from attendees")
            return {
                "message": "Student removed from calendar event successfully",
                "eventId": updated_event.get('id'),
            }, 200

        except HttpError as error:
            logger.error(f"HTTP Error cancelling event: {error}")
            return {"error": f"An error occurred: {error}"}, 500
        except Exception as e:
            logger.exception("General error cancelling meeting")
            return {"error": str(e)}, 500


@api.route("/delete-meeting")
class DeleteMeeting(Resource):
    @api.expect(delete_meeting_model)
    def post(self):
        """Deletes a Google Calendar event using the tutor's OAuth token. Notifies all attendees."""
        data = request.json
        event_id       = data.get('eventId')
        tutor_clerk_id = data.get('tutorClerkId')

        if not event_id or not tutor_clerk_id:
            return {"error": "eventId and tutorClerkId are required"}, 400

        try:
            service = get_calendar_service(clerk_user_id=tutor_clerk_id)
        except Exception as e:
            logger.error(f"Failed to get calendar service: {e}")
            return {"error": str(e)}, 401

        try:
            service.events().delete(
                calendarId='primary',
                eventId=event_id,
                sendUpdates='all'
            ).execute()

            logger.info(f"Event {event_id} deleted")
            return {"message": "Meeting deleted successfully"}, 200

        except HttpError as error:
            if error.resp.status == 410:
                # Already deleted — treat as success
                logger.warning(f"Event {event_id} already deleted (410 Gone)")
                return {"message": "Meeting already deleted"}, 200
            logger.error(f"HTTP Error deleting event: {error}")
            return {"error": f"An error occurred: {error}"}, 500
        except Exception as e:
            logger.exception("General error deleting meeting")
            return {"error": str(e)}, 500


@api.route("/reschedule-meeting")
class RescheduleMeeting(Resource):
    @api.expect(reschedule_meeting_model)
    def post(self):
        """Updates an existing Google Calendar event's time and/or title."""
        data = request.json
        event_id      = data.get('eventId')
        tutor_clerk_id = data.get('tutorClerkId')
        start_time    = data.get('start_time')
        end_time      = data.get('end_time')
        timezone      = data.get('timezone', 'UTC')
        summary       = data.get('summary')

        if not event_id or not tutor_clerk_id or not start_time or not end_time:
            return {"error": "eventId, tutorClerkId, start_time and end_time are required"}, 400

        try:
            service = get_calendar_service(clerk_user_id=tutor_clerk_id)
        except Exception as e:
            logger.error(f"Failed to get calendar service: {e}")
            return {"error": str(e)}, 401

        try:
            event = service.events().get(calendarId='primary', eventId=event_id).execute()

            event['start'] = {'dateTime': start_time, 'timeZone': timezone}
            event['end']   = {'dateTime': end_time,   'timeZone': timezone}
            if summary:
                event['summary'] = summary

            updated_event = service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event,
                sendUpdates='all'
            ).execute()

            logger.info(f"Event {event_id} rescheduled")
            return {
                "message": "Meeting rescheduled successfully",
                "eventId": updated_event.get('id'),
                "hangoutLink": updated_event.get('hangoutLink')
            }, 200

        except HttpError as error:
            logger.error(f"HTTP Error rescheduling event: {error}")
            return {"error": f"An error occurred: {error}"}, 500
        except Exception as e:
            logger.exception("General error rescheduling meeting")
            return {"error": str(e)}, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)
