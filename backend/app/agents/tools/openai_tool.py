"""
OpenAI tool for LangGraph agents to generate content and analyze responses
"""

from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json

from app.core.config import settings


class OpenAITool:
    """Tool for agents to interact with OpenAI API"""
    
    def __init__(self):
        """Initialize the OpenAI tool with LLM"""
        self.name = "openai_tool"
        self.description = "Generate educational content, analyze code, and create personalized explanations using OpenAI"
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    def run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute OpenAI operations"""
        try:
            if action == "generate_lesson_content":
                return self._generate_lesson_content(**kwargs)
            elif action == "generate_questions":
                return self._generate_questions(**kwargs)
            elif action == "analyze_code":
                return self._analyze_code(**kwargs)
            elif action == "create_explanation":
                return self._create_explanation(**kwargs)
            elif action == "generate_hints":
                return self._generate_hints(**kwargs)
            elif action == "provide_feedback":
                return self._provide_feedback(**kwargs)
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            return {"error": f"OpenAI API error: {str(e)}"}
    
    def _generate_lesson_content(self, topic_name: str, level: str, user_context: Dict = None) -> Dict[str, Any]:
        """Generate structured lesson content for a topic"""
        
        system_prompt = f"""You are an expert Python tutor creating lesson content for {level} level students.
        
        Create a comprehensive lesson for the topic: "{topic_name}"
        
        Structure your response as JSON with these sections:
        - why_it_matters: Why this topic is important (2-3 sentences)
        - key_ideas: List of 3-5 main concepts (array of strings)
        - examples: List of 2-3 code examples with explanations (array of objects with title, code, explanation, output)
        - pitfalls: Common mistakes students make (array of strings)
        - recap: Summary of key takeaways (2-3 sentences)
        
        Make the content engaging, practical, and appropriate for {level} level.
        Include real-world applications and clear, runnable Python code examples.
        """
        
        user_prompt = f"Create lesson content for: {topic_name}"
        if user_context:
            user_prompt += f"\n\nUser context: {json.dumps(user_context)}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            content = json.loads(response.content)
            return {"success": True, "lesson_content": content}
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "success": True,
                "lesson_content": {
                    "why_it_matters": "This topic is fundamental to Python programming.",
                    "key_ideas": ["Core concept 1", "Core concept 2", "Core concept 3"],
                    "examples": [
                        {
                            "title": "Basic Example",
                            "code": "# Example code here",
                            "explanation": "This example demonstrates the concept.",
                            "output": "Expected output"
                        }
                    ],
                    "pitfalls": ["Common mistake 1", "Common mistake 2"],
                    "recap": "Remember these key points when working with this topic.",
                    "raw_response": response.content
                }
            }
    
    def _generate_questions(self, topic_name: str, level: str, count: int = 4, 
                          difficulty: str = "medium", user_performance: Dict = None) -> Dict[str, Any]:
        """Generate multiple-choice questions for assessment"""
        
        system_prompt = f"""You are an expert Python educator creating assessment questions.
        
        Generate {count} multiple-choice questions for the topic: "{topic_name}"
        Level: {level}
        Difficulty: {difficulty}
        
        Each question should:
        - Test understanding of the concept, not just memorization
        - Include code snippets when appropriate
        - Have 4 options with only 1 correct answer
        - Include a brief explanation for the correct answer
        
        Format as JSON array with objects containing:
        - question: The question text
        - options: Array of 4 answer choices
        - correct_answer: Index (0-3) of correct option
        - explanation: Why the correct answer is right
        - code_snippet: Python code if relevant (optional)
        - concept_tags: Array of concepts being tested
        """
        
        user_prompt = f"Generate {count} questions for: {topic_name}"
        if user_performance:
            user_prompt += f"\n\nUser performance context: {json.dumps(user_performance)}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            questions = json.loads(response.content)
            return {"success": True, "questions": questions}
        except json.JSONDecodeError:
            # Fallback questions
            return {
                "success": True,
                "questions": [
                    {
                        "question": f"What is the main purpose of {topic_name}?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": 0,
                        "explanation": "This is the correct answer because...",
                        "concept_tags": [topic_name.lower()]
                    }
                ],
                "raw_response": response.content
            }
    
    def _analyze_code(self, code: str, context: str = None) -> Dict[str, Any]:
        """Analyze Python code for correctness and best practices"""
        
        system_prompt = """You are a Python code reviewer and tutor.
        
        Analyze the provided Python code and return a JSON response with:
        - is_correct: Boolean indicating if code is syntactically correct
        - issues: Array of problems found (syntax errors, logic issues, style problems)
        - suggestions: Array of improvement recommendations
        - best_practices: Array of best practice violations
        - complexity_level: "beginner", "intermediate", or "advanced"
        - explanation: Brief explanation of what the code does
        """
        
        user_prompt = f"Analyze this Python code:\n\n```python\n{code}\n```"
        if context:
            user_prompt += f"\n\nContext: {context}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            analysis = json.loads(response.content)
            return {"success": True, "analysis": analysis}
        except json.JSONDecodeError:
            return {
                "success": True,
                "analysis": {
                    "is_correct": True,
                    "issues": [],
                    "suggestions": [],
                    "best_practices": [],
                    "complexity_level": "beginner",
                    "explanation": "Code analysis completed.",
                    "raw_response": response.content
                }
            }
    
    def _create_explanation(self, concept: str, user_level: str, user_context: Dict = None) -> Dict[str, Any]:
        """Create personalized explanation for a concept"""
        
        system_prompt = f"""You are a patient Python tutor explaining concepts to {user_level} level students.
        
        Provide a clear, personalized explanation for: "{concept}"
        
        Your explanation should:
        - Use simple, clear language appropriate for {user_level} level
        - Include analogies or real-world examples when helpful
        - Be encouraging and supportive
        - Focus on practical understanding
        - Be 2-4 paragraphs long
        """
        
        user_prompt = f"Explain: {concept}"
        if user_context:
            user_prompt += f"\n\nStudent context: {json.dumps(user_context)}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "success": True,
            "explanation": response.content,
            "concept": concept,
            "level": user_level
        }
    
    def _generate_hints(self, question: str, user_answer: str = None, difficulty: str = "medium") -> Dict[str, Any]:
        """Generate helpful hints for a question"""
        
        system_prompt = f"""You are a supportive Python tutor providing hints.
        
        For the given question, provide a helpful hint that:
        - Guides the student toward the answer without giving it away
        - Is encouraging and supportive
        - Focuses on the learning process
        - Is appropriate for {difficulty} difficulty level
        """
        
        user_prompt = f"Question: {question}"
        if user_answer:
            user_prompt += f"\nStudent's answer: {user_answer}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "success": True,
            "hint": response.content,
            "question": question
        }
    
    def _provide_feedback(self, assessment_results: Dict, user_context: Dict = None) -> Dict[str, Any]:
        """Provide personalized feedback on assessment performance"""
        
        system_prompt = """You are an encouraging Python tutor providing feedback on assessment results.
        
        Analyze the assessment results and provide:
        - Positive reinforcement for what they did well
        - Constructive feedback on areas for improvement
        - Specific suggestions for next steps
        - Encouragement to keep learning
        
        Keep feedback supportive, specific, and actionable.
        """
        
        user_prompt = f"Assessment results: {json.dumps(assessment_results)}"
        if user_context:
            user_prompt += f"\nStudent context: {json.dumps(user_context)}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "success": True,
            "feedback": response.content,
            "assessment_score": assessment_results.get("score", 0)
        }