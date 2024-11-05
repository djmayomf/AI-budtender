import os
import stripe
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

stripe.api_key = 'YOUR_STRIPE_SECRET_KEY'

def process_apple_pay_payment(payment_token, amount, currency='usd', description='Example charge'):
    """
    Process an Apple Pay payment using Stripe.

    Parameters:
    - payment_token (str): The payment token received from Apple Pay.
    - amount (int): The amount to charge in cents.
    - currency (str): The currency for the charge (default is 'usd').
    - description (str): A description for the charge (default is 'Example charge').

    Returns:
    - dict: The charge object if successful.
    - str: An error message if the payment fails.
    """
    try:
        charge = stripe.Charge.create(
            amount=amount,  # amount in cents
            currency=currency,
            description=description,
            source=payment_token,
        )
        logging.info(f"Payment successful: {charge}")
        return charge
    except stripe.error.CardError as e:
        return f"Payment failed: {e}"
