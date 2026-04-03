from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)
api = Api(app, doc="/docs",
    title="Checkout Service",
    version="1.0",
    description="Checkout composite service",
    prefix="/checkout"
)

SESSION_SERVICE_URL = os.environ.get("SESSION_SERVICE_URL", "http://localhost:5003")
TUTOR_SERVICE_URL = os.environ.get("TUTOR_SERVICE_URL", "http://localhost:5002")
PAYMENT_SERVICE_URL = os.environ.get("PAYMENT_SERVICE_URL", "http://localhost:5007")

checkout_input = api.model('CheckoutInput', {
    'session_id': fields.String(required=True, description='The session UUID to book'),
    'student_id': fields.String(required=True, description='The student UUID who is booking')
})


@api.route("/health")
class Health(Resource):
    def get(self):
        return {"status": "healthy", "service": "checkout"}, 200


@api.route("/checkout")
class Checkout(Resource):
    @api.expect(checkout_input)
    def post(self):
        """Create a Stripe checkout session for booking a tuition session."""
        data = request.get_json()
        session_id = data.get("session_id")
        student_id = data.get("student_id")
        if not session_id or not student_id:
            return {"message": "session_id and student_id are required"}, 400

        # 1. Fetch session from session atomic service
        session_resp = requests.get(
            f"{SESSION_SERVICE_URL}/session/{session_id}",
            timeout=5
        )
        if session_resp.status_code == 404:
            return {"message": "Session not found"}, 404
        if session_resp.status_code != 200:
            return {"message": "Failed to retrieve session"}, 500

        session = session_resp.json()
        tutor_id = session.get("tutorId")
        tutor_subject_id = session.get("tutorSubjectId")
        duration_mins = session.get("durationMins", 0)
        start_time = session.get("startTime", "")

        # 2. Fetch tutor (includes name + subjects[]) in one call
        tutor_resp = requests.get(
            f"{TUTOR_SERVICE_URL}/tutor/{tutor_id}",
            timeout=5
        )
        if tutor_resp.status_code != 200:
            return {"message": "Failed to retrieve tutor"}, 500

        tutor_data = tutor_resp.json()
        tutor_name = tutor_data.get("name", "Tutor")

        matching = next(
            (s for s in tutor_data.get("subjects", []) if s.get("tutorSubjectId") == tutor_subject_id),
            None
        )
        if not matching:
            return {"message": "Tutor subject not found"}, 404

        hourly_rate = matching.get("hourlyRate", 0)
        subject_name = matching.get("subject", "Tuition")
        academic_level = matching.get("academicLevel", "")

        # 4. Calculate price server-side
        total_price = round(hourly_rate * (duration_mins / 60.0), 2)
        amount_cents = int(total_price * 100)

        # 5. Call payment atomic service
        payment_resp = requests.post(
            f"{PAYMENT_SERVICE_URL}/payment/create-checkout-session",
            json={
                "title": f"{subject_name} ({academic_level})",
                "description": f"{int(duration_mins)} min session",
                "amount": amount_cents,
                "tutor_name": tutor_name,
                "subject": subject_name,
                "lesson_date": start_time,
                "session_id": session_id,
                "student_id": student_id,
                "tutor_id": tutor_id,
            },
            timeout=10
        )
        if payment_resp.status_code != 200:
            return {"message": "Failed to create checkout session"}, 500

        return payment_resp.json(), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5100, debug=True)
