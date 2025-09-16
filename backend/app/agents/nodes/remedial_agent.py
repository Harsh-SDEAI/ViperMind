"""
Remedial Agent for generating targeted remedial content based on assessment failures
"""

from typing import Dict, List, Any, Optional
from app.agents.tools.openai_tool import OpenAITool
from app.agents.tools.database_tool import DatabaseTool
import json

class RemedialAgent:
    def __init__(self):
        self.openai_tool = OpenAITool()
        self.db_tool = DatabaseTool()
    
    def generate_mini_explainer(self, user_id: str, assessment_data: Dict[str, Any], 
                               weak_concepts: List[str]) -> Dict[str, Any]:
        """Generate a mini-remedial explainer for failed quiz"""
        
        topic_name = assessment_data.get("topic_name", "Python Topic")
        score = assessment_data.get("score", 0)
        
        prompt = f"""
        Create a mini-remedial explainer for a student who scored {score}% on a quiz about {topic_name}.
        
        The student struggled with these concepts: {', '.join(weak_concepts)}
        
        Generate a concise but helpful explanation that:
        1. Identifies the key concepts they missed
        2. Provides clear, simple explanations
        3. Includes a practical code example
        4. Offers 2-3 actionable tips for improvement
        5. Encourages the student to try again
        
        Format as JSON with:
        {{
            "title": "Quick Review: [Topic Name]",
            "explanation": "Main explanation text",
            "code_example": "Python code example",
            "key_points": ["point1", "point2", "point3"],
            "tips": ["tip1", "tip2", "tip3"],
            "encouragement": "Motivational message"
        }}
        """
        
        try:
            response = self.openai_tool.generate_content(prompt, {
                "user_id": user_id,
                "assessment_type": "quiz",
                "weak_concepts": weak_concepts
            })
            
            # Parse JSON response
            content = json.loads(response)
            
            return {
                "success": True,
                "content": content,
                "type": "mini_explainer"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_content": self._get_fallback_explainer(topic_name, weak_concepts)
            }
    
    def generate_remedial_cards(self, user_id: str, assessment_data: Dict[str, Any], 
                               weak_concepts: List[str], cards_per_concept: int = 2) -> Dict[str, Any]:
        """Generate remedial cards for failed section test"""
        
        section_name = assessment_data.get("section_name", "Python Section")
        score = assessment_data.get("score", 0)
        
        cards = []
        
        for concept in weak_concepts:
            for i in range(cards_per_concept):
                prompt = f"""
                Create a remedial learning card for the concept "{concept}" in {section_name}.
                This is card {i+1} of {cards_per_concept} for this concept.
                
                The student scored {score}% on their section test and needs targeted help with this concept.
                
                Generate a focused learning card with:
                1. Clear explanation of the concept
                2. Practical Python code example
                3. A practice question with multiple choice answers
                4. 2-3 helpful hints
                5. Common mistakes to avoid
                
                Format as JSON:
                {{
                    "concept": "{concept}",
                    "explanation": "Clear explanation",
                    "code_example": "Python code with comments",
                    "practice_question": {{
                        "question": "Question text",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": 0,
                        "explanation": "Why this is correct"
                    }},
                    "hints": ["hint1", "hint2", "hint3"],
                    "common_mistakes": ["mistake1", "mistake2"]
                }}
                """
                
                try:
                    response = self.openai_tool.generate_content(prompt, {
                        "user_id": user_id,
                        "concept": concept,
                        "card_number": i + 1
                    })
                    
                    card_content = json.loads(response)
                    cards.append(card_content)
                    
                except Exception as e:
                    # Add fallback card
                    cards.append(self._get_fallback_card(concept))
        
        return {
            "success": True,
            "cards": cards,
            "type": "remedial_cards",
            "total_cards": len(cards)
        }
    
    def generate_review_schedule(self, user_id: str, assessment_data: Dict[str, Any], 
                                weak_concepts: List[str]) -> Dict[str, Any]:
        """Generate a review schedule for failed level final"""
        
        level_name = assessment_data.get("level_name", "Python Level")
        score = assessment_data.get("score", 0)
        
        prompt = f"""
        Create a comprehensive review schedule for a student who scored {score}% on the {level_name} final exam.
        
        They struggled with: {', '.join(weak_concepts)}
        
        Generate a 7-day review plan with:
        1. Daily study goals and activities
        2. Specific topics to review each day
        3. Practice exercises and resources
        4. Milestones to track progress
        5. Preparation for retake
        
        Format as JSON:
        {{
            "title": "7-Day Review Plan for {level_name}",
            "overview": "Plan description",
            "daily_schedule": [
                {{
                    "day": 1,
                    "title": "Day 1 title",
                    "topics": ["topic1", "topic2"],
                    "activities": ["activity1", "activity2"],
                    "goal": "Daily goal",
                    "estimated_time": "2-3 hours"
                }}
            ],
            "resources": ["resource1", "resource2"],
            "milestones": ["milestone1", "milestone2"],
            "retake_preparation": "Final preparation advice"
        }}
        """
        
        try:
            response = self.openai_tool.generate_content(prompt, {
                "user_id": user_id,
                "assessment_type": "level_final",
                "weak_concepts": weak_concepts
            })
            
            schedule_content = json.loads(response)
            
            return {
                "success": True,
                "schedule": schedule_content,
                "type": "review_schedule",
                "duration_days": 7
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_schedule": self._get_fallback_schedule(level_name, weak_concepts)
            }
    
    def _get_fallback_explainer(self, topic_name: str, weak_concepts: List[str]) -> Dict[str, Any]:
        """Fallback content when AI generation fails"""
        return {
            "title": f"Review: {topic_name}",
            "explanation": f"You had some difficulty with {', '.join(weak_concepts)}. Let's review these concepts step by step.",
            "code_example": "# Review the basic concepts\nprint('Practice makes perfect!')",
            "key_points": [
                "Review the fundamental concepts",
                "Practice with code examples",
                "Take your time to understand"
            ],
            "tips": [
                "Read through the lesson material again",
                "Try coding the examples yourself",
                "Don't hesitate to ask for help"
            ],
            "encouragement": "You're making progress! Keep practicing and you'll master these concepts."
        }
    
    def _get_fallback_card(self, concept: str) -> Dict[str, Any]:
        """Fallback remedial card when AI generation fails"""
        return {
            "concept": concept,
            "explanation": f"Let's review the concept of {concept}. This is an important topic that requires practice.",
            "code_example": f"# Example for {concept}\n# Practice this concept step by step",
            "practice_question": {
                "question": f"Which of the following best describes {concept}?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": 0,
                "explanation": "Review the lesson material for more details."
            },
            "hints": [
                "Review the lesson material",
                "Practice with examples",
                "Take your time"
            ],
            "common_mistakes": [
                "Not understanding the basics",
                "Rushing through examples"
            ]
        }
    
    def _get_fallback_schedule(self, level_name: str, weak_concepts: List[str]) -> Dict[str, Any]:
        """Fallback review schedule when AI generation fails"""
        return {
            "title": f"7-Day Review Plan for {level_name}",
            "overview": "A structured review plan to help you prepare for your retake.",
            "daily_schedule": [
                {
                    "day": i + 1,
                    "title": f"Day {i + 1}: Review Session",
                    "topics": weak_concepts[:2] if i < len(weak_concepts) else ["General Review"],
                    "activities": ["Review lesson materials", "Practice coding", "Take notes"],
                    "goal": "Strengthen understanding of key concepts",
                    "estimated_time": "2-3 hours"
                } for i in range(7)
            ],
            "resources": ["Lesson materials", "Code examples", "Practice exercises"],
            "milestones": ["Complete daily reviews", "Practice coding", "Self-assessment"],
            "retake_preparation": "Review all materials and practice coding before your retake."
        }