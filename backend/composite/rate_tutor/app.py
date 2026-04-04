from flask import Flask, request, session
from flask_restx import Api, Resource, fields
from flask_cors import CORS
import os
import requests
import time

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
    "session_id": fields.String(required=True, description="Session UUID", example="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"),
    "tutor_id":   fields.String(required=True, description="Tutor UUID", example="c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a33"),
    "rating":     fields.Integer(required=True, description="Rating 1–5", example=5),
    "comment":    fields.String(required=True, description="Review comment", example="Excellent tutor, very clear explanations!"),
})

review_response = api.model("ReviewResponse", {
    "message": fields.String(example="Review submitted and tutor rating updated"),
    "review": fields.Raw(description="Review object returned by OutSystems"),
    "tutorRating": fields.Raw(description="Updated tutor rating object returned by Tutor Service"),
})

rt_error_model = api.model("RateTutorError", {
    "message": fields.String(description="Error message", example="You can only review completed sessions"),
})


@api.route("/health")
class Health(Resource):
    @api.response(200, "Service is healthy")
    def get(self):
        """Health check."""
        return {"status": "healthy", "service": "rate_tutor"}, 200


@api.route("/review")
class RateTutor(Resource):
    @api.expect(review_input)
    @api.response(200, "Review submitted/updated and tutor rating synced", review_response)
    @api.response(207, "Review submitted but rating fetch or tutor sync failed", review_response)
    @api.response(400, "Missing/invalid fields or tutor_id mismatch", rt_error_model)
    @api.response(404, "Session not found", rt_error_model)
    @api.response(409, "Session is not completed — cannot review", rt_error_model)
    @api.response(500, "Downstream service error", rt_error_model)
    def post(self):
        """
        Submit or update a review for a completed tuition session. Requires student Bearer JWT.

        **Business rules:**
        - Session must have status `completed`
        - `tutor_id` must match the session's tutor
        - If a review already exists for this session, it is updated (PUT); otherwise created (POST)

        **Flow:**
        1. Validate inputs
        2. Fetch session — verify status is `completed` and tutor matches (Session Service)
        3. Check for an existing review on this session (OutSystems Review API)
        4. Create or update the review (OutSystems Review API)
        5. Fetch updated average rating and review count (OutSystems Review API)
        6. Sync `averageRating` and `totalReviews` to the Tutor table (Tutor Service)
        """
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

        # 2. Fetch session — must be completed (SESSION ATOMIC SERVICE)
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

        # 3. Check for existing review on this session (REVIEW ATOMIC SERVICE)
        existing_review_id = None
        existing_resp = requests.get(
            f"{REVIEW_SERVICE_URL}/sess_review/{session_id}",
            timeout=10
        )
        
        if existing_resp.status_code == 200:
            existing_reviews = existing_resp.json().get("data", {}).get("reviews", [])
            match = next((r for r in existing_reviews if r.get("session_id") == session_id), None)
            if match:
                existing_review_id = match.get("review_id")

        # 4. Build review payload
        review_payload = {
            "review_id": existing_review_id if existing_review_id else int(time.time() * 1000),
            "student_id": session.get("studentId", ""),
            "session_id": session_id,
            "tutor_id": tutor_id,
            "rating": rating,
            "comment": comment,
            "createdAt": __import__('datetime').datetime.utcnow().isoformat() + "Z",
        }

        # 5. POST (create) or PUT (update) (REVIEW ATOMIC SERVICE)
        if existing_review_id:
            print(f"Existing review found (ID: {existing_review_id}), updating review and tutor rating...")
            print("Review payload for update:", review_payload)
            review_resp = requests.put(
                f"{REVIEW_SERVICE_URL}/review/",
                json=review_payload,
                timeout=10
            )
            action = "updated"

            if review_resp.status_code not in (200, 201):
                return {"message": f"Failed to {action} review", "error": review_resp.text}, 500

        else:
            review_resp = requests.post(
                f"{REVIEW_SERVICE_URL}/review",
                json=review_payload,
                timeout=10
            )
            action = "submitted"

            if review_resp.status_code not in (200, 201):
                return {"message": f"Failed to {action} review", "error": review_resp.text}, 500

        # 6. Fetch updated avg_rating and rating_count from OutSystems (REVIEW ATOMIC SERVICE)
        avg_resp = requests.get(
            f"{REVIEW_SERVICE_URL}/avg_review/{tutor_id}",
            timeout=10
        )
        if avg_resp.status_code != 200:
            return {
                "message": f"Review {action} but failed to fetch updated rating",
                "review": review_resp.json(),
                "ratingError": avg_resp.text
            }, 207

        avg_data = avg_resp.json()
        avg_rating = avg_data.get("avg_rating", 0)
        rating_count = avg_data.get("rating_count", 0)
        print(f"[rate_tutor] avg_rating={avg_rating}, rating_count={rating_count}")

        # 7. Sync averageRating and totalReviews to Tutor table (TUTOR ATOMIC SERVICE)
        tutor_rating_resp = requests.put(
            f"{TUTOR_SERVICE_URL}/tutor/updateRating",
            json={
                "tutorId": tutor_id,
                "averageRating": avg_rating,
                "totalReviews": rating_count
            },
            timeout=5
        )
        if tutor_rating_resp.status_code != 200:
            return {
                "message": f"Review {action} but tutor rating sync failed",
                "review": review_resp.json(),
                "ratingError": tutor_rating_resp.text
            }, 207

        return {
            "message": f"Review {action} and tutor rating updated",
            "review": review_resp.json(),
            "tutorRating": tutor_rating_resp.json()
        }, 200
        
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5102, debug=True)
