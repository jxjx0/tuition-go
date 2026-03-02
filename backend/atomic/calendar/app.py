from flask import Flask
from flask_restx import Api, Resource
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
api = Api(app, doc="/docs",
    title="Calendar Service",
    version="1.0",
    description="Calendar atomic service"
)


@api.route("/health")
class Health(Resource):
    def get(self):
        return {"status": "healthy", "service": "calendar"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)
