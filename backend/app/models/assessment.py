from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.db.base import Base

class AssessmentType(str, enum.Enum):
    QUIZ = "quiz"
    SECTION_TEST = "section_test"
    LEVEL_FINAL = "level_final"

class DifficultyLevel(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type = Column(Enum(AssessmentType), nullable=False)
    target_id = Column(UUID(as_uuid=True), nullable=False)  # topicId, sectionId, or levelId
    score = Column(Float)
    passed = Column(Boolean)
    attempt_number = Column(Integer, default=1)
    time_taken = Column(Integer)  # Total time taken in seconds
    submitted_at = Column(DateTime(timezone=True))  # When assessment was submitted
    completed_at = Column(DateTime(timezone=True))  # When assessment was completed (same as submitted_at)
    ai_generated = Column(Boolean, default=True)
    difficulty_level = Column(String, default="medium")  # Changed to String for flexibility
    personalization_factors = Column(JSON)
    ai_feedback = Column(Text)
    questions_data = Column(JSON)  # Store generated questions data
    user_answers = Column(JSON)  # Store user's answers
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="assessments")
    questions = relationship("Question", back_populates="assessment", cascade="all, delete-orphan")
    answers = relationship("Answer", back_populates="assessment", cascade="all, delete-orphan")
    remedial_content = relationship("RemedialContent", back_populates="assessment")
    review_schedules = relationship("ReviewSchedule", back_populates="assessment")

class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    text = Column(Text, nullable=False)
    options = Column(ARRAY(Text), nullable=False)
    correct_answer = Column(Integer, nullable=False)
    explanation = Column(Text)
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    ai_generated = Column(Boolean, default=True)
    generation_prompt = Column(Text)
    concept_tags = Column(ARRAY(String))
    code_snippet = Column(Text)
    order = Column(Integer, nullable=False)

    # Relationships
    assessment = relationship("Assessment", back_populates="questions")
    answers = relationship("Answer", back_populates="question")

class Answer(Base):
    __tablename__ = "answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    selected_option = Column(Integer, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_taken = Column(Integer)  # seconds
    confidence_level = Column(String)
    ai_hint_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    assessment = relationship("Assessment", back_populates="answers")
    question = relationship("Question", back_populates="answers")