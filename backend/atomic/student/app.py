from datetime import datetime, timezone
from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv
import traceback
import os

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")


def get_supabase() -> Client:
    return create_client(url, key)

app = Flask(__name__)
CORS(app)
api = Api(app, doc="/docs",
    title="Student Service",
    version="1.0",
    description="Student atomic service",
    prefix="/student"
)

student_register_input = api.model('StudentRegisterInput', {
    'name': fields.String(required=True, description='Full name of the student', example='Alice Tan'),
    'email': fields.String(required=True, description='Email address', example='alice@example.com'),
    'phone': fields.String(description='Phone number (optional)', example='+6591234567'),
    'clerkUserId': fields.String(required=True, description='Clerk user ID (user_xxx)', example='user_2abc123def456'),
})

student_model = api.model('StudentResponse', {
    'studentId': fields.String(description='Student UUID', example='a1b2c3d4-e5f6-7890-abcd-ef1234567890'),
    'name': fields.String(description='Full name', example='Alice Tan'),
    'email': fields.String(description='Email address', example='alice@example.com'),
    'phone': fields.String(description='Phone number', example='+6591234567'),
    'imageURL': fields.String(description='Profile image URL', example='https://storage.example.com/student.jpg'),
    'createdAt': fields.String(description='Creation timestamp (ISO 8601)', example='2026-01-15T08:00:00.000Z'),
    'updatedAt': fields.String(description='Last update timestamp (ISO 8601)', example='2026-03-20T12:30:00.000Z'),
})

error_model = api.model('StudentError', {
    'error': fields.String(description='Error message', example='Student not found'),
})


# POST register/create student
# Called once after Clerk sign-up to persist the student record in Supabase.
# Frontend should then store the returned studentId in Clerk unsafeMetadata.
@api.route("/register")
class StudentRegister(Resource):

    @api.expect(student_register_input)
    @api.response(201, 'Student created', student_model)
    @api.response(200, 'Student already exists (idempotent)', student_model)
    @api.response(400, 'Missing required fields', error_model)
    @api.response(409, 'Email already registered', error_model)
    @api.response(500, 'Internal server error', error_model)
    def post(self):
        """Register a new student. Idempotent — returns existing record if clerkUserId already exists."""
        data = request.get_json()

        if not data:
            return {"error": "No input data provided"}, 400

        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        clerk_user_id = data.get("clerkUserId")

        if not name or not email or not clerk_user_id:
            return {"error": "name, email, and clerkUserId are required"}, 400

        db = get_supabase()

        # Check if a student with this clerkUserId already exists
        existing = (
            db
            .table("Student")
            .select("studentId")
            .eq("clerkUserId", clerk_user_id)
            .execute()
        )

        if existing.data and len(existing.data) > 0:
            return existing.data[0], 200

        # Check if email already taken by another student
        email_check = (
            db
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
            response = db.table("Student").insert(student_data).execute()
            return response.data[0], 201

        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}, 500


# GET student by studentId
@api.route("/<string:studentId>")
class StudentById(Resource):
    @api.doc(params={'studentId': 'Student UUID'})
    @api.response(200, 'Student found', student_model)
    @api.response(404, 'Student not found', error_model)
    @api.response(500, 'Internal server error', error_model)
    def get(self, studentId):
        """Retrieve a student by their studentId."""
        try:
            response = (
                get_supabase()
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

    @api.doc(
        params={'studentId': 'Student UUID'},
        description=(
            'Update student profile. Send as **multipart/form-data**. '
            'Fields: `name` (string, optional), `phone` (string, optional), '
            '`profileImage` (file, optional — JPEG/PNG).'
        )
    )
    @api.response(200, 'Student updated successfully', api.model('StudentUpdateResponse', {
        'message': fields.String(example='Student updated successfully'),
        'data': fields.Nested(student_model),
    }))
    @api.response(400, 'No valid fields to update', error_model)
    @api.response(404, 'Student not found', error_model)
    @api.response(500, 'Internal server error', error_model)
    def put(self, studentId):
        """Update student profile (name, phone, profile image). Multipart/form-data."""
        import uuid

        form = request.form
        file = request.files.get("profileImage")

        update_data = {}

        try:
            # Text fields
            name = form.get("name")
            phone = form.get("phone")

            if name:
                update_data["name"] = name

            if phone:
                update_data["phone"] = phone

            # Image upload to Supabase Storage
            if file and file.filename != "":
                # Create unique file path with _student suffix to differentiate from tutors
                file_ext = file.filename.split(".")[-1]
                file_path = f"{studentId}_student/{uuid.uuid4()}.{file_ext}"

                db = get_supabase()
                # Upload to Supabase Storage
                db.storage.from_("tuitiongo").upload(
                    file_path,
                    file.read(),
                    {"content-type": file.content_type}
                )

                # Get public URL
                public_url = db.storage.from_("tuitiongo").get_public_url(file_path)

                update_data["imageURL"] = public_url

            if not update_data:
                return {"error": "No valid fields to update"}, 400

            # Update timestamp (UTC)
            update_data["updatedAt"] = datetime.now(timezone.utc).isoformat()

            # Update Student table
            response = (
                get_supabase()
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

    @api.doc(description='Alias for PUT — partial update of student profile (multipart/form-data).')
    @api.response(200, 'Student updated successfully')
    @api.response(400, 'No valid fields to update', error_model)
    @api.response(404, 'Student not found', error_model)
    def patch(self, studentId):
        """Partial update for student profile (same as PUT)."""
        return self.put(studentId)

    @api.doc(params={'studentId': 'Student UUID'})
    @api.response(200, 'Student deleted successfully', api.model('DeleteStudentResponse', {
        'message': fields.String(example='a1b2c3d4-e5f6-7890-abcd-ef1234567890 deleted successfully'),
    }))
    @api.response(404, 'Student not found', error_model)
    @api.response(500, 'Internal server error', error_model)
    def delete(self, studentId):
        """Delete a student account by studentId."""
        try:
            response = (
                get_supabase()
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
@api.route("/by-clerk/<string:clerkUserId>")
class StudentByClerkId(Resource):

    @api.doc(params={'clerkUserId': 'Clerk user ID (e.g. user_2abc123def456)'})
    @api.response(200, 'Student found', student_model)
    @api.response(404, 'Student not found', error_model)
    @api.response(500, 'Internal server error', error_model)
    def get(self, clerkUserId):
        """Retrieve a student by their Clerk user ID. Used when only the Clerk session is available."""
        try:
            response = (
                get_supabase()
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
    @api.response(200, 'Service is healthy')
    def get(self):
        """Health check."""
        return {"status": "healthy", "service": "student"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
