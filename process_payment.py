import stripe
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Set Stripe API key from environment variable
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def process_apple_pay_payment(payment_token):
    try:
        charge = stripe.Charge.create(
            amount=1000,  # amount in cents
            currency='usd',
            description='Example charge',
            source=payment_token,
        )
        logging.info(f"Payment successful: {charge}")
        return charge
    except stripe.error.CardError as e:
        logging.error(f"Card error: {e}")
        return f"Payment failed: {e}"
    except stripe.error.RateLimitError as e:
        logging.error(f"Rate limit error: {e}")
        return f"Payment failed: {e}"
    except stripe.error.InvalidRequestError as e:
        logging.error(f"Invalid request error: {e}")
        return f"Payment failed: {e}"
    except stripe.error.AuthenticationError as e:
        logging.error(f"Authentication error: {e}")
        return f"Payment failed: {e}"
    except stripe.error.APIConnectionError as e:
        logging.error(f"API connection error: {e}")
        return f"Payment failed: {e}"
    except stripe.error.StripeError as e:
        logging.error(f"Stripe error: {e}")
        return f"Payment failed: {e}"
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return f"Payment failed: {e}"

# Example usage
if __name__ == "__main__":
    payment_token = "tok_visa"  # Example token, replace with actual token
    result = process_apple_pay_payment(payment_token)
    print(result)