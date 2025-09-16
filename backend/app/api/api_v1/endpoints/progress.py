"""
Progress API endpoints for ViperMind
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth import get_current_active_user
from app.db.base import get_db
from app.models.user import User
from app.models.curriculum import Level, Section, Topic
from app.models.progress import UserProgress, LevelProgress, ProgressStatus
from app.models.assessment import Assessment, AssessmentType
from app.agents.vipermind_agent import analyze_progress
from pydantic import BaseModel
from datetime import datetime, timezone
from sqlalchemy import func, and_

router = APIRouter()


class ProgressUpdate(BaseModel):
    topic_id: str
    status: str = "completed"
    score: float = None
    time_spent: int = 0


class UnlockRequest(BaseModel):
    target_type: str  # "topic", "section", "level"
    target_id: str


class ProgressSummary(BaseModel):
    user_level: str
    current_level_id: str
    current_level_progress: float
    topics_completed: int
    total_topics: int
    quizzes_passed: int
    section_tests_passed: int
    level_finals_passed: int
    overall_score: float
    learning_velocity: float
    next_unlock: Dict[str, Any] = None


@router.get("/summary", response_model=ProgressSummary)
def get_progress_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get comprehensive progress summary for the user"""
    
    # Get user's current level
    user_level = current_user.current_level.value
    
    # Find current level details
    current_level = None
    if user_level == "beginner":
        current_level = db.query(Level).filter(Level.code == "B").first()
    elif user_level == "intermediate":
        current_level = db.query(Level).filter(Level.code == "I").first()
    elif user_level == "advanced":
        current_level = db.query(Level).filter(Level.code == "A").first()
    
    if not current_level:
        raise HTTPException(status_code=404, detail="Current level not found")
    
    # Get level progress
    level_progress = db.query(LevelProgress).filter(
        LevelProgress.user_id == current_user.id,
        LevelProgress.level_id == current_level.id
    ).first()
    
    current_level_progress = level_progress.overall_score if level_progress else 0.0
    
    # Get topic progress statistics
    topic_progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id
    ).all()
    
    topics_completed = len([p for p in topic_progress if p.status == ProgressStatus.COMPLETED])
    total_topics = db.query(Topic).count()
    
    # Get assessment statistics
    assessments = db.query(Assessment).filter(
        Assessment.user_id == current_user.id,
        Assessment.passed == True
    ).all()
    
    quizzes_passed = len([a for a in assessments if a.type == AssessmentType.QUIZ])
    section_tests_passed = len([a for a in assessments if a.type == AssessmentType.SECTION_TEST])
    level_finals_passed = len([a for a in assessments if a.type == AssessmentType.LEVEL_FINAL])
    
    # Calculate overall score
    scores = [p.best_score for p in topic_progress if p.best_score is not None]
    overall_score = sum(scores) / len(scores) if scores else 0.0
    
    # Calculate learning velocity (topics completed per day)
    if topic_progress:
        from datetime import timezone
        now = datetime.now(timezone.utc)
        first_progress = min(topic_progress, key=lambda p: p.created_at or now)
        first_date = first_progress.created_at or now
        if first_date.tzinfo is None:
            first_date = first_date.replace(tzinfo=timezone.utc)
        days_learning = (now - first_date).days + 1
        learning_velocity = topics_completed / max(days_learning, 1)
    else:
        learning_velocity = 0.0
    
    # Determine next unlock
    next_unlock = _get_next_unlock(current_user.id, db)
    
    return ProgressSummary(
        user_level=user_level,
        current_level_id=str(current_level.id),
        current_level_progress=current_level_progress,
        topics_completed=topics_completed,
        total_topics=total_topics,
        quizzes_passed=quizzes_passed,
        section_tests_passed=section_tests_passed,
        level_finals_passed=level_finals_passed,
        overall_score=overall_score,
        learning_velocity=learning_velocity,
        next_unlock=next_unlock
    )


