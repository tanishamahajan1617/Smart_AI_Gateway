from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    ForeignKey,
    DateTime,
    Index
)
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime, timezone
import uuid


class APIKeyModel(Base):
    __tablename__ = "api_key_models"

    # ======================================================
    # PRIMARY KEY
    # ======================================================

    model_id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # ======================================================
    # PARENT API KEY
    # ======================================================

    key_id = Column(
        String,
        ForeignKey(
            "api_keys.key_id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # ======================================================
    # MODEL INFORMATION
    # ======================================================

    model = Column(
        String,
        nullable=False,
        index=True
    )

    # ======================================================
    # MODEL CAPABILITIES
    # ======================================================

    context_window = Column(Integer)

    speed = Column(Float)

    latency = Column(Float)

    mmlu_score = Column(Float)

    arena_score = Column(Float)

    price_per_million_tokens = Column(Float)

    quality_rating = Column(Integer)

    speed_rating = Column(Integer)

    price_rating = Column(Integer)

    open_source = Column(Boolean)

    # ======================================================
    # USAGE METRICS
    # ======================================================

    tokens_used = Column(
        Integer,
        default=0
    )

    status = Column(
    String,
    default="active"
    )

    last_used_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    failure_count = Column(
        Integer,
        default=0
    )

    last_error = Column(
        String,
        nullable=True
    )

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

    api_key = relationship(
        "APIKey",
        back_populates="models"
    )

    # ======================================================
    # INDEXES
    # ======================================================

    __table_args__ = (

        Index(
            "idx_key_model",
            "key_id",
            "model"
        ),

    )