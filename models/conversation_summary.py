from datetime import datetime, timezone
import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship

from core.database import Base


class ConversationSummary(Base):
    __tablename__ = "conversation_summaries"

    summary_id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    session_id = Column(
        String,
        ForeignKey("sessions.session_id"),
        unique=True,
        nullable=False
    )

    summary = Column(
        Text,
        nullable=False
    )

    message_count = Column(
        Integer,
        nullable=False,
        default=0
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    session = relationship("Session")