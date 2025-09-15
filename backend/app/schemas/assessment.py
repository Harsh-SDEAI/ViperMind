from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.assessment import AssessmentType, DifficultyLevel

class QuestionBase(BaseModel):
    text: str
    options: List[str]
    correct_answer: int
    explanation: Optional[str] = None
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    concept_tags: List[str] = []
    code_snippet: Optional[str] = None
    order: int

class QuestionCreate(QuestionBase):
    assessment_id: str
    ai_generated: bool = True
    generation_prompt: Optional[str] = None

class Question(QuestionBase):
    id: str
    assessment_id: str
    ai_generated: bool
    generation_prompt: Optional[str] = None

    class Config:
        from_attributes = True

class AnswerBase(BaseModel):
    selected_option: int
    time_taken: Optional[int] = None
    confidence_level: Optional[str] = None
    ai_hint_used: bool = False

class AnswerCreate(AnswerBase):
    question_id: str

class Answer(AnswerBase):
    id: str
    assessment_id: str
    question_id: str
    is_correct: bool
    created_at: datetime

    class Config:
        from_attributes = True

class AssessmentBase(BaseModel):
    type: AssessmentType
    target_id: str
    difficulty_level: DifficultyLevel = DifficultyLevel.MEDIUM
    personalization_factors: Dict[str, Any] = {}

class AssessmentCreate(AssessmentBase):
    user_id: str

class AssessmentSubmit(BaseModel):
    answers: List[AnswerCreate]

class AssessmentResult(BaseModel):
    score: float
    passed: bool
    total_questions: int
    correct_answers: int
    ai_feedback: Optional[str] = None

class Assessment(AssessmentBase):
    id: str
    user_id: str
    score: Optional[float] = None
    passed: Optional[bool] = None
    attempt_number: int
    completed_at: Optional[datetime] = None
    ai_generated: bool
    ai_feedback: Optional[str] = None
    created_at: datetime
    questions: List[Question] = []
    answers: List[Answer] = []

    class Config:
        from_attributes = True