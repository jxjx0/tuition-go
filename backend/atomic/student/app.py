from datetime import datetime, timezone
from flask import Flask, request
from flask_restx import Api, Resource
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv
import traceback
import os

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)

app = Flask(__name__)
CORS(app)
api = Api(app, doc="/docs",
    title="Student Service",
    version="1.0",
    description="Student atomic service"
)


# POST register/create student
# Called once after Clerk sign-up to persist the student record in Supabase.
# Frontend should then store the returned studentId in Clerk unsafeMetadata.
@api.route("/student/register")
class StudentRegister(Resource):

    def post(self):
        data = request.get_json()

        if not data:
            return {"error": "No input data provided"}, 400

        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        clerk_user_id = data.get("clerkUserId")

        if not name or not email or not clerk_user_id:
            return {"error": "name, email, and clerkUserId are required"}, 400

        # Check if a student with this clerkUserId already exists
        existing = (
            supabase
            .table("Student")
            .select("studentId")
            .eq("clerkUserId", clerk_user_id)
            .execute()
        )

        if existing.data and len(existing.data) > 0:
            return existing.data[0], 200

        # Check if email already taken by another student
        email_check = (
            supabase
            .table("Student")
            .select("studentId")
            .eq("email", email)
            .execute()
        )

        if email_check.data and len(email_check.data) > 0:
            return {"error": "Email already registered"}, 409

        student_data = {
            "name": name,
            "email": email,
            "clerkUserId": clerk_user_id,
        }

        if phone:
            student_data["phone"] = phone

        try:
            response = supabase.table("Student").insert(student_data).execute()
            return response.data[0], 201

        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}, 500


# GET student by studentId
@api.route("/student/<string:studentId>")
class StudentById(Resource):
    def get(self, studentId):
        try:
            response = (
                supabase
                .table("Student")
                .select("studentId, name, email, phone, imageURL, createdAt, updatedAt")
                .eq("studentId", studentId)
                .single()
                .execute()
            )

            if not response.data:
                return {"error": "Student not found"}, 404

            return response.data, 200

        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}, 500

    # PUT update student profile

    def put(self, studentId):
        data = request.get_json()

        if not data:
            return {"error": "No input data provided"}, 400

        allowed_fields = ["name", "phone", "imageURL"]
        update_data = {k: data[k] for k in allowed_fields if k in data}

        if not update_data:
            return {"error": "No valid fields to update"}, 400

        update_data["updatedAt"] = datetime.now(timezone.utc).isoformat()

        try:
            response = (
                supabase
                .table("Student")
                .update(update_data)
                .eq("studentId", studentId)
                .execute()
            )

            if not response.data:
                return {"error": "Student not found"}, 404

            return {"message": "Student updated successfully", "data": response.data[0]}, 200

        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}, 500

    # DELETE student account

    def delete(self, studentId):
        try:
            response = (
                supabase
                .table("Student")
                .delete()
                .eq("studentId", studentId)
                .execute()
            )

            if not response.data:
                return {"error": "Student not found"}, 404

            return {"message": f"{studentId} deleted successfully"}, 200

        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}, 500


# GET student by Clerk user ID
# Used to look up a student record when only the Clerk session is available.
@api.route("/student/by-clerk/<string:clerkUserId>")
class StudentByClerkId(Resource):

    def get(self, clerkUserId):
        try:
            response = (
                supabase
                .table("Student")
                .select("studentId, name, email, phone, imageURL, createdAt, updatedAt")
                .eq("clerkUserId", clerkUserId)
                .single()
                .execute()
            )

            if not response.data:
                return {"error": "Student not found"}, 404

            return response.data, 200

        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}, 500


@api.route("/health")
class Health(Resource):
    def get(self):
        return {"status": "healthy", "service": "student"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
