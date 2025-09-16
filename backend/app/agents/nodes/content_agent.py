"""
Content Generation Agent - Creates dynamic educational content
"""

from typing import Dict, Any, List
from app.agents.tools.openai_tool import OpenAITool
from app.agents.tools.database_tool import DatabaseTool


class ContentAgent:
    """Agent responsible for generating dynamic educational content"""
    
    def __init__(self):
        self.openai_tool = OpenAITool()
        self.database_tool = DatabaseTool()
        self.name = "content_agent"
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process content generation requests"""
        
        request_type = state.get("request_type")
        
        if request_type == "generate_examples":
            return self._generate_examples(state)
        elif request_type == "create_practice_problems":
            return self._create_practice_problems(state)
        elif request_type == "generate_analogies":
            return self._generate_analogies(state)
        elif request_type == "create_visual_explanations":
            return self._create_visual_explanations(state)
        elif request_type == "generate_remedial_content":
            return self._generate_remedial_content(state)
        else:
            return {
                **state,
                "error": f"Unknown content request type: {request_type}",
                "agent": self.name
            }
    
    def _generate_examples(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code examples tailored to user interests"""
        
        topic_name = state.get("topic_name")
        user_id = state.get("user_id")
        example_count = state.get("example_count", 3)
        
        if not topic_name:
            return {**state, "error": "No topic specified", "agent": self.name}
        
        # Get user context for personalization
        user_progress = self.database_tool.run("get_user_progress", user_id=user_id)
        user_level = user_progress.get("user", {}).get("current_level", "beginner")
        
        # Generate personalized examples
        examples_result = self.openai_tool.run(
            "generate_lesson_content",
            topic_name=topic_name,
            level=user_level,
            user_context=user_progress.get("user", {})
        )
        
        if not examples_result.get("success"):
            return {**state, "error": examples_result.get("error"), "agent": self.name}
        
        lesson_content = examples_result.get("lesson_content", {})
        examples = lesson_content.get("examples", [])
        
        return {
            **state,
            "generated_examples": examples[:example_count],
            "topic": topic_name,
            "agent": self.name,
            "success": True
        }
    
    def _create_practice_problems(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create practice problems with varying difficulty"""
        
        topic_name = state.get("topic_name")
        user_id = state.get("user_id")
        difficulty_levels = state.get("difficulty_levels", ["easy", "medium", "hard"])
        
        if not topic_name:
            return {**state, "error": "No topic specified", "agent": self.name}
        
        # Get user context
        user_progress = self.database_tool.run("get_user_progress", user_id=user_id)
        user_level = user_progress.get("user", {}).get("current_level", "beginner")
        
        practice_problems = []
        
        for difficulty in difficulty_levels:
            # Generate problems for each difficulty level
            problems_result = self.openai_tool.run(
                "generate_questions",
                topic_name=topic_name,
                level=user_level,
                count=2,
                difficulty=difficulty,
                user_performance=self._extract_user_performance(user_progress)
            )
            
            if problems_result.get("success"):
                problems = problems_result.get("questions", [])
                for problem in problems:
                    problem["difficulty"] = difficulty
                    problem["type"] = "practice_problem"
                
                practice_problems.extend(problems)
        
        return {
            **state,
            "practice_problems": practice_problems,
            "topic": topic_name,
            "agent": self.name,
            "success": True
        }
    
    def _generate_analogies(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analogies and metaphors for complex concepts"""
        
        concept = state.get("concept")
        user_id = state.get("user_id")
        
        if not concept:
            return {**state, "error": "No concept specified", "agent": self.name}
        
        # Get user context
        user_progress = self.database_tool.run("get_user_progress", user_id=user_id)
        user_level = user_progress.get("user", {}).get("current_level", "beginner")
        
        # Generate analogies using OpenAI
        analogy_result = self.openai_tool.run(
            "create_explanation",
            concept=f"Create analogies and metaphors to explain: {concept}",
            user_level=user_level,
            user_context=user_progress.get("user", {})
        )
        
        if not analogy_result.get("success"):
            return {**state, "error": analogy_result.get("error"), "agent": self.name}
        
        return {
            **state,
            "analogies": analogy_result.get("explanation"),
            "concept": concept,
            "agent": self.name,
            "success": True
        }
    
    def _create_visual_explanations(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create visual explanations and diagrams"""
        
        concept = state.get("concept")
        user_id = state.get("user_id")
        
        if not concept:
            return {**state, "error": "No concept specified", "agent": self.name}
        
        # Get user context
        user_progress = self.database_tool.run("get_user_progress", user_id=user_id)
        user_level = user_progress.get("user", {}).get("current_level", "beginner")
        
        # Generate visual explanation descriptions
        visual_result = self.openai_tool.run(
            "create_explanation",
            concept=f"Create a visual explanation with step-by-step diagrams for: {concept}",
            user_level=user_level,
            user_context=user_progress.get("user", {})
        )
        
        if not visual_result.get("success"):
            return {**state, "error": visual_result.get("error"), "agent": self.name}
        
        return {
            **state,
            "visual_explanation": visual_result.get("explanation"),
            "concept": concept,
            "agent": self.name,
            "success": True
        }
    
    def _generate_remedial_content(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate remedial content for struggling students"""
        
        topic_name = state.get("topic_name")
        user_id = state.get("user_id")
        struggle_areas = state.get("struggle_areas", [])
        
        if not topic_name:
            return {**state, "error": "No topic specified", "agent": self.name}
        
        # Get user context
        user_progress = self.database_tool.run("get_user_progress", user_id=user_id)
        user_level = user_progress.get("user", {}).get("current_level", "beginner")
        
        # Generate targeted remedial content
        remedial_result = self.openai_tool.run(
            "create_explanation",
            concept=f"Create remedial content for {topic_name}, focusing on these struggle areas: {', '.join(struggle_areas)}",
            user_level=user_level,
            user_context={
                **user_progress.get("user", {}),
                "struggle_areas": struggle_areas
            }
        )
        
        if not remedial_result.get("success"):
            return {**state, "error": remedial_result.get("error"), "agent": self.name}
        
        # Generate additional practice exercises
        practice_result = self.openai_tool.run(
            "generate_questions",
            topic_name=topic_name,
            level=user_level,
            count=3,
            difficulty="easy",
            user_performance={"struggle_areas": struggle_areas}
        )
        
        remedial_content = {
            "explanation": remedial_result.get("explanation"),
            "practice_exercises": practice_result.get("questions", []) if practice_result.get("success") else [],
            "focus_areas": struggle_areas,
            "additional_resources": self._generate_additional_resources(topic_name, struggle_areas)
        }
        
        return {
            **state,
            "remedial_content": remedial_content,
            "topic": topic_name,
            "agent": self.name,
            "success": True
        }
    
    def _extract_user_performance(self, user_progress: Dict) -> Dict:
        """Extract user performance data for content personalization"""
        
        topic_progress = user_progress.get("topic_progress", [])
        
        # Aggregate performance data
        all_struggle_areas = []
        all_strength_areas = []
        scores = []
        
        for progress in topic_progress:
            if progress.get("struggle_areas"):
                all_struggle_areas.extend(progress["struggle_areas"])
            if progress.get("strength_areas"):
                all_strength_areas.extend(progress["strength_areas"])
            if progress.get("best_score") is not None:
                scores.append(progress["best_score"])
        
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return {
            "struggle_areas": list(set(all_struggle_areas)),
            "strength_areas": list(set(all_strength_areas)),
            "average_score": avg_score,
            "total_topics_attempted": len(topic_progress)
        }
    
    def _generate_additional_resources(self, topic_name: str, struggle_areas: List[str]) -> List[Dict]:
        """Generate additional learning resources"""
        
        resources = []
        
        # Add conceptual resources
        resources.append({
            "type": "concept_review",
            "title": f"Review: {topic_name} Fundamentals",
            "description": "Go back to the basics and review core concepts"
        })
        
        # Add practice resources based on struggle areas
        for area in struggle_areas[:3]:  # Limit to top 3 struggle areas
            resources.append({
                "type": "targeted_practice",
                "title": f"Practice: {area}",
                "description": f"Focused exercises on {area}"
            })
        
        # Add general resources
        resources.extend([
            {
                "type": "interactive_examples",
                "title": "Interactive Code Examples",
                "description": "Step-through examples with explanations"
            },
            {
                "type": "video_explanation",
                "title": "Video Walkthrough",
                "description": "Visual explanation of key concepts"
            }
        ])
        
        return resources