import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_otp(email: str, otp_code: str):
    """
    Send OTP code to the user's email.
    - **email**: Email address of the user.
    - **otp_code**: Generated OTP code.
    """
    msg = MIMEText(f"Your OTP code is {otp_code}")
    msg["Subject"] = "Your OTP Code"
    msg["From"] = SMTP_USERNAME
    msg["To"] = email

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()  # Secure the connection
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, email, msg.as_string())
