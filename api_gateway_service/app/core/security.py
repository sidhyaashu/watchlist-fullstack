from jose import jwt, JWTError
from fastapi import HTTPException
from app.core.config import settings


def decode_jwt(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")