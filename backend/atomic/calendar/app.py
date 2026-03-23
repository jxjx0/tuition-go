import os
# Enable insecure transport for local development (MUST be set before any oauthlib imports)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

import json
import pika
import uuid
import threading
from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from flask_cors import CORS

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from supabase import create_client, Client
from dotenv import load_dotenv

import logging
import sys

# Setup logging
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

# Global variables for background auth
auth_thread = None
auth_server = None
auth_flow = None
auth_url_cache = None

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.readonly"
]

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["Content-Type", "Authorization", "X-Google-Token", "X-User-Email"]}})
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

# Determine the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")
TOKEN_PATH = os.path.join(BASE_DIR, "token.json")

class AuthRequiredException(Exception):
    def __init__(self, auth_url):
        self.auth_url = auth_url

def run_interactive_auth(flow):
    """Wait for the user to complete auth on port 5080."""
    class RobustRedirectWSGIApp:
        def __init__(self, message, flow):
            self.message = message
            self.flow = flow
            self.done = False

        def __call__(self, environ, start_response):
            path = environ.get('PATH_INFO', '')
            query = environ.get('QUERY_STRING', '')
            logger.info(f"Callback Server: Received request {path}")
            
            if 'favicon.ico' in path:
                start_response('204 No Content', [('Content-Type', 'text/plain')])
                return [b'']
                
            if 'code=' in query or 'error=' in query:
                host = environ.get('HTTP_HOST', 'localhost:5080')
                authorization_response = f"http://{host}{path}?{query}"
                # Re-fix the URI if it needs https
                if 'localhost' not in host:
                    authorization_response = authorization_response.replace('http://', 'https://')
                
                logger.info(f"Callback Server: Auth code detected! Exchanging token...")
                try:
                    self.flow.fetch_token(authorization_response=authorization_response)
                    creds = self.flow.credentials
                    
                    logger.info(f"Token obtained! Saving to {TOKEN_PATH}...")
                    with open(TOKEN_PATH, "w") as token_file:
                        token_file.write(creds.to_json())
                    logger.info("Token saved successfully!")
                    
                    self.message = "Success! Your authentication token has been saved. You may now close this tab and return to the application."
                    self.done = True
                except Exception as e:
                    logger.error(f"Error during token exchange: {e}")
                    self.message = f"Error during authentication: {str(e)}. Please check container logs."
                    self.done = True # Stop even on error

            start_response('200 OK', [('Content-Type', 'text/html')])
            response_body = f"<html><body style='font-family: sans-serif; padding: 20px;'><h2>{self.message}</h2><p>You can close this tab if the message says Success.</p></body></html>"
            return [response_body.encode('utf-8')]

    wsgi_app = RobustRedirectWSGIApp("Authentication process started... exchanging code for token...", flow)
    global auth_server
    from google_auth_oauthlib.flow import _WSGIRequestHandler
    import wsgiref.simple_server
    
    try:
        auth_server = wsgiref.simple_server.make_server(
            '0.0.0.0', 5080, wsgi_app, handler_class=_WSGIRequestHandler)
        
        logger.info("Auth listener started on 0.0.0.0:5080. Waiting for OAuth code...")
        while not wsgi_app.done:
            auth_server.handle_request()
            
        logger.info("Interactive auth complete. Shutting down listener.")

    except Exception as e:
        logger.error(f"Error in auth listener loop: {e}")
    finally:
        global auth_flow, auth_url_cache
        auth_flow = None
        auth_url_cache = None
        if auth_server:
            auth_server.server_close()
            auth_server = None

def get_calendar_service(access_token=None):
    creds = None
    
    # If a direct access token is provided (pass-through from Clerk), use it
    if access_token:
        logger.info("Using provided access token from Clerk...")
        creds = Credentials(token=access_token)
    
    # Otherwise check for local token.json
    if not creds:
        if os.path.exists(TOKEN_PATH):
            logger.info("Token found. Loading credentials...")
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Token expired. Refreshing...")
            try:
                creds.refresh(Request())
                with open(TOKEN_PATH, "w") as token:
                    token.write(creds.to_json())
            except Exception as e:
                logger.error(f"Refresh failed: {e}")
                creds = None
        
        if not creds:
            if not os.path.exists(CREDENTIALS_PATH):
                raise Exception(f"credentials.json not found at {CREDENTIALS_PATH}")
            
            # Use globals to sync between /auth-url and background thread
            global auth_flow, auth_url_cache
            if not auth_flow:
                auth_flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH, SCOPES
                )
                auth_flow.redirect_uri = 'http://localhost:5080'
                auth_url_cache, _ = auth_flow.authorization_url(prompt='consent', access_type='offline')
            
            # Non-interactive mode (API calls), we just return the URL via exception
            raise AuthRequiredException(auth_url_cache)

    return build("calendar", "v3", credentials=creds)

# ==================== RabbitMQ Worker ====================
RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")

