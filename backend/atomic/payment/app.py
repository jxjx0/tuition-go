from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from flask_cors import CORS
import stripe
import os

app = Flask(__name__)
CORS(app)

api = Api(app, doc="/docs",
    title="Payment Service",
    version="1.0",
    description="Payment atomic service",
    prefix="/payment"
)

stripe_keys = {
    "secret_key": os.environ["STRIPE_SECRET_KEY"],
    "publishable_key": os.environ["STRIPE_PUBLISHABLE_KEY"],
}

stripe.api_key = stripe_keys["secret_key"]

@api.route("/config")
class GetConfig(Resource):
    def get(self):
        return jsonify({
            "publishable_key": os.environ["STRIPE_PUBLISHABLE_KEY"],
        })

# @api.route("/create-payment-intent")
# class CreateCheckoutSession(Resource):
#     def post(self):
#         data = request.get_json()
#         intent = stripe.PaymentIntent.create(
#             amount=data["amount"],
#             currency="sgd",
#             metadata={"booking_id": data["booking_id"]}
#         )
#         return jsonify({"client_secret": intent.client_secret})

@api.route("/create-checkout-session")
class CreateCheckoutSession(Resource):
    def post(self):
        data = request.get_json()
        session = stripe.checkout.Session.create(
            mode="payment",
             line_items=[{
            "price_data": {
                "currency": "sgd",
                "product_data": {
                    "name": data["title"],
                    "description": data["description"],
                },
                "unit_amount": int(data["amount"])
            },
                "quantity": 1,
                  "metadata": { 
                    "tutor_name": data["tutor_name"],
                    "subject": data["subject"],
                    "lesson_date": data["lesson_date"]
            }
            }],
                client_reference_id=str(data["booking_id"]),
                metadata={"booking_id": str(data["booking_id"])},
                success_url="http://localhost:5173/paymentSuccess",
                cancel_url="http://localhost:5173/paymentFailed"
            )

        return jsonify({"url": session.url})

@api.route("/health")
class Health(Resource):
    def get(self):
        return {"status": "healthy", "service": "payment"}, 200
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5007, debug=True)
