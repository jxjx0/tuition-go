import os
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
    description="Composite service to retrieve sessions (by student or tutor) and enrich with tutor details and pricing",
    prefix="/getsessions"
)

# Service URLs - Use environment variables when running in Docker
SESSION_SERVICE_URL = os.environ.get("SESSION_SERVICE_URL", "http://localhost:5003")
TUTOR_SERVICE_URL = os.environ.get("TUTOR_SERVICE_URL", "http://localhost:5002")
STUDENT_SERVICE_URL = os.environ.get("STUDENT_SERVICE_URL", "http://localhost:5001")
REVIEW_SERVICE_URL = os.environ.get("REVIEW_SERVICE_URL", "https://personal-rkcavjxu.outsystemscloud.com/Review/rest/Review/")


def _get_auth_headers():
    """Forward the Authorization header from the incoming request."""
    auth = request.headers.get("Authorization", "")
    if auth:
        return {"Authorization": auth}
    return {}

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
    'academicLevel': fields.String(description='The academic level from TutorSubjects'),
    'totalPrice': fields.Float(description='Total price calculated from hourly rate and duration'),
    'studentName': fields.String(description='The student full name'),
    'studentImageUrl': fields.String(description='The student image URL'),
    'review': fields.Raw(description='Review for this session, if any')
})


gs_error_model = api.model('GetSessionsError', {
    'message': fields.String(description='Error message', example='No sessions found for student b5eebc99-9c0b-4ef8-bb6d-6bb9bd380a22'),
})


@api.route("/health")
class Health(Resource):
    @api.response(200, 'Service is healthy')
    def get(self):
        """Health check."""
        return {"status": "healthy", "service": "get_sessions"}, 200


@api.route("/student/<string:studentId>/sessions")
class StudentSessions(Resource):

    @api.doc(params={'studentId': 'Student UUID'})
    @api.marshal_list_with(enhanced_session_model)
    @api.response(200, 'Successfully retrieved sessions')
    @api.response(404, 'No sessions found for student', gs_error_model)
    @api.response(500, 'Internal server error', gs_error_model)
    def get(self, studentId):
        """
        Retrieve all sessions for a student, enriched with tutor name, subject, pricing.

        **Flow:**
        1. Fetch all sessions for the student (Session Service)
        2. For each session: fetch tutor name, imageURL, subject name, academic level, and hourly rate (Tutor Service)
        3. Calculate `totalPrice` from hourly rate × durationMins
        """
        try:
            # 1. Get all sessions for the student
            auth_headers = _get_auth_headers()
            sessions_response = requests.get(
                f"{SESSION_SERVICE_URL}/session/all",
                params={"studentId": studentId},
                headers=auth_headers,
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

    @api.doc(params={'tutorId': 'Tutor UUID'})
    @api.marshal_list_with(enhanced_session_model)
    @api.response(200, 'Successfully retrieved sessions')
    @api.response(404, 'No sessions found for tutor', gs_error_model)
    @api.response(500, 'Internal server error', gs_error_model)
    def get(self, tutorId):
        """
        Retrieve all sessions for a tutor, enriched with subject, pricing, and student details.

        **Flow:**
        1. Fetch all sessions for the tutor (Session Service)
        2. For each session: fetch tutor subject/pricing (Tutor Service) and student name/avatar (Student Service)
        3. Calculate `totalPrice` from hourly rate × durationMins
        """
        try:
            # 1. Get all sessions for the tutor
            auth_headers = _get_auth_headers()
            sessions_response = requests.get(
                f"{SESSION_SERVICE_URL}/session/all",
                params={"tutorId": tutorId},
                headers=auth_headers,
                timeout=5
            )
            
            if sessions_response.status_code == 404:
                return {'message': f'No sessions found for tutor {tutorId}'}, 404
            
            if sessions_response.status_code != 200:
                return {'message': 'Failed to retrieve sessions from session service'}, 500
            
            sessions = sessions_response.json()
            
            if not sessions:
                return [], 200
            
            # 2. Enhance each session with tutor + student details and pricing
            enhanced_sessions = _enrich_sessions_for_tutor(sessions)

            return enhanced_sessions, 200

        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            return {'message': f'Error communicating with services: {str(e)}'}, 500
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'message': f'Internal server error: {str(e)}'}, 500


