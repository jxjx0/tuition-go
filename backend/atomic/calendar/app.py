import os
import datetime
import uuid
from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import logging
import sys

# Configure logging to output to stdout for Docker
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

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
    description="Calendar atomic service"
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

def get_calendar_service(access_token=None):
    creds = None
    
    # If a direct access token is provided (pass-through from Clerk), use it
    if access_token:
        logger.info("Using provided access token from Clerk...")
        creds = Credentials(token=access_token)
    
    # Otherwise check for local token.json
    if not creds:
        logger.info(f"Checking for token at {TOKEN_PATH}")
        if os.path.exists(TOKEN_PATH):
            logger.info("Token found. Loading credentials...")
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Token expired. Refreshing...")
            creds.refresh(Request())
        else:
            logger.info("No valid credentials. Starting OAuth flow...")
            # ... (rest of the OAuth flow code)
            if not os.path.exists(CREDENTIALS_PATH):
                raise Exception(f"credentials.json not found at {CREDENTIALS_PATH}")
            
            # Enable insecure transport for local development (http instead of https)
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
            
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES
            )
            
            # Use 127.0.0.1 instead of localhost (Google prefers IPs for local secure flows now)
            # Remove trailing slash to match some strict redirect URI policies
            flow.redirect_uri = 'http://127.0.0.1:5080'
            auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
            
            logger.info("=" * 50)
            logger.info("AUTHENTICATION REQUIRED")
            logger.info(f"Please visit this URL: {auth_url}")
            logger.info("=" * 50)
            
            from google_auth_oauthlib.flow import _WSGIRequestHandler, _RedirectWSGIApp
            import wsgiref.simple_server
            
            wsgi_app = _RedirectWSGIApp("Success! You have authenticated. You can close this tab.")
            try:
                local_server = wsgiref.simple_server.make_server(
                    '0.0.0.0', 5080, wsgi_app, handler_class=_WSGIRequestHandler)
            except OSError as e:
                if e.errno == 98:
                    logger.error("Port 5080 is already in use. Another authentication process may be running.")
                    raise Exception("Authentication port 5080 is busy. Please wait a moment and try again.")
                raise e
            
            logger.info("Waiting for your browser to redirect to port 5080...")
            
            # Robust loop: keep handling requests until we actually get the callback
            # This prevents crashing on background requests like favicon.ico
            while wsgi_app.last_request_uri is None:
                local_server.handle_request()
            
            logger.info("Callback received! Finalizing token...")
            
            # Fetch the token. We replace http with https for the library's internal check.
            authorization_response = wsgi_app.last_request_uri.replace('http://', 'https://')
            flow.fetch_token(authorization_response=authorization_response)
            creds = flow.credentials
        
        logger.info(f"Saving new token to {TOKEN_PATH}")
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

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
            service = get_calendar_service(access_token=access_token)
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