def handle_session_created(session_data):
    """Creates a Google Meeting for a new session slot."""
    logger.info(f"Worker: Handling session.created for {session_data.get('sessionId')}")
    service = get_calendar_service()
    if not service:
        logger.error("Worker: Could not get calendar service (unauthorized?)")
        return

    try:
        # Google Meet link generation
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
        
        # Update Supabase
        supabase.table('Session').update({
            'meetingLink': meeting_link,
        }).eq('sessionId', session_data['sessionId']).execute()
        
        logger.info(f"Worker: Successfully created meeting {meeting_link}")
    except Exception as e:
        logger.error(f"Worker error in session.created: {e}")

def handle_session_booked(session_data):
    """Updates the existing meeting with student details."""
    logger.info(f"Worker: Handling session.booked for {session_data.get('sessionId')}")
    service = get_calendar_service()
    if not service:
        return

    try:
        # We need the Google Event ID. If we don't have it in the DB yet,
        # we might have to search for it, or we should have stored it.
        # For now, let's assume meetingLink is used or we search by summary/time.
        # IMPROVEMENT: If we had eventId, we'd use service.events().get(...)
        
        # Searching for the event by start time and summary (fragile but works for demo)
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
            # Update event: Set summary to Booked and add attendee
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
            break # Success, exit retry loop
        except Exception as e:
            logger.warning(f"Worker connection attempt {attempt+1}/{max_retries} failed: {e}. Retrying in {retry_delay}s...")
            time.sleep(retry_delay)
    else:
        logger.error("Worker failed to connect after multiple retries. background work disabled.")

# Start worker thread on app load
worker_thread = threading.Thread(target=start_event_worker)
worker_thread.daemon = True
worker_thread.start()

@api.route("/health")
class Health(Resource):
    def get(self):
        return {"status": "healthy", "service": "calendar"}, 200

@api.route("/auth-status")
class AuthStatus(Resource):
    def get(self):
        """Checks if the service is authenticated with Google."""
        authenticated = os.path.exists(TOKEN_PATH)
        return {"authenticated": authenticated}, 200

@api.route("/auth-url")
class AuthUrl(Resource):
    def get(self):
        """Returns the Google Authorization URL and starts the listener in background."""
        if os.path.exists(TOKEN_PATH):
            return {"message": "Already authenticated", "authenticated": True}, 200
            
        try:
            # Use get_calendar_service to trigger AuthRequiredException if needed
            # which will use/create the global auth_flow
            try:
                get_calendar_service()
                return {"message": "Already authenticated", "authenticated": True}, 200
            except AuthRequiredException as auth_err:
                auth_url = auth_err.auth_url
                
                # Start the blocking listener in a background thread if not already running
                global auth_thread, auth_flow
                if auth_thread is None or not auth_thread.is_alive():
                    logger.info("Starting background auth listener on port 5080...")
                    # auth_flow was just created inside get_calendar_service
                    auth_thread = threading.Thread(target=lambda: run_interactive_auth(auth_flow))
                    auth_thread.daemon = True
                    auth_thread.start()
                    
                return {"authUrl": auth_url, "authenticated": False}, 200
        except Exception as e:
            logger.error(f"Error in /auth-url: {e}")
            return {"error": str(e)}, 500

@api.route("/create-meeting")
class CreateMeeting(Resource):
    @api.expect(meeting_model)
    def post(self):
        """Creates a Google Calendar event with a Google Meet link."""
        data = request.json
        
        # Check for Google Access Token and Backup Email from Clerk in headers
        access_token = request.headers.get('X-Google-Token')
        backup_email = request.headers.get('X-User-Email')
        
        summary = data.get('summary', 'Tutor Session')
        description = data.get('description', 'Generated by Tuition-Go')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        timezone = data.get('timezone', 'UTC')
        attendee_emails = data.get('attendees', [])

        if not start_time or not end_time:
            return {"error": "start_time and end_time are required"}, 400

        try:
            logger.info(f"Fetching calendar service (token from header: {bool(access_token)})...")
            try:
                service = get_calendar_service(access_token=access_token)
            except AuthRequiredException as auth_err:
                # Return 401 and the URL so frontend can show a button
                return {
                    "error": "Authentication required",
                    "authUrl": auth_err.auth_url
                }, 401
            
            logger.info("Service obtained. Fetching traveler identity...")
            
            # Build attendees list
            final_attendees = [{'email': email} for email in attendee_emails]
            
            # Fetch user email to ensure they are the host (if possible)
            try:
                user_email = None
                if backup_email:
                    logger.info(f"Using backup email from header: {backup_email}")
                    user_email = backup_email
                else:
                    logger.info("Fetching user identity from Google API...")
                    # Note: this might still fail if calendar.readonly scope is missing from token.json
                    primary_calendar = service.calendars().get(calendarId='primary').execute()
                    user_email = primary_calendar.get('id')
                
                if user_email:
                    logger.info(f"Establishing host: {user_email}")
                    # Ensure host is included and "accepted"
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
                # We proceed with original attendees if we can't get identity

            # Use the data precisely as received
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time,
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': timezone,
                },
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
