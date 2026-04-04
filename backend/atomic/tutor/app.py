import re
from datetime import datetime, timezone
from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from supabase import create_client, Client
from dotenv import load_dotenv

import os

load_dotenv()

# url=os.getenv("SUPABASE_URL")
# key=os.getenv("SUPABASE_SECRET_KEY")

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")


supabase: Client = create_client(url,key)

app = Flask(__name__)
CORS(app)
api = Api(app, doc="/docs",
    title="Tutor Service",
    version="1.0",
    description="Tutor atomic service",
    #All routes in this API will automatically start with /tutor, http://localhost:5002/tutor
    prefix="/tutor"
)

tutor_subject_model = api.model('TutorSubject', {
    'tutorSubjectId': fields.String(description='Tutor subject UUID', example='d2eebc99-9c0b-4ef8-bb6d-6bb9bd380a44'),
    'subject': fields.String(description='Subject name', example='Mathematics'),
    'academicLevel': fields.String(description='Academic level', example='A-Level'),
    'hourlyRate': fields.Float(description='Hourly rate in SGD', example=80.0),
})

tutor_model = api.model('TutorResponse', {
    'tutorId': fields.String(description='Tutor UUID', example='c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a33'),
    'clerkUserId': fields.String(description='Clerk user ID', example='user_2abc123def456'),
    'name': fields.String(description='Full name', example='Mr John Lim'),
    'email': fields.String(description='Gmail address', example='john@gmail.com'),
    'phone': fields.String(description='Phone number', example='+6598765432'),
    'bio': fields.String(description='Tutor bio', example='10 years experience teaching A-Level Mathematics.'),
    'imageURL': fields.String(description='Profile image URL', example='https://storage.example.com/john.jpg'),
    'averageRating': fields.Float(description='Average rating (0–5)', example=4.8),
    'totalReviews': fields.Integer(description='Total number of reviews', example=23),
    'subjects': fields.List(fields.Nested(tutor_subject_model), description='Subjects taught'),
})

tutor_register_input = api.model('TutorRegisterInput', {
    'name': fields.String(description='Full name (auto-derived from email if omitted)', example='Mr John Lim'),
    'email': fields.String(required=True, description='Gmail address (must be @gmail.com)', example='john@gmail.com'),
    'phone': fields.String(description='Phone number (optional)', example='+6598765432'),
    'password': fields.String(description='Password (optional, will be hashed)', example='secret123'),
    'clerkUserId': fields.String(required=True, description='Clerk user ID', example='user_2abc123def456'),
})

update_rating_input = api.model('UpdateRatingInput', {
    'tutorId': fields.String(required=True, description='Tutor UUID', example='c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a33'),
    'averageRating': fields.Float(required=True, description='New average rating (0–5)', example=4.8),
    'totalReviews': fields.Integer(required=True, description='New total review count', example=23),
})

add_subject_input = api.model('AddSubjectInput', {
    'subject': fields.String(required=True, description='Subject name', example='Mathematics'),
    'academicLevel': fields.String(required=True, description='Academic level', example='A-Level'),
    'hourlyRate': fields.Float(required=True, description='Hourly rate in SGD (must be > 0)', example=80.0),
})

update_subject_input = api.model('UpdateSubjectInput', {
    'subject': fields.String(description='Subject name', example='Physics'),
    'academicLevel': fields.String(description='Academic level', example='O-Level'),
    'hourlyRate': fields.Float(description='Hourly rate in SGD', example=70.0),
})

tutor_error_model = api.model('TutorError', {
    'error': fields.String(description='Error message', example='Tutor not found'),
})


#GET all tutors
@api.route("/all")
class Tutors(Resource):
    @api.marshal_list_with(tutor_model)
    @api.response(200, 'List of all tutors')
    def get(self):
        """Retrieve all tutors ordered by creation date (newest first)."""
        tutors = supabase.table("Tutor") .select("*").order("createdAt", desc=True).execute()

        return tutors.data, 200

#GET tutors by subject and/or academic level and/or sort and/or name
# GET /tutors/search?subject=Math
# GET /tutors/search?academicLevel=Secondary 4
# GET http://127.0.0.1:5002/tutors/search?subject=English&academicLevel=Secondary+4&sort=priceLowHigh
# GET /tutors/search?name=vincent
@api.route("/search")
class SearchTutors(Resource):
    @api.doc(params={
        'subject': 'Filter by subject name (e.g. Mathematics)',
        'academicLevel': 'Filter by academic level (e.g. A-Level)',
        'name': 'Search by tutor name (partial match)',
        'sort': 'Sort order: highestRated | mostReviews',
    })
    @api.marshal_list_with(tutor_model)
    @api.response(200, 'Filtered and sorted list of tutors')
    @api.response(500, 'Internal server error', tutor_error_model)
    def get(self):
        """Search and filter tutors by subject, academic level, name, and/or sort order."""

        subject = request.args.get("subject")
        academic_level = request.args.get("academicLevel")
        name = request.args.get("name")
        sort = request.args.get("sort")

        try:
            query = supabase.table("TutorSubjects").select(
                """
                tutorSubjectId,
                subject,
                academicLevel,
                hourlyRate,
                Tutor!inner (
                    tutorId,
                    name,
                    email,
                    phone,
                    averageRating,
                    totalReviews,
                    bio,
                    imageURL
                )
                """
            )

            # Filters
            if subject:
                query = query.eq("subject", subject)

            if academic_level:
                query = query.eq("academicLevel", academic_level)

            if name:
                query = query.ilike("Tutor.name", f"%{name}%")

            # Sorting

            # if sort == "highestRated":
            #     query = query.order("Tutor.averageRating", desc=True)

            # elif sort == "mostReviews":
            #     query = query.order("totalReviews", desc=True)

            response = query.execute()

            tutors = {}

            for record in response.data:
                tutor = record["Tutor"]
                tutor_id = tutor["tutorId"]

                if tutor_id not in tutors:
                    tutors[tutor_id] = {
                        "tutorId": tutor["tutorId"],
                        "name": tutor["name"],
                        "email": tutor["email"],
                        "phone": tutor["phone"],
                        "bio": tutor["bio"],
                        "imageURL": tutor["imageURL"],
                        "averageRating": tutor["averageRating"],
                        "totalReviews": tutor["totalReviews"],
                        "subjects": []
                    }

                tutors[tutor_id]["subjects"].append({
                    "tutorSubjectId": record["tutorSubjectId"],
                    "subject": record["subject"],
                    "academicLevel": record["academicLevel"],
                    "hourlyRate": record["hourlyRate"]
                })
            
            tutor_list = list(tutors.values())

            # Sorting tutors
            if sort == "highestRated":
                tutor_list = sorted(tutor_list, key=lambda x: x["averageRating"] or 0, reverse=True)

            elif sort == "mostReviews":
                tutor_list = sorted(tutor_list, key=lambda x: x["totalReviews"] or 0, reverse=True)


            return tutor_list, 200

        except Exception as e:
            print(f"Search error: {str(e)}")
            return {"error": str(e)}, 500

#GET subjects taught by tutor with filter subject and/or academic level and/or sort and/or tutor name (includes price sorting)
# @api.route("/tutors/search/subjects")
# class SearchTutors(Resource):
#     def get(self):

#         subject = request.args.get("subject")
#         academic_level = request.args.get("academicLevel")
#         name = request.args.get("name")
#         sort = request.args.get("sort")

#         try:
#             query = supabase.table("TutorSubjects").select(
#                 """
#                 tutorSubjectId,
#                 subject,
#                 academicLevel,
#                 hourlyRate,
#                 Tutor (
#                     tutorId,
#                     name,
#                     email,
#                     phone,
#                     averageRating,
#                     totalReviews,
#                     bio
#                 )
#                 """
#             )

#             # Filters
#             if subject:
#                 query = query.eq("subject", subject)

#             if academic_level:
#                 query = query.eq("academicLevel", academic_level)

#             # Search by tutor name
#             if name:
#                 query = query.ilike("Tutor.name", f"%{name}%")

#             # Sorting
#             if sort == "priceLowHigh":
#                 query = query.order("hourlyRate", desc=False)

#             elif sort == "priceHighLow":
#                 query = query.order("hourlyRate", desc=True)

#             elif sort == "highestRated":
#                 query = query.order("Tutor.averageRating", desc=True)

#             elif sort == "mostReviews":
#                 query = query.order("Tutor.totalReviews", desc=True)

#             response = query.execute()

#             # ✅ Remove rows where Tutor is null
#             filtered_results = [
#                 record for record in response.data if record.get("Tutor") is not None
#             ]

#             return filtered_results, 200

#         except Exception as e:
#             return {"error": str(e)}, 500

