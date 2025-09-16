"""
Remedial Content API endpoints for ViperMind
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth import get_current_active_user
from app.db.base import get_db
from app.models.user import User
from app.models.assessment import Assessment, AssessmentType
from app.models.remedial import RemedialContent, RemedialCard, ReviewSchedule, RemedialType, RemedialStatus
from app.schemas.remedial import (
    RemedialContent as RemedialContentSchema,
    RemedialCard as RemedialCardSchema,
    ReviewSchedule as ReviewScheduleSchema,
    RemedialProgress,
    RemedialAssignment
)
from app.agents.nodes.remedial_agent import RemedialAgent
from datetime import datetime, timedelta
import uuid

router = APIRouter()

@router.post("/generate")
def generate_remedial_content(
    assessment_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Generate remedial content based on failed assessment"""
    
    # Get the assessment
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    if assessment.passed:
        raise HTTPException(status_code=400, detail="Remedial content not needed for passed assessments")
    
    # Check if remedial content already exists
    existing_remedial = db.query(RemedialContent).filter(
        RemedialContent.assessment_id == assessment_id,
        RemedialContent.user_id == current_user.id
    ).first()
    
    if existing_remedial:
        return {"message": "Remedial content already exists", "remedial_id": str(existing_remedial.id)}
    
    # Determine remedial type based on assessment type and score
    remedial_type = _determine_remedial_type(assessment)
    
    # Extract weak concepts from assessment answers
    weak_concepts = _extract_weak_concepts(assessment)
    
    # Generate remedial content using AI agent
    remedial_agent = RemedialAgent()
    
    try:
        if remedial_type == RemedialType.MINI_EXPLAINER:
            result = remedial_agent.generate_mini_explainer(
                str(current_user.id),
                {
                    "topic_name": "Python Topic",  # Would get from curriculum
                    "score": assessment.score
                },
                weak_concepts
            )
            
            if result["success"]:
                content_data = result["content"]
                remedial_content = RemedialContent(
                    user_id=current_user.id,
                    assessment_id=assessment.id,
                    target_id=assessment.target_id,
                    type=RemedialType.MINI_EXPLAINER,
                    title=content_data["title"],
                    content=content_data["explanation"],
                    ai_generated_content=content_data,
                    weak_concepts=weak_concepts
                )
                
                db.add(remedial_content)
                db.commit()
                db.refresh(remedial_content)
                
                return {
                    "success": True,
                    "remedial_id": str(remedial_content.id),
                    "type": "mini_explainer",
                    "content": content_data
                }
        
        elif remedial_type == RemedialType.REMEDIAL_CARD:
            result = remedial_agent.generate_remedial_cards(
                str(current_user.id),
                {
                    "section_name": "Python Section",  # Would get from curriculum
                    "score": assessment.score
                },
                weak_concepts,
                cards_per_concept=2
            )
            
            if result["success"]:
                # Create main remedial content
                remedial_content = RemedialContent(
                    user_id=current_user.id,
                    assessment_id=assessment.id,
                    target_id=assessment.target_id,
                    type=RemedialType.REMEDIAL_CARD,
                    title=f"Remedial Cards - {len(result['cards'])} cards",
                    content=f"Complete {len(result['cards'])} remedial cards to strengthen your understanding.",
                    weak_concepts=weak_concepts
                )
                
                db.add(remedial_content)
                db.flush()
                
                # Create individual cards
                cards_created = []
                for card_data in result["cards"]:
                    remedial_card = RemedialCard(
                        remedial_content_id=remedial_content.id,
                        topic_concept=card_data["concept"],
                        explanation=card_data["explanation"],
                        code_example=card_data.get("code_example"),
                        practice_question=card_data.get("practice_question"),
                        hints=card_data.get("hints", [])
                    )
                    db.add(remedial_card)
                    cards_created.append(remedial_card)
                
                db.commit()
                
                return {
                    "success": True,
                    "remedial_id": str(remedial_content.id),
                    "type": "remedial_cards",
                    "cards_count": len(cards_created),
                    "cards": result["cards"]
                }
        
        elif remedial_type == RemedialType.REVIEW_WEEK:
            result = remedial_agent.generate_review_schedule(
                str(current_user.id),
                {
                    "level_name": "Python Level",  # Would get from curriculum
                    "score": assessment.score
                },
                weak_concepts
            )
            
            if result["success"]:
                # Create remedial content
                remedial_content = RemedialContent(
                    user_id=current_user.id,
                    assessment_id=assessment.id,
                    target_id=assessment.target_id,
                    type=RemedialType.REVIEW_WEEK,
                    title=result["schedule"]["title"],
                    content=result["schedule"]["overview"],
                    ai_generated_content=result["schedule"],
                    weak_concepts=weak_concepts
                )
                
                db.add(remedial_content)
                db.flush()
                
                # Create review schedule
                review_schedule = ReviewSchedule(
                    user_id=current_user.id,
                    assessment_id=assessment.id,
                    scheduled_date=datetime.utcnow() + timedelta(days=1),
                    review_duration_days=7,
                    review_topics=weak_concepts,
                    review_materials=result["schedule"]
                )
                
                db.add(review_schedule)
                db.commit()
                
                return {
                    "success": True,
                    "remedial_id": str(remedial_content.id),
                    "review_schedule_id": str(review_schedule.id),
                    "type": "review_week",
                    "schedule": result["schedule"]
                }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error generating remedial content: {str(e)}")
    
    raise HTTPException(status_code=500, detail="Failed to generate remedial content")


