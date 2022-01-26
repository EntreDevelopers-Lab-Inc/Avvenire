from website import app
from flask import jsonify, render_template, request
import stripe


# set some constants
STRIPE_PUBLISHABLE_KEY = ''
STRIPE_SECRET_KEY = ''
STRIPE_ENDPOINT_SECRET = ''
SITE_URL = ''

# setup stripe
stripe.api_key = STRIPE_SECRET_KEY


@app.route('/home')
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/config')
def get_publishable_key():
    stripe_config = {'publicKey': STRIPE_PUBLISHABLE_KEY}
    return jsonify(stripe_config)


# make success and cancelled page
@app.route('/success')
def success():
    # this will have some query sting as a session_id --> link this to the payment or use it to trigger another event
    return render_template('success.html')


@app.route('/cancelled')
def cancelled():
    return render_template('cancelled.html')


# use a separate checkout session to verify the key
@app.route('/create-checkout-session')
def create_checkout_session():
    # set the stripe key
    stripe.api_key = STRIPE_SECRET_KEY

    try:
        # Create new Checkout Session for the order
        # Other optional params include:
        # [billing_address_collection] - to display billing address details on the page
        # [customer] - if you have an existing Stripe Customer ID
        # [payment_intent_data] - lets capture the payment later
        # [customer_email] - lets you prefill the email input in the form
        # For full details see https:#stripe.com/docs/api/checkout/sessions/create
        # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
        checkout_session = stripe.checkout.Session.create(
            success_url=f"{SITE_URL}success?session_id=" +
            '{CHECKOUT_SESSION_ID}',
            cancel_url=f"{SITE_URL}cancelled",
            payment_method_types=['card'],
            mode='payment',
            line_items=[
                {
                    'name': 'T-shirt',
                    'quantity': 1,
                    'currency': 'usd',
                    'amount': 2000
                }
            ]
        )
        data = jsonify({'sessionId': checkout_session['id']})
        code = 201
    except Exception as e:
        data = jsonify(error=str(e))
        code = 403

    return data, code


# make a stripe webhook
@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    with open('payload.txt', 'w') as outfile:
        outfile.write(payload)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_ENDPOINT_SECRET
        )
    except ValueError:
        # invalid payload
        print('invalid payload')
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        # invalid signature
        print('invalid signature')
        return 'Invalid Signature', 400

    # handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print('Payment was successful')
        # use some code to link the session ID to an item --> verify --> authorize

    return 'success', 200


if __name__ == '__main__':
    app.run(debug=True)
