from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
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

checkout_input_model = api.model('CreateCheckoutInput', {
    'title': fields.String(required=True, description='Product title shown on Stripe checkout page', example='Mathematics (A-Level)'),
    'description': fields.String(required=True, description='Short description of the session', example='60 min session'),
    'amount': fields.Integer(required=True, description='Amount in cents (SGD)', example=8000),
    'tutor_name': fields.String(required=True, description='Tutor full name', example='Mr John Lim'),
    'subject': fields.String(required=True, description='Subject name', example='Mathematics'),
    'lesson_date': fields.String(required=True, description='Lesson start time (ISO 8601)', example='2027-06-15T10:00:00.000Z'),
    'session_id': fields.String(required=True, description='Session UUID', example='a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'),
    'student_id': fields.String(required=True, description='Student UUID', example='b5eebc99-9c0b-4ef8-bb6d-6bb9bd380a22'),
    'tutor_id': fields.String(required=True, description='Tutor UUID', example='c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a33'),
    'student_email': fields.String(description='Student email for Stripe receipt', example='student@example.com'),
})

checkout_response_model = api.model('CreateCheckoutResponse', {
    'url': fields.String(description='Stripe checkout URL to redirect the student to', example='https://checkout.stripe.com/pay/cs_test_abc123'),
})

verify_input_model = api.model('VerifyPaymentInput', {
    'stripe_session_id': fields.String(required=True, description='Stripe checkout session ID', example='cs_test_abc123xyz'),
})

verify_response_model = api.model('VerifyPaymentResponse', {
    'session_id': fields.String(description='Internal session UUID from Stripe metadata', example='a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'),
    'student_id': fields.String(description='Student UUID from Stripe metadata', example='b5eebc99-9c0b-4ef8-bb6d-6bb9bd380a22'),
    'tutor_id': fields.String(description='Tutor UUID from Stripe metadata', example='c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a33'),
    'amount_total': fields.Integer(description='Total amount charged in cents', example=8000),
})

refund_input_model = api.model('RefundInput', {
    'stripe_session_id': fields.String(required=True, description='Stripe checkout session ID to refund', example='cs_test_abc123xyz'),
})

refund_response_model = api.model('RefundResponse', {
    'refund_status': fields.String(description='Stripe refund status', example='succeeded'),
    'refund_id': fields.String(description='Stripe refund ID', example='re_1AbCdEfGhIjKlMnOpQrStUv'),
    'amount': fields.Integer(description='Refunded amount in cents', example=8000),
})

stripe_session_response_model = api.model('StripeSessionResponse', {
    'session_id': fields.String(description='Internal session UUID', example='a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'),
    'student_id': fields.String(description='Student UUID', example='b5eebc99-9c0b-4ef8-bb6d-6bb9bd380a22'),
    'tutor_id': fields.String(description='Tutor UUID', example='c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a33'),
    'amount_total': fields.Integer(description='Total amount in cents', example=8000),
    'payment_status': fields.String(description='Stripe payment status', example='paid'),
})

error_model = api.model('PaymentError', {
    'message': fields.String(description='Error message', example='stripe_session_id is required'),
})


@api.route("/config")
class GetConfig(Resource):
    @api.response(200, 'Stripe publishable key', api.model('StripeConfigResponse', {
        'publishable_key': fields.String(description='Stripe publishable key for frontend', example='pk_test_abc123'),
    }))
    def get(self):
        """Return the Stripe publishable key for the frontend."""
        return jsonify({
            "publishable_key": os.environ["STRIPE_PUBLISHABLE_KEY"],
        })

@api.route("/create-checkout-session")
class CreateCheckoutSession(Resource):
    @api.expect(checkout_input_model)
    @api.response(200, 'Stripe checkout session created', checkout_response_model)
    @api.response(500, 'Failed to create checkout session', error_model)
    def post(self):
        """Create a Stripe Checkout session. Returns a redirect URL for the student to complete payment."""
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
    @api.expect(verify_input_model)
    @api.response(200, 'Payment verified', verify_response_model)
    @api.response(400, 'stripe_session_id is required', error_model)
    @api.response(402, 'Payment not completed', error_model)
    def post(self):
        """Verify that a Stripe payment was completed. Returns booking metadata from Stripe session."""
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
    @api.doc(params={'stripe_session_id': 'Stripe checkout session ID (cs_test_... or cs_live_...)'})
    @api.response(200, 'Stripe session retrieved', stripe_session_response_model)
    @api.response(404, 'Stripe session not found', error_model)
    def get(self, stripe_session_id):
        """Retrieve Stripe session metadata without requiring payment to be completed. Used for payment success/failed pages."""
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
    @api.expect(refund_input_model)
    @api.response(200, 'Refund processed', refund_response_model)
    @api.response(400, 'Missing stripe_session_id or no payment intent found', error_model)
    @api.response(502, 'Stripe error during refund', error_model)
    @api.response(500, 'Internal server error', error_model)
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
    @api.response(200, 'Service is healthy')
    def get(self):
        """Health check."""
        return {"status": "healthy", "service": "payment"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5007, debug=True)
