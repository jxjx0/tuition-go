from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)
api = Api(app, doc="/docs",
    title="Rate Tutor Service",
    version="1.0",
    description="Rate Tutor composite service — validates session, submits review to OutSystems, updates tutor average rating.",
    prefix="/rate-tutor"
)

SESSION_SERVICE_URL = os.environ.get("SESSION_SERVICE_URL", "http://localhost:5003")
TUTOR_SERVICE_URL   = os.environ.get("TUTOR_SERVICE_URL",   "http://localhost:5002")
REVIEW_SERVICE_URL  = os.environ.get("REVIEW_SERVICE_URL",  "https://personal-rkcavjxu.outsystemscloud.com/Review/rest/Review")

review_input = api.model("ReviewInput", {
    "session_id": fields.String(required=True, description="Session UUID"),
    "tutor_id":   fields.String(required=True, description="Tutor UUID"),
    "rating":     fields.Integer(required=True, description="Rating 1–5"),
    "comment":    fields.String(required=True, description="Review comment"),
})


@api.route("/health")
class Health(Resource):
    def get(self):
        return {"status": "healthy", "service": "rate_tutor"}, 200


@api.route("/review")
class RateTutor(Resource):
    @api.expect(review_input)
    def post(self):
        """Submit a review for a completed session, then update tutor average rating."""
        auth_header = request.headers.get("Authorization", "")
        data = request.get_json()
        session_id = data.get("session_id")
        tutor_id   = data.get("tutor_id")
        rating     = data.get("rating")
        comment    = data.get("comment", "").strip()

        if not all([session_id, tutor_id, rating, comment]):
            return {"message": "session_id, tutor_id, rating, and comment are required"}, 400

        if not isinstance(rating, (int, float)) or not (1 <= rating <= 5):
            return {"message": "Rating must be between 1 and 5"}, 400

        # 2. Fetch session — must be completed
        session_resp = requests.get(
            f"{SESSION_SERVICE_URL}/session/{session_id}",
            headers={"Authorization": auth_header},
            timeout=5
        )
        if session_resp.status_code == 404:
            return {"message": "Session not found"}, 404
        if session_resp.status_code != 200:
            return {"message": "Failed to retrieve session"}, 500

        session = session_resp.json()

        if session.get("status") != "completed":
            return {"message": "You can only review completed sessions"}, 409

        if session.get("tutorId") != tutor_id:
            return {"message": "tutor_id does not match the session's tutor"}, 400

        # 3. Submit review to OutSystems
        import time
        review_payload = {
            "review_id": int(time.time() * 1000),
            "student_id": session.get("studentId", ""),
            "session_id": session_id,
            "tutor_id": tutor_id,
            "rating": rating,
            "comment": comment,
            "createdAt": __import__('datetime').datetime.utcnow().isoformat() + "Z",
        }

        review_resp = requests.post(
            f"{REVIEW_SERVICE_URL}/review",
            json=review_payload,
            timeout=10
        )
        if review_resp.status_code not in (200, 201):
            return {"message": "Failed to submit review", "error": review_resp.text}, 500

        # 4. Update tutor average rating
        rating_resp = requests.put(
            f"{TUTOR_SERVICE_URL}/tutor/updateRating",
            json={"tutorId": tutor_id, "newRating": rating},
            timeout=5
        )
        if rating_resp.status_code != 200:
            # Non-fatal — review saved, rating update failed
            return {
                "message": "Review submitted but tutor rating update failed",
                "review": review_resp.json(),
                "ratingError": rating_resp.text
            }, 207

        return {
            "message": "Review submitted and tutor rating updated",
            "review": review_resp.json(),
            "tutorRating": rating_resp.json()
        }, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5102, debug=True)
