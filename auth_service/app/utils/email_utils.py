import smtplib
from email.mime.text import MIMEText
from fastapi.concurrency import run_in_threadpool
from app.core.config import settings

def send_verification_email(email, token):
    print(f"DEBUG: Triggering verification email to {email}")
    verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    subject = "Verify Your Email"

    body = f"""
    Welcome to our service!
    Click the link below to verify your email address:

    {verification_link}

    This link expires in {settings.OTP_EXPIRY_MINUTES} minutes.
    """

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_ADDRESS}>"
    msg["To"] = email

    with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.EMAIL_ADDRESS, settings.EMAIL_PASSWORD)
        server.sendmail(settings.EMAIL_ADDRESS, email, msg.as_string())

def send_email_otp_sync(email, otp):
    subject = "OTP Verification"

    body = f"""
    Your OTP code is: {otp}
    This OTP will expire in {settings.OTP_EXPIRY_MINUTES} minutes.
    """

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_ADDRESS}>"
    msg["To"] = email

    with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.EMAIL_ADDRESS, settings.EMAIL_PASSWORD)
        server.sendmail(settings.EMAIL_ADDRESS, email, msg.as_string())


def send_already_registered_email(email):
    login_link = f"{settings.FRONTEND_URL}/login"
    reset_link = f"{settings.FRONTEND_URL}/forgot-password"

    subject = "Account Already Exists"

    body = f"""
    You tried to register an account with this email address, but an account already exists.
    
    If this was you, you can log in here: {login_link}
    If you forgot your password, you can reset it here: {reset_link}
    """

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_ADDRESS}>"
    msg["To"] = email

    with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.EMAIL_ADDRESS, settings.EMAIL_PASSWORD)
        server.sendmail(settings.EMAIL_ADDRESS, email, msg.as_string())

def send_google_user_help_email(email):
    login_link = f"{settings.FRONTEND_URL}/login"
    reset_link = f"{settings.FRONTEND_URL}/forgot-password"

    subject = "Account Exists (Signed up with Google)"

    body = f"""
    You tried to register with a password, but you previously signed up using your Google account.
    
    To access your account, please use "Continue with Google" on the login page: {login_link}
    
    If you want to set a password so you can login with either Google or email/password, you can use the "Forgot Password" feature to set one: {reset_link}
    """

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_ADDRESS}>"
    msg["To"] = email

    with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.EMAIL_ADDRESS, settings.EMAIL_PASSWORD)
        server.sendmail(settings.EMAIL_ADDRESS, email, msg.as_string())


async def send_verification_email_async(email, token):
    await run_in_threadpool(send_verification_email, email, token)

async def send_email_otp(email, otp):
    await run_in_threadpool(send_email_otp_sync, email, otp)

async def send_already_registered_email_async(email):
    await run_in_threadpool(send_already_registered_email, email)

async def send_google_user_help_email_async(email):
    await run_in_threadpool(send_google_user_help_email, email)
