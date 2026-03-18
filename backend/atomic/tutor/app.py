import re
from datetime import datetime, timezone
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

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")


supabase: Client = create_client(url,key)

app = Flask(__name__)
CORS(app)
api = Api(app, doc="/docs",
    title="Tutor Service",
    version="1.0",
    description="Tutor atomic service"
)


#GET all tutors
@api.route("/tutors")
class Tutors(Resource):
    def get(self):
        tutors = supabase.table("Tutor") .select("*").order("createdAt", desc=True).execute()

        return tutors.data, 200

#GET tutors by subject and/or academic level and/or sort and/or name
# GET /tutors/search?subject=Math
# GET /tutors/search?academicLevel=Secondary 4
# GET http://127.0.0.1:5002/tutors/search?subject=English&academicLevel=Secondary+4&sort=priceLowHigh
# GET /tutors/search?name=vincent
@api.route("/tutors/search")
class SearchTutors(Resource):
    def get(self):

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

#GET particular tutor with id
@api.route("/tutor/<string:tutorID>")
class GetTutorById(Resource):
    def get(self, tutorID):
        try:
            response = (
                supabase.table("Tutor")
                .select("""
                    tutorId,
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
        
        # Check if a student with this clerkUserId already exists
        existing2 = (
            supabase
            .table("Tutor")
            .select("tutorId")
            .eq("clerkUserId", clerk_user_id)
            .execute()
        )
        
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


#PUT update tutor info
#Accept file from frontend (multipart/form-data)
@api.route("/tutor/<string:tutorID>")
class UpdateTutor(Resource):

    def put(self, tutorID):

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

            # Update timestamp (UTC)
            updated_time = datetime.now(timezone.utc).isoformat()

            # Update tutor record
            update_response = (supabase.table("Tutor").update({"averageRating": new_average,"totalReviews": new_total, "updatedAt":updated_time}).eq("tutorId", tutor_id).execute())

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

        # Update timestamp (UTC)
        update_data["updatedAt"] = datetime.now(timezone.utc).isoformat()

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
