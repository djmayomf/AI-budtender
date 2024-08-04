import random
import smtplib
from email.mime.text import MIMEText

def send_verification_code(email):
    verification_code = random.randint(100000, 999999)
    
    # Send email with verification code
    msg = MIMEText(f'Your verification code is {verification_code}')
    msg['Subject'] = 'Your Verification Code'
    msg['From'] = 'your-email@example.com'
    msg['To'] = email

    try:
        with smtplib.SMTP('smtp.example.com') as server:
            server.login('your-email@example.com', 'your-password')
            server.send_message(msg)
        return verification_code
    except Exception as e:
        return f"Failed to send email: {e}"

def verify_code(input_code, actual_code):
    return input_code == actual_code
