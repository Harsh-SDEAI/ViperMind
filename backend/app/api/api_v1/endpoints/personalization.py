"""
Personalization API endpoints for ViperMind
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth import get_current_active_user
from app.db.base import get_db
from app.models.user import User
from app.models.personalization import UserProfile, LearningInteraction, PersonalizedContent, AdaptiveDifficulty
from app.models.assessment import Assessment
from app.models.progress import UserProgress
from app.agents.nodes.personalization_agent import PersonalizationAgent
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter()

class LearningStyleUpdate(BaseModel):
    interests: List[str] = []
    preferred_examples: str = "general"  # programming, games, science, business, etc.
    learning_pace_preference: str = "moderate"  # fast, moderate, thorough

class HintRequest(BaseModel):
    question_id: str
    topic: str
    difficulty: str = "medium"
    attempts: int = 0
    context: Dict[str, Any] = {}

class ContentRequest(BaseModel):
    topic: str
    content_type: str = "lesson"  # lesson, example, exercise
    current_level: str = "beginner"

@router.get("/profile")
def get_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get user's personalization profile"""
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    if not profile:
        # Create default profile
        profile = UserProfile(
            user_id=current_user.id,
            interests=[],
            adaptation_strategies={},
            personalization_data={}
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return {
        "user_id": str(profile.user_id),
        "primary_learning_style": profile.primary_learning_style.value if profile.primary_learning_style else "balanced",
        "content_preference": profile.content_preference.value if profile.content_preference else "examples_first",
        "learning_pace": profile.learning_pace.value if profile.learning_pace else "moderate",
        "interests": profile.interests or [],
        "difficulty_preference": profile.difficulty_preference,
        "engagement_style": profile.engagement_style,
        "learning_style_confidence": profile.learning_style_confidence,
        "adaptation_strategies": profile.adaptation_strategies or {},
        "last_analysis_date": profile.last_analysis_date.isoformat() if profile.last_analysis_date else None
    }

@router.post("/analyze-learning-style")
def analyze_learning_style(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Analyze user's learning style based on their behavior"""
    
    try:
        # Gather learning data
        learning_data = _gather_user_learning_data(str(current_user.id), db)
        
        # Use AI to analyze learning style
        personalization_agent = PersonalizationAgent()
        result = personalization_agent.detect_learning_style(str(current_user.id), learning_data)
        
        if result["success"]:
            # Update user profile
            profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
            if not profile:
                profile = UserProfile(user_id=current_user.id)
                db.add(profile)
            
            learning_style_data = result["learning_style"]
            profile.primary_learning_style = learning_style_data.get("primary_learning_style", "balanced")
            profile.content_preference = learning_style_data.get("content_preference", "examples_first")
            profile.learning_pace = learning_style_data.get("learning_pace", "moderate")
            profile.difficulty_preference = learning_style_data.get("difficulty_preference", "moderate")
            profile.engagement_style = learning_style_data.get("engagement_style", "progress_focused")
            profile.learning_style_confidence = learning_style_data.get("confidence_score", 0.5)
            profile.adaptation_strategies = learning_style_data.get("adaptation_strategies", {})
            profile.last_analysis_date = datetime.utcnow()
            profile.analysis_count = (profile.analysis_count or 0) + 1
            
            db.commit()
            
            return {
                "success": True,
                "learning_style": learning_style_data,
                "message": "Learning style analysis completed and profile updated"
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Analysis failed"),
                "fallback_used": True
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing learning style: {str(e)}")

@router.post("/update-preferences")
def update_learning_preferences(
    preferences: LearningStyleUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update user's learning preferences"""
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    # Update preferences
    profile.interests = preferences.interests
    profile.learning_pace = preferences.learning_pace_preference
    
    # Store additional preferences in personalization_data
    if not profile.personalization_data:
        profile.personalization_data = {}
    
    profile.personalization_data.update({
        "preferred_examples": preferences.preferred_examples,
        "updated_at": datetime.utcnow().isoformat()
    })
    
    db.commit()
    
    return {
        "success": True,
        "message": "Learning preferences updated successfully"
    }

@router.post("/hint")
def get_personalized_hint(
    hint_request: HintRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get a personalized hint based on user's learning style"""
    
    try:
        # Get user profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        
        # Prepare context
        context = {
            "learning_style": {
                "primary_learning_style": profile.primary_learning_style.value if profile and profile.primary_learning_style else "balanced",
                "content_preference": profile.content_preference.value if profile and profile.content_preference else "examples_first",
                "learning_pace": profile.learning_pace.value if profile and profile.learning_pace else "moderate"
            },
            "question": {
                "question_id": hint_request.question_id,
                "topic": hint_request.topic,
                "difficulty": hint_request.difficulty
            },
            "attempts": hint_request.attempts,
            "struggle_areas": _get_user_struggle_areas(str(current_user.id), db),
            **hint_request.context
        }
        
        # Generate personalized hint
        personalization_agent = PersonalizationAgent()
        result = personalization_agent.generate_personalized_hint(str(current_user.id), context)
        
        # Log interaction
        _log_learning_interaction(
            user_id=str(current_user.id),
            interaction_type="hint_request",
            content_id=hint_request.question_id,
            content_type="assessment_question",
            context_data=context,
            personalization_applied=result["success"],
            db=db
        )
        
        if result["success"]:
            return {
                "success": True,
                "hint": result["hint"],
                "personalized": True
            }
        else:
            return {
                "success": True,
                "hint": result.get("fallback_hint", {}),
                "personalized": False,
                "message": "Using fallback hint due to personalization error"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating hint: {str(e)}")

@router.post("/examples")
def get_personalized_examples(
    content_request: ContentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get personalized code examples based on user interests"""
    
    try:
        # Get user profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        user_interests = profile.interests if profile and profile.interests else []
        
        # Generate personalized examples
        personalization_agent = PersonalizationAgent()
        result = personalization_agent.generate_personalized_examples(
            str(current_user.id), 
            content_request.topic, 
            user_interests
        )
        
        # Log interaction
        _log_learning_interaction(
            user_id=str(current_user.id),
            interaction_type="example_request",
            content_id=content_request.topic,
            content_type="examples",
            context_data={"interests": user_interests},
            personalization_applied=result["success"],
            db=db
        )
        
        if result["success"]:
            # Store personalized content for future use
            _store_personalized_content(
                user_id=str(current_user.id),
                content_type="examples",
                topic=content_request.topic,
                generated_content=result["examples"],
                learning_style=profile.primary_learning_style.value if profile and profile.primary_learning_style else "balanced",
                db=db
            )
            
            return {
                "success": True,
                "examples": result["examples"],
                "personalized": True
            }
        else:
            return {
                "success": True,
                "examples": result.get("fallback_examples", {}),
                "personalized": False
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating examples: {str(e)}")

@router.post("/optimize-difficulty")
def optimize_difficulty(
    topic_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Optimize difficulty for a specific topic based on user performance"""
    
    try:
        # Gather performance data
        performance_data = _gather_performance_data(str(current_user.id), topic_id, db)
        
        # Use AI to optimize difficulty
        personalization_agent = PersonalizationAgent()
        result = personalization_agent.optimize_difficulty(str(current_user.id), performance_data)
        
        if result["success"]:
            # Update adaptive difficulty record
            adaptive_difficulty = db.query(AdaptiveDifficulty).filter(
                AdaptiveDifficulty.user_id == current_user.id,
                AdaptiveDifficulty.topic_id == topic_id
            ).first()
            
            if not adaptive_difficulty:
                adaptive_difficulty = AdaptiveDifficulty(
                    user_id=current_user.id,
                    topic_id=topic_id
                )
                db.add(adaptive_difficulty)
            
            optimization = result["optimization"]
            adjustment = optimization.get("difficulty_adjustment", 0.0)
            
            # Apply difficulty adjustment
            new_difficulty = max(0.0, min(1.0, adaptive_difficulty.current_difficulty + adjustment))
            adaptive_difficulty.current_difficulty = new_difficulty
            adaptive_difficulty.last_adjustment = adjustment
            adaptive_difficulty.adjustment_reason = optimization.get("reasoning", "")
            
            # Update performance tracking
            if performance_data.get("recent_scores"):
                adaptive_difficulty.recent_scores = performance_data["recent_scores"][-10:]  # Keep last 10
                adaptive_difficulty.success_rate = sum(s >= 70 for s in adaptive_difficulty.recent_scores) / len(adaptive_difficulty.recent_scores)
            
            db.commit()
            
            return {
                "success": True,
                "optimization": optimization,
                "new_difficulty": new_difficulty,
                "adjustment_applied": adjustment
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Optimization failed")
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error optimizing difficulty: {str(e)}")

@router.get("/adaptive-content/{topic}")
def get_adaptive_content(
    topic: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get adaptive content for a specific topic"""
    
    try:
        # Get user profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        
        # Check for existing personalized content
        existing_content = db.query(PersonalizedContent).filter(
            PersonalizedContent.user_id == current_user.id,
            PersonalizedContent.topic == topic,
            PersonalizedContent.content_type == "lesson",
            PersonalizedContent.is_active == True
        ).first()
        
        if existing_content and existing_content.avg_effectiveness and existing_content.avg_effectiveness > 0.7:
            # Use existing high-quality personalized content
            existing_content.usage_count += 1
            existing_content.last_used = datetime.utcnow()
            db.commit()
            
            return {
                "success": True,
                "content": existing_content.generated_content,
                "personalized": True,
                "source": "cached"
            }
        
        # Generate new adaptive content
        content_request = {
            "topic": topic,
            "current_level": current_user.current_level.value,
            "learning_style": {
                "primary_learning_style": profile.primary_learning_style.value if profile and profile.primary_learning_style else "balanced",
                "content_preference": profile.content_preference.value if profile and profile.content_preference else "examples_first"
            },
            "interests": profile.interests if profile and profile.interests else []
        }
        
        personalization_agent = PersonalizationAgent()
        result = personalization_agent.generate_adaptive_content(str(current_user.id), content_request)
        
        if result["success"]:
            # Store new personalized content
            _store_personalized_content(
                user_id=str(current_user.id),
                content_type="lesson",
                topic=topic,
                generated_content=result["content"],
                learning_style=profile.primary_learning_style.value if profile and profile.primary_learning_style else "balanced",
                db=db
            )
            
            return {
                "success": True,
                "content": result["content"],
                "personalized": True,
                "source": "generated"
            }
        else:
            return {
                "success": True,
                "content": result.get("fallback_content", {}),
                "personalized": False,
                "source": "fallback"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating adaptive content: {str(e)}")

@router.get("/effectiveness-stats")
def get_personalization_effectiveness(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get statistics on personalization effectiveness"""
    
    # Get personalized content usage
    personalized_content = db.query(PersonalizedContent).filter(
        PersonalizedContent.user_id == current_user.id
    ).all()
    
    # Get learning interactions
    interactions = db.query(LearningInteraction).filter(
        LearningInteraction.user_id == current_user.id,
        LearningInteraction.personalization_applied == True
    ).all()
    
    # Calculate effectiveness metrics
    total_personalized_content = len(personalized_content)
    avg_effectiveness = sum(c.avg_effectiveness for c in personalized_content if c.avg_effectiveness) / max(1, len([c for c in personalized_content if c.avg_effectiveness]))
    
    personalized_interactions = len(interactions)
    avg_interaction_effectiveness = sum(i.effectiveness_score for i in interactions if i.effectiveness_score) / max(1, len([i for i in interactions if i.effectiveness_score]))
    
    return {
        "total_personalized_content": total_personalized_content,
        "avg_content_effectiveness": round(avg_effectiveness, 2) if avg_effectiveness else 0,
        "personalized_interactions": personalized_interactions,
        "avg_interaction_effectiveness": round(avg_interaction_effectiveness, 2) if avg_interaction_effectiveness else 0,
        "content_breakdown": {
            content_type: len([c for c in personalized_content if c.content_type == content_type])
            for content_type in set(c.content_type for c in personalized_content)
        }
    }

# Helper functions

def _gather_user_learning_data(user_id: str, db: Session) -> Dict[str, Any]:
    """Gather user's learning behavior data for analysis"""
    
    # Get recent assessments
    recent_assessments = db.query(Assessment).filter(
        Assessment.user_id == user_id,
        Assessment.submitted_at.isnot(None)
    ).order_by(Assessment.submitted_at.desc()).limit(20).all()
    
    # Get progress data
    progress_data = db.query(UserProgress).filter(
        UserProgress.user_id == user_id
    ).all()
    
    # Calculate metrics
    avg_lesson_time = sum(p.time_spent for p in progress_data) / max(1, len(progress_data)) / 60  # minutes
    
    assessment_performance = {
        "total_assessments": len(recent_assessments),
        "pass_rate": sum(1 for a in recent_assessments if a.passed) / max(1, len(recent_assessments)),
        "avg_score": sum(a.score for a in recent_assessments if a.score) / max(1, len([a for a in recent_assessments if a.score]))
    }
    
    return {
        "avg_lesson_time": avg_lesson_time,
        "assessment_performance": assessment_performance,
        "interaction_patterns": {},  # Would be populated from learning_interactions table
        "content_preferences": {},   # Would be analyzed from user behavior
        "struggle_areas": _get_user_struggle_areas(user_id, db),
        "success_patterns": []       # Would be analyzed from successful interactions
    }

def _get_user_struggle_areas(user_id: str, db: Session) -> List[str]:
    """Get areas where user struggles based on assessment performance"""
    
    failed_assessments = db.query(Assessment).filter(
        Assessment.user_id == user_id,
        Assessment.passed == False
    ).all()
    
    struggle_areas = []
    for assessment in failed_assessments:
        if assessment.user_answers:
            for answer in assessment.user_answers:
                if not answer.get("is_correct", True):
                    # Extract concepts from failed questions
                    struggle_areas.append("Python Fundamentals")  # Simplified
    
    return list(set(struggle_areas))

def _gather_performance_data(user_id: str, topic_id: str, db: Session) -> Dict[str, Any]:
    """Gather performance data for difficulty optimization"""
    
    # Get recent scores for this topic
    recent_assessments = db.query(Assessment).filter(
        Assessment.user_id == user_id,
        Assessment.target_id == topic_id,
        Assessment.submitted_at.isnot(None)
    ).order_by(Assessment.submitted_at.desc()).limit(10).all()
    
    recent_scores = [a.score for a in recent_assessments if a.score is not None]
    
    return {
        "recent_scores": recent_scores,
        "time_patterns": {
            "avg_time_per_question": 30  # Simplified
        },
        "engagement_metrics": {
            "completion_rate": 85,  # Simplified
            "help_requests": 2,
            "skip_rate": 5
        }
    }

def _log_learning_interaction(user_id: str, interaction_type: str, content_id: str, 
                            content_type: str, context_data: Dict[str, Any], 
                            personalization_applied: bool, db: Session):
    """Log a learning interaction for analysis"""
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    interaction = LearningInteraction(
        user_id=user_id,
        user_profile_id=profile.id if profile else None,
        interaction_type=interaction_type,
        content_id=content_id,
        content_type=content_type,
        context_data=context_data,
        personalization_applied=personalization_applied,
        personalization_type="ai_generated" if personalization_applied else None
    )
    
    db.add(interaction)
    db.commit()

def _store_personalized_content(user_id: str, content_type: str, topic: str, 
                               generated_content: Dict[str, Any], learning_style: str, db: Session):
    """Store personalized content for future use"""
    
    personalized_content = PersonalizedContent(
        user_id=user_id,
        content_type=content_type,
        topic=topic,
        learning_style_applied=learning_style,
        generated_content=generated_content,
        usage_count=1,
        last_used=datetime.utcnow()
    )
    
    db.add(personalized_content)
    db.commit()