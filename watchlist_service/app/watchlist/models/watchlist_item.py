import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    watchlist_id = Column(
        UUID(as_uuid=True),
        ForeignKey("app.watchlists.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    instrument_id = Column(Integer, nullable=False, index=True)

    symbol = Column(String(20), nullable=False)
    exchange = Column(String(10), nullable=False)

    position = Column(Integer, nullable=True)  # for ordering

    added_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationship
    watchlist = relationship("Watchlist", back_populates="items")

    # constraints
    __table_args__ = (
        UniqueConstraint("watchlist_id", "instrument_id", name="uq_watchlist_instrument"),
        {"schema": "app"}
    )