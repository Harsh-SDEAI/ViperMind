from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.db.base import Base

class ProgressStatus(str, enum.Enum):
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    level_id = Column(UUID(as_uuid=True), ForeignKey("levels.id"), nullable=False)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id"), nullable=False)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id"), nullable=False)
    status = Column(Enum(ProgressStatus), default=ProgressStatus.LOCKED)
    best_score = Column(Float)
    attempts = Column(Integer, default=0)
    time_spent = Column(Integer, default=0)  # Total time spent in seconds
    last_attempt_at = Column(DateTime(timezone=True))
    last_accessed = Column(DateTime(timezone=True))  # Last time topic was accessed
    unlocked_at = Column(DateTime(timezone=True))
    learning_velocity = Column(Float)  # AI-calculated learning speed
    struggle_areas = Column(ARRAY(String))  # AI-identified weak concepts
    strength_areas = Column(ARRAY(String))  # AI-identified strong concepts
    recommended_difficulty = Column(String)  # AI-recommended next difficulty level
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="user_progress")
    topic = relationship("Topic", back_populates="user_progress")

class LevelProgress(Base):
    __tablename__ = "level_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    level_id = Column(UUID(as_uuid=True), ForeignKey("levels.id"), nullable=False)
    topic_quiz_average = Column(Float, default=0.0)
    section_test_average = Column(Float, default=0.0)
    level_final_score = Column(Float)
    overall_score = Column(Float, default=0.0)
    is_unlocked = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)
    can_advance = Column(Boolean, default=False)
    ai_insights = Column(JSON)  # AI-generated learning insights
    predicted_completion_time = Column(Integer)  # AI prediction in hours
    personalized_recommendations = Column(ARRAY(String))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="level_progress")
    level = relationship("Level", back_populates="level_progress")

class LearningAnalytics(Base):
    __tablename__ = "learning_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_id = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    activity_type = Column(String, nullable=False)  # 'lesson_view', 'quiz_attempt', etc.
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id"))
    time_spent = Column(Integer)  # seconds
    performance_metrics = Column(JSON)
    ai_observations = Column(JSON)  # AI-noted patterns and behaviors
    engagement_score = Column(Float)  # AI-calculated engagement level

    # Relationships
    user = relationship("User", back_populates="learning_analytics")