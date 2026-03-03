import re

from flask import Flask, jsonify, request
from flask_restx import Api, Resource
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

# url=os.getenv("SUPABASE_URL")
# key=os.getenv("SUPABASE_SECRET_KEY")

url="https://mbywmrfzaurxucjnjnjb.supabase.co"
key="sb_secret_BASQ0MdW1FzdOqKWLbzvDQ_F2e81yxf"

supabase: Client = create_client(url,key)

app = Flask(__name__)
CORS(app)
api = Api(app, doc="/docs",
    title="Tutor Service",
    version="1.0",
    description="Tutor atomic service"
)
#testing purposes
#GET all tutors
@api.route("/tutors")
class Tutors(Resource):
    def get(self):
        tutors = supabase.table("Tutor") .select("*").order("createdAt", desc=True).execute()

        return tutors.data, 200
    
#GET particular tutor with id
@api.route("/tutor/<string:tutorID>")
class GetTutorById(Resource):
    def get(self, tutorID):
        try:
            #ensures only 1 record
            response = (
                supabase.table("Tutor").select("*").eq("tutorId", tutorID).single().execute()
            )

            if not response.data:
                return {"error": "Tutor not found"}, 404

            return response.data, 200

        except Exception as e:
            return {"error": str(e)}, 500

#POST register/create tutor
@api.route("/tutor/register")
class TutorRegister(Resource):
    def post(self):
        data = request.get_json()

        if not data:
            return {"error": "No input data provided"}, 400

        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        password = data.get("password")
        clerk_user_id = data.get("clerkUserId")

        if not name or not email:
            return {"error": "Name and email are required"}, 400
        
        #ensure the email is gmail
        email_regex = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'

        if not re.match(email_regex, email):
            return {"error": "Email must be a valid Gmail address"}, 400

        #Check if email already exists
        existing = (
            supabase
            .table("Tutor")
            .select("tutorId")
            .eq("email", email)
            .execute()
        )

        if existing.data and len(existing.data) > 0:
            return {"error": "Email already exists"}, 400

        #Hash password if provided
        password_hash = None
        if password:
            password_hash = generate_password_hash(password)

        #Format data exactly matching DB column names
        tutor_data = {
            "name": name,
            "email": email,
            "phone": phone,
            "passwordHash": password_hash,
            "clerkUserId": clerk_user_id
        }

        # Remove None values (optional clean-up)
        tutor_data = {k: v for k, v in tutor_data.items() if v is not None}

        try:
            response = supabase.table("Tutor").insert(tutor_data).execute()
            return response.data, 201

        except Exception as e:
            return {"error": str(e)}, 500

#PUT update tutor info
@api.route("/tutor/<string:tutorID>")
class UpdateTutor(Resource):
    def put(self, tutorID):
        data = request.get_json()

        if not data:
            return {"error": "No input data provided"}, 400

        # Only allow specific fields to be updated by the user
        allowed_fields = ["name", "phone", "password"]

        update_data = {}

        for field in allowed_fields:
            if field in data:
                if field == "password":
                    update_data["passwordHash"] = generate_password_hash(data["password"])
                else:
                    update_data[field] = data[field]

        if not update_data:
            return {"error": "No valid fields to update"}, 400

        try:
            response = (
                supabase.table("Tutor").update(update_data).eq("tutorId", tutorID).execute()
            )

            if not response.data:
                return {"error": "Tutor not found"}, 404

            return response.data, 200

        except Exception as e:
            return {"error": str(e)}, 500

#DELETE delete tutor user
@api.route("/tutor/<string:tutorID>")
class DeleteTutor(Resource):
    def delete(self, tutorID):
        try:
            response = (
                supabase.table("Tutor").delete().eq("tutorId", tutorID).execute()
            )

            if not response.data:
                return {"error": tutorID+" not found"}, 404

            return {"message": tutorID+" deleted successfully"}, 200

        except Exception as e:
            return {"error": str(e)}, 500
        
