import random
import smtplib
from email.mime.text import MIMEText

def send_verification_code(email, smtp_server, smtp_port, sender_email, sender_password):
    """
    Send a verification code to the specified email address.

    Parameters:
    - email (str): The recipient's email address.
    - smtp_server (str): The SMTP server address.
    - smtp_port (int): The SMTP server port.
    - sender_email (str): The sender's email address.
    - sender_password (str): The sender's email password.

    Returns:
    - int: The generated verification code.
    - str: An error message if sending fails.
    """
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
    msg['From'] = 'your-email@example.com'
    msg['To'] = email

    try:
        with smtplib.SMTP('smtp.example.com') as server:
            server.login('your-email@example.com', 'your-password')
            server.send_message(msg)
        logging.info(f"Verification code sent to {email}")
        return verification_code
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return f"Failed to send email: {e}"

def verify_code(input_code, actual_code):
    return input_code == actual_code
