"""
Curriculum API endpoints for ViperMind
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth import get_current_active_user
from app.db.base import get_db
from app.models.user import User
from app.models.curriculum import Level, Section, Topic, LessonContent
from app.models.progress import UserProgress, LevelProgress
from app.schemas.curriculum import Level as LevelSchema, Section as SectionSchema, Topic as TopicSchema
from pydantic import BaseModel

router = APIRouter()


class CurriculumStructure(BaseModel):
    levels: List[LevelSchema]


class TopicWithProgress(BaseModel):
    id: str
    name: str
    order: int
    is_unlocked: bool = False
    is_completed: bool = False
    progress_percentage: float = 0.0


class SectionWithProgress(BaseModel):
    id: str
    name: str
    code: str
    description: str = None
    order: int
    topics: List[TopicWithProgress] = []
    is_unlocked: bool = False
    completion_percentage: float = 0.0


class LevelWithProgress(BaseModel):
    id: str
    name: str
    code: str
    description: str = None
    order: int
    sections: List[SectionWithProgress] = []
    is_unlocked: bool = False
    completion_percentage: float = 0.0


class CurriculumWithProgress(BaseModel):
    levels: List[LevelWithProgress]


@router.get("/structure", response_model=CurriculumStructure)
def get_curriculum_structure(
    db: Session = Depends(get_db)
) -> Any:
    """Get the complete curriculum structure without progress information"""
    
    levels = db.query(Level).order_by(Level.order).all()
    
    curriculum_levels = []
    for level in levels:
        sections = db.query(Section).filter(Section.level_id == level.id).order_by(Section.order).all()
        
        level_sections = []
        for section in sections:
            topics = db.query(Topic).filter(Topic.section_id == section.id).order_by(Topic.order).all()
            
            section_topics = [
                TopicSchema(
                    id=str(topic.id),
                    section_id=str(topic.section_id),
                    name=topic.name,
                    order=topic.order
                )
                for topic in topics
            ]
            
            level_sections.append(
                SectionSchema(
                    id=str(section.id),
                    level_id=str(section.level_id),
                    name=section.name,
                    code=section.code,
                    description=section.description,
                    order=section.order,
                    topics=section_topics
                )
            )
        
        curriculum_levels.append(
            LevelSchema(
                id=str(level.id),
                name=level.name,
                code=level.code,
                description=level.description,
                order=level.order,
                sections=level_sections
            )
        )
    
    return CurriculumStructure(levels=curriculum_levels)


@router.get("/progress", response_model=CurriculumWithProgress)
def get_curriculum_with_progress(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get curriculum structure with user progress information"""
    
    # Get all levels
    levels = db.query(Level).order_by(Level.order).all()
    
    # Get user's progress data
    user_progress = db.query(UserProgress).filter(UserProgress.user_id == current_user.id).all()
    level_progress = db.query(LevelProgress).filter(LevelProgress.user_id == current_user.id).all()
    
    # Create progress lookup dictionaries
    topic_progress_map = {str(up.topic_id): up for up in user_progress}
    level_progress_map = {str(lp.level_id): lp for lp in level_progress}
    
    curriculum_levels = []
    
    for level_index, level in enumerate(levels):
        # Get level progress
        level_prog = level_progress_map.get(str(level.id))
        level_unlocked = level_index == 0 or (level_prog and level_prog.is_unlocked)
        level_completion = level_prog.overall_score if level_prog else 0.0
        
        sections = db.query(Section).filter(Section.level_id == level.id).order_by(Section.order).all()
        level_sections = []
        
        for section_index, section in enumerate(sections):
            topics = db.query(Topic).filter(Topic.section_id == section.id).order_by(Topic.order).all()
            section_topics = []
            
            completed_topics = 0
            total_topics = len(topics)
            
            for topic_index, topic in enumerate(topics):
                topic_prog = topic_progress_map.get(str(topic.id))
                
                # Topic is unlocked if it's the first topic in first section of unlocked level,
                # or if previous topic is completed
                topic_unlocked = False
                if level_unlocked:
                    if section_index == 0 and topic_index == 0:
                        topic_unlocked = True
                    elif topic_index > 0:
                        # Check if previous topic is completed
                        prev_topic = topics[topic_index - 1]
                        prev_prog = topic_progress_map.get(str(prev_topic.id))
                        topic_unlocked = prev_prog and prev_prog.status.value == "completed"
                    elif section_index > 0:
                        # Check if previous section is completed
                        prev_section = sections[section_index - 1]
                        prev_topics = db.query(Topic).filter(Topic.section_id == prev_section.id).all()
                        prev_section_completed = all(
                            topic_progress_map.get(str(t.id)) and 
                            topic_progress_map.get(str(t.id)).status.value == "completed"
                            for t in prev_topics
                        )
                        topic_unlocked = prev_section_completed
                
                topic_completed = bool(topic_prog and topic_prog.status.value == "completed")
                if topic_completed:
                    completed_topics += 1
                
                progress_percentage = (topic_prog.best_score or 0.0) if topic_prog else 0.0
                
                section_topics.append(
                    TopicWithProgress(
                        id=str(topic.id),
                        name=topic.name,
                        order=topic.order,
                        is_unlocked=bool(topic_unlocked),
                        is_completed=topic_completed,
                        progress_percentage=float(progress_percentage)
                    )
                )
            
            # Calculate section completion percentage
            section_completion = (completed_topics / total_topics * 100) if total_topics > 0 else 0.0
            section_unlocked = bool(level_unlocked and (section_index == 0 or section_completion > 0))
            
            level_sections.append(
                SectionWithProgress(
                    id=str(section.id),
                    name=section.name,
                    code=section.code,
                    description=section.description,
                    order=section.order,
                    topics=section_topics,
                    is_unlocked=section_unlocked,
                    completion_percentage=float(section_completion)
                )
            )
        
        curriculum_levels.append(
            LevelWithProgress(
                id=str(level.id),
                name=level.name,
                code=level.code,
                description=level.description,
                order=level.order,
                sections=level_sections,
                is_unlocked=bool(level_unlocked),
                completion_percentage=float(level_completion)
            )
        )
    
    return CurriculumWithProgress(levels=curriculum_levels)


