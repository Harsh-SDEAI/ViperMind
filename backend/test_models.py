#!/usr/bin/env python3
"""
Simple test script to verify database models work correctly
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import User, Level, Section, Topic, Assessment, UserProgress
from app.models.user import UserLevel
from app.models.assessment import AssessmentType
from app.models.progress import ProgressStatus
import uuid

def test_models():
    """Test that all models can be created and relationships work"""
    print("Testing database models...")
    
    # Create engine and session
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Test User model
        test_user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            current_level=UserLevel.BEGINNER
        )
        db.add(test_user)
        db.flush()
        print("✓ User model works")
        
        # Test Level model
        test_level = Level(
            name="Test Level",
            code="T",
            description="Test level description",
            order=1
        )
        db.add(test_level)
        db.flush()
        print("✓ Level model works")
        
        # Test Section model
        test_section = Section(
            level_id=test_level.id,
            name="Test Section",
            code="T1",
            description="Test section description",
            order=1
        )
        db.add(test_section)
        db.flush()
        print("✓ Section model works")
        
        # Test Topic model
        test_topic = Topic(
            section_id=test_section.id,
            name="Test Topic",
            order=1
        )
        db.add(test_topic)
        db.flush()
        print("✓ Topic model works")
        
        # Test Assessment model
        test_assessment = Assessment(
            user_id=test_user.id,
            type=AssessmentType.QUIZ,
            target_id=test_topic.id,
            attempt_number=1
        )
        db.add(test_assessment)
        db.flush()
        print("✓ Assessment model works")
        
        # Test UserProgress model
        test_progress = UserProgress(
            user_id=test_user.id,
            level_id=test_level.id,
            section_id=test_section.id,
            topic_id=test_topic.id,
            status=ProgressStatus.AVAILABLE
        )
        db.add(test_progress)
        db.flush()
        print("✓ UserProgress model works")
        
        # Test relationships
        user_assessments = test_user.assessments
        level_sections = test_level.sections
        section_topics = test_section.topics
        print("✓ Model relationships work")
        
        # Rollback to avoid polluting the database
        db.rollback()
        print("✓ All models tested successfully!")
        
    except Exception as e:
        print(f"✗ Model test failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_models()