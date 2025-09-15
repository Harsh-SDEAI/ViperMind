from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class CodeExample(BaseModel):
    title: str
    code: str
    explanation: str
    output: Optional[str] = None

class LessonContentBase(BaseModel):
    why_it_matters: str
    key_ideas: List[str]
    examples: List[CodeExample]
    pitfalls: List[str]
    recap: str

class LessonContentCreate(LessonContentBase):
    topic_id: str

class LessonContent(LessonContentBase):
    id: str
    topic_id: str

    class Config:
        from_attributes = True

class RemedialContentBase(BaseModel):
    explanation: str
    practice_exercises: List[Dict[str, Any]]
    additional_resources: List[Dict[str, Any]]

class RemedialContentCreate(RemedialContentBase):
    topic_id: str

class RemedialContent(RemedialContentBase):
    id: str
    topic_id: str

    class Config:
        from_attributes = True

class TopicBase(BaseModel):
    name: str
    order: int

class TopicCreate(TopicBase):
    section_id: str

class Topic(TopicBase):
    id: str
    section_id: str
    lesson_content: Optional[LessonContent] = None
    remedial_content: Optional[RemedialContent] = None

    class Config:
        from_attributes = True

class SectionBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    order: int

class SectionCreate(SectionBase):
    level_id: str

class Section(SectionBase):
    id: str
    level_id: str
    topics: List[Topic] = []

    class Config:
        from_attributes = True

class LevelBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    order: int

class LevelCreate(LevelBase):
    pass

class Level(LevelBase):
    id: str
    sections: List[Section] = []

    class Config:
        from_attributes = True