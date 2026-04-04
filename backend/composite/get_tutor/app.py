from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)
api = Api(app, doc="/docs",
    title="Get Tutor Service",
    version="1.0",
    description="Get Tutor composite service — returns tutor info with enriched reviews (student name + avatar).",
    prefix="/get-tutor"
)

TUTOR_SERVICE_URL   = os.environ.get("TUTOR_SERVICE_URL",   "http://localhost:5002")
STUDENT_SERVICE_URL = os.environ.get("STUDENT_SERVICE_URL", "http://localhost:5001")
REVIEW_SERVICE_URL  = os.environ.get("REVIEW_SERVICE_URL",  "https://personal-rkcavjxu.outsystemscloud.com/Review/rest/Review")

subject_model = api.model('TutorSubject', {
    'tutorSubjectId': fields.String(description='Tutor subject UUID', example='d2eebc99-9c0b-4ef8-bb6d-6bb9bd380a44'),
    'subject': fields.String(description='Subject name', example='Mathematics'),
    'academicLevel': fields.String(description='Academic level', example='A-Level'),
    'hourlyRate': fields.Float(description='Hourly rate in SGD', example=80.0),
})

enriched_review_model = api.model('EnrichedReview', {
    'review_id': fields.String(description='Review UUID from OutSystems', example='rv_001'),
    'tutor_id': fields.String(description='Tutor UUID', example='c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a33'),
    'student_id': fields.String(description='Student UUID', example='b5eebc99-9c0b-4ef8-bb6d-6bb9bd380a22'),
    'rating': fields.Integer(description='Rating (1–5)', example=5),
    'comment': fields.String(description='Review comment', example='Excellent tutor, very clear explanations!'),
    'studentName': fields.String(description='Student full name (enriched)', example='Alice Tan'),
    'studentAvatar': fields.String(description='Student profile image URL (enriched)', example='https://storage.example.com/alice.jpg'),
})

get_tutor_response = api.model('GetTutorResponse', {
    'tutorId': fields.String(description='Tutor UUID', example='c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a33'),
    'name': fields.String(description='Tutor full name', example='Mr John Lim'),
    'email': fields.String(description='Tutor email', example='john@example.com'),
    'bio': fields.String(description='Tutor bio', example='Experienced A-Level Mathematics tutor with 10 years experience.'),
    'imageURL': fields.String(description='Profile image URL', example='https://storage.example.com/john.jpg'),
    'averageRating': fields.Float(description='Average rating from reviews', example=4.8),
    'subjects': fields.List(fields.Nested(subject_model), description='Subjects taught by this tutor'),
    'reviews': fields.List(fields.Nested(enriched_review_model), description='Reviews enriched with student name and avatar'),
})

gt_error_model = api.model('GetTutorError', {
    'message': fields.String(description='Error message', example='Tutor not found'),
})


@api.route("/health")
class Health(Resource):
    @api.response(200, 'Service is healthy')
    def get(self):
        """Health check."""
        return {"status": "healthy", "service": "get_tutor"}, 200


@api.route("/<string:tutor_id>")
class GetTutor(Resource):
    @api.doc(params={'tutor_id': 'Tutor UUID'})
    @api.response(200, 'Tutor info with enriched reviews', get_tutor_response)
    @api.response(404, 'Tutor not found', gt_error_model)
    @api.response(500, 'Downstream service error', gt_error_model)
    def get(self, tutor_id):
        """
        Get tutor info with enriched reviews (student name + avatar).

        **Flow:**
        1. Fetch tutor profile and subjects (Tutor Service)
        2. Fetch all reviews for this tutor (OutSystems Review API)
        3. Enrich each review with student name and avatar (Student Service)
        """
        auth_header = request.headers.get("Authorization", "")

        # 1. Fetch tutor info
        tutor_resp = requests.get(
            f"{TUTOR_SERVICE_URL}/tutor/{tutor_id}",
            timeout=5
        )
        if tutor_resp.status_code == 404:
            return {"message": "Tutor not found"}, 404
        if tutor_resp.status_code != 200:
            return {"message": "Failed to retrieve tutor"}, 500

        tutor = tutor_resp.json()

        # 2. Fetch reviews from OutSystems
        reviews_resp = requests.get(
            f"{REVIEW_SERVICE_URL}/tut_review/{tutor_id}",
            timeout=10
        )
        raw_reviews = []
        if reviews_resp.status_code == 200:
            raw_reviews = reviews_resp.json().get("data", {}).get("reviews", [])

        # 3. Enrich each review with student name + avatar
        student_cache = {}
        enriched_reviews = []
        for review in raw_reviews:
            student_id = review.get("student_id", "")
            if student_id and student_id not in student_cache:
                try:
                    s_resp = requests.get(
                        f"{STUDENT_SERVICE_URL}/student/{student_id}",
                        headers={"Authorization": auth_header},
                        timeout=5
                    )
                    if s_resp.status_code == 200:
                        student_cache[student_id] = s_resp.json()
                    else:
                        student_cache[student_id] = None
                except Exception:
                    student_cache[student_id] = None

            student = student_cache.get(student_id)
            enriched_reviews.append({
                **review,
                "studentName": student.get("name") if student else "Anonymous",
                "studentAvatar": student.get("imageURL") if student else None,
            })

        return {
            **tutor,
            "reviews": enriched_reviews
        }, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5109, debug=True)
