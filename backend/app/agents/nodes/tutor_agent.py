"""
Tutor Agent - Provides personalized explanations and learning guidance
"""

from typing import Dict, Any, List
import hashlib
import json
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from app.agents.tools.openai_tool import OpenAITool
from app.agents.tools.database_tool import DatabaseTool
from app.core.errors import AIServiceError, error_handler, fallback_content
from app.core.cache import cache_manager, CacheKeys, CacheTTL
from app.core.fallback import ai_fallback_manager, with_ai_fallback


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
        
        # Create cache key for lesson content
        cache_context = {
            "topic_id": topic_id,
            "user_id": user_id,
            "request_type": "generate_lesson"
        }
        context_hash = hashlib.md5(json.dumps(cache_context, sort_keys=True).encode()).hexdigest()
        cache_key = cache_manager._generate_key(CacheKeys.AI_CONTEXT, f"lesson:{context_hash}")
        
        # Try to get from cache first
        cached_result = cache_manager.get(cache_key)
        if cached_result:
            return {**state, **cached_result, "from_cache": True}
        
        # Get topic details
        topic_result = self.database_tool.run("get_topic_details", topic_id=topic_id)
        if "error" in topic_result:
            return {**state, "error": topic_result["error"], "agent": self.name}
        
        # Get user context for personalization
        user_progress = self.database_tool.run("get_user_progress", user_id=user_id)
        
        topic_name = topic_result["topic"]["name"]
        level = topic_result["level"]["name"].lower()
        
        # Generate lesson content with fallback
        try:
            content_result = self.openai_tool.run(
                "generate_lesson_content",
                topic_name=topic_name,
                level=level,
                user_context=user_progress.get("user", {})
            )
            
            if not content_result.get("success"):
                raise AIServiceError(f"OpenAI lesson generation failed: {content_result.get('error')}")
                
        except Exception as e:
            # Use fallback content
            fallback_context = {
                "topic_id": topic_id,
                "topic_name": topic_name,
                "level": level,
                "user_context": user_progress.get("user", {})
            }
            content_result = ai_fallback_manager.handle_ai_failure("openai", "generate_lesson", fallback_context)
        
        result = {
            "lesson_content": content_result["lesson_content"],
            "topic_info": topic_result,
            "agent": self.name,
            "success": True
        }
        
        # Cache the result
        cache_manager.set(cache_key, result, CacheTTL.AI_RESPONSES)
        
        return {**state, **result}
    
    def _explain_concept(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Provide personalized explanation for a concept"""
        
        concept = state.get("concept")
        user_id = state.get("user_id")
        
        if not concept:
            return {**state, "error": "No concept specified", "agent": self.name}
        
        # Create cache key for concept explanation
        cache_context = {
            "concept": concept,
            "user_id": user_id,
            "request_type": "explain_concept"
        }
        context_hash = hashlib.md5(json.dumps(cache_context, sort_keys=True).encode()).hexdigest()
        cache_key = cache_manager._generate_key(CacheKeys.AI_CONTEXT, f"explanation:{context_hash}")
        
        # Try to get from cache first
        cached_result = cache_manager.get(cache_key)
        if cached_result:
            return {**state, **cached_result, "from_cache": True}
        
        # Get user context
        user_progress = self.database_tool.run("get_user_progress", user_id=user_id)
        user_level = user_progress.get("user", {}).get("current_level", "beginner")
        
        # Generate explanation with fallback
        try:
            explanation_result = self.openai_tool.run(
                "create_explanation",
                concept=concept,
                user_level=user_level,
                user_context=user_progress.get("user", {})
            )
            
            if not explanation_result.get("success"):
                raise AIServiceError(f"OpenAI explanation generation failed: {explanation_result.get('error')}")
                
        except Exception as e:
            # Use fallback content
            fallback_context = {
                "concept": concept,
                "user_level": user_level,
                "user_context": user_progress.get("user", {})
            }
            explanation_result = ai_fallback_manager.handle_ai_failure("openai", "explain_concept", fallback_context)
        
        result = {
            "explanation": explanation_result["explanation"],
            "concept": concept,
            "agent": self.name,
            "success": True
        }
        
        # Cache the result
        cache_manager.set(cache_key, result, CacheTTL.AI_RESPONSES)
        
        return {**state, **result}
    
    def _provide_hint(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate helpful hints for struggling students"""
        
        question = state.get("question")
        user_answer = state.get("user_answer")
        difficulty = state.get("difficulty", "medium")
        
        if not question:
            return {**state, "error": "No question specified", "agent": self.name}
        
        # Generate hint with fallback
        try:
            hint_result = self.openai_tool.run(
                "generate_hints",
                question=question,
                user_answer=user_answer,
                difficulty=difficulty
            )
            
            if not hint_result.get("success"):
                raise AIServiceError(f"OpenAI hint generation failed: {hint_result.get('error')}")
                
        except Exception as e:
            # Use fallback content
            fallback_context = {
                "question": question,
                "user_answer": user_answer,
                "difficulty": difficulty,
                "context": "general"
            }
            hint_result = ai_fallback_manager.handle_ai_failure("openai", "generate_hint", fallback_context)
        
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