"""
Personalization Agent for AI-powered learning customization
"""

from typing import Dict, List, Any, Optional
from app.agents.tools.openai_tool import OpenAITool
from app.agents.tools.database_tool import DatabaseTool
import json
from datetime import datetime, timedelta

class PersonalizationAgent:
    def __init__(self):
        self.openai_tool = OpenAITool()
        self.db_tool = DatabaseTool()
    
    def detect_learning_style(self, user_id: str, learning_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect user's learning style based on their behavior and preferences"""
        
        prompt = f"""
        Analyze the following learning data to determine the user's learning style and preferences:
        
        Learning Data:
        - Time spent on lessons: {learning_data.get('avg_lesson_time', 0)} minutes
        - Assessment performance: {learning_data.get('assessment_performance', {})}
        - Interaction patterns: {learning_data.get('interaction_patterns', {})}
        - Content preferences: {learning_data.get('content_preferences', {})}
        - Struggle areas: {learning_data.get('struggle_areas', [])}
        - Success patterns: {learning_data.get('success_patterns', [])}
        
        Based on this data, determine:
        1. Primary learning style (visual, auditory, kinesthetic, reading/writing)
        2. Preferred content format (examples-first, theory-first, practice-first)
        3. Optimal difficulty progression (gradual, moderate, challenging)
        4. Engagement preferences (gamification, achievements, progress tracking)
        5. Learning pace (fast, moderate, thorough)
        
        Format as JSON:
        {{
            "primary_learning_style": "visual|auditory|kinesthetic|reading_writing",
            "content_preference": "examples_first|theory_first|practice_first",
            "difficulty_preference": "gradual|moderate|challenging",
            "engagement_style": "gamified|achievement_focused|progress_focused",
            "learning_pace": "fast|moderate|thorough",
            "confidence_score": 0.0-1.0,
            "recommendations": [
                "recommendation1",
                "recommendation2"
            ],
            "adaptation_strategies": {{
                "content_delivery": "strategy for content",
                "assessment_approach": "strategy for assessments",
                "hint_style": "strategy for hints"
            }}
        }}
        """
        
        try:
            response = self.openai_tool.generate_content(prompt, {
                "user_id": user_id,
                "analysis_type": "learning_style_detection"
            })
            
            learning_style = json.loads(response)
            
            return {
                "success": True,
                "learning_style": learning_style,
                "detected_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_style": self._get_default_learning_style()
            }
    
    def generate_personalized_hint(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a personalized hint based on user's learning style and current context"""
        
        learning_style = context.get("learning_style", {})
        question_context = context.get("question", {})
        user_attempts = context.get("attempts", 0)
        struggle_areas = context.get("struggle_areas", [])
        
        prompt = f"""
        Generate a personalized hint for a Python learner with the following profile:
        
        Learning Style: {learning_style.get('primary_learning_style', 'balanced')}
        Content Preference: {learning_style.get('content_preference', 'examples_first')}
        Learning Pace: {learning_style.get('learning_pace', 'moderate')}
        
        Current Context:
        - Question: {question_context.get('question', 'Python question')}
        - Topic: {question_context.get('topic', 'Python fundamentals')}
        - Difficulty: {question_context.get('difficulty', 'medium')}
        - User attempts: {user_attempts}
        - Known struggle areas: {struggle_areas}
        
        Generate a hint that:
        1. Matches their learning style (visual learners get diagrams/examples, etc.)
        2. Provides just enough guidance without giving away the answer
        3. Builds on their existing knowledge
        4. Addresses their specific struggle areas
        5. Encourages continued learning
        
        Format as JSON:
        {{
            "hint_text": "The main hint text",
            "hint_type": "conceptual|example|step_by_step|analogy",
            "code_snippet": "optional code example",
            "visual_aid": "optional ASCII diagram or description",
            "follow_up_questions": ["question1", "question2"],
            "encouragement": "motivational message",
            "difficulty_level": "beginner|intermediate|advanced"
        }}
        """
        
        try:
            response = self.openai_tool.generate_content(prompt, {
                "user_id": user_id,
                "hint_generation": True,
                "context": context
            })
            
            hint_data = json.loads(response)
            
            return {
                "success": True,
                "hint": hint_data,
                "personalized": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_hint": self._get_generic_hint(question_context)
            }
    
    def generate_personalized_examples(self, user_id: str, topic: str, user_interests: List[str]) -> Dict[str, Any]:
        """Generate code examples tailored to user's interests and learning style"""
        
        prompt = f"""
        Generate personalized Python code examples for the topic: {topic}
        
        User Interests: {', '.join(user_interests) if user_interests else 'general programming'}
        
        Create 3 different code examples that:
        1. Demonstrate the core concept of {topic}
        2. Use contexts related to the user's interests when possible
        3. Progress from simple to more complex
        4. Include clear comments explaining each step
        5. Are practical and engaging
        
        Format as JSON:
        {{
            "examples": [
                {{
                    "title": "Example title",
                    "description": "What this example demonstrates",
                    "code": "Python code with comments",
                    "explanation": "Step-by-step explanation",
                    "interest_connection": "How this relates to user interests",
                    "difficulty": "beginner|intermediate|advanced"
                }}
            ],
            "learning_objectives": ["objective1", "objective2"],
            "next_steps": "What to practice next"
        }}
        """
        
        try:
            response = self.openai_tool.generate_content(prompt, {
                "user_id": user_id,
                "topic": topic,
                "interests": user_interests
            })
            
            examples_data = json.loads(response)
            
            return {
                "success": True,
                "examples": examples_data,
                "personalized": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_examples": self._get_generic_examples(topic)
            }
    
    def optimize_difficulty(self, user_id: str, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize difficulty based on user performance and engagement"""
        
        recent_scores = performance_data.get("recent_scores", [])
        time_patterns = performance_data.get("time_patterns", {})
        engagement_metrics = performance_data.get("engagement_metrics", {})
        
        prompt = f"""
        Analyze user performance to optimize difficulty and engagement:
        
        Performance Data:
        - Recent assessment scores: {recent_scores}
        - Average time per question: {time_patterns.get('avg_time_per_question', 0)} seconds
        - Completion rate: {engagement_metrics.get('completion_rate', 0)}%
        - Help requests: {engagement_metrics.get('help_requests', 0)}
        - Skip rate: {engagement_metrics.get('skip_rate', 0)}%
        
        Provide recommendations for:
        1. Optimal difficulty level for next content
        2. Engagement strategies to maintain motivation
        3. Pacing adjustments
        4. Support level needed
        
        Format as JSON:
        {{
            "recommended_difficulty": "easier|same|harder",
            "difficulty_adjustment": -0.5 to +0.5,
            "engagement_strategies": [
                "strategy1",
                "strategy2"
            ],
            "pacing_recommendation": "slower|same|faster",
            "support_level": "high|medium|low",
            "reasoning": "Explanation of recommendations",
            "confidence": 0.0-1.0
        }}
        """
        
        try:
            response = self.openai_tool.generate_content(prompt, {
                "user_id": user_id,
                "optimization_type": "difficulty_engagement"
            })
            
            optimization_data = json.loads(response)
            
            return {
                "success": True,
                "optimization": optimization_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_optimization": self._get_default_optimization()
            }
    
    def generate_adaptive_content(self, user_id: str, content_request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content adapted to user's learning style and current needs"""
        
        learning_style = content_request.get("learning_style", {})
        topic = content_request.get("topic", "")
        current_level = content_request.get("current_level", "beginner")
        user_interests = content_request.get("interests", [])
        
        prompt = f"""
        Create adaptive learning content for:
        
        Topic: {topic}
        User Level: {current_level}
        Learning Style: {learning_style.get('primary_learning_style', 'balanced')}
        Content Preference: {learning_style.get('content_preference', 'examples_first')}
        User Interests: {', '.join(user_interests)}
        
        Generate content that includes:
        1. Introduction tailored to their learning style
        2. Core concepts explained in their preferred format
        3. Examples related to their interests
        4. Practice exercises at appropriate difficulty
        5. Assessment questions that match their style
        
        Format as JSON:
        {{
            "introduction": "Engaging introduction",
            "core_concepts": [
                {{
                    "concept": "concept name",
                    "explanation": "tailored explanation",
                    "example": "relevant example"
                }}
            ],
            "practice_exercises": [
                {{
                    "exercise": "exercise description",
                    "code_template": "starter code",
                    "solution_hint": "guidance"
                }}
            ],
            "assessment_questions": [
                {{
                    "question": "question text",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": 0,
                    "explanation": "why this is correct"
                }}
            ],
            "personalization_notes": "How this content was adapted"
        }}
        """
        
        try:
            response = self.openai_tool.generate_content(prompt, {
                "user_id": user_id,
                "content_type": "adaptive_lesson"
            })
            
            content_data = json.loads(response)
            
            return {
                "success": True,
                "content": content_data,
                "adapted": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_content": self._get_generic_content(topic)
            }
    
    def _get_default_learning_style(self) -> Dict[str, Any]:
        """Default learning style for fallback"""
        return {
            "primary_learning_style": "visual",
            "content_preference": "examples_first",
            "difficulty_preference": "moderate",
            "engagement_style": "progress_focused",
            "learning_pace": "moderate",
            "confidence_score": 0.5,
            "recommendations": [
                "Start with visual examples",
                "Provide step-by-step guidance"
            ],
            "adaptation_strategies": {
                "content_delivery": "Use visual aids and examples",
                "assessment_approach": "Include code examples in questions",
                "hint_style": "Provide visual or example-based hints"
            }
        }
    
    def _get_generic_hint(self, question_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generic hint for fallback"""
        return {
            "hint_text": "Think about the core concept being tested. Break down the problem into smaller steps.",
            "hint_type": "conceptual",
            "code_snippet": None,
            "visual_aid": None,
            "follow_up_questions": ["What is the main concept here?", "What steps are needed?"],
            "encouragement": "You're on the right track! Keep thinking through it step by step.",
            "difficulty_level": "beginner"
        }
    
    def _get_generic_examples(self, topic: str) -> Dict[str, Any]:
        """Generic examples for fallback"""
        return {
            "examples": [
                {
                    "title": f"Basic {topic} Example",
                    "description": f"A simple demonstration of {topic}",
                    "code": f"# Example code for {topic}\nprint('Hello, {topic}!')",
                    "explanation": f"This example shows the basics of {topic}",
                    "interest_connection": "General programming concept",
                    "difficulty": "beginner"
                }
            ],
            "learning_objectives": [f"Understand {topic} basics"],
            "next_steps": f"Practice more {topic} examples"
        }
    
    def _get_default_optimization(self) -> Dict[str, Any]:
        """Default optimization for fallback"""
        return {
            "recommended_difficulty": "same",
            "difficulty_adjustment": 0.0,
            "engagement_strategies": [
                "Provide clear feedback",
                "Use encouraging language"
            ],
            "pacing_recommendation": "same",
            "support_level": "medium",
            "reasoning": "Maintaining current approach due to insufficient data",
            "confidence": 0.5
        }
    
    def _get_generic_content(self, topic: str) -> Dict[str, Any]:
        """Generic content for fallback"""
        return {
            "introduction": f"Let's learn about {topic}!",
            "core_concepts": [
                {
                    "concept": topic,
                    "explanation": f"This is an important concept in Python programming.",
                    "example": f"# Example of {topic}\nprint('Learning {topic}')"
                }
            ],
            "practice_exercises": [
                {
                    "exercise": f"Try using {topic} in your own code",
                    "code_template": f"# Your {topic} code here\n",
                    "solution_hint": "Follow the examples provided"
                }
            ],
            "assessment_questions": [],
            "personalization_notes": "Generic content - personalization not available"
        }