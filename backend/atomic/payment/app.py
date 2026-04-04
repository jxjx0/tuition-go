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
                customer_email=data.get("student_email"),
                payment_intent_data={
                    "receipt_email": data.get("student_email"), 
                },
                client_reference_id=str(data["session_id"]),
                metadata={
                    "session_id": str(data["session_id"]),
                    "student_id": str(data.get("student_id", "")),
                    "tutor_id": str(data.get("tutor_id", "")),
                },
                success_url="http://localhost:5173/paymentSuccess?stripe_session_id={CHECKOUT_SESSION_ID}",
                cancel_url="http://localhost:5173/paymentFailed?stripe_session_id={CHECKOUT_SESSION_ID}"
            )

        return jsonify({"url": session.url})

@api.route("/verify")
class VerifyPayment(Resource):
    def post(self):
        data = request.get_json()
        stripe_session_id = data.get("stripe_session_id")
        if not stripe_session_id:
            return {"message": "stripe_session_id is required"}, 400

        stripe_session = stripe.checkout.Session.retrieve(stripe_session_id)

        if stripe_session.payment_status != "paid":
            return {"message": "Payment not completed"}, 402

        metadata = stripe_session.metadata
        return {
            "session_id": metadata.get("session_id"),
            "student_id": metadata.get("student_id"),
            "tutor_id":   metadata.get("tutor_id"),
            "amount_total": stripe_session.amount_total,
        }, 200

      
@api.route("/stripe-session/<string:stripe_session_id>")
class GetStripeSession(Resource):
    def get(self, stripe_session_id):
        """Retrieve Stripe session metadata without requiring payment to be completed."""
        try:
            stripe_session = stripe.checkout.Session.retrieve(stripe_session_id)
            metadata = stripe_session.metadata
            return {
                "session_id": metadata.get("session_id"),
                "student_id": metadata.get("student_id"),
                "tutor_id": metadata.get("tutor_id"),
                "amount_total": stripe_session.amount_total,
                "payment_status": stripe_session.payment_status,
            }, 200
        except stripe.error.InvalidRequestError:
            return {"message": "Stripe session not found"}, 404

@api.route("/refund")
class ProcessRefund(Resource):
    def post(self):
        """Process a full refund for a cancelled session via Stripe."""
        data = request.get_json()
        stripe_session_id = data.get("stripe_session_id")
        if not stripe_session_id:
            return {"message": "stripe_session_id is required"}, 400

        try:
            # Retrieve Stripe Checkout Session to get the payment_intent ID
            stripe_session = stripe.checkout.Session.retrieve(stripe_session_id)
            payment_intent_id = stripe_session.payment_intent

            if not payment_intent_id:
                return {"message": "No payment intent found for this Stripe session"}, 400

            # Create a full refund against the payment intent
            refund = stripe.Refund.create(payment_intent=payment_intent_id)

            return {
                "refund_status": refund.status,
                "refund_id": refund.id,
                "amount": refund.amount,
            }, 200

        except stripe.error.InvalidRequestError as e:
            return {"message": f"Invalid Stripe request: {str(e)}"}, 400
        except stripe.error.StripeError as e:
            return {"message": f"Stripe error: {str(e)}"}, 502
        except Exception as e:
            return {"message": f"Failed to process refund: {str(e)}"}, 500


@api.route("/health")
class Health(Resource):
    def get(self):
        return {"status": "healthy", "service": "payment"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5007, debug=True)
