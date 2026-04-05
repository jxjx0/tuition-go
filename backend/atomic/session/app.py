import os
from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv
from postgrest.exceptions import APIError
from datetime import datetime, timezone


load_dotenv()

app = Flask(__name__)
app.config['RESTX_MASK_SWAGGER'] = False
CORS(app)
api = Api(app, doc="/docs",
    title="Session Service",
    version="1.0",
    description="Session atomic service",
    prefix="/session"
)

# Supabase setup
# Create a .env file in the same directory as app.py
# with the following content:
# SUPABASE_URL=your_supabase_url
# SUPABASE_KEY=your_supabase_key
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")


supabase: Client = create_client(url, key)

session_model = api.model('Session', {
    'sessionId': fields.String(description='The session UUID'),
    'tutorId': fields.String(required=True, description='The tutor UUID'),
    'studentId': fields.String(required=True, description='The student UUID'),
    'tutorSubjectId': fields.String(description='The tutor subject UUID (references TutorSubjects table)'),
    'startTime': fields.DateTime(required=True, description='The session start time'),
    'endTime': fields.DateTime(required=True, description='The session end time'),
    'status': fields.String(description='The session status'),
    'durationMins': fields.Float(description='The duration of the session in minutes'),
    'meetingLink': fields.String(description='The meeting link'),
    'calendarEventId': fields.String(description='The Google Calendar event ID'),
    'stripeSessionId': fields.String(description='The Stripe Checkout Session ID for refund tracking'),
    'createdAt': fields.DateTime(description='The creation timestamp'),
    'updatedAt': fields.DateTime(description='The last update timestamp')
})

session_input_model = api.model('SessionInput', {
    'tutorId': fields.String(required=True, description='The tutor UUID', example='a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'),
    'studentId': fields.String(required=True, description='The student UUID', example='b5eebc99-9c0b-4ef8-bb6d-6bb9bd380a22'),
    'tutorSubjectId': fields.String(required=True, description='The tutor subject UUID (references TutorSubjects table)', example='c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a33'),
    'startTime': fields.DateTime(required=True, description='The session start time', example='2027-03-03T10:00:00.000Z'),
    'endTime': fields.DateTime(required=True, description='The session end time', example='2028-03-03T11:00:00.000Z'),
    'status': fields.String(description='The session status', example='pending'),
    'durationMins': fields.Float(description='The duration of the session in minutes', example=60),
    'meetingLink': fields.String(description='The meeting link', example='https://meet.google.com/abc-defg-hij'),
    'calendarEventId': fields.String(description='The Google Calendar event ID', example='abc123xyz'),
})

session_update_model = api.model('SessionUpdate', {
    'tutorSubjectId': fields.String(description='The tutor subject UUID (references TutorSubjects table)', example='c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a33'),
    'startTime': fields.DateTime(description='The session start time', example='2027-03-03T10:00:00.000Z'),
    'endTime': fields.DateTime(description='The session end time', example='2028-03-03T11:00:00.000Z'),
    'status': fields.String(description='The session status', example='confirmed'),
    'studentId': fields.String(description='The student UUID — set to null to clear', example='b5eebc99-9c0b-4ef8-bb6d-6bb9bd380a22'),
    'durationMins': fields.Float(description='The duration of the session in minutes', example=90),
    'meetingLink': fields.String(description='The meeting link', example='https://meet.google.com/abc-defg-hij'),
    'calendarEventId': fields.String(description='The Google Calendar event ID', example='abc123xyz'),
    'stripeSessionId': fields.String(description='The Stripe Checkout Session ID for refund tracking', example='cs_test_abc123'),
})



@api.route("/health")
class Health(Resource):
    @api.response(200, 'Service is healthy')
    def get(self):
        """Health check."""
        return {"status": "healthy", "service": "session"}, 200


@api.route('/session')
class CreateSession(Resource):

    @api.expect(session_input_model)
    @api.response(201, 'Session created successfully', session_model)
    @api.response(409, 'Tutor has an overlapping session at this time.')
    @api.response(400, 'Failed to create session')
    @api.response(500, 'Internal server error')
    def post(self):
        """Create a new session record."""
        data = request.get_json()

        try:
            # Check for overlapping sessions
            conflict_check = supabase.table('Session').select('sessionId', count='exact') \
                .eq('tutorId', data['tutorId']) \
                .lt('startTime', data['endTime']) \
                .gt('endTime', data['startTime']) \
                .execute()

            if conflict_check.count > 0:
                return {'message': 'Tutor has an overlapping session at this time.'}, 409

            # If no conflict, create the session
            response = supabase.table('Session').insert(data).execute()
            
            if response.data:
                return response.data[0], 201
            
            return {'message': 'Failed to create session, no data returned.'}, 400

        except Exception as e:
            return {'message': 'Failed to create session', 'error': str(e)}, 500


