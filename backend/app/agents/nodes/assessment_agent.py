"""
Assessment Agent - Creates and evaluates dynamic assessments
"""

from typing import Dict, Any, List
from app.agents.tools.openai_tool import OpenAITool
from app.agents.tools.database_tool import DatabaseTool


class AssessmentAgent:
    """Agent responsible for creating and evaluating assessments"""
    
    def __init__(self):
        self.openai_tool = OpenAITool()
        self.database_tool = DatabaseTool()
        self.name = "assessment_agent"
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process assessment-related requests"""
        
        request_type = state.get("request_type")
        
        if request_type == "generate_quiz":
            return self._generate_quiz(state)
        elif request_type == "generate_test":
            return self._generate_test(state)
        elif request_type == "generate_final":
            return self._generate_final(state)
        elif request_type == "evaluate_assessment":
            return self._evaluate_assessment(state)
        elif request_type == "analyze_performance":
            return self._analyze_performance(state)
        else:
            return {
                **state,
                "error": f"Unknown assessment request type: {request_type}",
                "agent": self.name
            }
    
    def _generate_quiz(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a topic quiz (4 questions)"""
        
        topic_id = state.get("topic_id")
        user_id = state.get("user_id")
        
        # Get topic details
        topic_result = self.database_tool.run("get_topic_details", topic_id=topic_id)
        if "error" in topic_result:
            return {**state, "error": topic_result["error"], "agent": self.name}
        
        # Get user performance history for personalization
        user_progress = self.database_tool.run("get_user_progress", user_id=user_id)
        
        topic_name = topic_result["topic"]["name"]
        level = topic_result["level"]["name"].lower()
        
        # Determine difficulty based on user performance
        difficulty = self._determine_difficulty(user_progress, topic_id)
        
        # Generate questions
        questions_result = self.openai_tool.run(
            "generate_questions",
            topic_name=topic_name,
            level=level,
            count=4,
            difficulty=difficulty,
            user_performance=self._extract_performance_context(user_progress, topic_id)
        )
        
        if not questions_result.get("success"):
            return {**state, "error": questions_result.get("error"), "agent": self.name}
        
        return {
            **state,
            "questions": questions_result["questions"],
            "assessment_type": "quiz",
            "target_id": topic_id,
            "difficulty": difficulty,
            "total_questions": 4,
            "passing_score": 70,
            "agent": self.name,
            "success": True
        }
    
    def _generate_test(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate section test (15 questions) or level final (30 questions)"""
        
        test_type = state.get("test_type")  # "section_test" or "level_final"
        target_id = state.get("target_id")  # section_id or level_id
        user_id = state.get("user_id")
        
        question_count = 15 if test_type == "section_test" else 30
        passing_score = 75 if test_type == "section_test" else 80
        
        # Get curriculum structure
        curriculum = self.database_tool.run("get_curriculum_structure")
        
        # Get user progress
        user_progress = self.database_tool.run("get_user_progress", user_id=user_id)
        
        # Find topics to test based on target
        topics_to_test = self._get_topics_for_test(curriculum, target_id, test_type)
        
        if not topics_to_test:
            return {**state, "error": "No topics found for test", "agent": self.name}
        
        # Generate questions across topics
        all_questions = []
        questions_per_topic = max(1, question_count // len(topics_to_test))
        
        for topic in topics_to_test:
            topic_questions_result = self.openai_tool.run(
                "generate_questions",
                topic_name=topic["name"],
                level=topic.get("level", "beginner"),
                count=questions_per_topic,
                difficulty="medium",
                user_performance=self._extract_performance_context(user_progress, topic["id"])
            )
            
            if topic_questions_result.get("success"):
                all_questions.extend(topic_questions_result["questions"][:questions_per_topic])
        
        # Ensure we have the right number of questions
        all_questions = all_questions[:question_count]
        
        return {
            **state,
            "questions": all_questions,
            "assessment_type": test_type,
            "target_id": target_id,
            "total_questions": len(all_questions),
            "passing_score": passing_score,
            "topics_covered": [topic["name"] for topic in topics_to_test],
            "agent": self.name,
            "success": True
        }
    
    def _generate_final(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate level final exam (comprehensive test)"""
        
        target_id = state.get("target_id")  # level_id
        user_id = state.get("user_id")
        question_count = state.get("question_count", 20)
        
        # Get curriculum structure
        curriculum = self.database_tool.run("get_curriculum_structure")
        
        # Get user progress
        user_progress = self.database_tool.run("get_user_progress", user_id=user_id)
        
        # Find all topics in the level
        topics_to_test = self._get_topics_for_test(curriculum, target_id, "level_final")
        
        if not topics_to_test:
            return {**state, "error": "No topics found for level final", "agent": self.name}
        
        # Generate questions across all topics in the level
        all_questions = []
        questions_per_topic = max(1, question_count // len(topics_to_test))
        
        for topic in topics_to_test:
            topic_questions_result = self.openai_tool.run(
                "generate_questions",
                topic_name=topic["name"],
                level=topic.get("level", "beginner"),
                count=questions_per_topic,
                difficulty="medium",  # Level finals are comprehensive, medium difficulty
                user_performance=self._extract_performance_context(user_progress, topic["id"])
            )
            
            if topic_questions_result.get("success"):
                all_questions.extend(topic_questions_result["questions"][:questions_per_topic])
        
        # Ensure we have the right number of questions
        all_questions = all_questions[:question_count]
        
        return {
            **state,
            "questions": all_questions,
            "assessment_type": "level_final",
            "target_id": target_id,
            "total_questions": len(all_questions),
            "passing_score": 80,  # Level finals require 80% to pass
            "topics_covered": [topic["name"] for topic in topics_to_test],
            "agent": self.name,
            "success": True
        }
    
    def _evaluate_assessment(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate assessment results and provide feedback"""
        
        assessment_data = state.get("assessment")
        user_answers = state.get("user_answers", [])
        user_id = state.get("user_id")
        
        if not assessment_data or not user_answers:
            return {**state, "error": "Missing assessment data or answers", "agent": self.name}
        
        questions = assessment_data.get("questions", [])
        total_questions = len(questions)
        correct_answers = 0
        
        # Calculate score
        for i, answer in enumerate(user_answers):
            if i < len(questions):
                correct_index = questions[i].get("correct_answer", -1)
                if answer.get("selected_option") == correct_index:
                    correct_answers += 1
        
        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        passing_score = assessment_data.get("passing_score", 70)
        passed = score >= passing_score
        
        # Generate AI feedback
        feedback_result = self.openai_tool.run(
            "provide_feedback",
            assessment_results={
                "score": score,
                "correct_answers": correct_answers,
                "total_questions": total_questions,
                "passed": passed,
                "assessment_type": assessment_data.get("type")
            },
            user_context={"user_id": user_id}
        )
        
        # Save results to database
        save_result = self.database_tool.run(
            "save_assessment_results",
            user_id=user_id,
            assessment_type=assessment_data.get("type"),
            target_id=assessment_data.get("target_id") or assessment_data.get("topic_id"),
            score=score,
            passed=passed,
            ai_feedback=feedback_result.get("feedback") if feedback_result.get("success") else None
        )
        
        return {
            **state,
            "assessment_results": {
                "score": score,
                "correct_answers": correct_answers,
                "total_questions": total_questions,
                "passed": passed,
                "feedback": feedback_result.get("feedback") if feedback_result.get("success") else "Great job completing the assessment!",
                "assessment_id": save_result.get("assessment_id") if save_result.get("success") else None
            },
            "agent": self.name,
            "success": True
        }
    
    def _analyze_performance(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user performance patterns and suggest improvements"""
        
        user_id = state.get("user_id")
        
        # Get comprehensive user progress
        user_progress = self.database_tool.run("get_user_progress", user_id=user_id)
        
        if "error" in user_progress:
            return {**state, "error": user_progress["error"], "agent": self.name}
        
        # Analyze patterns
        topic_progress = user_progress.get("topic_progress", [])
        level_progress = user_progress.get("level_progress", [])
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        for progress in topic_progress:
            if progress.get("best_score", 0) >= 80:
                strengths.extend(progress.get("strength_areas", []))
            elif progress.get("best_score", 0) < 60:
                weaknesses.extend(progress.get("struggle_areas", []))
        
        # Calculate overall performance metrics
        scores = [p.get("best_score", 0) for p in topic_progress if p.get("best_score") is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return {
            **state,
            "performance_analysis": {
                "average_score": avg_score,
                "strengths": list(set(strengths)),
                "weaknesses": list(set(weaknesses)),
                "topics_completed": len([p for p in topic_progress if p.get("status") == "completed"]),
                "topics_in_progress": len([p for p in topic_progress if p.get("status") == "in_progress"]),
                "recommendations": self._generate_recommendations(avg_score, weaknesses, strengths)
            },
            "agent": self.name,
            "success": True
        }
    
    def _determine_difficulty(self, user_progress: Dict, topic_id: str) -> str:
        """Determine appropriate difficulty based on user performance"""
        
        topic_progress = user_progress.get("topic_progress", [])
        user_level = user_progress.get("user", {}).get("current_level", "beginner")
        
        # Find this topic's progress
        current_topic = next((p for p in topic_progress if p.get("topic_id") == topic_id), None)
        
        if current_topic:
            attempts = current_topic.get("attempts", 0) or 0
            best_score = current_topic.get("best_score") or 0
            
            if attempts > 2 and best_score < 60:
                return "easy"
            elif best_score > 80:
                return "hard"
        
        # Default based on user level
        level_difficulty_map = {
            "beginner": "easy",
            "intermediate": "medium",
            "advanced": "hard"
        }
        
        return level_difficulty_map.get(user_level, "medium")
    
    def _extract_performance_context(self, user_progress: Dict, topic_id: str) -> Dict:
        """Extract relevant performance context for question generation"""
        
        topic_progress = user_progress.get("topic_progress", [])
        current_topic = next((p for p in topic_progress if p.get("topic_id") == topic_id), None)
        
        if current_topic:
            return {
                "attempts": current_topic.get("attempts", 0) or 0,
                "best_score": current_topic.get("best_score") or 0,
                "struggle_areas": current_topic.get("struggle_areas", []) or [],
                "strength_areas": current_topic.get("strength_areas", []) or []
            }
        
        return {}
    
    def _get_topics_for_test(self, curriculum: Dict, target_id: str, test_type: str) -> List[Dict]:
        """Get topics that should be included in the test"""
        
        topics = []
        
        for level in curriculum.get("curriculum", []):
            for section in level.get("sections", []):
                if test_type == "section_test" and section.get("id") == target_id:
                    for topic in section.get("topics", []):
                        topics.append({
                            "id": topic["id"],
                            "name": topic["name"],
                            "level": level["name"].lower()
                        })
                elif test_type == "level_final" and level.get("id") == target_id:
                    for section in level.get("sections", []):
                        for topic in section.get("topics", []):
                            topics.append({
                                "id": topic["id"],
                                "name": topic["name"],
                                "level": level["name"].lower()
                            })
        
        return topics
    
    def _generate_recommendations(self, avg_score: float, weaknesses: List[str], strengths: List[str]) -> List[str]:
        """Generate personalized recommendations based on performance"""
        
        recommendations = []
        
        if avg_score < 60:
            recommendations.append("Focus on reviewing fundamental concepts before moving forward")
            recommendations.append("Consider spending more time on practice exercises")
        elif avg_score < 75:
            recommendations.append("You're making good progress! Focus on areas where you struggled")
            recommendations.append("Try explaining concepts to reinforce your understanding")
        else:
            recommendations.append("Excellent work! You're ready for more challenging material")
            recommendations.append("Consider exploring advanced applications of these concepts")
        
        if weaknesses:
            recommendations.append(f"Pay special attention to: {', '.join(weaknesses[:3])}")
        
        if strengths:
            recommendations.append(f"Build on your strengths in: {', '.join(strengths[:3])}")
        
        return recommendations