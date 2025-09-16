"""
Tutor Agent - Provides personalized explanations and learning guidance
"""

from typing import Dict, Any, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from app.agents.tools.openai_tool import OpenAITool
from app.agents.tools.database_tool import DatabaseTool
from app.core.errors import AIServiceError, error_handler, fallback_content


class TutorAgent:
    """Agent responsible for providing personalized tutoring and explanations"""
    
    def __init__(self):
        self.openai_tool = OpenAITool()
        self.database_tool = DatabaseTool()
        self.name = "tutor_agent"
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process tutor-related requests"""
        
        request_type = state.get("request_type")
        user_id = state.get("user_id")
        
        if request_type == "generate_lesson":
            return self._generate_lesson(state)
        elif request_type == "explain_concept":
            return self._explain_concept(state)
        elif request_type == "provide_hint":
            return self._provide_hint(state)
        elif request_type == "personalize_content":
            return self._personalize_content(state)
        else:
            return {
                **state,
                "error": f"Unknown tutor request type: {request_type}",
                "agent": self.name
            }
    
    def _generate_lesson(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized lesson content"""
        
        topic_id = state.get("topic_id")
        user_id = state.get("user_id")
        
        # Get topic details
        topic_result = self.database_tool.run("get_topic_details", topic_id=topic_id)
        if "error" in topic_result:
            return {**state, "error": topic_result["error"], "agent": self.name}
        
        # Get user context for personalization
        user_progress = self.database_tool.run("get_user_progress", user_id=user_id)
        
        topic_name = topic_result["topic"]["name"]
        level = topic_result["level"]["name"].lower()
        
        # Generate lesson content
        content_result = self.openai_tool.run(
            "generate_lesson_content",
            topic_name=topic_name,
            level=level,
            user_context=user_progress.get("user", {})
        )
        
        if not content_result.get("success"):
            return {**state, "error": content_result.get("error"), "agent": self.name}
        
        return {
            **state,
            "lesson_content": content_result["lesson_content"],
            "topic_info": topic_result,
            "agent": self.name,
            "success": True
        }
    
    def _explain_concept(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Provide personalized explanation for a concept"""
        
        concept = state.get("concept")
        user_id = state.get("user_id")
        
        if not concept:
            return {**state, "error": "No concept specified", "agent": self.name}
        
        # Get user context
        user_progress = self.database_tool.run("get_user_progress", user_id=user_id)
        user_level = user_progress.get("user", {}).get("current_level", "beginner")
        
        # Generate explanation
        explanation_result = self.openai_tool.run(
            "create_explanation",
            concept=concept,
            user_level=user_level,
            user_context=user_progress.get("user", {})
        )
        
        if not explanation_result.get("success"):
            return {**state, "error": explanation_result.get("error"), "agent": self.name}
        
        return {
            **state,
            "explanation": explanation_result["explanation"],
            "concept": concept,
            "agent": self.name,
            "success": True
        }
    
    def _provide_hint(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate helpful hints for struggling students"""
        
        question = state.get("question")
        user_answer = state.get("user_answer")
        difficulty = state.get("difficulty", "medium")
        
        if not question:
            return {**state, "error": "No question specified", "agent": self.name}
        
        # Generate hint
        hint_result = self.openai_tool.run(
            "generate_hints",
            question=question,
            user_answer=user_answer,
            difficulty=difficulty
        )
        
        if not hint_result.get("success"):
            return {**state, "error": hint_result.get("error"), "agent": self.name}
        
        return {
            **state,
            "hint": hint_result["hint"],
            "agent": self.name,
            "success": True
        }
    
    def _personalize_content(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt content based on user's learning style and progress"""
        
        user_id = state.get("user_id")
        content = state.get("content")
        
        if not content:
            return {**state, "error": "No content to personalize", "agent": self.name}
        
        # Get user progress and learning patterns
        user_progress = self.database_tool.run("get_user_progress", user_id=user_id)
        
        # Analyze user's learning patterns
        struggle_areas = []
        strength_areas = []
        
        for progress in user_progress.get("topic_progress", []):
            if progress.get("struggle_areas"):
                struggle_areas.extend(progress["struggle_areas"])
            if progress.get("strength_areas"):
                strength_areas.extend(progress["strength_areas"])
        
        # Personalize content based on patterns
        personalization_context = {
            "struggle_areas": list(set(struggle_areas)),
            "strength_areas": list(set(strength_areas)),
            "user_level": user_progress.get("user", {}).get("current_level", "beginner")
        }
        
        return {
            **state,
            "personalized_content": content,
            "personalization_applied": personalization_context,
            "agent": self.name,
            "success": True
        }