#GET, PUT, DELETE for a specific tutor by ID
@api.route("/<string:tutorID>")
class TutorById(Resource):
    @api.doc(params={'tutorID': 'Tutor UUID'})
    @api.marshal_with(tutor_model)
    @api.response(200, 'Tutor found', tutor_model)
    @api.response(404, 'Tutor not found', tutor_error_model)
    @api.response(500, 'Internal server error', tutor_error_model)
    def get(self, tutorID):
        """Retrieve a tutor by ID, including their subjects and hourly rates."""
        try:
            response = (
                supabase.table("Tutor")
                .select("""
                    tutorId,
                    clerkUserId,
                    name,
                    email,
                    phone,
                    bio,
                    imageURL,
                    averageRating,
                    totalReviews,
                    subjects:TutorSubjects(
                        tutorSubjectId,
                        subject,
                        academicLevel,
                        hourlyRate
                    )
                """)
                .eq("tutorId", tutorID)
                .single()
                .execute()
            )

            if not response.data:
                return {"error": "Tutor not found"}, 404

            return response.data, 200

        except Exception as e:
            return {"error": str(e)}, 500

    @api.doc(
        params={'tutorID': 'Tutor UUID'},
        description=(
            'Update tutor profile. Send as **multipart/form-data**. '
            'Fields: `name` (string, optional), `phone` (string, optional), '
            '`bio` (string, optional), `password` (string, optional), '
            '`profileImage` (file, optional — JPEG/PNG).'
        )
    )
    @api.response(200, 'Tutor updated successfully', api.model('TutorUpdateResponse', {
        'message': fields.String(example='Tutor updated successfully'),
        'data': fields.Raw(description='Updated tutor record'),
    }))
    @api.response(400, 'No valid fields to update', tutor_error_model)
    @api.response(500, 'Internal server error', tutor_error_model)
    def put(self, tutorID):
        """Update tutor profile (name, phone, bio, password, profile image). Multipart/form-data."""

        form = request.form
        file = request.files.get("profileImage")

        update_data = {}

        try:
            # Text fields
            name = form.get("name")
            phone = form.get("phone")
            password = form.get("password")
            bio = form.get("bio")

            if name:
                update_data["name"] = name

            if phone:
                update_data["phone"] = phone

            if bio:
                update_data["bio"] = bio

            if password:
                update_data["passwordHash"] = generate_password_hash(password)

            # Image upload
            if file and file.filename != "":
                import uuid

                # Create unique file path
                file_ext = file.filename.split(".")[-1]
                file_path = f"{tutorID}/{uuid.uuid4()}.{file_ext}"

                # Upload to Supabase Storage
                supabase.storage.from_("tuitiongo").upload(
                    file_path,
                    file.read(),
                    {"content-type": file.content_type}
                )

                # Get public URL
                public_url = supabase.storage.from_("tuitiongo").get_public_url(file_path)

                update_data["imageURL"] = public_url

            if not update_data:
                return {"error": "No valid fields to update"}, 400

            # Update timestamp (UTC)
            update_data["updatedAt"] = datetime.now(timezone.utc).isoformat()

            # Update Tutor table
            response = (
                supabase.table("Tutor")
                .update(update_data)
                .eq("tutorId", tutorID)
                .execute()
            )

            return {
                "message": "Tutor updated successfully",
                "data": response.data
            }, 200

        except Exception as e:
            return {"error": str(e)}, 500

    @api.doc(params={'tutorID': 'Tutor UUID'})
    @api.response(200, 'Tutor deleted successfully', api.model('TutorDeleteResponse', {
        'message': fields.String(example='c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a33 deleted successfully'),
    }))
    @api.response(404, 'Tutor not found', tutor_error_model)
    @api.response(500, 'Internal server error', tutor_error_model)
    def delete(self, tutorID):
        """Delete a tutor account by tutorId."""
        try:
            response = (
                supabase.table("Tutor").delete().eq("tutorId", tutorID).execute()
            )

            if not response.data:
                return {"error": tutorID+" not found"}, 404

            return {"message": tutorID+" deleted successfully"}, 200

        except Exception as e:
            return {"error": str(e)}, 500


