from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.progress import ProgressStatus

class UserProgressBase(BaseModel):
    status: ProgressStatus = ProgressStatus.LOCKED
    best_score: Optional[float] = None
    attempts: int = 0
    learning_velocity: Optional[float] = None
    struggle_areas: List[str] = []
    strength_areas: List[str] = []
    recommended_difficulty: Optional[str] = None

class UserProgressCreate(UserProgressBase):
    user_id: str
    level_id: str
    section_id: str
    topic_id: str

class UserProgressUpdate(BaseModel):
    status: Optional[ProgressStatus] = None
    best_score: Optional[float] = None
    attempts: Optional[int] = None
    last_attempt_at: Optional[datetime] = None
    learning_velocity: Optional[float] = None
    struggle_areas: Optional[List[str]] = None
    strength_areas: Optional[List[str]] = None
    recommended_difficulty: Optional[str] = None

class UserProgress(UserProgressBase):
    id: str
    user_id: str
    level_id: str
    section_id: str
    topic_id: str
    last_attempt_at: Optional[datetime] = None
    unlocked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LevelProgressBase(BaseModel):
    topic_quiz_average: float = 0.0
    section_test_average: float = 0.0
    level_final_score: Optional[float] = None
    overall_score: float = 0.0
    is_unlocked: bool = False
    is_completed: bool = False
    can_advance: bool = False
    ai_insights: Dict[str, Any] = {}
    predicted_completion_time: Optional[int] = None
    personalized_recommendations: List[str] = []

class LevelProgressCreate(LevelProgressBase):
    user_id: str
    level_id: str

class LevelProgressUpdate(BaseModel):
    topic_quiz_average: Optional[float] = None
    section_test_average: Optional[float] = None
    level_final_score: Optional[float] = None
    overall_score: Optional[float] = None
    is_unlocked: Optional[bool] = None
    is_completed: Optional[bool] = None
    can_advance: Optional[bool] = None
    ai_insights: Optional[Dict[str, Any]] = None
    predicted_completion_time: Optional[int] = None
    personalized_recommendations: Optional[List[str]] = None

class LevelProgress(LevelProgressBase):
    id: str
    user_id: str
    level_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LearningAnalyticsBase(BaseModel):
    session_id: str
    activity_type: str
    topic_id: Optional[str] = None
    time_spent: Optional[int] = None
    performance_metrics: Dict[str, Any] = {}
    ai_observations: Dict[str, Any] = {}
    engagement_score: Optional[float] = None

class LearningAnalyticsCreate(LearningAnalyticsBase):
    user_id: str

class LearningAnalytics(LearningAnalyticsBase):
    id: str
    user_id: str
    timestamp: datetime

    class Config:
        from_attributes = True