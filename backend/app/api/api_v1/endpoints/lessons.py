"""
Lesson API endpoints for ViperMind
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth import get_current_active_user
from app.db.base import get_db
from app.models.user import User
from app.models.curriculum import Topic, LessonContent
from app.models.progress import UserProgress, ProgressStatus
from app.schemas.curriculum import LessonContent as LessonContentSchema
from app.agents.vipermind_agent import generate_lesson
from pydantic import BaseModel

router = APIRouter()


class LessonRequest(BaseModel):
    topic_id: str


class LessonResponse(BaseModel):
    topic_id: str
    topic_name: str
    lesson_content: Dict[str, Any]
    is_generated: bool = True
    user_progress: Dict[str, Any] = {}


class LessonProgressUpdate(BaseModel):
    topic_id: str
    completed: bool = False
    time_spent: int = 0  # in seconds


@router.get("/topic/{topic_id}", response_model=LessonResponse)
def get_lesson_content(
    topic_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get lesson content for a specific topic"""
    
    # Get topic details
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Check if user has access to this topic (basic unlock logic)
    user_progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.topic_id == topic_id
    ).first()
    
    # For now, allow access to all topics for testing
    # TODO: Implement proper unlock logic based on previous topic completion
    
    # Check if we have stored lesson content
    stored_content = db.query(LessonContent).filter(LessonContent.topic_id == topic_id).first()
    
    if stored_content:
        # Return stored content
        lesson_content = {
            "why_it_matters": stored_content.why_it_matters,
            "key_ideas": stored_content.key_ideas,
            "examples": stored_content.examples,
            "pitfalls": stored_content.pitfalls,
            "recap": stored_content.recap
        }
        is_generated = False
    else:
        # Generate content using AI agent
        try:
            result = generate_lesson(
                user_id=str(current_user.id),
                topic_id=topic_id
            )
            
            if not result.get("success"):
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to generate lesson content: {result.get('error', 'Unknown error')}"
                )
            
            lesson_content = result.get("lesson_content", {})
            is_generated = True
            
            # Optionally store the generated content for future use
            # This could be done asynchronously or based on user preference
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating lesson content: {str(e)}"
            )
    
    # Get user progress for this topic
    progress_data = {}
    if user_progress:
        progress_data = {
            "status": user_progress.status.value,
            "best_score": user_progress.best_score,
            "attempts": user_progress.attempts,
            "time_spent": user_progress.time_spent or 0,
            "last_accessed": user_progress.last_accessed.isoformat() if user_progress.last_accessed else None
        }
    
    return LessonResponse(
        topic_id=topic_id,
        topic_name=topic.name,
        lesson_content=lesson_content,
        is_generated=is_generated,
        user_progress=progress_data
    )


@router.post("/progress/update")
def update_lesson_progress(
    progress_update: LessonProgressUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update user progress for a lesson"""
    
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
            status=ProgressStatus.IN_PROGRESS,
            attempts=0,
            time_spent=0
        )
        db.add(user_progress)
    
    # Update progress
    if progress_update.completed:
        user_progress.status = ProgressStatus.COMPLETED
    else:
        user_progress.status = ProgressStatus.IN_PROGRESS
    
    if progress_update.time_spent > 0:
        user_progress.time_spent = (user_progress.time_spent or 0) + progress_update.time_spent
    
    # Update last accessed timestamp
    from datetime import datetime
    user_progress.last_accessed = datetime.utcnow()
    
    db.commit()
    
    return {
        "success": True,
        "message": "Progress updated successfully",
        "status": user_progress.status.value,
        "total_time_spent": user_progress.time_spent
    }


@router.get("/topic/{topic_id}/next")
def get_next_topic(
    topic_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get the next topic in the learning sequence"""
    
    # Get current topic
    current_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not current_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Find next topic in the same section
    next_topic = db.query(Topic).filter(
        Topic.section_id == current_topic.section_id,
        Topic.order == current_topic.order + 1
    ).first()
    
    if next_topic:
        return {
            "next_topic": {
                "id": str(next_topic.id),
                "name": next_topic.name,
                "order": next_topic.order
            },
            "same_section": True
        }
    
    # If no next topic in section, find first topic of next section
    from app.models.curriculum import Section
    next_section = db.query(Section).filter(
        Section.level_id == current_topic.section.level_id,
        Section.order == current_topic.section.order + 1
    ).first()
    
    if next_section:
        first_topic_next_section = db.query(Topic).filter(
            Topic.section_id == next_section.id,
            Topic.order == 1
        ).first()
        
        if first_topic_next_section:
            return {
                "next_topic": {
                    "id": str(first_topic_next_section.id),
                    "name": first_topic_next_section.name,
                    "order": first_topic_next_section.order
                },
                "same_section": False,
                "next_section": {
                    "id": str(next_section.id),
                    "name": next_section.name,
                    "code": next_section.code
                }
            }
    
    # No next topic found
    return {
        "next_topic": None,
        "message": "You've completed this section!"
    }


@router.get("/topic/{topic_id}/previous")
def get_previous_topic(
    topic_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get the previous topic in the learning sequence"""
    
    # Get current topic
    current_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not current_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Find previous topic in the same section
    previous_topic = db.query(Topic).filter(
        Topic.section_id == current_topic.section_id,
        Topic.order == current_topic.order - 1
    ).first()
    
    if previous_topic:
        return {
            "previous_topic": {
                "id": str(previous_topic.id),
                "name": previous_topic.name,
                "order": previous_topic.order
            },
            "same_section": True
        }
    
    # If no previous topic in section, find last topic of previous section
    from app.models.curriculum import Section
    previous_section = db.query(Section).filter(
        Section.level_id == current_topic.section.level_id,
        Section.order == current_topic.section.order - 1
    ).first()
    
    if previous_section:
        last_topic_prev_section = db.query(Topic).filter(
            Topic.section_id == previous_section.id
        ).order_by(Topic.order.desc()).first()
        
        if last_topic_prev_section:
            return {
                "previous_topic": {
                    "id": str(last_topic_prev_section.id),
                    "name": last_topic_prev_section.name,
                    "order": last_topic_prev_section.order
                },
                "same_section": False,
                "previous_section": {
                    "id": str(previous_section.id),
                    "name": previous_section.name,
                    "code": previous_section.code
                }
            }
    
    # No previous topic found
    return {
        "previous_topic": None,
        "message": "This is the first topic!"
    }