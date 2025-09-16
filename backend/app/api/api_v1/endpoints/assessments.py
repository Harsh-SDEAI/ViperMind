"""
Assessment API endpoints for ViperMind
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth import get_current_active_user
from app.db.base import get_db
from app.models.user import User
from app.models.curriculum import Topic, Section, Level
from app.models.assessment import Assessment, AssessmentType
from app.models.progress import UserProgress, ProgressStatus
from app.agents.vipermind_agent import create_quiz, evaluate_assessment
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class QuestionOption(BaseModel):
    text: str
    is_correct: bool


class Question(BaseModel):
    id: str
    question: str
    options: List[str]
    correct_answer: int
    explanation: str
    code_snippet: Optional[str] = None
    concept_tags: List[str] = []
    difficulty: str = "medium"


class AssessmentRequest(BaseModel):
    target_id: str  # topic_id, section_id, or level_id
    assessment_type: str  # "quiz", "section_test", "level_final"
    difficulty: str = "medium"
    question_count: int = 5


class AssessmentResponse(BaseModel):
    assessment_id: str
    target_id: str
    target_name: str
    assessment_type: str
    questions: List[Question]
    time_limit: int  # in minutes
    attempt_number: int
    max_attempts: int
    instructions: str


class AnswerSubmission(BaseModel):
    question_id: str
    selected_answer: int


class AssessmentSubmission(BaseModel):
    assessment_id: str
    answers: List[AnswerSubmission]
    time_taken: int  # in seconds


class AssessmentResult(BaseModel):
    assessment_id: str
    score: float
    passed: bool
    total_questions: int
    correct_answers: int
    time_taken: int
    feedback: str
    question_results: List[Dict[str, Any]]
    next_steps: Dict[str, Any]


@router.post("/generate", response_model=AssessmentResponse)
def generate_assessment(
    request: AssessmentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Generate a new assessment (quiz, section test, or level final)"""
    
    # Validate assessment type
    valid_types = ["quiz", "section_test", "level_final"]
    if request.assessment_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid assessment type. Must be one of: {valid_types}"
        )
    
    # Get target details and validate access
    target_name = ""
    if request.assessment_type == "quiz":
        topic = db.query(Topic).filter(Topic.id == request.target_id).first()
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        target_name = topic.name
        
    elif request.assessment_type == "section_test":
        section = db.query(Section).filter(Section.id == request.target_id).first()
        if not section:
            raise HTTPException(status_code=404, detail="Section not found")
        target_name = section.name
        
    elif request.assessment_type == "level_final":
        level = db.query(Level).filter(Level.id == request.target_id).first()
        if not level:
            raise HTTPException(status_code=404, detail="Level not found")
        target_name = level.name
    
    # Check existing attempts
    existing_assessments = db.query(Assessment).filter(
        Assessment.user_id == current_user.id,
        Assessment.type == AssessmentType(request.assessment_type),
        Assessment.target_id == request.target_id,
        Assessment.submitted_at.isnot(None)  # Only count completed assessments
    ).all()
    
    existing_attempts = len(existing_assessments)
    
    # Set attempt limits
    max_attempts = {
        "quiz": 999,  # Unlimited
        "section_test": 2,  # 1 initial + 1 retake
        "level_final": 2   # 1 initial + 1 retake
    }
    
    if existing_attempts >= max_attempts[request.assessment_type]:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum attempts ({max_attempts[request.assessment_type]}) reached for this {request.assessment_type}"
        )
    
    # Generate questions using AI agent
    try:
        if request.assessment_type == "quiz":
            result = create_quiz(
                user_id=str(current_user.id),
                topic_id=request.target_id
            )
        else:
            # For section tests and level finals, use the assessment agent directly
            from app.agents.vipermind_agent import vipermind_agent
            result = vipermind_agent.invoke_sync({
                "user_id": str(current_user.id),
                "request_type": "generate_test" if request.assessment_type == "section_test" else "generate_final",
                "target_id": request.target_id,
                "difficulty": request.difficulty,
                "question_count": request.question_count
            })
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate assessment: {result.get('error', 'Unknown error')}"
            )
        
        # Extract questions from result
        questions_data = result.get("questions", [])
        if not questions_data:
            raise HTTPException(
                status_code=500,
                detail="No questions generated"
            )
        
        # Create assessment record
        assessment = Assessment(
            user_id=current_user.id,
            type=AssessmentType(request.assessment_type),
            target_id=request.target_id,
            attempt_number=existing_attempts + 1,
            ai_generated=True,
            difficulty_level=request.difficulty,
            questions_data=questions_data,
            created_at=datetime.utcnow()
        )
        
        db.add(assessment)
        db.flush()
        
        # Format questions for response
        formatted_questions = []
        for i, q in enumerate(questions_data):
            formatted_questions.append(Question(
                id=f"{assessment.id}_{i}",
                question=q.get("question", ""),
                options=q.get("options", []),
                correct_answer=q.get("correct_answer", 0),
                explanation=q.get("explanation", ""),
                code_snippet=q.get("code_snippet"),
                concept_tags=q.get("concept_tags", []),
                difficulty=q.get("difficulty", request.difficulty)
            ))
        
        # Set time limits
        time_limits = {
            "quiz": 15,  # 15 minutes
            "section_test": 30,  # 30 minutes
            "level_final": 60   # 60 minutes
        }
        
        # Set instructions
        instructions = {
            "quiz": f"This quiz covers the topic '{target_name}'. You have unlimited attempts to improve your understanding.",
            "section_test": f"This is a section test for '{target_name}'. You have one attempt, so take your time and think carefully.",
            "level_final": f"This is the final exam for '{target_name}' level. You have one attempt. Good luck!"
        }
        
        db.commit()
        
        return AssessmentResponse(
            assessment_id=str(assessment.id),
            target_id=request.target_id,
            target_name=target_name,
            assessment_type=request.assessment_type,
            questions=formatted_questions,
            time_limit=time_limits[request.assessment_type],
            attempt_number=assessment.attempt_number,
            max_attempts=max_attempts[request.assessment_type],
            instructions=instructions[request.assessment_type]
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error generating assessment: {str(e)}"
        )


