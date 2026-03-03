import re

from flask import Flask, jsonify, request
from flask_restx import Api, Resource
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

url=os.getenv("SUPABASE_URL")
key=os.getenv("SUPABASE_SECRET_KEY")

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

#POST register tutor
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

        # ✅ Check if email already exists
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

#create new subject that the tutor teaches

#update subject that the tutor teaches

#delete subject that the tutor taught


@api.route("/health")
class Health(Resource):
    def get(self):
        return {"status": "healthy", "service": "tutor"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
