from sqlalchemy import Column, String, Integer, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base

class Level(Base):
    __tablename__ = "levels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    code = Column(String(1), unique=True, nullable=False)  # B, I, A
    description = Column(Text)
    order = Column(Integer, nullable=False)

    # Relationships
    sections = relationship("Section", back_populates="level", cascade="all, delete-orphan")
    level_progress = relationship("LevelProgress", back_populates="level")

class Section(Base):
    __tablename__ = "sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    level_id = Column(UUID(as_uuid=True), ForeignKey("levels.id"), nullable=False)
    name = Column(String, nullable=False)
    code = Column(String(2), nullable=False)  # B1, B2, I1, etc.
    description = Column(Text)
    order = Column(Integer, nullable=False)

    # Relationships
    level = relationship("Level", back_populates="sections")
    topics = relationship("Topic", back_populates="section", cascade="all, delete-orphan")

class Topic(Base):
    __tablename__ = "topics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id"), nullable=False)
    name = Column(String, nullable=False)
    order = Column(Integer, nullable=False)

    # Relationships
    section = relationship("Section", back_populates="topics")
    lesson_content = relationship("LessonContent", back_populates="topic", uselist=False)
    topic_remedial_content = relationship("TopicRemedialContent", back_populates="topic", uselist=False)
    user_progress = relationship("UserProgress", back_populates="topic")

class LessonContent(Base):
    __tablename__ = "lesson_contents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id"), nullable=False)
    why_it_matters = Column(Text, nullable=False)
    key_ideas = Column(ARRAY(Text), nullable=False)
    examples = Column(JSON)  # List of CodeExample objects
    pitfalls = Column(ARRAY(Text), nullable=False)
    recap = Column(Text, nullable=False)

    # Relationships
    topic = relationship("Topic", back_populates="lesson_content")

class TopicRemedialContent(Base):
    __tablename__ = "topic_remedial_contents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id"), nullable=False)
    explanation = Column(Text, nullable=False)
    practice_exercises = Column(JSON)  # List of practice problems
    additional_resources = Column(JSON)  # Links and references

    # Relationships
    topic = relationship("Topic", back_populates="topic_remedial_content")