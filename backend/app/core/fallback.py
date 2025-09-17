"""
Comprehensive fallback system for AI agent failures and service unavailability.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from app.core.errors import AIServiceError, fallback_content
from app.core.cache import cache_manager, CacheKeys, CacheTTL

logger = logging.getLogger(__name__)

class FallbackContentProvider:
    """Provides fallback content when AI services are unavailable."""
    
    def __init__(self):
        self.fallback_data_path = Path(__file__).parent.parent / "data" / "fallback"
        self.fallback_data_path.mkdir(parents=True, exist_ok=True)
        self._initialize_fallback_content()
    
    def _initialize_fallback_content(self):
        """Initialize fallback content files if they don't exist."""
        
        # Fallback lesson content
        lessons_file = self.fallback_data_path / "lessons.json"
        if not lessons_file.exists():
            fallback_lessons = {
                "python_basics": {
                    "title": "Introduction to Python",
                    "why_it_matters": "Python is one of the most popular programming languages due to its simplicity and versatility. It's used in web development, data science, AI, and automation.",
                    "key_ideas": [
                        "Python uses indentation to define code blocks",
                        "Variables don't need type declarations",
                        "Python is interpreted, not compiled",
                        "Everything in Python is an object"
                    ],
                    "examples": [
                        {
                            "title": "Hello World",
                            "code": "print('Hello, World!')",
                            "explanation": "This is the traditional first program that displays text."
                        },
                        {
                            "title": "Variables",
                            "code": "name = 'Alice'\nage = 25\nprint(f'Hello, {name}! You are {age} years old.')",
                            "explanation": "Variables store data and can be used in expressions."
                        }
                    ],
                    "pitfalls": [
                        "Forgetting proper indentation",
                        "Mixing tabs and spaces",
                        "Case sensitivity issues"
                    ],
                    "recap": "Python is a beginner-friendly language that emphasizes readability and simplicity."
                },
                "variables": {
                    "title": "Variables and Data Types",
                    "why_it_matters": "Variables are fundamental to programming - they store and manipulate data throughout your program.",
                    "key_ideas": [
                        "Variables are containers for data",
                        "Python has dynamic typing",
                        "Variable names should be descriptive",
                        "Multiple assignment is possible"
                    ],
                    "examples": [
                        {
                            "title": "Basic Variables",
                            "code": "x = 10\ny = 'Hello'\nz = True",
                            "explanation": "Different data types can be assigned to variables."
                        },
                        {
                            "title": "Multiple Assignment",
                            "code": "a, b, c = 1, 2, 3\nprint(a, b, c)",
                            "explanation": "Multiple variables can be assigned in one line."
                        }
                    ],
                    "pitfalls": [
                        "Using reserved keywords as variable names",
                        "Starting variable names with numbers",
                        "Overwriting built-in functions"
                    ],
                    "recap": "Variables are essential for storing and manipulating data in Python programs."
                }
            }
            
            with open(lessons_file, 'w') as f:
                json.dump(fallback_lessons, f, indent=2)
        
        # Fallback assessment questions
        questions_file = self.fallback_data_path / "questions.json"
        if not questions_file.exists():
            fallback_questions = {
                "python_basics": [
                    {
                        "text": "What is Python?",
                        "options": [
                            "A high-level programming language",
                            "A type of snake",
                            "A web browser",
                            "An operating system"
                        ],
                        "correct_answer": 0,
                        "explanation": "Python is a high-level, interpreted programming language known for its simplicity and readability.",
                        "difficulty": "easy",
                        "concept_tags": ["basics", "introduction"]
                    },
                    {
                        "text": "Which of the following is used to define code blocks in Python?",
                        "options": [
                            "Curly braces {}",
                            "Parentheses ()",
                            "Indentation",
                            "Square brackets []"
                        ],
                        "correct_answer": 2,
                        "explanation": "Python uses indentation (whitespace) to define code blocks, unlike many other languages that use braces.",
                        "difficulty": "easy",
                        "concept_tags": ["syntax", "indentation"]
                    },
                    {
                        "text": "What will be the output of: print(type(42))?",
                        "options": [
                            "<class 'str'>",
                            "<class 'int'>",
                            "<class 'float'>",
                            "<class 'number'>"
                        ],
                        "correct_answer": 1,
                        "explanation": "42 is an integer, so type(42) returns <class 'int'>.",
                        "difficulty": "medium",
                        "concept_tags": ["data_types", "built_in_functions"]
                    },
                    {
                        "text": "Which statement correctly creates a variable in Python?",
                        "options": [
                            "int x = 5;",
                            "var x = 5;",
                            "x = 5",
                            "declare x = 5"
                        ],
                        "correct_answer": 2,
                        "explanation": "Python uses simple assignment without type declarations or semicolons.",
                        "difficulty": "easy",
                        "concept_tags": ["variables", "syntax"]
                    }
                ],
                "variables": [
                    {
                        "text": "What is the correct way to assign multiple values to multiple variables?",
                        "options": [
                            "a = 1, b = 2, c = 3",
                            "a, b, c = 1, 2, 3",
                            "a = b = c = 1, 2, 3",
                            "assign a, b, c = 1, 2, 3"
                        ],
                        "correct_answer": 1,
                        "explanation": "Python supports tuple unpacking for multiple assignment: a, b, c = 1, 2, 3",
                        "difficulty": "medium",
                        "concept_tags": ["variables", "multiple_assignment"]
                    },
                    {
                        "text": "Which of the following is NOT a valid variable name in Python?",
                        "options": [
                            "my_variable",
                            "_private_var",
                            "2nd_variable",
                            "variable2"
                        ],
                        "correct_answer": 2,
                        "explanation": "Variable names cannot start with a number. They must start with a letter or underscore.",
                        "difficulty": "easy",
                        "concept_tags": ["variables", "naming_rules"]
                    }
                ]
            }
            
            with open(questions_file, 'w') as f:
                json.dump(fallback_questions, f, indent=2)
        
        # Fallback hints
        hints_file = self.fallback_data_path / "hints.json"
        if not hints_file.exists():
            fallback_hints = {
                "general": {
                    "hint_text": "Break down the problem into smaller steps. Think about what the question is really asking.",
                    "encouragement": "You're on the right track! Take your time to think through each option.",
                    "strategy": "Read each option carefully and eliminate the ones that are clearly incorrect."
                },
                "syntax": {
                    "hint_text": "Remember Python's syntax rules: indentation matters, no semicolons needed, and case sensitivity.",
                    "encouragement": "Syntax questions test your attention to detail. You've got this!",
                    "strategy": "Look for common syntax patterns you've learned."
                },
                "variables": {
                    "hint_text": "Think about how variables are created and used in Python. No type declarations needed!",
                    "encouragement": "Variables are fundamental - you're building important skills!",
                    "strategy": "Consider the rules for variable naming and assignment."
                },
                "data_types": {
                    "hint_text": "Python has several built-in data types: int, float, str, bool, list, dict, etc.",
                    "encouragement": "Understanding data types is key to effective programming!",
                    "strategy": "Think about what type of data each example represents."
                }
            }
            
            with open(hints_file, 'w') as f:
                json.dump(fallback_hints, f, indent=2)
    
    def get_fallback_lesson(self, topic_id: str, topic_name: str = None) -> Dict[str, Any]:
        """Get fallback lesson content for a topic."""
        try:
            lessons_file = self.fallback_data_path / "lessons.json"
            with open(lessons_file, 'r') as f:
                lessons = json.load(f)
            
            # Try to find exact match first
            if topic_id in lessons:
                return lessons[topic_id]
            
            # Try to find by topic name
            if topic_name:
                for key, lesson in lessons.items():
                    if topic_name.lower() in lesson.get('title', '').lower():
                        return lesson
            
            # Return default lesson
            return lessons.get('python_basics', {
                "title": "Python Programming",
                "why_it_matters": "Programming is a valuable skill in today's digital world.",
                "key_ideas": ["Practice makes perfect", "Start with basics", "Build incrementally"],
                "examples": [{"title": "Example", "code": "print('Hello!')", "explanation": "Basic output"}],
                "pitfalls": ["Don't rush", "Read carefully"],
                "recap": "Keep practicing and you'll improve!"
            })
            
        except Exception as e:
            logger.error(f"Failed to load fallback lesson: {e}")
            return {
                "title": "Programming Lesson",
                "why_it_matters": "Learning programming opens many opportunities.",
                "key_ideas": ["Practice regularly", "Learn from mistakes", "Ask questions"],
                "examples": [],
                "pitfalls": [],
                "recap": "Keep learning and practicing!"
            }
    
    def get_fallback_questions(self, topic_id: str, count: int = 4, difficulty: str = None) -> List[Dict[str, Any]]:
        """Get fallback assessment questions for a topic."""
        try:
            questions_file = self.fallback_data_path / "questions.json"
            with open(questions_file, 'r') as f:
                all_questions = json.load(f)
            
            # Get questions for the topic
            questions = all_questions.get(topic_id, all_questions.get('python_basics', []))
            
            # Filter by difficulty if specified
            if difficulty:
                questions = [q for q in questions if q.get('difficulty') == difficulty]
            
            # Return requested number of questions
            return questions[:count] if questions else self._get_default_questions(count)
            
        except Exception as e:
            logger.error(f"Failed to load fallback questions: {e}")
            return self._get_default_questions(count)
    
    def get_fallback_hint(self, context: str = "general", question_text: str = None) -> Dict[str, Any]:
        """Get fallback hint for a question."""
        try:
            hints_file = self.fallback_data_path / "hints.json"
            with open(hints_file, 'r') as f:
                hints = json.load(f)
            
            # Try to find context-specific hint
            if context in hints:
                return hints[context]
            
            # Return general hint
            return hints.get('general', {
                "hint_text": "Take your time and think through the problem step by step.",
                "encouragement": "You can do this! Every expert was once a beginner.",
                "strategy": "Break down complex problems into smaller, manageable parts."
            })
            
        except Exception as e:
            logger.error(f"Failed to load fallback hint: {e}")
            return {
                "hint_text": "Consider what you've learned so far and apply it to this question.",
                "encouragement": "Keep trying! Learning takes practice.",
                "strategy": "Review the key concepts and try again."
            }
    
    def _get_default_questions(self, count: int) -> List[Dict[str, Any]]:
        """Get default questions when no fallback questions are available."""
        default_question = {
            "text": "What is the primary goal of learning programming?",
            "options": [
                "To solve problems and create solutions",
                "To memorize syntax",
                "To compete with others",
                "To use complex algorithms"
            ],
            "correct_answer": 0,
            "explanation": "Programming is fundamentally about problem-solving and creating solutions to real-world challenges.",
            "difficulty": "easy",
            "concept_tags": ["general", "problem_solving"]
        }
        
        return [default_question] * min(count, 1)

