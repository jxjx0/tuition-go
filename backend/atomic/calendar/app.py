import os
import json
import pika
import uuid
import jwt as pyjwt
import threading
import requests as http_requests
from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from supabase import create_client, Client
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
supabase_url = os.environ.get("SUPABASE_URL", "")
supabase_key = os.environ.get("SUPABASE_KEY", "")
supabase: Client = create_client(supabase_url, supabase_key)

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


def get_google_token_for_user(clerk_user_id: str) -> str:
    """Fetches the user's Google OAuth token from Clerk's Backend API."""
    url = f"https://api.clerk.com/v1/users/{clerk_user_id}/oauth_access_tokens/google"
    resp = http_requests.get(url, headers={"Authorization": f"Bearer {CLERK_SECRET_KEY}"})
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise Exception("No Google OAuth token found for this user. Have they signed in with Google via Clerk?")
    return data[0]["token"]


def get_calendar_service(clerk_user_id: str = None, access_token: str = None):
    """Builds a Google Calendar API service using a Clerk user's OAuth token."""
    creds = None

    if access_token:
        logger.info("Using provided access token...")
        creds = Credentials(token=access_token)
    elif clerk_user_id:
        logger.info(f"Fetching Google token from Clerk for user {clerk_user_id}...")
        token = get_google_token_for_user(clerk_user_id)
        creds = Credentials(token=token)

    if not creds:
        raise Exception("No authentication source available. Provide clerk_user_id or access_token.")

    return build("calendar", "v3", credentials=creds)


# ==================== RabbitMQ Worker ====================
RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")

def handle_session_created(session_data):
    """Creates a Google Meeting for a new session slot."""
    logger.info(f"Worker: Handling session.created for {session_data.get('sessionId')}")
    # Requires tutorClerkId in the session message payload.
    # TODO: Update the session service to include tutorClerkId when publishing session.created.
    tutor_clerk_id = session_data.get('tutorClerkId')
    if not tutor_clerk_id:
        logger.error("Worker: No tutorClerkId in session data. Cannot authenticate with Google Calendar.")
        return

    try:
        service = get_calendar_service(clerk_user_id=tutor_clerk_id)
    except Exception as e:
        logger.error(f"Worker: Could not get calendar service: {e}")
        return

    try:
        event_body = {
            'summary': f"Tutor Session (Pending)",
            'description': 'Generated automatically by TuitionGo.',
            'start': {'dateTime': session_data['startTime'] + 'Z', 'timeZone': 'UTC'},
            'end': {'dateTime': session_data['endTime'] + 'Z', 'timeZone': 'UTC'},
            'conferenceData': {
                'createRequest': {
                    'requestId': f"req-{session_data['sessionId']}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        }

        event = service.events().insert(
            calendarId='primary',
            body=event_body,
            conferenceDataVersion=1
        ).execute()

        meeting_link = event.get('hangoutLink')

        supabase.table('Session').update({
            'meetingLink': meeting_link,
        }).eq('sessionId', session_data['sessionId']).execute()

        logger.info(f"Worker: Successfully created meeting {meeting_link}")
    except Exception as e:
        logger.error(f"Worker error in session.created: {e}")


def handle_session_booked(session_data):
    """Updates the existing meeting with student details."""
    logger.info(f"Worker: Handling session.booked for {session_data.get('sessionId')}")
    tutor_clerk_id = session_data.get('tutorClerkId')
    if not tutor_clerk_id:
        logger.error("Worker: No tutorClerkId in session data. Cannot authenticate with Google Calendar.")
        return

    try:
        service = get_calendar_service(clerk_user_id=tutor_clerk_id)
    except Exception as e:
        logger.error(f"Worker: Could not get calendar service: {e}")
        return

    try:
        start_time = session_data['startTime'] + 'Z'
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_time,
            maxResults=10,
            singleEvents=True
        ).execute()
        events = events_result.get('items', [])

        target_event = None
        for event in events:
            if event.get('start', {}).get('dateTime') == start_time:
                target_event = event
                break

        if target_event:
            target_event['summary'] = f"Tutor Session (Booked)"
            attendees = target_event.get('attendees', [])
            if session_data.get('studentEmail'):
                attendees.append({'email': session_data['studentEmail']})
                target_event['attendees'] = attendees

            service.events().update(
                calendarId='primary',
                eventId=target_event['id'],
                body=target_event,
                sendUpdates='all'
            ).execute()
            logger.info(f"Worker: Successfully updated event {target_event['id']} for booking.")
        else:
            logger.warning(f"Worker: Could not find event to update for session {session_data.get('sessionId')}")

    except Exception as e:
        logger.error(f"Worker error in session.booked: {e}")


def start_event_worker():
    """Starts the RabbitMQ consumer loop with retry logic."""
    import time
    max_retries = 10
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            params = pika.URLParameters(RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()

            channel.exchange_declare(exchange='session_events', exchange_type='topic', durable=True)
            result = channel.queue_declare(queue='calendar_updates', durable=True)
            queue_name = result.method.queue

            channel.queue_bind(exchange='session_events', queue=queue_name, routing_key='session.*')

            def callback(ch, method, properties, body):
                try:
                    data = json.loads(body)
                    routing_key = method.routing_key
                    if routing_key == 'session.created':
                        handle_session_created(data)
                    elif routing_key == 'session.booked':
                        handle_session_booked(data)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as cb_err:
                    logger.error(f"Worker callback error: {cb_err}")

            channel.basic_consume(queue=queue_name, on_message_callback=callback)
            logger.info(" [*] Calendar worker started. Waiting for messages...")
            channel.start_consuming()
            break
        except Exception as e:
            logger.warning(f"Worker connection attempt {attempt+1}/{max_retries} failed: {e}. Retrying in {retry_delay}s...")
            time.sleep(retry_delay)
    else:
        logger.error("Worker failed to connect after multiple retries. Background work disabled.")


worker_thread = threading.Thread(target=start_event_worker)
worker_thread.daemon = True
worker_thread.start()


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)
