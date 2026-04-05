import os
import requests
import jwt as pyjwt
from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
api = Api(app, doc="/docs",
    title="Delete Subject Service",
    version="1.0",
    description="Delete Subject composite service — prevents deleting a tutor subject if any sessions exist for it.",
    prefix="/delete-subject"
)

SESSION_SERVICE_URL = os.environ.get("SESSION_SERVICE_URL", "http://localhost:5003")
TUTOR_SERVICE_URL = os.environ.get("TUTOR_SERVICE_URL", "http://localhost:5002")

error_model = api.model('DeleteSubjectError', {
    'message': fields.String(description='Error message', example='Cannot delete subject with existing sessions.'),
})


@api.route("/health")
class Health(Resource):

    @api.response(200, 'Service is healthy')
    def get(self):
        """Health check."""
        return {"status": "healthy", "service": "delete_subject"}, 200


@api.route("/<string:tutor_id>/subjects/<string:subject_id>")
class DeleteSubject(Resource):

    @api.doc(params={'tutor_id': 'Tutor UUID', 'subject_id': 'Tutor subject UUID'})
    @api.response(200, 'Subject deleted successfully', api.model('DeleteSubjectResponse', {
        'message': fields.String(example='Subject deleted successfully'),
    }))
    @api.response(401, 'Invalid or missing Bearer JWT', error_model)
    @api.response(404, 'Subject not found', error_model)
    @api.response(409, 'Cannot delete subject with existing sessions', error_model)
    @api.response(500, 'Failed to delete subject', error_model)
    def delete(self, tutor_id, subject_id):
        """
        Delete a tutor subject only if there are no existing sessions using it.

        Flow:
        1. Validate Bearer JWT.
        2. Confirm subject exists for the tutor.
        3. Check for any sessions referencing tutorSubjectId.
        4. Delete subject via Tutor atomic service.
        """
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "", 1).strip()

        if not token:
            return {"message": "Invalid authorization token"}, 401

        try:
            pyjwt.decode(token, options={"verify_signature": False})
        except Exception:
            return {"message": "Invalid authorization token"}, 401

        # 1. Confirm that the subject exists
        try:
            subjects_resp = requests.get(
                f"{TUTOR_SERVICE_URL}/tutor/{tutor_id}/subjects",
                headers={"Authorization": auth_header},
                timeout=5
            )
        except requests.RequestException as exc:
            return {"message": "Failed to contact tutor service", "error": str(exc)}, 500

        if subjects_resp.status_code != 200:
            return {"message": "Failed to retrieve tutor subjects"}, 500

        try:
            tutor_subjects = subjects_resp.json() or []
        except ValueError:
            return {"message": "Tutor service returned invalid JSON"}, 500

        subject = next((s for s in tutor_subjects if s.get("tutorSubjectId") == subject_id), None)
        if not subject:
            return {"message": "Subject not found"}, 404

        # 2. Check if any sessions exist for this tutor subject
        try:
            sessions_resp = requests.get(
                f"{SESSION_SERVICE_URL}/session/all",
                params={"tutorId": tutor_id},
                headers={"Authorization": auth_header},
                timeout=5
            )
        except requests.RequestException as exc:
            return {"message": "Failed to contact session service", "error": str(exc)}, 500

        if sessions_resp.status_code == 404:
            sessions = []
        elif sessions_resp.status_code != 200:
            return {"message": "Failed to retrieve sessions"}, 500
        else:
            try:
                sessions = sessions_resp.json() or []
            except ValueError:
                return {"message": "Session service returned invalid JSON"}, 500

        sessions_for_subject = [s for s in sessions if s.get("tutorSubjectId") == subject_id]
        if sessions_for_subject:
            return {"message": "Cannot delete subject while sessions exist for it."}, 409

        # 3. Delete the tutor subject
        try:
            delete_resp = requests.delete(
                f"{TUTOR_SERVICE_URL}/tutor/{tutor_id}/subjects/{subject_id}",
                headers={"Authorization": auth_header},
                timeout=5
            )
        except requests.RequestException as exc:
            return {"message": "Failed to contact tutor service", "error": str(exc)}, 500

        if delete_resp.status_code == 404:
            return {"message": "Subject not found"}, 404
        if delete_resp.status_code not in (200, 204):
            return {"message": "Failed to delete subject", "error": delete_resp.text}, 500

        return {"message": "Subject deleted successfully"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5110, debug=True)
