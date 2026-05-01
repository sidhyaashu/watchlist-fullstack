import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Index, text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Watchlist(Base):
    __tablename__ = "watchlists"

    __table_args__ = (
        Index('unique_user_watchlist_name', 'user_id', text('lower(name)'), unique=True),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id = Column(Integer, nullable=False, index=True)
    
    name = Column(String(100), nullable=False)
    
    is_default = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # relationship
    items = relationship(
        "WatchlistItem",
        back_populates="watchlist",
        cascade="all, delete-orphan"
    )