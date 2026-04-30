import jwt
import datetime
from app.core.config import settings


def create_access_token(user):
    payload = {
        "sub": str(user.id),
        "user_id": user.id,
        "email": user.email,
        "token_version": user.token_version,
        "type": "access",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(user):
    payload = {
        "sub": str(user.id),
        "user_id": user.id,
        "token_version": user.token_version,   
        "type": "refresh",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_reset_token(user):
    payload = {
        "sub": str(user.id),
        "user_id": user.id,
        "email": user.email,
        "token_version": user.token_version,   
        "type": "password_reset",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError as exc:
        raise ValueError("Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise ValueError("Invalid token") from exc

def create_email_verification_token(user):
    payload = {
        "sub": str(user.id),
        "user_id": user.id,
        "email": user.email,
        "token_version": user.token_version,
        "type": "email_verification",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
