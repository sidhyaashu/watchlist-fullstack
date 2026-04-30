from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Enum, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.session import Base
from app.models.enums import UserStatusEnum, AuthProviderEnum

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(50), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=True)
    dob = Column(Date, nullable=True)
    auth_provider = Column(Enum(AuthProviderEnum), default=AuthProviderEnum.LOCAL, nullable=False)
    status = Column(Enum(UserStatusEnum), default=UserStatusEnum.ACTIVE, nullable=False, index=True)
    is_verified = Column(Boolean, default=False)
    

    failed_attempts = Column(Integer, default=0)
    lock_until = Column(DateTime(timezone=True), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    last_ip = Column(String(50), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    token_version = Column(Integer, default=0)

    # Relationships
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    otps = relationship("OTPCode", back_populates="user", cascade="all, delete-orphan")
    analytics = relationship("UserAnalytics", back_populates="user", cascade="all, delete-orphan")
    daily_activity = relationship("UserDailyActivity", back_populates="user", cascade="all, delete-orphan")

# Indexes
Index("idx_users_email", User.email)
Index("idx_users_phone", User.phone)
Index("idx_users_status", User.status)