#PUT update reviews portion of tutor
# get the new review from the student & calculate what is the new no. of review and average rating 
@api.route("/tutor/updateRating")
class UpdateTutorRating(Resource):

    def put(self):
        data = request.get_json()

        if not data:
            return {"error": "No input data provided"}, 400

        tutor_id = data.get("tutorId")
        new_rating = data.get("newRating")

        if not tutor_id or new_rating is None:
            return {"error": "tutorId and rating are required"}, 400

        # Ensure rating is valid (1 to 5 for example)
        if not isinstance(new_rating, (int, float)) or not (1 <= new_rating <= 5):
            return {"error": "Rating must be a number between 1 and 5"}, 400

        try:
            # Get current tutor data
            response_tutor = (supabase.table("Tutor").select("name, averageRating, totalReviews").eq("tutorId", tutor_id).single().execute())

            if not response_tutor.data:
                return {"error": "Tutor not found"}, 404

            current_avg = response_tutor.data["averageRating"]
            current_total = response_tutor.data["totalReviews"]
            tutor_name=response_tutor.data["name"]

            #Compute new values
            new_total = current_total + 1

            new_average = ((current_avg * current_total) + new_rating) / new_total

            # Optional: round to 1 decimal place
            new_average = round(new_average, 1)

            # Update tutor record
            update_response = (supabase.table("Tutor").update({"averageRating": new_average,"totalReviews": new_total}).eq("tutorId", tutor_id).execute())

            return {
                "tutorId": tutor_id,
                "name":tutor_name,
                "newAverageRating": new_average,
                "totalReviews": new_total
            }, 200

        except Exception as e:
            return {"error": str(e)}, 500

#POST create new subject that the tutor teaches
@api.route("/tutor/<string:tutorId>/subjects")
class TutorAddSubject(Resource):

    def post(self, tutorId):
        data = request.get_json()

        if not data:
            return {"error": "No input data provided"}, 400

        subject = data.get("subject")
        academic_level = data.get("academicLevel")
        hourly_rate = data.get("hourlyRate")

        if not subject or not academic_level or hourly_rate is None:
            return {"error": "subject, academicLevel and hourlyRate are required"}, 400

        if hourly_rate <= 0:
            return {"error": "hourlyRate must be positive"}, 400

        subject_data = {
            "tutorId": tutorId,
            "subject": subject,
            "academicLevel": academic_level,
            "hourlyRate": hourly_rate
        }

        try:
            response = supabase.table("TutorSubjects").insert(subject_data).execute()
            return response.data, 201

        except Exception as e:
            return {"error": str(e)}, 500

#GET get subjects tutor is teaching
@api.route("/tutor/<string:tutorId>/subjects")
class TutorSubjects(Resource):
    def get(self, tutorId):
        try:
            response = (supabase.table("TutorSubjects").select("*").eq("tutorId", tutorId).order("createdAt", desc=True).execute())

            return response.data, 200

        except Exception as e:
            return {"error": str(e)}, 500

#PUT update subject that the tutor teaches
@api.route("/tutor/<string:tutorId>/subjects/<string:subjectId>")
class UpdateTutorSubject(Resource):

    def put(self, tutorId, subjectId):
        data = request.get_json()

        if not data:
            return {"error": "No input data provided"}, 400

        allowed_fields = ["subject", "academicLevel", "hourlyRate"]
        update_data = {}

        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]

        if not update_data:
            return {"error": "No valid fields to update"}, 400

        try:
            response = (supabase.table("TutorSubjects").update(update_data).eq("tutorSubjectId", subjectId).eq("tutorId", tutorId).execute())

            if not response.data:
                return {"error": "Subject not found"}, 404

            return response.data, 200

        except Exception as e:
            return {"error": str(e)}, 500

#DELETE delete subject that the tutor taught
@api.route("/tutor/<string:tutorId>/subjects/<string:subjectId>")
class DeleteTutorSubject(Resource):
    def delete(self, tutorId, subjectId):
        try:
            response = (supabase.table("TutorSubjects").delete().eq("tutorSubjectId", subjectId).eq("tutorId", tutorId).execute())

            if not response.data:
                return {"error": "Subject not found"}, 404

            return {"message": "Subject deleted successfully"}, 200

        except Exception as e:
            return {"error": str(e)}, 500


@api.route("/health")
class Health(Resource):
    def get(self):
        return {"status": "healthy", "service": "tutor"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