@router.get("/levels/{level_id}", response_model=LevelSchema)
def get_level_details(
    level_id: str,
    db: Session = Depends(get_db)
) -> Any:
    """Get detailed information about a specific level"""
    
    level = db.query(Level).filter(Level.id == level_id).first()
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    
    sections = db.query(Section).filter(Section.level_id == level.id).order_by(Section.order).all()
    
    level_sections = []
    for section in sections:
        topics = db.query(Topic).filter(Topic.section_id == section.id).order_by(Topic.order).all()
        
        section_topics = [
            TopicSchema(
                id=str(topic.id),
                section_id=str(topic.section_id),
                name=topic.name,
                order=topic.order
            )
            for topic in topics
        ]
        
        level_sections.append(
            SectionSchema(
                id=str(section.id),
                level_id=str(section.level_id),
                name=section.name,
                code=section.code,
                description=section.description,
                order=section.order,
                topics=section_topics
            )
        )
    
    return LevelSchema(
        id=str(level.id),
        name=level.name,
        code=level.code,
        description=level.description,
        order=level.order,
        sections=level_sections
    )


@router.get("/sections/{section_id}", response_model=SectionSchema)
def get_section_details(
    section_id: str,
    db: Session = Depends(get_db)
) -> Any:
    """Get detailed information about a specific section"""
    
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    topics = db.query(Topic).filter(Topic.section_id == section.id).order_by(Topic.order).all()
    
    section_topics = [
        TopicSchema(
            id=str(topic.id),
            section_id=str(topic.section_id),
            name=topic.name,
            order=topic.order
        )
        for topic in topics
    ]
    
    return SectionSchema(
        id=str(section.id),
        level_id=str(section.level_id),
        name=section.name,
        code=section.code,
        description=section.description,
        order=section.order,
        topics=section_topics
    )


@router.get("/topics/{topic_id}", response_model=TopicSchema)
def get_topic_details(
    topic_id: str,
    db: Session = Depends(get_db)
) -> Any:
    """Get detailed information about a specific topic"""
    
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    return TopicSchema(
        id=str(topic.id),
        section_id=str(topic.section_id),
        name=topic.name,
        order=topic.order
    )