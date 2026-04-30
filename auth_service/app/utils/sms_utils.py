import os
from fastapi.concurrency import run_in_threadpool
from twilio.rest import Client

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")



client = Client(ACCOUNT_SID, AUTH_TOKEN)
def send_sms_otp_sync(phone, otp):

    message = client.messages.create(
        body=f"Your login OTP is: {otp}",
        from_=TWILIO_PHONE,
        to=phone
    )

    return message.sid


async def send_sms_otp(phone, otp):
    return await run_in_threadpool(send_sms_otp_sync, phone, otp)
