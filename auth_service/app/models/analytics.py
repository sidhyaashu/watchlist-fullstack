from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.session import Base
from app.models.enums import AnalyticsEventTypeEnum

class UserAnalytics(Base):
    __tablename__ = "user_analytics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_type = Column(Enum(AnalyticsEventTypeEnum), nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="analytics")


class UserDailyActivity(Base):
    __tablename__ = "user_daily_activity"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_date = Column(DateTime(timezone=True), nullable=False)
    login_count = Column(Integer, default=0)
    profile_update_count = Column(Integer, default=0)
    last_activity_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="daily_activity")

Index("idx_analytics_user_id", UserAnalytics.user_id)
Index("idx_daily_activity_date", UserDailyActivity.activity_date)
