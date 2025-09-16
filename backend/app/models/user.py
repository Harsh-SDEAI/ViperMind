from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.db.base import Base

class UserLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    current_level = Column(Enum(UserLevel), default=UserLevel.BEGINNER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    assessments = relationship("Assessment", back_populates="user")
    user_progress = relationship("UserProgress", back_populates="user")
    level_progress = relationship("LevelProgress", back_populates="user")
    learning_analytics = relationship("LearningAnalytics", back_populates="user")
    remedial_content = relationship("RemedialContent", back_populates="user")
    review_schedules = relationship("ReviewSchedule", back_populates="user")
    profile = relationship("UserProfile", back_populates="user", uselist=False)