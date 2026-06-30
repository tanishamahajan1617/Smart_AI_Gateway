from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    DateTime,
    Index
)
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime, timezone
import uuid


class APIKey(Base):
    __tablename__ = "api_keys"

    # ======================================================
    # PRIMARY KEY
    # ======================================================

    key_id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # ======================================================
    # OWNER
    # ======================================================

    user_id = Column(
        String,
        ForeignKey("users.user_id"),
        nullable=False,
        index=True
    )

    # ======================================================
    # PROVIDER
    # ======================================================

    provider = Column(
        String,
        nullable=False,
        index=True
    )

    # ======================================================
    # ENCRYPTED API KEY
    # ======================================================

    api_key = Column(
        String,
        nullable=False
    )

    # Used for duplicate detection
    api_key_hash = Column(
        String,
        nullable=False,
        index=True
    )

    # ======================================================
    # USER PREFERENCES
    # ======================================================

    priority = Column(
        Integer,
        default=3
    )

    limit = Column(
        Integer,
        nullable=True
    )

    status = Column(
        String,
        default="active",
        index=True
    )

    tokens_used = Column(
        Integer,
        default=0
    )

    daily_token_used = Column(Integer,
                              default=0)
    
    monthly_token_used = Column(Integer,default=0)


    # ======================================================
    # TIMESTAMPS
    # ======================================================

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

   

    # ======================================================
    # RELATIONSHIPS
    # ======================================================

    # Owner
    user = relationship(
        "User",
        back_populates="keys"
    )

    # One API Key -> Many Models
    models = relationship(
        "APIKeyModel",
        back_populates="api_key",
        cascade="all, delete-orphan"
    )

    # ======================================================
    # INDEXES
    # ======================================================

    __table_args__ = (

        Index(
            "idx_user_provider",
            "user_id",
            "provider"
        ),

        Index(
            "idx_user_hash",
            "user_id",
            "api_key_hash"
        ),

    )