#POST register/create tutor
@api.route("/register")
class TutorRegister(Resource):
    @api.expect(tutor_register_input)
    @api.response(201, 'Tutor created', tutor_model)
    @api.response(200, 'Tutor already exists (idempotent)', tutor_model)
    @api.response(400, 'Missing required fields or email not Gmail', tutor_error_model)
    @api.response(500, 'Internal server error', tutor_error_model)
    def post(self):
        """Register a new tutor. Email must be @gmail.com. Idempotent — returns existing record if clerkUserId already exists."""
        data = request.get_json()

        if not data:
            return {"error": "No input data provided"}, 400

        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        password = data.get("password")
        clerk_user_id = data.get("clerkUserId")

        # If name is missing, generate it from email
        if not name and email:
            name = email.split("@")[0]

        if not name or not email or not clerk_user_id:
            return {"error": "name, email, and clerkUserId are required"}, 400

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

        # Check if a tutor with this clerkUserId already exists
        existing2 = (
            supabase
            .table("Tutor")
            .select("tutorId")
            .eq("clerkUserId", clerk_user_id)
            .execute()
        )

        # Set in clerk unsafemetadata the tutorId to be inside it
        if existing2.data and len(existing2.data) > 0:
            return existing2.data[0], 200

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


#PUT update reviews portion of tutor (averageRating and totalReviews)
@api.route("/updateRating")
class UpdateTutorRating(Resource):

    @api.expect(update_rating_input)
    @api.response(200, 'Tutor rating updated', api.model('UpdateRatingResponse', {
        'tutorId': fields.String(example='c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a33'),
        'name': fields.String(example='Mr John Lim'),
        'averageRating': fields.Float(example=4.8),
        'totalReviews': fields.Integer(example=23),
    }))
    @api.response(400, 'Missing/invalid fields', tutor_error_model)
    @api.response(404, 'Tutor not found', tutor_error_model)
    @api.response(500, 'Internal server error', tutor_error_model)
    def put(self):
        """Sync averageRating and totalReviews to the Tutor table. Called internally by Rate Tutor service."""
        data = request.get_json()

        if not data:
            return {"error": "No input data provided"}, 400

        tutor_id = data.get("tutorId")
        average_rating = data.get("averageRating")
        total_reviews = data.get("totalReviews")

        if not tutor_id or average_rating is None or total_reviews is None:
            return {
                "error": "tutorId, averageRating and totalReviews are required"
            }, 400

        # Validate rating
        if not isinstance(average_rating, (int, float)) or not (0 <= average_rating <= 5):
            return {"error": "averageRating must be between 0 and 5"}, 400

        # Validate totalReviews
        if not isinstance(total_reviews, int) or total_reviews < 0:
            return {"error": "totalReviews must be a positive integer"}, 400

        try:

            # Check tutor exists
            response_tutor = (
                supabase.table("Tutor")
                .select("name")
                .eq("tutorId", tutor_id)
                .single()
                .execute()
            )

            if not response_tutor.data:
                return {"error": "Tutor not found"}, 404

            tutor_name = response_tutor.data["name"]

            # Update timestamp
            updated_time = datetime.now(timezone.utc).isoformat()

            # Update tutor record
            update_response = (
                supabase.table("Tutor")
                .update({
                    "averageRating": average_rating,
                    "totalReviews": total_reviews,
                    "updatedAt": updated_time
                })
                .eq("tutorId", tutor_id)
                .execute()
            )

            return {
                "tutorId": tutor_id,
                "name": tutor_name,
                "averageRating": average_rating,
                "totalReviews": total_reviews
            }, 200

        except Exception as e:
            return {"error": str(e)}, 500


