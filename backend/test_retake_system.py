#!/usr/bin/env python3
"""
Test script for the retake system and attempt management
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.assessment import Assessment, AssessmentType
from app.models.curriculum import Topic, Section, Level
from app.core.security import get_password_hash
import uuid
from datetime import datetime

def create_test_user(db: Session) -> User:
    """Create a test user for retake testing"""
    test_user = User(
        email="retake_test@example.com",
        username="retake_tester",
        password_hash=get_password_hash("testpass123"),
        is_active=True
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    return test_user

def create_test_curriculum(db: Session) -> tuple:
    """Create test curriculum structure"""
    # Create level
    level = Level(
        name="Test Level",
        code="T",
        description="Test level for retake system",
        order=1
    )
    db.add(level)
    db.flush()
    
    # Create section
    section = Section(
        level_id=level.id,
        name="Test Section",
        code="T1",
        description="Test section",
        order=1
    )
    db.add(section)
    db.flush()
    
    # Create topic
    topic = Topic(
        section_id=section.id,
        name="Test Topic",
        order=1
    )
    db.add(topic)
    db.commit()
    
    return level, section, topic

def create_test_assessment(db: Session, user: User, target_id: str, assessment_type: AssessmentType, 
                          score: float, passed: bool, attempt_number: int) -> Assessment:
    """Create a test assessment with specific results"""
    assessment = Assessment(
        user_id=user.id,
        type=assessment_type,
        target_id=target_id,
        score=score,
        passed=passed,
        attempt_number=attempt_number,
        submitted_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        ai_generated=True,
        difficulty_level="medium",
        questions_data=[
            {
                "question": "Test question",
                "options": ["A", "B", "C", "D"],
                "correct_answer": 0,
                "explanation": "Test explanation"
            }
        ],
        user_answers=[
            {
                "question_id": "test_q1",
                "user_answer": 0 if passed else 1,
                "correct_answer": 0,
                "is_correct": passed
            }
        ]
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment

def test_quiz_retakes(db: Session, user: User, topic: Topic):
    """Test unlimited quiz retakes"""
    print("\n=== Testing Quiz Retakes (Unlimited) ===")
    
    # Create multiple quiz attempts
    attempts = [
        (50.0, False, 1),  # First attempt - failed
        (65.0, False, 2),  # Second attempt - failed
        (75.0, True, 3),   # Third attempt - passed
        (85.0, True, 4),   # Fourth attempt - better score
    ]
    
    for score, passed, attempt_num in attempts:
        assessment = create_test_assessment(
            db, user, str(topic.id), AssessmentType.QUIZ, 
            score, passed, attempt_num
        )
        print(f"Created quiz attempt {attempt_num}: {score}% ({'PASSED' if passed else 'FAILED'})")
    
    # Test getting attempts info
    from app.api.api_v1.endpoints.assessments import get_remaining_attempts
    from app.core.auth import get_current_active_user
    
    # Mock current user
    class MockUser:
        def __init__(self, user):
            self.id = user.id
    
    mock_user = MockUser(user)
    
    attempts_info = get_remaining_attempts(
        str(topic.id), "quiz", mock_user, db
    )
    
    print(f"Quiz attempts info:")
    print(f"  - Attempts used: {attempts_info['attempts_used']}")
    print(f"  - Max attempts: {attempts_info['max_attempts']}")
    print(f"  - Can attempt: {attempts_info['can_attempt']}")
    print(f"  - Can retake: {attempts_info['can_retake']}")
    print(f"  - Best score: {attempts_info['best_score']}%")
    print(f"  - Best passed: {attempts_info['best_passed']}")
    
    assert attempts_info['attempts_used'] == 4
    assert attempts_info['max_attempts'] == 999
    assert attempts_info['can_attempt'] == True
    assert attempts_info['can_retake'] == True
    assert attempts_info['best_score'] == 85.0
    assert attempts_info['best_passed'] == True
    
    print("✅ Quiz retake tests passed!")

def test_section_test_retakes(db: Session, user: User, section: Section):
    """Test limited section test retakes"""
    print("\n=== Testing Section Test Retakes (1 Retake) ===")
    
    # Create section test attempts
    attempts = [
        (60.0, False, 1),  # First attempt - failed
        (80.0, True, 2),   # Retake - passed
    ]
    
    for score, passed, attempt_num in attempts:
        assessment = create_test_assessment(
            db, user, str(section.id), AssessmentType.SECTION_TEST, 
            score, passed, attempt_num
        )
        print(f"Created section test attempt {attempt_num}: {score}% ({'PASSED' if passed else 'FAILED'})")
    
    # Test getting attempts info
    from app.api.api_v1.endpoints.assessments import get_remaining_attempts
    
    class MockUser:
        def __init__(self, user):
            self.id = user.id
    
    mock_user = MockUser(user)
    
    attempts_info = get_remaining_attempts(
        str(section.id), "section_test", mock_user, db
    )
    
    print(f"Section test attempts info:")
    print(f"  - Attempts used: {attempts_info['attempts_used']}")
    print(f"  - Max attempts: {attempts_info['max_attempts']}")
    print(f"  - Can attempt: {attempts_info['can_attempt']}")
    print(f"  - Can retake: {attempts_info['can_retake']}")
    print(f"  - Best score: {attempts_info['best_score']}%")
    print(f"  - Best passed: {attempts_info['best_passed']}")
    
    assert attempts_info['attempts_used'] == 2
    assert attempts_info['max_attempts'] == 2
    assert attempts_info['can_attempt'] == False  # No more attempts
    assert attempts_info['can_retake'] == False   # Already passed
    assert attempts_info['best_score'] == 80.0
    assert attempts_info['best_passed'] == True
    
    print("✅ Section test retake tests passed!")

def test_level_final_retakes(db: Session, user: User, level: Level):
    """Test limited level final retakes with review requirement"""
    print("\n=== Testing Level Final Retakes (1 Retake + Review) ===")
    
    # Create level final attempt (failed)
    assessment = create_test_assessment(
        db, user, str(level.id), AssessmentType.LEVEL_FINAL, 
        70.0, False, 1
    )
    print(f"Created level final attempt 1: 70% (FAILED)")
    
    # Test getting attempts info
    from app.api.api_v1.endpoints.assessments import get_remaining_attempts
    
    class MockUser:
        def __init__(self, user):
            self.id = user.id
    
    mock_user = MockUser(user)
    
    attempts_info = get_remaining_attempts(
        str(level.id), "level_final", mock_user, db
    )
    
    print(f"Level final attempts info:")
    print(f"  - Attempts used: {attempts_info['attempts_used']}")
    print(f"  - Max attempts: {attempts_info['max_attempts']}")
    print(f"  - Can attempt: {attempts_info['can_attempt']}")
    print(f"  - Can retake: {attempts_info['can_retake']}")
    print(f"  - Best score: {attempts_info['best_score']}%")
    print(f"  - Best passed: {attempts_info['best_passed']}")
    print(f"  - Retake requirements: {attempts_info.get('retake_requirements')}")
    
    assert attempts_info['attempts_used'] == 1
    assert attempts_info['max_attempts'] == 2
    assert attempts_info['can_attempt'] == True
    assert attempts_info['can_retake'] == True
    assert attempts_info['best_score'] == 70.0
    assert attempts_info['best_passed'] == False
    assert attempts_info['retake_requirements']['review_required'] == True
    
    print("✅ Level final retake tests passed!")

def test_best_score_tracking(db: Session, user: User):
    """Test best score tracking across multiple attempts"""
    print("\n=== Testing Best Score Tracking ===")
    
    from app.api.api_v1.endpoints.assessments import get_user_best_scores
    
    class MockUser:
        def __init__(self, user):
            self.id = user.id
    
    mock_user = MockUser(user)
    
    best_scores = get_user_best_scores(str(user.id), mock_user, db)
    
    print(f"Best scores summary:")
    for score_info in best_scores['best_scores']:
        print(f"  - {score_info['assessment_type']}: {score_info['best_score']}% "
              f"({'PASSED' if score_info['passed'] else 'FAILED'}) "
              f"in {score_info['attempts']} attempts")
    
    # Verify we have scores for all assessment types we tested
    assessment_types = [score['assessment_type'] for score in best_scores['best_scores']]
    assert 'quiz' in assessment_types
    assert 'section_test' in assessment_types
    assert 'level_final' in assessment_types
    
    print("✅ Best score tracking tests passed!")

def main():
    """Run all retake system tests"""
    print("🧪 Starting Retake System Tests")
    
    db = SessionLocal()
    try:
        # Clean up any existing test data
        db.query(Assessment).filter(Assessment.user_id.in_(
            db.query(User.id).filter(User.email == "retake_test@example.com")
        )).delete(synchronize_session=False)
        
        db.query(User).filter(User.email == "retake_test@example.com").delete()
        db.commit()
        
        # Create test data
        user = create_test_user(db)
        level, section, topic = create_test_curriculum(db)
        
        # Run tests
        test_quiz_retakes(db, user, topic)
        test_section_test_retakes(db, user, section)
        test_level_final_retakes(db, user, level)
        test_best_score_tracking(db, user)
        
        print("\n🎉 All retake system tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up test data
        try:
            db.query(Assessment).filter(Assessment.user_id == user.id).delete()
            db.query(Topic).filter(Topic.id == topic.id).delete()
            db.query(Section).filter(Section.id == section.id).delete()
            db.query(Level).filter(Level.id == level.id).delete()
            db.query(User).filter(User.id == user.id).delete()
            db.commit()
        except:
            pass
        db.close()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)