@router.post("/update")
def update_progress(
    progress_update: ProgressUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update user progress for a topic"""
    
    # Get or create user progress record
    user_progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.topic_id == progress_update.topic_id
    ).first()
    
    if not user_progress:
        # Get topic to get section and level info
        topic = db.query(Topic).filter(Topic.id == progress_update.topic_id).first()
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        user_progress = UserProgress(
            user_id=current_user.id,
            level_id=topic.section.level_id,
            section_id=topic.section_id,
            topic_id=progress_update.topic_id,
            status=ProgressStatus.AVAILABLE,
            attempts=0,
            time_spent=0
        )
        db.add(user_progress)
    
    # Update progress
    user_progress.status = ProgressStatus(progress_update.status)
    if progress_update.score is not None:
        if user_progress.best_score is None or progress_update.score > user_progress.best_score:
            user_progress.best_score = progress_update.score
        user_progress.attempts += 1
    
    if progress_update.time_spent > 0:
        user_progress.time_spent = (user_progress.time_spent or 0) + progress_update.time_spent
    
    user_progress.last_accessed = datetime.now(timezone.utc)
    
    # Check for unlocks and level advancement
    unlocks = _check_and_update_unlocks(current_user.id, db)
    level_advancement = _check_level_advancement(current_user.id, db)
    
    db.commit()
    
    return {
        "success": True,
        "progress": {
            "topic_id": str(user_progress.topic_id),
            "status": user_progress.status.value,
            "best_score": user_progress.best_score,
            "attempts": user_progress.attempts
        },
        "unlocks": unlocks,
        "level_advancement": level_advancement
    }


@router.post("/unlock")
def unlock_content(
    unlock_request: UnlockRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Manually unlock content (for testing or admin purposes)"""
    
    if unlock_request.target_type == "topic":
        # Check if topic can be unlocked
        can_unlock, reason = _can_unlock_topic(current_user.id, unlock_request.target_id, db)
        if not can_unlock:
            raise HTTPException(status_code=400, detail=reason)
        
        # Unlock topic
        _unlock_topic(current_user.id, unlock_request.target_id, db)
        
    elif unlock_request.target_type == "section":
        # Check if section can be unlocked
        can_unlock, reason = _can_unlock_section(current_user.id, unlock_request.target_id, db)
        if not can_unlock:
            raise HTTPException(status_code=400, detail=reason)
        
        # Unlock all topics in section
        _unlock_section(current_user.id, unlock_request.target_id, db)
        
    elif unlock_request.target_type == "level":
        # Check if level can be unlocked
        can_unlock, reason = _can_unlock_level(current_user.id, unlock_request.target_id, db)
        if not can_unlock:
            raise HTTPException(status_code=400, detail=reason)
        
        # Unlock level
        _unlock_level(current_user.id, unlock_request.target_id, db)
    
    db.commit()
    
    return {
        "success": True,
        "message": f"{unlock_request.target_type.title()} unlocked successfully"
    }


@router.get("/analytics")
def get_progress_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get detailed progress analytics using AI agent"""
    
    try:
        result = analyze_progress(user_id=str(current_user.id))
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to analyze progress: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "analytics": result.get("learning_patterns", {}),
            "insights": result.get("pattern_insights", {}),
            "agent": result.get("agent")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing progress: {str(e)}"
        )


def _get_next_unlock(user_id: str, db: Session) -> Dict[str, Any]:
    """Determine what content can be unlocked next"""
    
    # Get user's current progress
    user_progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).all()
    completed_topics = [p.topic_id for p in user_progress if p.status == ProgressStatus.COMPLETED]
    
    # Find next topic to unlock
    all_topics = db.query(Topic).join(Section).join(Level).order_by(
        Level.order, Section.order, Topic.order
    ).all()
    
    for topic in all_topics:
        if str(topic.id) not in [str(t) for t in completed_topics]:
            # Check if this topic can be unlocked
            can_unlock, reason = _can_unlock_topic(user_id, str(topic.id), db)
            if can_unlock:
                return {
                    "type": "topic",
                    "id": str(topic.id),
                    "name": topic.name,
                    "section": topic.section.name,
                    "level": topic.section.level.name
                }
    
    return None


def _check_and_update_unlocks(user_id: str, db: Session) -> List[Dict[str, Any]]:
    """Check and update any content that should be unlocked"""
    
    unlocks = []
    
    # Check for topic unlocks
    user_progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).all()
    completed_topics = [p.topic_id for p in user_progress if p.status == ProgressStatus.COMPLETED]
    
    # Get all topics in order
    all_topics = db.query(Topic).join(Section).join(Level).order_by(
        Level.order, Section.order, Topic.order
    ).all()
    
    for topic in all_topics:
        if str(topic.id) not in [str(t) for t in completed_topics]:
            can_unlock, _ = _can_unlock_topic(user_id, str(topic.id), db)
            if can_unlock:
                # Check if already unlocked
                existing_progress = next((p for p in user_progress if p.topic_id == topic.id), None)
                if not existing_progress or existing_progress.status == ProgressStatus.LOCKED:
                    _unlock_topic(user_id, str(topic.id), db)
                    unlocks.append({
                        "type": "topic",
                        "id": str(topic.id),
                        "name": topic.name
                    })
    
    return unlocks


def _check_level_advancement(user_id: str, db: Session) -> Dict[str, Any]:
    """Check if user can advance to next level"""
    
    user = db.query(User).filter(User.id == user_id).first()
    current_level_code = user.current_level.value
    
    # Get current level
    level_map = {"beginner": "B", "intermediate": "I", "advanced": "A"}
    current_level = db.query(Level).filter(Level.code == level_map[current_level_code]).first()
    
    if not current_level:
        return {"can_advance": False, "reason": "Current level not found"}
    
    # Check if all sections in current level are completed with required averages
    sections = db.query(Section).filter(Section.level_id == current_level.id).all()
    
    for section in sections:
        section_average = _calculate_section_average(user_id, str(section.id), db)
        required_average = 75.0  # 75% average required for section completion
        
        if section_average < required_average:
            return {
                "can_advance": False,
                "reason": f"Section '{section.name}' requires {required_average}% average (current: {section_average:.1f}%)"
            }
    
    # Check if level final is passed
    level_final = db.query(Assessment).filter(
        Assessment.user_id == user_id,
        Assessment.type == AssessmentType.LEVEL_FINAL,
        Assessment.target_id == current_level.id,
        Assessment.passed == True
    ).first()
    
    if not level_final:
        return {
            "can_advance": False,
            "reason": "Level final exam must be passed"
        }
    
    # User can advance to next level
    next_level_codes = {"B": "I", "I": "A", "A": None}
    next_code = next_level_codes.get(current_level.code)
    
    if not next_code:
        return {
            "can_advance": False,
            "reason": "Already at highest level"
        }
    
    # Update user level
    from app.models.user import UserLevel
    level_enum_map = {"I": UserLevel.INTERMEDIATE, "A": UserLevel.ADVANCED}
    user.current_level = level_enum_map[next_code]
    
    # Unlock next level
    next_level = db.query(Level).filter(Level.code == next_code).first()
    if next_level:
        _unlock_level(user_id, str(next_level.id), db)
    
    return {
        "can_advance": True,
        "advanced_to": next_code,
        "level_name": next_level.name if next_level else "Unknown"
    }


def _can_unlock_topic(user_id: str, topic_id: str, db: Session) -> tuple[bool, str]:
    """Check if a topic can be unlocked"""
    
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        return False, "Topic not found"
    
    # First topic in first section of first level is always unlocked
    if topic.order == 1 and topic.section.order == 1 and topic.section.level.order == 1:
        return True, "First topic"
    
    # Check if previous topic is completed
    if topic.order > 1:
        prev_topic = db.query(Topic).filter(
            Topic.section_id == topic.section_id,
            Topic.order == topic.order - 1
        ).first()
        
        if prev_topic:
            prev_progress = db.query(UserProgress).filter(
                UserProgress.user_id == user_id,
                UserProgress.topic_id == prev_topic.id
            ).first()
            
            if not prev_progress or prev_progress.status != ProgressStatus.COMPLETED:
                return False, "Previous topic must be completed"
    
    # Check if previous section is completed (for first topic of new section)
    elif topic.order == 1 and topic.section.order > 1:
        prev_section = db.query(Section).filter(
            Section.level_id == topic.section.level_id,
            Section.order == topic.section.order - 1
        ).first()
        
        if prev_section:
            section_average = _calculate_section_average(user_id, str(prev_section.id), db)
            if section_average < 70.0:  # 70% average required to unlock next section
                return False, f"Previous section requires 70% average (current: {section_average:.1f}%)"
    
    return True, "Can unlock"


def _can_unlock_section(user_id: str, section_id: str, db: Session) -> tuple[bool, str]:
    """Check if a section can be unlocked"""
    
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        return False, "Section not found"
    
    # First section is always unlocked
    if section.order == 1:
        return True, "First section"
    
    # Check if previous section is completed
    prev_section = db.query(Section).filter(
        Section.level_id == section.level_id,
        Section.order == section.order - 1
    ).first()
    
    if prev_section:
        section_average = _calculate_section_average(user_id, str(prev_section.id), db)
        if section_average < 70.0:
            return False, f"Previous section requires 70% average (current: {section_average:.1f}%)"
    
    return True, "Can unlock"


def _can_unlock_level(user_id: str, level_id: str, db: Session) -> tuple[bool, str]:
    """Check if a level can be unlocked"""
    
    level = db.query(Level).filter(Level.id == level_id).first()
    if not level:
        return False, "Level not found"
    
    # First level is always unlocked
    if level.order == 1:
        return True, "First level"
    
    # Check if previous level is completed
    prev_level = db.query(Level).filter(Level.order == level.order - 1).first()
    if prev_level:
        # Check if level final is passed
        level_final = db.query(Assessment).filter(
            Assessment.user_id == user_id,
            Assessment.type == AssessmentType.LEVEL_FINAL,
            Assessment.target_id == prev_level.id,
            Assessment.passed == True
        ).first()
        
        if not level_final:
            return False, "Previous level final must be passed"
    
    return True, "Can unlock"


def _unlock_topic(user_id: str, topic_id: str, db: Session):
    """Unlock a specific topic"""
    
    existing_progress = db.query(UserProgress).filter(
        UserProgress.user_id == user_id,
        UserProgress.topic_id == topic_id
    ).first()
    
    if existing_progress:
        existing_progress.status = ProgressStatus.AVAILABLE
        existing_progress.unlocked_at = datetime.now(timezone.utc)
    else:
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if topic:
            new_progress = UserProgress(
                user_id=user_id,
                level_id=topic.section.level_id,
                section_id=topic.section_id,
                topic_id=topic_id,
                status=ProgressStatus.AVAILABLE,
                unlocked_at=datetime.now(timezone.utc)
            )
            db.add(new_progress)


def _unlock_section(user_id: str, section_id: str, db: Session):
    """Unlock all topics in a section"""
    
    topics = db.query(Topic).filter(Topic.section_id == section_id).all()
    for topic in topics:
        _unlock_topic(user_id, str(topic.id), db)


def _unlock_level(user_id: str, level_id: str, db: Session):
    """Unlock a level and its first section"""
    
    # Get or create level progress
    level_progress = db.query(LevelProgress).filter(
        LevelProgress.user_id == user_id,
        LevelProgress.level_id == level_id
    ).first()
    
    if not level_progress:
        level_progress = LevelProgress(
            user_id=user_id,
            level_id=level_id,
            is_unlocked=True
        )
        db.add(level_progress)
    else:
        level_progress.is_unlocked = True
    
    # Unlock first section
    first_section = db.query(Section).filter(
        Section.level_id == level_id,
        Section.order == 1
    ).first()
    
    if first_section:
        # Unlock first topic of first section
        first_topic = db.query(Topic).filter(
            Topic.section_id == first_section.id,
            Topic.order == 1
        ).first()
        
        if first_topic:
            _unlock_topic(user_id, str(first_topic.id), db)


def _calculate_section_average(user_id: str, section_id: str, db: Session) -> float:
    """Calculate average score for all topics in a section"""
    
    topics = db.query(Topic).filter(Topic.section_id == section_id).all()
    topic_ids = [str(topic.id) for topic in topics]
    
    progress_records = db.query(UserProgress).filter(
        UserProgress.user_id == user_id,
        UserProgress.topic_id.in_(topic_ids),
        UserProgress.best_score.isnot(None)
    ).all()
    
    if not progress_records:
        return 0.0
    
    scores = [p.best_score for p in progress_records if p.best_score is not None]
    return sum(scores) / len(scores) if scores else 0.0