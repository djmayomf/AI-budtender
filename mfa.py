import random
import smtplib
from email.mime.text import MIMEText
from getpass import getpass

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
    
    # Send email with verification code
    msg = MIMEText(f'Your verification code is {verification_code}')
    msg['Subject'] = 'Your Verification Code'
    msg['From'] = sender_email
    msg['To'] = email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return verification_code
    except smtplib.SMTPAuthenticationError:
        return "Authentication failed. Check your email and password."
    except smtplib.SMTPConnectError:
        return "Failed to connect to the SMTP server. Check the server address and port."
    except Exception as e:
        return f"Failed to send email: {e}"

def verify_code(input_code, actual_code):
    """
    Verify if the input code matches the actual verification code.

    Parameters:
    - input_code (str): The code entered by the user.
    - actual_code (int): The actual verification code.

    Returns:
    - bool: True if the codes match, False otherwise.
    """
    try:
        return int(input_code) == actual_code
    except ValueError:
        return False

# Example usage
if __name__ == '__main__':
    recipient_email = 'recipient@example.com'
    smtp_server = 'smtp.example.com'
    smtp_port = 587  # Common port for TLS
    sender_email = 'your-email@example.com'
    sender_password = getpass("Enter your email password: ")  # Securely get the password

    verification_code = send_verification_code(recipient_email, smtp_server, smtp_port, sender_email, sender_password)
    if isinstance(verification_code, int):
        print(f"Verification code sent: {verification_code}")
    else:
        print(verification_code)  # Print the error message