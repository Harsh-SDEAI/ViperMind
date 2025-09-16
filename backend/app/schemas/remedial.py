from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.remedial import RemedialType, RemedialStatus

class RemedialCardBase(BaseModel):
    topic_concept: str
    explanation: str
    code_example: Optional[str] = None
    practice_question: Optional[Dict[str, Any]] = None
    hints: List[str] = []

class RemedialCardCreate(RemedialCardBase):
    remedial_content_id: str

class RemedialCard(RemedialCardBase):
    id: str
    remedial_content_id: str
    is_completed: bool
    attempts: int
    time_spent: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RemedialContentBase(BaseModel):
    title: str
    content: str
    type: RemedialType
    weak_concepts: List[str] = []

class RemedialContentCreate(RemedialContentBase):
    user_id: str
    assessment_id: str
    target_id: str
    ai_generated_content: Optional[Dict[str, Any]] = None

class RemedialContent(RemedialContentBase):
    id: str
    user_id: str
    assessment_id: str
    target_id: str
    status: RemedialStatus
    ai_generated_content: Optional[Dict[str, Any]] = None
    time_spent: int
    completion_percentage: float
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    remedial_cards: List[RemedialCard] = []

    class Config:
        from_attributes = True

class ReviewScheduleBase(BaseModel):
    scheduled_date: datetime
    review_duration_days: int = 7
    review_topics: List[str] = []
    review_materials: Optional[Dict[str, Any]] = None

class ReviewScheduleCreate(ReviewScheduleBase):
    user_id: str
    assessment_id: str

class ReviewSchedule(ReviewScheduleBase):
    id: str
    user_id: str
    assessment_id: str
    is_completed: bool
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RemedialProgress(BaseModel):
    total_assigned: int
    completed: int
    in_progress: int
    completion_percentage: float
    time_spent_total: int
    weak_concepts: List[str]

class RemedialAssignment(BaseModel):
    assessment_id: str
    assessment_type: str
    score: float
    remedial_content: List[RemedialContent]
    review_schedule: Optional[ReviewSchedule] = None