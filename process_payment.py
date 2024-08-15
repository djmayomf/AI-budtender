import os
import stripe

# Set the Stripe API key from an environment variable for security
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

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
        return charge
    except stripe.error.CardError as e:
        return f"Payment failed: {e.user_message}"  # Provide user-friendly error message
    except stripe.error.StripeError as e:
        return f"Payment processing error: {e.user_message}"  # Handle other Stripe errors
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"  # Handle unexpected errors

# Example usage
if __name__ == '__main__':
    # This block is for demonstration purposes and should be part of your application logic
    payment_token = 'tok_visa'  # Example token for testing
    amount = 1000  # Amount in cents
    result = process_apple_pay_payment(payment_token, amount)
    print(result)