@router.post("/submit", response_model=AssessmentResult)
def submit_assessment(
    submission: AssessmentSubmission,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Submit assessment answers and get results"""
    
    # Get assessment
    assessment = db.query(Assessment).filter(
        Assessment.id == submission.assessment_id,
        Assessment.user_id == current_user.id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    if assessment.submitted_at:
        raise HTTPException(status_code=400, detail="Assessment already submitted")
    
    # Process answers
    questions_data = assessment.questions_data
    user_answers = []
    correct_count = 0
    question_results = []
    
    # Create answer lookup
    answer_lookup = {ans.question_id: ans.selected_answer for ans in submission.answers}
    
    for i, question in enumerate(questions_data):
        question_id = f"{assessment.id}_{i}"
        user_answer = answer_lookup.get(question_id, -1)
        correct_answer = question.get("correct_answer", 0)
        is_correct = user_answer == correct_answer
        
        if is_correct:
            correct_count += 1
        
        user_answers.append({
            "question_id": question_id,
            "question": question.get("question", ""),
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": question.get("explanation", "")
        })
        
        question_results.append({
            "question_id": question_id,
            "question": question.get("question", ""),
            "options": question.get("options", []),
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": question.get("explanation", ""),
            "concept_tags": question.get("concept_tags", [])
        })
    
    # Calculate score
    total_questions = len(questions_data)
    score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
    
    # Determine pass/fail based on assessment type
    pass_thresholds = {
        "quiz": 70.0,
        "section_test": 75.0,
        "level_final": 80.0
    }
    
    passed = score >= pass_thresholds.get(assessment.type.value, 70.0)
    
    # Update assessment record
    assessment.score = score
    assessment.passed = passed
    assessment.time_taken = submission.time_taken
    assessment.user_answers = user_answers
    assessment.submitted_at = datetime.utcnow()
    
    # Generate AI feedback
    try:
        feedback_result = evaluate_assessment(
            user_id=str(current_user.id),
            assessment={
                "type": assessment.type.value,
                "target_id": assessment.target_id,
                "score": score,
                "passed": passed,
                "questions": len(questions_data),
                "correct": correct_count
            },
            user_answers=user_answers
        )
        
        ai_feedback = feedback_result.get("feedback", "Great job on completing the assessment!")
        assessment.ai_feedback = ai_feedback
        
    except Exception as e:
        print(f"Error generating AI feedback: {e}")
        ai_feedback = "Assessment completed successfully!"
    
    # Determine next steps
    next_steps = {}
    if passed:
        if assessment.type.value == "quiz":
            next_steps = {
                "message": "Great job! You can now proceed to the next topic.",
                "action": "continue_learning",
                "unlock_next": True
            }
        elif assessment.type.value == "section_test":
            next_steps = {
                "message": "Excellent! You've completed this section. Move on to the next section.",
                "action": "next_section",
                "unlock_next": True
            }
        elif assessment.type.value == "level_final":
            next_steps = {
                "message": "Congratulations! You've completed this level. Advance to the next level.",
                "action": "next_level",
                "unlock_next": True
            }
    else:
        if assessment.type.value == "quiz":
            next_steps = {
                "message": "Review the material and try again. You can retake this quiz unlimited times.",
                "action": "review_and_retake",
                "unlock_next": False
            }
        else:
            next_steps = {
                "message": "You need to review the material before you can retake this assessment.",
                "action": "review_required",
                "unlock_next": False,
                "review_topics": [q["concept_tags"] for q in question_results if not q["is_correct"]]
            }
    
    # Update progress and best scores
    from app.api.api_v1.endpoints.progress import _check_and_update_unlocks, _check_level_advancement
    
    # Always update best score tracking regardless of assessment type
    if assessment.type == AssessmentType.QUIZ:
        # Update topic progress
        user_progress = db.query(UserProgress).filter(
            UserProgress.user_id == current_user.id,
            UserProgress.topic_id == assessment.target_id
        ).first()
        
        if user_progress:
            # Update best score if this is better
            if user_progress.best_score is None or score > user_progress.best_score:
                user_progress.best_score = score
            
            # Update status if passed
            if passed:
                user_progress.status = ProgressStatus.COMPLETED
            
            user_progress.attempts += 1
            user_progress.last_attempt_at = datetime.utcnow()
            user_progress.last_accessed = datetime.utcnow()
        
        # Check for unlocks and level advancement only if passed
        if passed:
            unlocks = _check_and_update_unlocks(str(current_user.id), db)
            level_advancement = _check_level_advancement(str(current_user.id), db)
            
            # Update next steps if content was unlocked
            if unlocks:
                next_steps["unlocked_content"] = unlocks
            if level_advancement.get("can_advance"):
                next_steps["level_advancement"] = level_advancement
    
    # For section tests and level finals, update level progress
    elif assessment.type in [AssessmentType.SECTION_TEST, AssessmentType.LEVEL_FINAL]:
        from app.models.progress import LevelProgress
        
        # Get or create level progress
        level_progress = db.query(LevelProgress).filter(
            LevelProgress.user_id == current_user.id,
            LevelProgress.level_id == assessment.target_id if assessment.type == AssessmentType.LEVEL_FINAL else None
        ).first()
        
        if level_progress:
            if assessment.type == AssessmentType.SECTION_TEST:
                # Update section test average (simplified - would need section mapping)
                if level_progress.section_test_average is None or score > level_progress.section_test_average:
                    level_progress.section_test_average = score
            elif assessment.type == AssessmentType.LEVEL_FINAL:
                # Update level final score
                if level_progress.level_final_score is None or score > level_progress.level_final_score:
                    level_progress.level_final_score = score
                    level_progress.is_completed = passed
                    level_progress.can_advance = passed
    
    # Add retake information to next steps
    if not passed:
        # Get retake info
        retake_info = get_remaining_attempts(
            assessment.target_id, 
            assessment.type.value, 
            current_user, 
            db
        )
        next_steps["retake_info"] = retake_info
        
        # Generate remedial content for failed assessments
        try:
            from app.api.api_v1.endpoints.remedial import generate_remedial_content
            from app.models.remedial import RemedialContent
            
            # Check if remedial content already exists
            existing_remedial = db.query(RemedialContent).filter(
                RemedialContent.assessment_id == assessment.id,
                RemedialContent.user_id == current_user.id
            ).first()
            
            if not existing_remedial:
                # Generate remedial content in background
                # For now, just indicate that remedial content is available
                next_steps["remedial_available"] = True
                next_steps["assessment_id"] = str(assessment.id)
        except Exception as e:
            print(f"Error checking remedial content: {e}")
            # Don't fail the assessment submission if remedial generation fails
    
    db.commit()
    
    return AssessmentResult(
        assessment_id=str(assessment.id),
        score=score,
        passed=passed,
        total_questions=total_questions,
        correct_answers=correct_count,
        time_taken=submission.time_taken,
        feedback=ai_feedback,
        question_results=question_results,
        next_steps=next_steps
    )


@router.get("/history")
def get_assessment_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    assessment_type: str = None,
    target_id: str = None
) -> Any:
    """Get user's assessment history"""
    
    query = db.query(Assessment).filter(Assessment.user_id == current_user.id)
    
    if assessment_type:
        query = query.filter(Assessment.type == AssessmentType(assessment_type))
    
    if target_id:
        query = query.filter(Assessment.target_id == target_id)
    
    assessments = query.order_by(Assessment.created_at.desc()).all()
    
    history = []
    for assessment in assessments:
        history.append({
            "id": str(assessment.id),
            "type": assessment.type.value,
            "target_id": assessment.target_id,
            "score": assessment.score,
            "passed": assessment.passed,
            "attempt_number": assessment.attempt_number,
            "time_taken": assessment.time_taken,
            "created_at": assessment.created_at.isoformat(),
            "submitted_at": assessment.submitted_at.isoformat() if assessment.submitted_at else None
        })
    
    return {"assessments": history}


@router.get("/attempts/{target_id}")
def get_remaining_attempts(
    target_id: str,
    assessment_type: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get remaining attempts for a specific assessment"""
    
    existing_assessments = db.query(Assessment).filter(
        Assessment.user_id == current_user.id,
        Assessment.type == AssessmentType(assessment_type),
        Assessment.target_id == target_id,
        Assessment.submitted_at.isnot(None)  # Only count completed assessments
    ).all()
    
    attempts_used = len(existing_assessments)
    
    # Get best score from completed assessments
    best_score = None
    best_passed = False
    if existing_assessments:
        best_assessment = max(existing_assessments, key=lambda a: a.score or 0)
        best_score = best_assessment.score
        best_passed = best_assessment.passed or False
    
    # Set attempt limits based on assessment type
    max_attempts = {
        "quiz": 999,  # Unlimited
        "section_test": 2,  # 1 initial + 1 retake
        "level_final": 2   # 1 initial + 1 retake
    }
    
    max_allowed = max_attempts.get(assessment_type, 1)
    remaining = max(0, max_allowed - attempts_used)
    
    # Check if retake is allowed
    can_retake = False
    retake_requirements = None
    
    if assessment_type == "quiz":
        # Unlimited retakes for quizzes
        can_retake = True
    elif assessment_type in ["section_test", "level_final"]:
        # One retake allowed if failed and haven't used all attempts
        if attempts_used > 0 and not best_passed and remaining > 0:
            can_retake = True
            if assessment_type == "level_final":
                # Level finals require review before retake
                retake_requirements = {
                    "review_required": True,
                    "message": "You must complete a review session before retaking the level final."
                }
    
    return {
        "target_id": target_id,
        "assessment_type": assessment_type,
        "attempts_used": attempts_used,
        "max_attempts": max_allowed,
        "remaining_attempts": remaining,
        "can_attempt": remaining > 0,
        "can_retake": can_retake,
        "best_score": best_score,
        "best_passed": best_passed,
        "retake_requirements": retake_requirements,
        "assessment_history": [
            {
                "id": str(a.id),
                "attempt_number": a.attempt_number,
                "score": a.score,
                "passed": a.passed,
                "submitted_at": a.submitted_at.isoformat() if a.submitted_at else None
            } for a in existing_assessments
        ]
    }


@router.post("/retake", response_model=AssessmentResponse)
def initiate_retake(
    request: AssessmentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Initiate a retake for a failed assessment"""
    
    # Get existing assessments for this target
    existing_assessments = db.query(Assessment).filter(
        Assessment.user_id == current_user.id,
        Assessment.type == AssessmentType(request.assessment_type),
        Assessment.target_id == request.target_id,
        Assessment.submitted_at.isnot(None)
    ).all()
    
    if not existing_assessments:
        raise HTTPException(
            status_code=400,
            detail="No previous assessment found. Use /generate endpoint for first attempt."
        )
    
    # Check if retake is allowed
    attempts_used = len(existing_assessments)
    best_assessment = max(existing_assessments, key=lambda a: a.score or 0)
    
    # Retake rules
    if request.assessment_type == "quiz":
        # Unlimited retakes for quizzes
        pass
    elif request.assessment_type in ["section_test", "level_final"]:
        # Check if already passed
        if best_assessment.passed:
            raise HTTPException(
                status_code=400,
                detail="Cannot retake a passed assessment."
            )
        
        # Check attempt limit (1 initial + 1 retake = 2 total)
        if attempts_used >= 2:
            raise HTTPException(
                status_code=400,
                detail="Maximum retake attempts reached."
            )
        
        # For level finals, check if review is required
        if request.assessment_type == "level_final":
            # In a real implementation, you'd check if user completed review
            # For now, we'll assume review is completed
            pass
    
    # Generate new assessment (reuse existing logic)
    return generate_assessment(request, current_user, db)


@router.get("/best-scores/{user_id}")
def get_user_best_scores(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get user's best scores for all assessments"""
    
    # Only allow users to see their own scores (or admin in future)
    if str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get all completed assessments
    assessments = db.query(Assessment).filter(
        Assessment.user_id == user_id,
        Assessment.submitted_at.isnot(None)
    ).all()
    
    # Group by target_id and assessment_type, keep best score
    best_scores = {}
    for assessment in assessments:
        key = f"{assessment.target_id}_{assessment.type.value}"
        
        if key not in best_scores or (assessment.score or 0) > (best_scores[key]["score"] or 0):
            best_scores[key] = {
                "target_id": assessment.target_id,
                "assessment_type": assessment.type.value,
                "best_score": assessment.score,
                "passed": assessment.passed,
                "attempts": 1,
                "last_attempt": assessment.submitted_at.isoformat()
            }
        else:
            best_scores[key]["attempts"] += 1
    
    return {"best_scores": list(best_scores.values())}