@api.route("/session/<string:sessionId>")
class SessionDetail(Resource):

    @api.doc(params={'sessionId': 'Session UUID'})
    @api.marshal_with(enhanced_session_model)
    @api.response(200, 'Successfully retrieved session')
    @api.response(404, 'Session not found', gs_error_model)
    @api.response(500, 'Internal server error', gs_error_model)
    def get(self, sessionId):
        """
        Retrieve a single session by ID, enriched with tutor, subject, pricing, student, and review.

        **Flow:**
        1. Fetch session by ID (Session Service)
        2. Enrich with tutor/subject/pricing and student details (Tutor + Student Services)
        3. Fetch the review for this specific session, if any (OutSystems Review API)
        """
        try:
            # 1. Get the specific session
            auth_headers = _get_auth_headers()
            session_response = requests.get(
                f"{SESSION_SERVICE_URL}/session/{sessionId}",
                headers=auth_headers,
                timeout=5
            )
            
            if session_response.status_code == 404:
                return {'message': f'Session {sessionId} not found'}, 404
            
            if session_response.status_code != 200:
                return {'message': 'Failed to retrieve session from session service'}, 500
            
            session = session_response.json()
            
            # 2. Enhance the session with tutor, subject, pricing and student details
            enhanced_sessions = _enrich_sessions_for_tutor([session])
            
            enriched = enhanced_sessions[0]
        
            try:
                review_response = requests.get(
                    f"{REVIEW_SERVICE_URL}/sess_review/{sessionId}",
                    timeout=5
                )
                if review_response.status_code == 200:
                    review_data = review_response.json()
                    # API returns a list or single object — normalise to single or None
                    reviews = review_data.get("data", {}).get("reviews", [])
                    enriched['review'] = reviews[0] if reviews else None
                else:
                    enriched['review'] = None
            except Exception:
                enriched['review'] = None  # Non-fatal — don't break the whole response

            return enriched, 200
            
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

            # Single call to GET /tutor/{id} — returns name, imageURL, and subjects[]
            if tutor_id:
                tutor_response = requests.get(
                    f"{TUTOR_SERVICE_URL}/tutor/{tutor_id}",
                    timeout=5
                )

                if tutor_response.status_code == 200:
                    tutor_data = tutor_response.json()
                    enhanced_session['tutorName'] = tutor_data.get('name', 'Unknown')
                    enhanced_session['tutorImageUrl'] = tutor_data.get('imageURL', None)

                    # Find matching subject from the nested subjects list
                    subjects = tutor_data.get('subjects', [])
                    matching_subject = next(
                        (s for s in subjects if s.get('tutorSubjectId') == tutor_subject_id),
                        None
                    )

                    if matching_subject:
                        hourly_rate = matching_subject.get('hourlyRate', 0)
                        enhanced_session['subjectName'] = matching_subject.get('subject', 'Unknown')
                        enhanced_session['academicLevel'] = matching_subject.get('academicLevel', 'Unknown')
                        duration_mins = session.get('durationMins', 0)
                        if duration_mins and hourly_rate:
                            enhanced_session['totalPrice'] = round(hourly_rate * (duration_mins / 60.0), 2)
                        else:
                            enhanced_session['totalPrice'] = 0.0
                    else:
                        enhanced_session['subjectName'] = 'Unknown'
                        enhanced_session['academicLevel'] = 'Unknown'
                        enhanced_session['totalPrice'] = 0.0
                else:
                    enhanced_session['tutorName'] = 'Unknown'
                    enhanced_session['tutorImageUrl'] = None
                    enhanced_session['subjectName'] = 'Unknown'
                    enhanced_session['academicLevel'] = 'Unknown'
                    enhanced_session['totalPrice'] = 0.0
            else:
                enhanced_session['tutorName'] = 'Unknown'
                enhanced_session['tutorImageUrl'] = None
                enhanced_session['subjectName'] = 'Unknown'
                enhanced_session['academicLevel'] = 'Unknown'
                enhanced_session['totalPrice'] = 0.0

            enhanced_sessions.append(enhanced_session)

        except Exception as e:
            print(f"Error enhancing session {session.get('sessionId')}: {str(e)}")
            enhanced_session = session.copy()
            enhanced_session.setdefault('tutorName', 'Unknown')
            enhanced_session.setdefault('tutorImageUrl', None)
            enhanced_session.setdefault('subjectName', 'Unknown')
            enhanced_session.setdefault('academicLevel', 'Unknown')
            enhanced_session.setdefault('totalPrice', 0.0)
            enhanced_sessions.append(enhanced_session)

    return enhanced_sessions


def _enrich_sessions_for_tutor(sessions):
    """Enrich sessions with tutor subject details, pricing, and student details."""
    enhanced_sessions = _enrich_sessions(sessions)

    for enhanced_session in enhanced_sessions:
        student_id = enhanced_session.get('studentId')
        if student_id:
            try:
                student_response = requests.get(
                    f"{STUDENT_SERVICE_URL}/student/{student_id}",
                    timeout=5
                )
                if student_response.status_code == 200:
                    student_data = student_response.json()
                    enhanced_session['studentName'] = student_data.get('name', 'Unknown')
                    enhanced_session['studentImageUrl'] = student_data.get('imageURL', None)
                else:
                    enhanced_session['studentName'] = 'Unknown'
                    enhanced_session['studentImageUrl'] = None
            except Exception as e:
                print(f"Error fetching student {student_id}: {str(e)}")
                enhanced_session['studentName'] = 'Unknown'
                enhanced_session['studentImageUrl'] = None
        else:
            enhanced_session['studentName'] = None
            enhanced_session['studentImageUrl'] = None

    return enhanced_sessions


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5103, debug=True)