class AIServiceFallbackManager:
    """Manages fallback strategies when AI services fail."""
    
    def __init__(self):
        self.content_provider = FallbackContentProvider()
        self.service_status = {}
        self.fallback_enabled = True
    
    def handle_ai_failure(self, service_name: str, operation: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle AI service failure and provide fallback response."""
        
        # Log the failure
        logger.warning(f"AI service {service_name} failed for operation {operation}")
        
        # Update service status
        self.service_status[service_name] = {
            "status": "unavailable",
            "last_failure": "now",
            "operation": operation
        }
        
        # Provide fallback based on operation type
        if operation == "generate_lesson":
            return self._handle_lesson_fallback(context)
        elif operation == "generate_questions":
            return self._handle_questions_fallback(context)
        elif operation == "generate_hint":
            return self._handle_hint_fallback(context)
        elif operation == "explain_concept":
            return self._handle_explanation_fallback(context)
        else:
            return self._handle_generic_fallback(context)
    
    def _handle_lesson_fallback(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle lesson generation fallback."""
        topic_id = context.get('topic_id', 'python_basics')
        topic_name = context.get('topic_name', '')
        
        fallback_lesson = self.content_provider.get_fallback_lesson(topic_id, topic_name)
        
        return {
            "success": True,
            "lesson_content": fallback_lesson,
            "fallback": True,
            "message": "Using offline lesson content due to AI service unavailability.",
            "recovery_suggestions": [
                "The lesson content is still educational and complete",
                "Try again later for AI-personalized content",
                "Contact support if issues persist"
            ]
        }
    
    def _handle_questions_fallback(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle question generation fallback."""
        topic_id = context.get('topic_id', 'python_basics')
        count = context.get('count', 4)
        difficulty = context.get('difficulty')
        
        fallback_questions = self.content_provider.get_fallback_questions(topic_id, count, difficulty)
        
        return {
            "success": True,
            "questions": fallback_questions,
            "fallback": True,
            "message": "Using pre-generated questions due to AI service unavailability.",
            "recovery_suggestions": [
                "These questions are still valid assessments",
                "Try again later for AI-generated questions",
                "Your progress will be saved normally"
            ]
        }
    
    def _handle_hint_fallback(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle hint generation fallback."""
        hint_context = context.get('context', 'general')
        question_text = context.get('question_text')
        
        fallback_hint = self.content_provider.get_fallback_hint(hint_context, question_text)
        
        return {
            "success": True,
            "hint": fallback_hint,
            "fallback": True,
            "message": "Using general guidance due to AI service unavailability.",
            "recovery_suggestions": [
                "The hint provides general problem-solving strategies",
                "Try again later for personalized hints",
                "Review the lesson content for additional help"
            ]
        }
    
    def _handle_explanation_fallback(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle concept explanation fallback."""
        concept = context.get('concept', 'programming concept')
        
        return {
            "success": True,
            "explanation": {
                "concept": concept,
                "explanation": f"This is an important {concept} in programming. Please refer to the lesson content for detailed information.",
                "examples": [],
                "related_concepts": []
            },
            "fallback": True,
            "message": "Using basic explanation due to AI service unavailability.",
            "recovery_suggestions": [
                "Check the lesson content for detailed explanations",
                "Try again later for AI-generated explanations",
                "Ask in the community forum for additional help"
            ]
        }
    
    def _handle_generic_fallback(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generic AI operation fallback."""
        return {
            "success": False,
            "error": "AI service temporarily unavailable",
            "fallback": True,
            "message": "The AI service is currently unavailable. Please try again later.",
            "recovery_suggestions": [
                "Try again in a few minutes",
                "Use alternative learning resources",
                "Contact support if the issue persists"
            ]
        }
    
    def is_service_available(self, service_name: str) -> bool:
        """Check if an AI service is currently available."""
        status = self.service_status.get(service_name, {})
        return status.get("status") != "unavailable"
    
    def mark_service_available(self, service_name: str):
        """Mark an AI service as available again."""
        self.service_status[service_name] = {
            "status": "available",
            "last_success": "now"
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all AI services."""
        return {
            "services": self.service_status,
            "fallback_enabled": self.fallback_enabled,
            "content_provider_ready": True
        }

# Global fallback manager instance
ai_fallback_manager = AIServiceFallbackManager()

def with_ai_fallback(service_name: str, operation: str):
    """Decorator to add AI fallback capability to functions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                # Try the original function
                result = func(*args, **kwargs)
                
                # Mark service as available on success
                ai_fallback_manager.mark_service_available(service_name)
                
                return result
                
            except Exception as e:
                # Handle AI service failure
                context = {
                    "args": args,
                    "kwargs": kwargs,
                    "error": str(e)
                }
                
                logger.warning(f"AI service {service_name} failed, using fallback: {e}")
                
                return ai_fallback_manager.handle_ai_failure(service_name, operation, context)
        
        return wrapper
    return decorator