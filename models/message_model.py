from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from core.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    session_id = Column(
        String,
        ForeignKey("sessions.session_id"),
        nullable=False
    )

    role = Column(
        String,
        nullable=False
    )  # user / assistant / system

    content = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

   
    session = relationship(
    "Session",
    back_populates="messages"
)