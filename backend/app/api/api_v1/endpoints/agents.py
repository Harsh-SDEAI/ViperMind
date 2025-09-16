"""
Agent API endpoints for ViperMind LangGraph agents
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth import get_current_active_user
from app.db.base import get_db
from app.models.user import User
from app.agents.vipermind_agent import (
    vipermind_agent,
    generate_lesson,
    create_quiz,
    evaluate_assessment,
    explain_concept,
    analyze_progress,
    generate_hint
)
from pydantic import BaseModel

router = APIRouter()


# Request/Response models
class LessonRequest(BaseModel):
    topic_id: str


class QuizRequest(BaseModel):
    topic_id: str


class AssessmentEvaluationRequest(BaseModel):
    assessment: Dict[str, Any]
    user_answers: List[Dict[str, Any]]


class ConceptExplanationRequest(BaseModel):
    concept: str


class HintRequest(BaseModel):
    question: str
    user_answer: str = None


class AgentRequest(BaseModel):
    request_type: str
    data: Dict[str, Any] = {}


@router.post("/lesson/generate")
def generate_lesson_content(
    request: LessonRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Generate personalized lesson content for a topic"""
    
    try:
        result = generate_lesson(
            user_id=str(current_user.id),
            topic_id=request.topic_id
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to generate lesson")
            )
        
        return {
            "success": True,
            "lesson_content": result.get("lesson_content"),
            "topic_info": result.get("topic_info"),
            "agent": result.get("agent")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {str(e)}"
        )


@router.post("/quiz/generate")
def generate_quiz_questions(
    request: QuizRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Generate a personalized quiz for a topic"""
    
    try:
        result = create_quiz(
            user_id=str(current_user.id),
            topic_id=request.topic_id
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to generate quiz")
            )
        
        return {
            "success": True,
            "assessment": result.get("assessment"),
            "agent": result.get("agent")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {str(e)}"
        )


@router.post("/assessment/evaluate")
def evaluate_user_assessment(
    request: AssessmentEvaluationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Evaluate an assessment submission and provide feedback"""
    
    try:
        result = evaluate_assessment(
            user_id=str(current_user.id),
            assessment=request.assessment,
            user_answers=request.user_answers
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to evaluate assessment")
            )
        
        return {
            "success": True,
            "assessment_results": result.get("assessment_results"),
            "agent": result.get("agent")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {str(e)}"
        )


@router.post("/concept/explain")
def explain_programming_concept(
    request: ConceptExplanationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get a personalized explanation for a programming concept"""
    
    try:
        result = explain_concept(
            user_id=str(current_user.id),
            concept=request.concept
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to generate explanation")
            )
        
        return {
            "success": True,
            "explanation": result.get("explanation"),
            "concept": result.get("concept"),
            "agent": result.get("agent")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {str(e)}"
        )


@router.get("/progress/analyze")
def analyze_user_progress(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Analyze user's learning progress and patterns"""
    
    try:
        result = analyze_progress(user_id=str(current_user.id))
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to analyze progress")
            )
        
        return {
            "success": True,
            "learning_patterns": result.get("learning_patterns"),
            "pattern_insights": result.get("pattern_insights"),
            "agent": result.get("agent")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {str(e)}"
        )


@router.post("/hint/generate")
def generate_learning_hint(
    request: HintRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Generate a helpful hint for a question"""
    
    try:
        result = generate_hint(
            user_id=str(current_user.id),
            question=request.question,
            user_answer=request.user_answer
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to generate hint")
            )
        
        return {
            "success": True,
            "hint": result.get("hint"),
            "question": result.get("question"),
            "agent": result.get("agent")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {str(e)}"
        )


@router.post("/invoke")
def invoke_agent_directly(
    request: AgentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Direct agent invocation for advanced use cases"""
    
    try:
        # Prepare the request with user ID
        agent_request = {
            "user_id": str(current_user.id),
            "request_type": request.request_type,
            **request.data
        }
        
        result = vipermind_agent.invoke_sync(agent_request)
        
        return {
            "success": result.get("success", False),
            "result": result,
            "agent": result.get("agent")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {str(e)}"
        )


@router.get("/status")
def get_agent_status(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get the status of the agent system"""
    
    return {
        "success": True,
        "status": "operational",
        "agents": {
            "tutor_agent": "available",
            "assessment_agent": "available", 
            "content_agent": "available",
            "progress_agent": "available"
        },
        "capabilities": [
            "lesson_generation",
            "quiz_creation",
            "assessment_evaluation",
            "concept_explanation",
            "progress_analysis",
            "hint_generation",
            "content_personalization"
        ]
    }