@router.get("/user/{user_id}")
def get_user_remedial_content(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get all remedial content for a user"""
    
    # Only allow users to see their own remedial content
    if str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    remedial_content = db.query(RemedialContent).filter(
        RemedialContent.user_id == user_id
    ).order_by(RemedialContent.created_at.desc()).all()
    
    result = []
    for content in remedial_content:
        content_dict = {
            "id": str(content.id),
            "assessment_id": str(content.assessment_id),
            "target_id": str(content.target_id),
            "type": content.type.value,
            "title": content.title,
            "content": content.content,
            "status": content.status.value,
            "weak_concepts": content.weak_concepts,
            "completion_percentage": content.completion_percentage,
            "time_spent": content.time_spent,
            "created_at": content.created_at.isoformat(),
            "started_at": content.started_at.isoformat() if content.started_at else None,
            "completed_at": content.completed_at.isoformat() if content.completed_at else None
        }
        
        # Add cards if it's a remedial card type
        if content.type == RemedialType.REMEDIAL_CARD:
            cards = db.query(RemedialCard).filter(
                RemedialCard.remedial_content_id == content.id
            ).all()
            content_dict["cards"] = [
                {
                    "id": str(card.id),
                    "topic_concept": card.topic_concept,
                    "explanation": card.explanation,
                    "code_example": card.code_example,
                    "practice_question": card.practice_question,
                    "hints": card.hints,
                    "is_completed": card.is_completed,
                    "attempts": card.attempts,
                    "time_spent": card.time_spent
                } for card in cards
            ]
        
        result.append(content_dict)
    
    return {"remedial_content": result}


@router.get("/{remedial_id}")
def get_remedial_content(
    remedial_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get specific remedial content"""
    
    remedial_content = db.query(RemedialContent).filter(
        RemedialContent.id == remedial_id,
        RemedialContent.user_id == current_user.id
    ).first()
    
    if not remedial_content:
        raise HTTPException(status_code=404, detail="Remedial content not found")
    
    # Mark as started if not already
    if not remedial_content.started_at:
        remedial_content.started_at = datetime.utcnow()
        remedial_content.status = RemedialStatus.IN_PROGRESS
        db.commit()
    
    result = {
        "id": str(remedial_content.id),
        "type": remedial_content.type.value,
        "title": remedial_content.title,
        "content": remedial_content.content,
        "ai_generated_content": remedial_content.ai_generated_content,
        "weak_concepts": remedial_content.weak_concepts,
        "status": remedial_content.status.value,
        "completion_percentage": remedial_content.completion_percentage,
        "time_spent": remedial_content.time_spent
    }
    
    # Add cards if it's a remedial card type
    if remedial_content.type == RemedialType.REMEDIAL_CARD:
        cards = db.query(RemedialCard).filter(
            RemedialCard.remedial_content_id == remedial_content.id
        ).order_by(RemedialCard.created_at).all()
        
        result["cards"] = [
            {
                "id": str(card.id),
                "topic_concept": card.topic_concept,
                "explanation": card.explanation,
                "code_example": card.code_example,
                "practice_question": card.practice_question,
                "hints": card.hints,
                "is_completed": card.is_completed,
                "attempts": card.attempts,
                "time_spent": card.time_spent
            } for card in cards
        ]
    
    return result


@router.post("/{remedial_id}/complete")
def complete_remedial_content(
    remedial_id: str,
    time_spent: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Mark remedial content as completed"""
    
    remedial_content = db.query(RemedialContent).filter(
        RemedialContent.id == remedial_id,
        RemedialContent.user_id == current_user.id
    ).first()
    
    if not remedial_content:
        raise HTTPException(status_code=404, detail="Remedial content not found")
    
    # Update completion status
    remedial_content.status = RemedialStatus.COMPLETED
    remedial_content.completion_percentage = 100.0
    remedial_content.completed_at = datetime.utcnow()
    remedial_content.time_spent += time_spent
    
    db.commit()
    
    return {
        "success": True,
        "message": "Remedial content completed",
        "can_retake_assessment": True
    }


@router.post("/cards/{card_id}/complete")
def complete_remedial_card(
    card_id: str,
    time_spent: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Mark a remedial card as completed"""
    
    card = db.query(RemedialCard).join(RemedialContent).filter(
        RemedialCard.id == card_id,
        RemedialContent.user_id == current_user.id
    ).first()
    
    if not card:
        raise HTTPException(status_code=404, detail="Remedial card not found")
    
    # Update card completion
    card.is_completed = True
    card.time_spent += time_spent
    card.attempts += 1
    
    # Check if all cards in the remedial content are completed
    remedial_content = card.remedial_content
    all_cards = db.query(RemedialCard).filter(
        RemedialCard.remedial_content_id == remedial_content.id
    ).all()
    
    completed_cards = sum(1 for c in all_cards if c.is_completed)
    total_cards = len(all_cards)
    
    # Update remedial content progress
    remedial_content.completion_percentage = (completed_cards / total_cards) * 100
    remedial_content.time_spent += time_spent
    
    if completed_cards == total_cards:
        remedial_content.status = RemedialStatus.COMPLETED
        remedial_content.completed_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "success": True,
        "card_completed": True,
        "progress": {
            "completed_cards": completed_cards,
            "total_cards": total_cards,
            "completion_percentage": remedial_content.completion_percentage,
            "all_completed": completed_cards == total_cards
        }
    }


@router.get("/progress/{user_id}")
def get_remedial_progress(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get user's overall remedial progress"""
    
    if str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    remedial_content = db.query(RemedialContent).filter(
        RemedialContent.user_id == user_id
    ).all()
    
    total_assigned = len(remedial_content)
    completed = sum(1 for c in remedial_content if c.status == RemedialStatus.COMPLETED)
    in_progress = sum(1 for c in remedial_content if c.status == RemedialStatus.IN_PROGRESS)
    
    # Collect all weak concepts
    all_weak_concepts = []
    for content in remedial_content:
        all_weak_concepts.extend(content.weak_concepts or [])
    
    # Remove duplicates and count frequency
    concept_counts = {}
    for concept in all_weak_concepts:
        concept_counts[concept] = concept_counts.get(concept, 0) + 1
    
    # Sort by frequency
    weak_concepts = sorted(concept_counts.keys(), key=lambda x: concept_counts[x], reverse=True)
    
    total_time_spent = sum(c.time_spent for c in remedial_content)
    overall_completion = (completed / total_assigned * 100) if total_assigned > 0 else 100
    
    return {
        "total_assigned": total_assigned,
        "completed": completed,
        "in_progress": in_progress,
        "completion_percentage": overall_completion,
        "time_spent_total": total_time_spent,
        "weak_concepts": weak_concepts[:10],  # Top 10 most frequent
        "concept_frequency": concept_counts
    }


def _determine_remedial_type(assessment: Assessment) -> RemedialType:
    """Determine what type of remedial content to generate"""
    if assessment.type == AssessmentType.QUIZ and assessment.score < 70:
        return RemedialType.MINI_EXPLAINER
    elif assessment.type == AssessmentType.SECTION_TEST and assessment.score < 75:
        return RemedialType.REMEDIAL_CARD
    elif assessment.type == AssessmentType.LEVEL_FINAL and assessment.score < 80:
        return RemedialType.REVIEW_WEEK
    else:
        return RemedialType.MINI_EXPLAINER  # Default


def _extract_weak_concepts(assessment: Assessment) -> List[str]:
    """Extract weak concepts from assessment answers"""
    weak_concepts = []
    
    if assessment.user_answers:
        for answer in assessment.user_answers:
            if not answer.get("is_correct", True):
                # Extract concept tags from the question
                question_data = None
                if assessment.questions_data:
                    for q in assessment.questions_data:
                        if q.get("question") == answer.get("question"):
                            question_data = q
                            break
                
                if question_data and question_data.get("concept_tags"):
                    weak_concepts.extend(question_data["concept_tags"])
    
    # Remove duplicates and return
    return list(set(weak_concepts)) if weak_concepts else ["Python Fundamentals"]