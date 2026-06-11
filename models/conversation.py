from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import uuid


class Conversation(Base):
    __tablename__ = "conversations"

    # 🔹 Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # 🔹 User relation
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)

    # 🔹 Core data (MAIN)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)

    # EDA FIELDS (VERY IMPORTANT)
    provider = Column(String, nullable=False)      # openai / gemini etc.
    tokens_used = Column(Integer, default=0)       # cost tracking

    #  INPUT TYPE TRACKING
    file_type = Column(String, nullable=True)      # text / image / pdf

    # QUERY ANALYSIS
    query_length = Column(Integer)                 # number of words

    #  ROUTING ANALYSIS (future use)
    selected_priority = Column(Integer, nullable=True)

    #  TIME TRACKING
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="conversations")