import stripe

stripe.api_key = 'YOUR_STRIPE_SECRET_KEY'

def process_apple_pay_payment(payment_token):
    try:
        charge = stripe.Charge.create(
            amount=1000,  # amount in cents
            currency='usd',
            description='Example charge',
            source=payment_token,
        )
        return charge
    except stripe.error.CardError as e:
        return f"Payment failed: {e}"
