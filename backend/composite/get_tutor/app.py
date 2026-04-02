from flask import Flask, request
from flask_restx import Api, Resource
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


@api.route("/health")
class Health(Resource):
    def get(self):
        return {"status": "healthy", "service": "get_tutor"}, 200


@api.route("/<string:tutor_id>")
class GetTutor(Resource):
    def get(self, tutor_id):
        """Get tutor info with enriched reviews."""
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
