import datetime
import logging
import jwt
import json
from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.base_service import BaseService
from app.services.user_service import UserService
from app.services.analytics_service import AnalyticsService
from app.models import User, UserStatusEnum, AuthProviderEnum
from app.repository.user_repository import (
    get_user_by_email, get_user_by_id, store_refresh_token, 
    get_refresh_token, revoke_refresh_token
)
from app.core.security import verify_password, hash_password
from app.services.token_service import (
    create_access_token, create_refresh_token, create_reset_token, decode_token
)
from app.core.config import settings
from app.core.oauth import oauth

logger = logging.getLogger(__name__)

class AuthService(BaseService):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.user_service = UserService(db)
        self.analytics = AnalyticsService(db)

    async def _invalidate_user_caches(self, user_id: int):
        redis = await self.get_redis_client()
        if redis:
            await redis.delete(f"user_data:{user_id}")
            await redis.delete(f"user_status:{user_id}")
            await redis.delete(f"user_profile:{user_id}")

    async def _decode_and_validate_token(self, token: str, check_blacklist: bool = False):
        if check_blacklist:
            redis = await self.get_redis_client()
            if redis and await redis.get(f"blacklist:{token}"):
                raise HTTPException(status_code=401, detail="Token has been revoked")
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except jwt.ExpiredSignatureError as e:
            logger.debug(f"Token expired: {e}")
            raise HTTPException(status_code=401, detail="Token expired") from e
        except jwt.PyJWTError as exc:
            logger.debug(f"Token decoding failed: {exc}")
            raise HTTPException(status_code=401, detail="Invalid token") from exc

    async def validate_token_and_get_user(self, token: str) -> User:
        payload = await self._decode_and_validate_token(token, check_blacklist=True)

        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = payload.get("user_id")
        token_version = payload.get("token_version")
        
        # Get Redis client
        redis = await self.get_redis_client()
        
        # Performance optimization: Quick validation from cache before DB hit
        if redis:
            cached_data = await redis.get(f"user_data:{user_id}")
            if cached_data:
                user_dict = json.loads(cached_data)
                # Fail early if cache identifies invalid state
                if user_dict.get("token_version") != token_version:
                    raise HTTPException(status_code=401, detail="Invalid credentials")
                if user_dict.get("status") != UserStatusEnum.ACTIVE.value:
                    raise HTTPException(status_code=403, detail="Account is inactive or banned")

        user = await get_user_by_id(self.db, user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Final validation from DB source of truth
        if token_version != user.token_version:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if user.status != UserStatusEnum.ACTIVE:
            raise HTTPException(status_code=403, detail="Account is inactive or banned")
        
        # Update cache to keep it fresh
        if redis:
            user_data = {"id": user.id, "token_version": user.token_version, "status": user.status.value}
            await redis.setex(f"user_data:{user_id}", 30, json.dumps(user_data))

        return user

    async def login_user(self, login_data, request: Request):
        login_data.email = login_data.email.lower()
        user = await get_user_by_email(self.db, login_data.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not user.is_verified:
            raise HTTPException(status_code=403, detail="Email not verified")

        if user.lock_until and user.lock_until > datetime.datetime.now(datetime.timezone.utc):
            await self.analytics.track_failed_login(user.id, request)
            raise HTTPException(status_code=403, detail="Account locked")

        if user.status == UserStatusEnum.INACTIVE:
            raise HTTPException(status_code=403, detail="Account deleted")

        if user.auth_provider not in [AuthProviderEnum.LOCAL, AuthProviderEnum.BOTH]:
            raise HTTPException(status_code=403, detail="Please use 'Continue with Google' to sign in.")

        if not verify_password(login_data.password, user.password_hash):
            user.failed_attempts += 1
            if user.failed_attempts >= settings.ACCOUNT_LOCKOUT_ATTEMPTS:
                user.lock_until = datetime.datetime.now(datetime.timezone.utc) + \
                    datetime.timedelta(minutes=settings.ACCOUNT_LOCKOUT_MINUTES)
                user.failed_attempts = 0
            await self.db.commit()
            await self.analytics.track_failed_login(user.id, request)
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user.failed_attempts = 0
        user.lock_until = None
        user.last_login = datetime.datetime.now(datetime.timezone.utc)
        user.last_ip = getattr(request.client, 'host', '127.0.0.1')
        await self.db.commit()

        # Track Analytics
        await self.analytics.track_login(user.id, request)

        access = create_access_token(user)
        refresh = create_refresh_token(user)
        await store_refresh_token(self.db, user.id, refresh)

        return {"access_token": access, "refresh_token": refresh}

    async def logout_user(self, access_token: str, refresh_token: str, request: Request = None):
        payload = None
        try:
            payload = await self._decode_and_validate_token(access_token)
        except (HTTPException, jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            logger.debug("Logout: Access token invalid or expired, skipping analytics/blacklist")

        if payload and request:
            user_id = payload.get("user_id")
            if user_id:
                try:
                    await self.analytics.track_logout(user_id, request)
                except Exception as e:
                    logger.warning(f"Failed to track logout analytics for user {user_id}: {e}")

        # Revoke refresh token in DB - Always attempt this
        try:
            await revoke_refresh_token(self.db, refresh_token)
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Logout failed. Please try again."
            )

        # Blacklist access token in Redis if payload is available
        if payload:
            redis = await self.get_redis_client()
            if redis:
                try:
                    exp = payload.get("exp")
                    if exp:
                        now = datetime.datetime.now(datetime.timezone.utc).timestamp()
                        ttl = max(0, int(exp - now))
                        if ttl > 0:
                            await redis.setex(f"blacklist:{access_token}", ttl, "1")
                except Exception as e:
                    logger.debug(f"Failed to blacklist token: {e}")

        return {"message": "Logged out successfully"}

    async def refresh_access_token(self, refresh_token: str):
        try:
            payload = await self._decode_and_validate_token(refresh_token)
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=401, detail="Invalid token type")
        except HTTPException as exc:
            logger.debug(f"Failed to decode refresh token: {exc.detail}")
            raise HTTPException(status_code=401, detail="Invalid refresh token") from exc

        user_id = payload.get("user_id")
        user = await get_user_by_id(self.db, user_id)
        if not user or user.status != UserStatusEnum.ACTIVE:
            logger.warning(f"Refresh rejected for user {user_id}: status is {user.status if user else 'NOT FOUND'}")
            raise HTTPException(status_code=403, detail="Account is inactive or banned")

        if payload.get("token_version") != user.token_version:
            raise HTTPException(status_code=401, detail="Token expired")

        db_token = await get_refresh_token(self.db, refresh_token)
        if not db_token or db_token.is_revoked or db_token.expires_at < datetime.datetime.now(datetime.timezone.utc):
            raise HTTPException(status_code=401, detail="Token invalid")

        await revoke_refresh_token(self.db, refresh_token)

        new_access = create_access_token(user)
        new_refresh = create_refresh_token(user)
        await store_refresh_token(self.db, user.id, new_refresh)

        return {"access_token": new_access, "refresh_token": new_refresh}

    # Helper for password reset
    async def reset_password_user(self, reset_data):
        try:
            token_payload = decode_token(reset_data.reset_token)
        except ValueError as e:
            raise HTTPException(status_code=401, detail=str(e)) from e

        if token_payload.get("type") != "password_reset":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user = await get_user_by_id(self.db, token_payload["user_id"])
        if not user or user.status != UserStatusEnum.ACTIVE:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user.password_hash = hash_password(reset_data.new_password)
        if user.auth_provider == AuthProviderEnum.GOOGLE:
            user.auth_provider = AuthProviderEnum.BOTH
        user.token_version += 1
        await self.db.commit()
        
        # Invalidate Cache
        redis = await self.get_redis_client()
        if redis:
            await redis.delete(f"user_data:{user.id}")
            await redis.delete(f"user_status:{user.id}")
            await redis.delete(f"user_profile:{user.id}")

        return {"message": "Password reset successful"}

    async def logout_all_user(self, user: User):
        user.token_version += 1
        await self.db.commit()
        # Invalidate cache
        redis = await self.get_redis_client()
        if redis:
            await redis.delete(f"user_data:{user.id}")
            await redis.delete(f"user_status:{user.id}")
            await redis.delete(f"user_profile:{user.id}")
        return {"message": "Logged out from all devices"}

    async def google_login_user(self, request: Request):
        redirect_uri = request.url_for("google_callback")
        logger.info(f"Initiating Google OAuth login. Generated redirect_uri: {redirect_uri}")
        return await oauth.google.authorize_redirect(request, str(redirect_uri))

    async def google_callback_user(self, request: Request):
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo")
        if not user_info or "email" not in user_info:
            raise HTTPException(status_code=400, detail="Failed to fetch user info")

        email = user_info["email"].lower()
        user = await get_user_by_email(self.db, email)
        if user:
            if user.auth_provider not in [AuthProviderEnum.GOOGLE, AuthProviderEnum.BOTH]:
                raise HTTPException(status_code=400, detail="Mismatched provider")
            if user.status != UserStatusEnum.ACTIVE:
                raise HTTPException(status_code=403, detail="Account is inactive or banned")
            user.last_login = datetime.datetime.now(datetime.timezone.utc)
            user.last_ip = getattr(request.client, 'host', '127.0.0.1')
        else:
            user = User(
                email=email,
                name=user_info.get("name") or "Unknown",
                is_verified=True,
                auth_provider=AuthProviderEnum.GOOGLE,
                last_login=datetime.datetime.now(datetime.timezone.utc),
                last_ip=getattr(request.client, 'host', '127.0.0.1')
            )
            self.db.add(user)
        
        await self.db.commit()
        await self.db.refresh(user)

        # Track analytics
        await self.analytics.track_login(user.id, request)

        access = create_access_token(user)
        refresh = create_refresh_token(user)
        await store_refresh_token(self.db, user.id, refresh)

        return {"access_token": access, "refresh_token": refresh}
