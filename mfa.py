import random
import smtplib
from email.mime.text import MIMEText
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def send_verification_code(email):
    verification_code = random.randint(100000, 999999)
    
    # Retrieve environment variables
    email_address = os.getenv('EMAIL_ADDRESS')
    email_password = os.getenv('EMAIL_PASSWORD')
    smtp_server = os.getenv('SMTP_SERVER')

    # Validate environment variables
    if not email_address or not email_password or not smtp_server:
        logging.error("Missing environment variables for email configuration.")
        return "Failed to send email: Configuration error"

    # Send email with verification code
    msg = MIMEText(f'Your verification code is {verification_code}')
    msg['Subject'] = 'Your Verification Code'
    msg['From'] = email_address
    msg['To'] = email

    try:
        with smtplib.SMTP(smtp_server) as server:
            server.login(email_address, email_password)
            server.send_message(msg)
        logging.info(f"Verification code sent to {email}")
        return verification_code
    except smtplib.SMTPAuthenticationError:
        logging.error("Failed to authenticate with the SMTP server.")
        return "Failed to send email: Authentication error"
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
        return f"Failed to send email: {e}"
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return f"Failed to send email: {e}"

def verify_code(input_code, actual_code):
    return input_code == actual_code

# Example usage
if __name__ == "__main__":
    email = "recipient@example.com"
    code = send_verification_code(email)
    print(f"Sent verification code: {code}")
    # Simulate user input for verification
    user_input = int(input("Enter the verification code: "))
    if verify_code(user_input, code):
        print("Verification successful!")
    else:
        print("Verification failed.")