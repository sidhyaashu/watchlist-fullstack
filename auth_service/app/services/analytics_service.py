import logging
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.base_service import BaseService
from app.repository.analytics_repository import log_event, increment_login_count, increment_profile_update_count
from app.models import AnalyticsEventTypeEnum

logger = logging.getLogger(__name__)

class AnalyticsService(BaseService):
    async def track_login(self, user_id: int, request: Request):
        await log_event(
            self.db, 
            user_id, 
            AnalyticsEventTypeEnum.LOGIN, 
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        await increment_login_count(self.db, user_id)

    async def track_logout(self, user_id: int, request: Request):
        await log_event(
            self.db, 
            user_id, 
            AnalyticsEventTypeEnum.LOGOUT, 
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )

    async def track_failed_login(self, user_id: int, request: Request):
        await log_event(
            self.db, 
            user_id, 
            AnalyticsEventTypeEnum.FAILED_LOGIN, 
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )

    async def track_registration(self, user_id: int, request: Request):
        await log_event(
            self.db, 
            user_id, 
            AnalyticsEventTypeEnum.REGISTER, 
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )

    async def track_profile_update(self, user_id: int, request: Request):
        await log_event(
            self.db, 
            user_id, 
            AnalyticsEventTypeEnum.PROFILE_UPDATE, 
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        await increment_profile_update_count(self.db, user_id)

    async def track_password_change(self, user_id: int, request: Request):
        await log_event(
            self.db, 
            user_id, 
            AnalyticsEventTypeEnum.PASSWORD_CHANGE, 
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )

    async def track_account_delete(self, user_id: int, request: Request):
        await log_event(
            self.db, 
            user_id, 
            AnalyticsEventTypeEnum.ACCOUNT_DELETE, 
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
