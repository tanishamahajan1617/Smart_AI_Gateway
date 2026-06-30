from datetime import datetime, timezone
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.orm import relationship

from core.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    # ======================================================
    # PRIMARY KEY
    # ======================================================

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # ======================================================
    # USER INFORMATION
    # ======================================================

    user_id = Column(
        String,
        ForeignKey("users.user_id"),
        nullable=False
    )

    session_id = Column(
        String,
        nullable=False
    )

    # Which API key handled this request
    key_id = Column(
        String,
        ForeignKey("api_keys.key_id"),
        nullable=False
    )
    model_id = Column(
    String,
    ForeignKey("api_key_models.model_id"),
    nullable=True
    )

    # ======================================================
    # QUERY & RESPONSE
    # ======================================================

    query = Column(
        Text,
        nullable=False
    )

    response = Column(
        Text,
        nullable=False
    )

    source = Column(
        String,
        default="llm"
    )  # llm / cache / rag

    # ======================================================
    # MODEL INFORMATION
    # ======================================================

    provider = Column(
        String,
        nullable=False
    )

    model = Column(
        String,
        nullable=False
    )

    # ======================================================
    # TOKEN USAGE
    # ======================================================

    input_tokens = Column(
        Integer,
        default=0
    )

    output_tokens = Column(
        Integer,
        default=0
    )

    tokens_used = Column(
        Integer,
        default=0
    )

    total_cost_usd = Column(
        Float,
        default=0.0
    )

    # ======================================================
    # INPUT INFORMATION
    # ======================================================

    file_type = Column(
        String,
        nullable=True
    )  # text / image / pdf / audio

    query_length = Column(
        Integer
    )

    prompt_category = Column(
        String,
        nullable=True
    )  # coding / reasoning / summarization / translation ...

    # ======================================================
    # ROUTING ANALYTICS
    # ======================================================

    routing_hint = Column(
        String,
        nullable=True
    )  # fast / balanced / reasoning

    selected_by = Column(
        String,
        default="rule_engine"
    )  # rule_engine / ml_router / manual / fallback

    retry_count = Column(
        Integer,
        default=0
    )

    success = Column(
        Boolean,
        default=True
    )

    latency_ms = Column(
        Float,
        nullable=True
    )

    # ======================================================
    # TIMESTAMPS
    # ======================================================

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    attempt_count = Column(
    Integer,
    default=1)

    selected_rank = Column(
            Integer,
            default=1
        )

    router_confidence = Column(
        Float,
        nullable=True
    )

    failure_reason = Column(
            String,
            nullable=True
        )

    # ======================================================
    # RELATIONSHIPS
    # ======================================================

    user = relationship(
        "User",
        back_populates="conversations"
    )

    api_key = relationship(
        "APIKey"
    )