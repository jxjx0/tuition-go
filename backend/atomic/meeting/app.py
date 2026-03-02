from flask import Flask
from flask_restx import Api, Resource
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
api = Api(app, doc="/docs",
    title="Meeting Service",
    version="1.0",
    description="Meeting atomic service"
)


@api.route("/health")
class Health(Resource):
    def get(self):
        return {"status": "healthy", "service": "meeting"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)
