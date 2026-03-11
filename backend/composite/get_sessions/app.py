from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)
api = Api(app, doc="/docs",
    title="Get Sessions Service",
    version="1.0",
    description="Composite service to retrieve sessions (by student or tutor) and enrich with tutor details and pricing"
)

# Service URLs
SESSION_SERVICE_URL = "http://session:5003"
TUTOR_SERVICE_URL = "http://tutor:5002"

# Response model
enhanced_session_model = api.model('EnhancedSession', {
    'sessionId': fields.String(description='The session UUID'),
    'tutorId': fields.String(description='The tutor UUID'),
    'studentId': fields.String(description='The student UUID'),
    'tutorSubjectId': fields.String(description='The tutor subject UUID'),
    'startTime': fields.DateTime(description='The session start time'),
    'endTime': fields.DateTime(description='The session end time'),
    'status': fields.String(description='The session status'),
    'durationMins': fields.Float(description='The duration in minutes'),
    'meetingLink': fields.String(description='The meeting link'),
    'createdAt': fields.DateTime(description='Creation timestamp'),
    'updatedAt': fields.DateTime(description='Update timestamp'),
    'tutorName': fields.String(description='The tutor full name'),
    'tutorImageUrl': fields.String(description='The tutor image URL'),
    'subjectName': fields.String(description='The subject name from TutorSubjects'),
    'totalPrice': fields.Float(description='Total price calculated from hourly rate and duration')
})


@api.route("/health")
class Health(Resource):
    def get(self):
        return {"status": "healthy", "service": "get_sessions"}, 200


@api.route("/student/<string:studentId>/sessions")
class StudentSessions(Resource):
    @api.marshal_list_with(enhanced_session_model)
    @api.response(200, 'Successfully retrieved sessions')
    @api.response(404, 'No sessions found for student')
    @api.response(500, 'Internal server error')
    def get(self, studentId):
        """Retrieve all sessions for a student with tutor details and pricing"""
        try:
            # 1. Get all sessions for the student
            sessions_response = requests.get(
                f"{SESSION_SERVICE_URL}/sessions",
                params={"studentId": studentId},
                timeout=5
            )
            
            if sessions_response.status_code == 404:
                return {'message': f'No sessions found for student {studentId}'}, 404
            
            if sessions_response.status_code != 200:
                return {'message': 'Failed to retrieve sessions from session service'}, 500
            
            sessions = sessions_response.json()
            
            if not sessions:
                return [], 200
            
            # 2. Enhance each session with tutor details and pricing
            enhanced_sessions = _enrich_sessions(sessions)
            
            return enhanced_sessions, 200
            
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            return {'message': f'Error communicating with services: {str(e)}'}, 500
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'message': f'Internal server error: {str(e)}'}, 500


@api.route("/tutor/<string:tutorId>/sessions")
class TutorSessions(Resource):
    @api.marshal_list_with(enhanced_session_model)
    @api.response(200, 'Successfully retrieved sessions')
    @api.response(404, 'No sessions found for tutor')
    @api.response(500, 'Internal server error')
    def get(self, tutorId):
        """Retrieve all sessions for a tutor with student details and pricing"""
        try:
            # 1. Get all sessions for the tutor
            sessions_response = requests.get(
                f"{SESSION_SERVICE_URL}/sessions",
                params={"tutorId": tutorId},
                timeout=5
            )
            
            if sessions_response.status_code == 404:
                return {'message': f'No sessions found for tutor {tutorId}'}, 404
            
            if sessions_response.status_code != 200:
                return {'message': 'Failed to retrieve sessions from session service'}, 500
            
            sessions = sessions_response.json()
            
            if not sessions:
                return [], 200
            
            # 2. Enhance each session with tutor details and pricing
            enhanced_sessions = _enrich_sessions(sessions)
            
            return enhanced_sessions, 200
            
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            return {'message': f'Error communicating with services: {str(e)}'}, 500
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'message': f'Internal server error: {str(e)}'}, 500


def _enrich_sessions(sessions):
    """Helper function to enrich sessions with tutor details and pricing"""
    enhanced_sessions = []
    
    for session in sessions:
        try:
            enhanced_session = session.copy()
            tutor_id = session.get('tutorId')
            tutor_subject_id = session.get('tutorSubjectId')
            
            # Get tutor details
            if tutor_id:
                tutor_response = requests.get(
                    f"{TUTOR_SERVICE_URL}/tutor/{tutor_id}",
                    timeout=5
                )
                
                if tutor_response.status_code == 200:
                    tutor_data = tutor_response.json()
                    enhanced_session['tutorName'] = tutor_data.get('name', 'Unknown')
                    enhanced_session['tutorImageUrl'] = tutor_data.get('imageURL', None)
                else:
                    enhanced_session['tutorName'] = 'Unknown'
                    enhanced_session['tutorImageUrl'] = None
            else:
                enhanced_session['tutorName'] = 'Unknown'
                enhanced_session['tutorImageUrl'] = None
            
            # Get tutor subject details (hourlyRate and subject name)
            if tutor_id and tutor_subject_id:
                subjects_response = requests.get(
                    f"{TUTOR_SERVICE_URL}/tutor/{tutor_id}/subjects",
                    timeout=5
                )
                
                if subjects_response.status_code == 200:
                    subjects = subjects_response.json()
                    # Find the matching tutorSubject
                    matching_subject = next(
                        (s for s in subjects if s.get('tutorSubjectId') == tutor_subject_id),
                        None
                    )
                    
                    if matching_subject:
                        hourly_rate = matching_subject.get('hourlyRate', 0)
                        enhanced_session['subjectName'] = matching_subject.get('subject', 'Unknown')
                        
                        # Calculate total price based on duration
                        duration_mins = session.get('durationMins', 0)
                        if duration_mins and hourly_rate:
                            # Convert minutes to hours and multiply by hourly rate
                            duration_hours = duration_mins / 60.0
                            enhanced_session['totalPrice'] = round(hourly_rate * duration_hours, 2)
                        else:
                            enhanced_session['totalPrice'] = 0.0
                    else:
                        enhanced_session['subjectName'] = 'Unknown'
                        enhanced_session['totalPrice'] = 0.0
                else:
                    enhanced_session['subjectName'] = 'Unknown'
                    enhanced_session['totalPrice'] = 0.0
            else:
                enhanced_session['subjectName'] = 'Unknown'
                enhanced_session['totalPrice'] = 0.0
            
            enhanced_sessions.append(enhanced_session)
            
        except Exception as e:
            print(f"Error enhancing session {session.get('sessionId')}: {str(e)}")
            # Add session with default values on error
            enhanced_session = session.copy()
            enhanced_session.setdefault('tutorName', 'Unknown')
            enhanced_session.setdefault('tutorImageUrl', None)
            enhanced_session.setdefault('subjectName', 'Unknown')
            enhanced_session.setdefault('totalPrice', 0.0)
            enhanced_sessions.append(enhanced_session)
    
    return enhanced_sessions


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5103, debug=True)
