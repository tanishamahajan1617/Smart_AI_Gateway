from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base
import uuid


class APIKey(Base):
    __tablename__ = "api_keys"

    key_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)

    provider = Column(String, nullable=False)   # openai, gemini, etc
    api_key = Column(String, nullable=False)

    priority = Column(Integer, default=1)       # routing priority
    used_tokens = Column(Integer, default=0)
    limit = Column(Integer, nullable=True)

    status = Column(String, default="active")   # active / exhausted / failed

    user = relationship("User", back_populates="keys")