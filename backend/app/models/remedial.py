from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.db.base import Base

class RemedialType(str, enum.Enum):
    MINI_EXPLAINER = "mini_explainer"
    REMEDIAL_CARD = "remedial_card"
    REVIEW_WEEK = "review_week"

class RemedialStatus(str, enum.Enum):
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"

class RemedialContent(Base):
    __tablename__ = "remedial_content"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    target_id = Column(UUID(as_uuid=True), nullable=False)  # topic, section, or level ID
    type = Column(Enum(RemedialType), nullable=False)
    status = Column(Enum(RemedialStatus), default=RemedialStatus.ASSIGNED)
    
    # Content data
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    ai_generated_content = Column(JSON)  # AI-generated explanations, examples, etc.
    weak_concepts = Column(ARRAY(String))  # Concepts that need reinforcement
    
    # Progress tracking
    time_spent = Column(Integer, default=0)  # seconds
    completion_percentage = Column(Float, default=0.0)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="remedial_content")
    assessment = relationship("Assessment", back_populates="remedial_content")

class RemedialCard(Base):
    __tablename__ = "remedial_cards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    remedial_content_id = Column(UUID(as_uuid=True), ForeignKey("remedial_content.id"), nullable=False)
    topic_concept = Column(String, nullable=False)
    
    # Card content
    explanation = Column(Text, nullable=False)
    code_example = Column(Text)
    practice_question = Column(JSON)  # Question with options and answer
    hints = Column(ARRAY(String))
    
    # Progress
    is_completed = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    time_spent = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    remedial_content = relationship("RemedialContent", back_populates="remedial_cards")

# Add the reverse relationship to RemedialContent
RemedialContent.remedial_cards = relationship("RemedialCard", back_populates="remedial_content", cascade="all, delete-orphan")

class ReviewSchedule(Base):
    __tablename__ = "review_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    
    # Schedule details
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    review_duration_days = Column(Integer, default=7)  # Default 1 week
    is_completed = Column(Boolean, default=False)
    
    # Review content
    review_topics = Column(ARRAY(String))
    review_materials = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="review_schedules")
    assessment = relationship("Assessment", back_populates="review_schedules")