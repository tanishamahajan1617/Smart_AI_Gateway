from sqlalchemy import Column, String
from core.database import Base
from sqlalchemy.orm import relationship
import uuid


class User(Base):
    __tablename__ = "users"

    user_id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    username = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    password = Column(
        String,
        nullable=False
    )



    keys = relationship("APIKey", back_populates="user", cascade="all, delete")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete")
    sessions = relationship(
    "Session",
    back_populates="user",
    cascade="all, delete-orphan"
)