#GET and POST subjects for a tutor
@api.route("/<string:tutorId>/subjects")
class TutorSubjectsList(Resource):

    @api.doc(params={'tutorId': 'Tutor UUID'})
    @api.expect(add_subject_input)
    @api.response(201, 'Subject added successfully', api.model('AddSubjectResponse', {
        'message': fields.String(example='Subject added successfully'),
        'data': fields.List(fields.Nested(tutor_subject_model)),
    }))
    @api.response(200, 'Hourly rate updated (same subject+level already exists)', api.model('UpdateSubjectRateResponse', {
        'message': fields.String(example='Hourly rate updated successfully.'),
        'data': fields.List(fields.Nested(tutor_subject_model)),
    }))
    @api.response(400, 'Missing fields or hourly rate not positive', tutor_error_model)
    @api.response(409, 'Exact duplicate subject already exists', tutor_error_model)
    @api.response(500, 'Internal server error', tutor_error_model)
    def post(self, tutorId):
        """Add a subject for a tutor. If the same subject+level exists with a different rate, the rate is updated instead."""
        data = request.get_json()

        if not data:
            return {"error": "No input data provided"}, 400

        subject = data.get("subject")
        academic_level = data.get("academicLevel")
        hourly_rate = data.get("hourlyRate")

        if not subject or not academic_level or hourly_rate is None:
            return {"error": "Subject, Academic Level and Hourly Rate are required"}, 400

        if hourly_rate <= 0:
            return {"error": "Hourly Rate must be positive"}, 400

        try:
            #Check if subject + academic level already exists
            existing = (
                supabase.table("TutorSubjects")
                .select("*")
                .eq("tutorId", tutorId)
                .eq("subject", subject)
                .eq("academicLevel", academic_level)
                .execute()
            )

            if existing.data:
                existing_record = existing.data[0]

                #Exact duplicate check
                if existing_record["hourlyRate"] == hourly_rate:
                    return {
                        "error": "This subject with the same academic level and hourly rate already exists for this tutor."
                    }, 409

                #Same subject + level but different hourly rate → update
                update_response = (
                    supabase.table("TutorSubjects")
                    .update({"hourlyRate": hourly_rate})
                    .eq("tutorId", tutorId)
                    .eq("subject", subject)
                    .eq("academicLevel", academic_level)
                    .execute()
                )

                return {
                    "message": "Hourly rate updated successfully.",
                    "data": update_response.data
                }, 200

            #No duplicate → insert new subject
            subject_data = {
                "tutorId": tutorId,
                "subject": subject,
                "academicLevel": academic_level,
                "hourlyRate": hourly_rate
            }

            insert_response = (
                supabase.table("TutorSubjects")
                .insert(subject_data)
                .execute()
            )

            return {
                "message": "Subject added successfully",
                "data": insert_response.data
            }, 201

        except Exception as e:
            return {"error": str(e)}, 500


    @api.doc(params={'tutorId': 'Tutor UUID'})
    @api.marshal_list_with(tutor_subject_model)
    @api.response(200, 'List of subjects for this tutor')
    @api.response(500, 'Internal server error', tutor_error_model)
    def get(self, tutorId):
        """Retrieve all subjects taught by a tutor, ordered by creation date."""
        try:
            response = (supabase.table("TutorSubjects").select("*").eq("tutorId", tutorId).order("createdAt", desc=True).execute())

            return response.data, 200

        except Exception as e:
            return {"error": str(e)}, 500


#PUT and DELETE a specific subject
@api.route("/<string:tutorId>/subjects/<string:subjectId>")
class TutorSubjectById(Resource):

    @api.doc(params={'tutorId': 'Tutor UUID', 'subjectId': 'Tutor subject UUID'})
    @api.expect(update_subject_input)
    @api.response(200, 'Subject updated', tutor_subject_model)
    @api.response(400, 'No valid fields provided', tutor_error_model)
    @api.response(404, 'Subject not found', tutor_error_model)
    @api.response(500, 'Internal server error', tutor_error_model)
    def put(self, tutorId, subjectId):
        """Update a subject's name, academic level, or hourly rate."""
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

        # Update timestamp (UTC)
        update_data["updatedAt"] = datetime.now(timezone.utc).isoformat()

        try:
            response = (supabase.table("TutorSubjects").update(update_data).eq("tutorSubjectId", subjectId).eq("tutorId", tutorId).execute())

            if not response.data:
                return {"error": "Subject not found"}, 404

            return response.data, 200

        except Exception as e:
            return {"error": str(e)}, 500


    @api.doc(params={'tutorId': 'Tutor UUID', 'subjectId': 'Tutor subject UUID'})
    @api.response(200, 'Subject deleted', api.model('DeleteSubjectResponse', {
        'message': fields.String(example='Subject deleted successfully'),
    }))
    @api.response(404, 'Subject not found', tutor_error_model)
    @api.response(500, 'Internal server error', tutor_error_model)
    def delete(self, tutorId, subjectId):
        """Delete a subject that a tutor teaches."""
        try:
            response = (supabase.table("TutorSubjects").delete().eq("tutorSubjectId", subjectId).eq("tutorId", tutorId).execute())

            if not response.data:
                return {"error": "Subject not found"}, 404

            return {"message": "Subject deleted successfully"}, 200

        except Exception as e:
            return {"error": str(e)}, 500


@api.route("/health")
class Health(Resource):
    @api.response(200, 'Service is healthy')
    def get(self):
        """Health check."""
        return {"status": "healthy", "service": "tutor"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
