from flask import Flask
from flask_restx import Api, Resource
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
api = Api(app, doc="/docs",
    title="Book Session Service",
    version="1.0",
    description="Book Session composite service",
    prefix="/book-session"
)

# Service URLs
SESSION_SERVICE_URL = "http://session:5003"
TUTOR_SERVICE_URL = "http://tutor:5002"
STUDENT_SERVICE_URL = "http://student:5001"
CALENDAR_SERVICE_URL = "http://calendar:5005"
EMAIL_SERVICE_URL = "http://email:5006"

@api.route("/health")
class Health(Resource):
    def get(self):
        return {"status": "healthy", "service": "book_session"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5100, debug=True)
