import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    ForeignKey
)

from core.database import Base


class PasswordResetToken(Base):

    __tablename__ = "password_reset_tokens"

    token_id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id = Column(
        String,
        ForeignKey(
            "users.user_id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    token = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    used = Column(
        Boolean,
        default=False
    )

    expires_at = Column(
        DateTime(timezone=True),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )