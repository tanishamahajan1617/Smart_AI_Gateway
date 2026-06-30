from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from core.database import Base


class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id = Column(
        String,
        ForeignKey("users.user_id"),
        nullable=False
    )

    title = Column(
        String,
        default="New Chat"
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    user = relationship(
        "User",
        back_populates="sessions"
    )

    messages = relationship(
        "Message",
        back_populates="session",
        cascade="all, delete-orphan"
    )
    summary = relationship(
    "ConversationSummary",
    uselist=False,
    cascade="all, delete-orphan"
)