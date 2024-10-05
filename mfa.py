import random
import smtplib
from email.mime.text import MIMEText
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def send_verification_code(email):
    verification_code = random.randint(100000, 999999)
    
    # Send email with verification code
    msg = MIMEText(f'Your verification code is {verification_code}')
    msg['Subject'] = 'Your Verification Code'
    msg['From'] = os.getenv('EMAIL_ADDRESS')
    msg['To'] = email

    try:
        with smtplib.SMTP(os.getenv('SMTP_SERVER')) as server:
            server.login(os.getenv('EMAIL_ADDRESS'), os.getenv('EMAIL_PASSWORD'))
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