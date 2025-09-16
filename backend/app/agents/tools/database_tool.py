"""
Database tool for LangGraph agents to interact with the ViperMind database
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.db.base import SessionLocal
from app.models import User, Level, Section, Topic, Assessment, UserProgress, LevelProgress
from app.models.user import UserLevel
from app.models.assessment import AssessmentType
from app.models.progress import ProgressStatus


class DatabaseTool:
    """Tool for agents to interact with the database"""
    
    def __init__(self):
        self.name = "database_tool"
        self.description = "Access and modify ViperMind database for user progress, curriculum, and assessments"
    
    def run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute database operations"""
        db = SessionLocal()
        try:
            if action == "get_user_progress":
                return self._get_user_progress(db, kwargs.get("user_id"))
            elif action == "get_curriculum_structure":
                return self._get_curriculum_structure(db)
            elif action == "get_topic_details":
                return self._get_topic_details(db, kwargs.get("topic_id"))
            elif action == "update_user_progress":
                return self._update_user_progress(db, **kwargs)
            elif action == "save_assessment_results":
                return self._save_assessment_results(db, **kwargs)
            elif action == "get_user_level_progress":
                return self._get_user_level_progress(db, kwargs.get("user_id"), kwargs.get("level_id"))
            else:
                return {"error": f"Unknown action: {action}"}
        finally:
            db.close()
    
    def _get_user_progress(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user progress"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        
        # Get all user progress
        progress_records = db.query(UserProgress).filter(UserProgress.user_id == user_id).all()
        
        # Get level progress
        level_progress = db.query(LevelProgress).filter(LevelProgress.user_id == user_id).all()
        
        return {
            "user": {
                "id": str(user.id),
                "username": user.username,
                "current_level": user.current_level.value,
                "is_active": user.is_active
            },
            "topic_progress": [
                {
                    "topic_id": str(p.topic_id),
                    "status": p.status.value,
                    "best_score": p.best_score,
                    "attempts": p.attempts,
                    "struggle_areas": p.struggle_areas or [],
                    "strength_areas": p.strength_areas or []
                }
                for p in progress_records
            ],
            "level_progress": [
                {
                    "level_id": str(lp.level_id),
                    "topic_quiz_average": lp.topic_quiz_average,
                    "section_test_average": lp.section_test_average,
                    "level_final_score": lp.level_final_score,
                    "overall_score": lp.overall_score,
                    "is_unlocked": lp.is_unlocked,
                    "is_completed": lp.is_completed,
                    "can_advance": lp.can_advance
                }
                for lp in level_progress
            ]
        }
    
    def _get_curriculum_structure(self, db: Session) -> Dict[str, Any]:
        """Get the complete curriculum structure"""
        levels = db.query(Level).order_by(Level.order).all()
        
        curriculum = []
        for level in levels:
            sections = db.query(Section).filter(Section.level_id == level.id).order_by(Section.order).all()
            
            level_data = {
                "id": str(level.id),
                "name": level.name,
                "code": level.code,
                "description": level.description,
                "order": level.order,
                "sections": []
            }
            
            for section in sections:
                topics = db.query(Topic).filter(Topic.section_id == section.id).order_by(Topic.order).all()
                
                section_data = {
                    "id": str(section.id),
                    "name": section.name,
                    "code": section.code,
                    "description": section.description,
                    "order": section.order,
                    "topics": [
                        {
                            "id": str(topic.id),
                            "name": topic.name,
                            "order": topic.order
                        }
                        for topic in topics
                    ]
                }
                level_data["sections"].append(section_data)
            
            curriculum.append(level_data)
        
        return {"curriculum": curriculum}
    
    def _get_topic_details(self, db: Session, topic_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific topic"""
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            return {"error": "Topic not found"}
        
        # Get section and level info
        section = db.query(Section).filter(Section.id == topic.section_id).first()
        level = db.query(Level).filter(Level.id == section.level_id).first()
        
        return {
            "topic": {
                "id": str(topic.id),
                "name": topic.name,
                "order": topic.order
            },
            "section": {
                "id": str(section.id),
                "name": section.name,
                "code": section.code
            },
            "level": {
                "id": str(level.id),
                "name": level.name,
                "code": level.code
            }
        }
    
    def _update_user_progress(self, db: Session, user_id: str, topic_id: str, 
                            status: str = None, score: float = None, **kwargs) -> Dict[str, Any]:
        """Update user progress for a topic"""
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.topic_id == topic_id
        ).first()
        
        if not progress:
            # Create new progress record
            topic = db.query(Topic).filter(Topic.id == topic_id).first()
            if not topic:
                return {"error": "Topic not found"}
            
            section = db.query(Section).filter(Section.id == topic.section_id).first()
            
            progress = UserProgress(
                user_id=user_id,
                level_id=section.level_id,
                section_id=topic.section_id,
                topic_id=topic_id,
                status=ProgressStatus.AVAILABLE
            )
            db.add(progress)
        
        # Update progress
        if status:
            progress.status = ProgressStatus(status)
        if score is not None:
            if progress.best_score is None or score > progress.best_score:
                progress.best_score = score
            progress.attempts += 1
        
        db.commit()
        
        return {
            "success": True,
            "progress": {
                "topic_id": str(progress.topic_id),
                "status": progress.status.value,
                "best_score": progress.best_score,
                "attempts": progress.attempts
            }
        }
    
    def _save_assessment_results(self, db: Session, user_id: str, assessment_type: str,
                               target_id: str, score: float, passed: bool, 
                               questions_data: List[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Save assessment results to database"""
        
        # Create assessment record
        assessment = Assessment(
            user_id=user_id,
            type=AssessmentType(assessment_type),
            target_id=target_id,
            score=score,
            passed=passed,
            attempt_number=1,  # Will be updated based on existing attempts
            ai_generated=True,
            difficulty_level=kwargs.get("difficulty_level", "medium"),
            personalization_factors=kwargs.get("personalization_factors", {}),
            ai_feedback=kwargs.get("ai_feedback")
        )
        
        # Check for existing attempts
        existing_count = db.query(Assessment).filter(
            Assessment.user_id == user_id,
            Assessment.type == AssessmentType(assessment_type),
            Assessment.target_id == target_id
        ).count()
        
        assessment.attempt_number = existing_count + 1
        
        db.add(assessment)
        db.flush()  # Get the assessment ID
        
        return {
            "success": True,
            "assessment_id": str(assessment.id),
            "attempt_number": assessment.attempt_number,
            "score": score,
            "passed": passed
        }
    
    def _get_user_level_progress(self, db: Session, user_id: str, level_id: str) -> Dict[str, Any]:
        """Get user progress for a specific level"""
        level_progress = db.query(LevelProgress).filter(
            LevelProgress.user_id == user_id,
            LevelProgress.level_id == level_id
        ).first()
        
        if not level_progress:
            return {"error": "Level progress not found"}
        
        return {
            "level_progress": {
                "level_id": str(level_progress.level_id),
                "topic_quiz_average": level_progress.topic_quiz_average,
                "section_test_average": level_progress.section_test_average,
                "level_final_score": level_progress.level_final_score,
                "overall_score": level_progress.overall_score,
                "is_unlocked": level_progress.is_unlocked,
                "is_completed": level_progress.is_completed,
                "can_advance": level_progress.can_advance,
                "ai_insights": level_progress.ai_insights or {},
                "personalized_recommendations": level_progress.personalized_recommendations or []
            }
        }