@api.route("/<string:sessionId>")
class SessionDetail(Resource):

    @api.marshal_with(session_model)
    @api.response(200, 'Session found', session_model)
    @api.response(404, 'Session not found')
    @api.response(500, 'Internal server error')
    def get(self, sessionId):
        """Retrieve a session record by ID."""
        try:
            response = supabase.table('Session').select('*').eq('sessionId', sessionId).execute()
            if response.data:
                return response.data[0], 200
            return {'message': 'Session not found'}, 404
        except Exception as e:
            return {'message': 'Failed to retrieve session', 'error': str(e)}, 500


    @api.expect(session_update_model)
    @api.marshal_with(session_model)
    @api.response(200, 'Session updated', session_model)
    @api.response(404, 'Session not found')
    @api.response(500, 'Internal server error')
    def put(self, sessionId):
        """Update a session record. Null values are explicitly applied (e.g. to clear studentId)."""
        data = request.get_json()
        try:
            # Supabase Python client skips None values in .update(), so we must
            # separate the payload: non-null fields are updated normally, and
            # null fields are explicitly set via a second update call.
            non_null = {k: v for k, v in data.items() if v is not None}
            null_keys = [k for k, v in data.items() if v is None]

            # Apply non-null updates first (or all fields if no nulls)
            if non_null:
                response = supabase.table('Session').update(non_null).eq('sessionId', sessionId).execute()
                if not response.data:
                    return {'message': 'Session not found for update'}, 404

            # Explicitly clear null fields using a raw dict with None preserved
            if null_keys:
                null_payload = {k: None for k in null_keys}
                response = supabase.table('Session').update(null_payload).eq('sessionId', sessionId).execute()
                if not response.data:
                    return {'message': 'Session not found when clearing fields'}, 404

            # Return the latest state
            final = supabase.table('Session').select('*').eq('sessionId', sessionId).execute()
            if final.data:
                return final.data[0], 200
            return {'message': 'Session not found after update'}, 404
        except Exception as e:
            return {'message': 'Failed to update session', 'error': str(e)}, 500


    @api.response(200, 'Session deleted successfully')
    @api.response(404, 'Session not found')
    @api.response(500, 'Internal server error')
    def delete(self, sessionId):
        """Delete a session record."""
        try:
            response = supabase.table('Session').delete().eq('sessionId', sessionId).execute()
            if response.data:
                return {'message': 'Session deleted successfully'}, 200
            return {'message': 'Session not found for deletion'}, 404
        except APIError as e:
            return {'message': 'Failed to delete session', 'error': str(e)}, 500

complete_model = api.model('CompleteSession', {
    'tutorId': fields.String(required=True, description='The tutor UUID — must match the session owner'),
})

@api.route("/<string:sessionId>/complete")
class CompleteSession(Resource):
    @api.expect(complete_model)
    @api.response(200, 'Session marked as completed', session_model)
    @api.response(400, 'tutorId missing')
    @api.response(403, 'Not authorised to complete this session')
    @api.response(404, 'Session not found')
    @api.response(409, 'Session is not in booked status')
    @api.response(422, 'Session end time has not passed yet')
    @api.response(500, 'Internal server error')
    def post(self, sessionId):
        """Mark a booked session as completed. Validates tutor ownership and that end time has passed."""
        data = request.get_json() or {}
        tutor_id = data.get("tutorId")
        if not tutor_id:
            return {"message": "tutorId is required"}, 400

        try:
            resp = supabase.table('Session').select('*').eq('sessionId', sessionId).execute()
            if not resp.data:
                return {"message": "Session not found"}, 404
            session = resp.data[0]
        except Exception as e:
            return {"message": "Failed to retrieve session", "error": str(e)}, 500

        if session.get("tutorId") != tutor_id:
            return {"message": "You are not authorised to complete this session"}, 403

        if session.get("status") != "booked":
            return {"message": f"Session cannot be completed — current status is '{session.get('status')}'"}, 409

        end_time_str = session.get("endTime")
        if not end_time_str:
            return {"message": "Session has no end time"}, 500

        try:
            end_time = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))
            # Make timezone-aware if naive (Supabase may return without tz)
            if end_time.tzinfo is None:
                end_time = end_time.replace(tzinfo=timezone.utc)
        except Exception:
            return {"message": "Invalid end time format"}, 500

        if datetime.now(timezone.utc) < end_time:
            return {"message": "Session cannot be marked complete before it has ended"}, 422

        try:
            update = supabase.table('Session').update({"status": "completed"}).eq('sessionId', sessionId).execute()
            if update.data:
                return update.data[0], 200
            return {"message": "Failed to update session"}, 500
        except Exception as e:
            return {"message": "Failed to update session", "error": str(e)}, 500


@api.route("/all")
class SessionList(Resource):

    @api.doc(params={'tutorId': 'The ID of the tutor to filter by.', 'studentId': 'The ID of the student to filter by.'})
    @api.marshal_list_with(session_model)
    @api.response(200, 'Sessions returned')
    @api.response(404, 'No sessions found for the given filters')
    @api.response(500, 'Internal server error')
    def get(self):
        """Retrieve sessions, optionally filtered by tutorId and/or studentId."""
        tutor_id = request.args.get('tutorId')
        student_id = request.args.get('studentId')
        query = supabase.table('Session').select('*')
        
        if tutor_id:
            query = query.eq('tutorId', tutor_id)
        if student_id:
            query = query.eq('studentId', student_id)
        
        try:
            response = query.execute()
        except APIError as e:
            return {'message': 'An error occurred', 'error': str(e)}, 500

        if not response.data and (tutor_id or student_id):
            filters = []
            if tutor_id:
                filters.append(f'tutor {tutor_id}')
            if student_id:
                filters.append(f'student {student_id}')
            return {'message': f'No sessions found for {" and ".join(filters)}'}, 404
        
        return response.data, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
