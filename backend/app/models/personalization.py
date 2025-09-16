from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.db.base import Base

class LearningStyle(str, enum.Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"
    BALANCED = "balanced"

class ContentPreference(str, enum.Enum):
    EXAMPLES_FIRST = "examples_first"
    THEORY_FIRST = "theory_first"
    PRACTICE_FIRST = "practice_first"
    BALANCED = "balanced"

class LearningPace(str, enum.Enum):
    FAST = "fast"
    MODERATE = "moderate"
    THOROUGH = "thorough"

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    
    # Learning Style Detection
    primary_learning_style = Column(Enum(LearningStyle), default=LearningStyle.BALANCED)
    content_preference = Column(Enum(ContentPreference), default=ContentPreference.EXAMPLES_FIRST)
    learning_pace = Column(Enum(LearningPace), default=LearningPace.MODERATE)
    
    # Personalization Data
    interests = Column(ARRAY(String), default=[])
    difficulty_preference = Column(String, default="moderate")  # gradual, moderate, challenging
    engagement_style = Column(String, default="progress_focused")  # gamified, achievement_focused, progress_focused
    
    # AI Analysis Results
    learning_style_confidence = Column(Float, default=0.5)
    adaptation_strategies = Column(JSON)
    personalization_data = Column(JSON)
    
    # Tracking
    last_analysis_date = Column(DateTime(timezone=True))
    analysis_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="profile")
    learning_interactions = relationship("LearningInteraction", back_populates="user_profile")

class LearningInteraction(Base):
    __tablename__ = "learning_interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user_profile_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)
    
    # Interaction Details
    interaction_type = Column(String, nullable=False)  # hint_request, example_view, content_skip, etc.
    content_id = Column(String)  # topic_id, lesson_id, etc.
    content_type = Column(String)  # lesson, assessment, hint, example
    
    # Context Data
    context_data = Column(JSON)
    user_action = Column(String)
    time_spent = Column(Integer)  # seconds
    success_indicator = Column(Boolean)
    
    # Personalization Impact
    personalization_applied = Column(Boolean, default=False)
    personalization_type = Column(String)  # hint_style, example_type, difficulty_adjustment
    effectiveness_score = Column(Float)  # 0.0-1.0 how effective the personalization was
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")
    user_profile = relationship("UserProfile", back_populates="learning_interactions")

class PersonalizedContent(Base):
    __tablename__ = "personalized_content"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Content Details
    content_type = Column(String, nullable=False)  # hint, example, lesson, assessment
    original_content_id = Column(String)
    topic = Column(String, nullable=False)
    
    # Personalization Applied
    learning_style_applied = Column(Enum(LearningStyle))
    personalization_factors = Column(JSON)
    generated_content = Column(JSON)
    
    # Usage and Effectiveness
    usage_count = Column(Integer, default=0)
    effectiveness_ratings = Column(ARRAY(Float), default=[])
    avg_effectiveness = Column(Float)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User")

class AdaptiveDifficulty(Base):
    __tablename__ = "adaptive_difficulty"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Difficulty Tracking
    topic_id = Column(String, nullable=False)
    current_difficulty = Column(Float, default=0.5)  # 0.0 (easiest) to 1.0 (hardest)
    base_difficulty = Column(Float, default=0.5)
    
    # Performance Data
    recent_scores = Column(ARRAY(Float), default=[])
    success_rate = Column(Float, default=0.5)
    engagement_score = Column(Float, default=0.5)
    
    # Adjustment History
    adjustment_history = Column(JSON, default=[])
    last_adjustment = Column(Float, default=0.0)
    adjustment_reason = Column(String)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")