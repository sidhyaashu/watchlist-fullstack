import datetime
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import UserAnalytics, UserDailyActivity, AnalyticsEventTypeEnum

async def log_event(db: AsyncSession, user_id: int, event_type: AnalyticsEventTypeEnum, ip_address: str = None, user_agent: str = None):
    event = UserAnalytics(
        user_id=user_id,
        event_type=event_type,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(event)
    await db.commit()
    return event

async def get_or_create_daily_activity(db: AsyncSession, user_id: int):
    today = datetime.datetime.now(datetime.timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    query = select(UserDailyActivity).where(
        UserDailyActivity.user_id == user_id,
        UserDailyActivity.activity_date == today
    )
    result = await db.execute(query)
    activity = result.scalar_one_or_none()
    
    if not activity:
        activity = UserDailyActivity(
            user_id=user_id,
            activity_date=today
        )
        db.add(activity)
        await db.commit()
        await db.refresh(activity)
    
    return activity

async def increment_login_count(db: AsyncSession, user_id: int):
    activity = await get_or_create_daily_activity(db, user_id)
    activity.login_count += 1
    await db.commit()

async def increment_profile_update_count(db: AsyncSession, user_id: int):
    activity = await get_or_create_daily_activity(db, user_id)
    activity.profile_update_count += 1
    await db.commit()
