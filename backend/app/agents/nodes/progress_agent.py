"""
Progress Tracking Agent - Analyzes learning patterns and progress
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from app.agents.tools.openai_tool import OpenAITool
from app.agents.tools.database_tool import DatabaseTool


class ProgressAgent:
    """Agent responsible for tracking and analyzing learning progress"""
    
    def __init__(self):
        self.openai_tool = OpenAITool()
        self.database_tool = DatabaseTool()
        self.name = "progress_agent"
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process progress tracking requests"""
        
        request_type = state.get("request_type")
        
        if request_type == "analyze_patterns":
            return self._analyze_patterns(state)
        elif request_type == "predict_outcomes":
            return self._predict_outcomes(state)
        elif request_type == "recommend_difficulty":
            return self._recommend_difficulty(state)
        elif request_type == "generate_insights":
            return self._generate_insights(state)
        elif request_type == "calculate_progress":
            return self._calculate_progress(state)
        elif request_type == "update_progress":
            return self._update_progress(state)
        else:
            return {
                **state,
                "error": f"Unknown progress request type: {request_type}",
                "agent": self.name
            }
    
    def _analyze_patterns(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze learning patterns and behaviors"""
        
        user_id = state.get("user_id")
        
        # Get comprehensive user progress
        user_progress = self.database_tool.run("get_user_progress", user_id=user_id)
        
        if "error" in user_progress:
            return {**state, "error": user_progress["error"], "agent": self.name}
        
        topic_progress = user_progress.get("topic_progress", [])
        
        # Analyze learning patterns
        patterns = self._identify_learning_patterns(topic_progress)
        
        # Generate AI insights about patterns
        insights_result = self.openai_tool.run(
            "create_explanation",
            concept=f"Analyze these learning patterns and provide insights: {patterns}",
            user_level="intermediate",  # Analysis level
            user_context={"patterns": patterns}
        )
        
        return {
            **state,
            "learning_patterns": patterns,
            "pattern_insights": insights_result.get("explanation") if insights_result.get("success") else "Patterns analyzed successfully",
            "agent": self.name,
            "success": True
        }
    
    def _predict_outcomes(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Predict learning outcomes and completion times"""
        
        user_id = state.get("user_id")
        target_level = state.get("target_level")  # Optional: predict for specific level
        
        # Get user progress
        user_progress = self.database_tool.run("get_user_progress", user_id=user_id)
        
        if "error" in user_progress:
            return {**state, "error": user_progress["error"], "agent": self.name}
        
        # Calculate predictions
        predictions = self._calculate_predictions(user_progress, target_level)
        
        return {
            **state,
            "predictions": predictions,
            "agent": self.name,
            "success": True
        }
    
    def _recommend_difficulty(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend optimal difficulty adjustments"""
        
        user_id = state.get("user_id")
        topic_id = state.get("topic_id")
        
        # Get user progress
        user_progress = self.database_tool.run("get_user_progress", user_id=user_id)
        
        if "error" in user_progress:
            return {**state, "error": user_progress["error"], "agent": self.name}
        
        # Analyze performance for difficulty recommendation
        recommendation = self._analyze_difficulty_needs(user_progress, topic_id)
        
        return {
            **state,
            "difficulty_recommendation": recommendation,
            "agent": self.name,
            "success": True
        }
    
    def _generate_insights(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized learning insights"""
        
        user_id = state.get("user_id")
        
        # Get comprehensive data
        user_progress = self.database_tool.run("get_user_progress", user_id=user_id)
        
        if "error" in user_progress:
            return {**state, "error": user_progress["error"], "agent": self.name}
        
        # Generate comprehensive insights
        insights = self._create_comprehensive_insights(user_progress)
        
        # Use AI to enhance insights with personalized recommendations
        ai_insights_result = self.openai_tool.run(
            "provide_feedback",
            assessment_results=insights,
            user_context=user_progress.get("user", {})
        )
        
        if ai_insights_result.get("success"):
            insights["ai_recommendations"] = ai_insights_result.get("feedback")
        
        return {
            **state,
            "learning_insights": insights,
            "agent": self.name,
            "success": True
        }
    
    def _calculate_progress(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate detailed progress metrics"""
        
        user_id = state.get("user_id")
        level_id = state.get("level_id")  # Optional: calculate for specific level
        
        # Get user progress
        user_progress = self.database_tool.run("get_user_progress", user_id=user_id)
        
        if "error" in user_progress:
            return {**state, "error": user_progress["error"], "agent": self.name}
        
        # Calculate comprehensive progress metrics
        progress_metrics = self._calculate_detailed_metrics(user_progress, level_id)
        
        return {
            **state,
            "progress_metrics": progress_metrics,
            "agent": self.name,
            "success": True
        }
    
    def _update_progress(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Update user progress based on assessment results"""
        
        user_id = state.get("user_id")
        assessment_results = state.get("assessment_results")
        
        if not assessment_results:
            return {**state, "error": "No assessment results provided", "agent": self.name}
        
        # Update progress in database
        update_result = self.database_tool.run(
            "update_user_progress",
            user_id=user_id,
            topic_id=assessment_results.get("topic_id"),
            score=assessment_results.get("score"),
            status="completed" if assessment_results.get("passed") else "in_progress"
        )
        
        if not update_result.get("success"):
            return {**state, "error": update_result.get("error"), "agent": self.name}
        
        # Analyze what this means for overall progress
        progress_impact = self._analyze_progress_impact(assessment_results)
        
        return {
            **state,
            "progress_updated": True,
            "progress_impact": progress_impact,
            "agent": self.name,
            "success": True
        }
    
    def _identify_learning_patterns(self, topic_progress: List[Dict]) -> Dict[str, Any]:
        """Identify patterns in learning behavior"""
        
        patterns = {
            "learning_velocity": 0,
            "consistency": "unknown",
            "difficulty_preference": "medium",
            "strength_areas": [],
            "struggle_areas": [],
            "improvement_trend": "stable"
        }
        
        if not topic_progress:
            return patterns
        
        # Calculate learning velocity (topics completed per unit time)
        completed_topics = [p for p in topic_progress if p.get("status") == "completed"]
        patterns["learning_velocity"] = len(completed_topics)
        
        # Analyze consistency (variation in scores)
        scores = [p.get("best_score", 0) for p in topic_progress if p.get("best_score") is not None]
        if scores:
            score_variance = self._calculate_variance(scores)
            if score_variance < 100:  # Low variance
                patterns["consistency"] = "high"
            elif score_variance < 300:
                patterns["consistency"] = "medium"
            else:
                patterns["consistency"] = "low"
        
        # Aggregate strength and struggle areas
        all_strengths = []
        all_struggles = []
        
        for progress in topic_progress:
            if progress.get("strength_areas"):
                all_strengths.extend(progress["strength_areas"])
            if progress.get("struggle_areas"):
                all_struggles.extend(progress["struggle_areas"])
        
        patterns["strength_areas"] = list(set(all_strengths))[:5]  # Top 5
        patterns["struggle_areas"] = list(set(all_struggles))[:5]  # Top 5
        
        # Analyze improvement trend
        if len(scores) >= 3:
            recent_scores = scores[-3:]
            earlier_scores = scores[:-3] if len(scores) > 3 else scores[:1]
            
            recent_avg = sum(recent_scores) / len(recent_scores)
            earlier_avg = sum(earlier_scores) / len(earlier_scores)
            
            if recent_avg > earlier_avg + 10:
                patterns["improvement_trend"] = "improving"
            elif recent_avg < earlier_avg - 10:
                patterns["improvement_trend"] = "declining"
            else:
                patterns["improvement_trend"] = "stable"
        
        return patterns
    
    def _calculate_predictions(self, user_progress: Dict, target_level: str = None) -> Dict[str, Any]:
        """Calculate predictions for learning outcomes"""
        
        topic_progress = user_progress.get("topic_progress", [])
        level_progress = user_progress.get("level_progress", [])
        
        predictions = {
            "estimated_completion_time": "unknown",
            "success_probability": 0.5,
            "recommended_pace": "moderate",
            "next_milestone": "unknown"
        }
        
        if not topic_progress:
            return predictions
        
        # Calculate average time per topic (simplified)
        completed_topics = len([p for p in topic_progress if p.get("status") == "completed"])
        
        if completed_topics > 0:
            # Estimate based on current progress
            total_topics = 30  # Total topics in curriculum
            remaining_topics = total_topics - completed_topics
            
            # Simple prediction: assume current pace continues
            avg_score = sum(p.get("best_score", 0) for p in topic_progress if p.get("best_score")) / len(topic_progress)
            
            if avg_score > 80:
                predictions["estimated_completion_time"] = f"{remaining_topics * 2} days"
                predictions["success_probability"] = 0.9
                predictions["recommended_pace"] = "accelerated"
            elif avg_score > 60:
                predictions["estimated_completion_time"] = f"{remaining_topics * 3} days"
                predictions["success_probability"] = 0.7
                predictions["recommended_pace"] = "moderate"
            else:
                predictions["estimated_completion_time"] = f"{remaining_topics * 5} days"
                predictions["success_probability"] = 0.5
                predictions["recommended_pace"] = "careful"
        
        return predictions
    
    def _analyze_difficulty_needs(self, user_progress: Dict, topic_id: str = None) -> Dict[str, Any]:
        """Analyze and recommend difficulty adjustments"""
        
        topic_progress = user_progress.get("topic_progress", [])
        
        recommendation = {
            "current_difficulty": "medium",
            "recommended_difficulty": "medium",
            "reason": "Maintaining current difficulty level",
            "confidence": 0.5
        }
        
        if topic_id:
            # Analyze specific topic
            topic_data = next((p for p in topic_progress if p.get("topic_id") == topic_id), None)
            
            if topic_data:
                attempts = topic_data.get("attempts", 0)
                best_score = topic_data.get("best_score", 0)
                
                if attempts > 3 and best_score < 50:
                    recommendation.update({
                        "recommended_difficulty": "easy",
                        "reason": "Multiple attempts with low scores suggest need for easier content",
                        "confidence": 0.8
                    })
                elif best_score > 90 and attempts == 1:
                    recommendation.update({
                        "recommended_difficulty": "hard",
                        "reason": "High score on first attempt suggests readiness for harder content",
                        "confidence": 0.7
                    })
        else:
            # Analyze overall performance
            scores = [p.get("best_score", 0) for p in topic_progress if p.get("best_score") is not None]
            
            if scores:
                avg_score = sum(scores) / len(scores)
                
                if avg_score > 85:
                    recommendation.update({
                        "recommended_difficulty": "hard",
                        "reason": "Consistently high performance indicates readiness for increased difficulty",
                        "confidence": 0.8
                    })
                elif avg_score < 60:
                    recommendation.update({
                        "recommended_difficulty": "easy",
                        "reason": "Lower average scores suggest need for easier content to build confidence",
                        "confidence": 0.7
                    })
        
        return recommendation
    
    def _create_comprehensive_insights(self, user_progress: Dict) -> Dict[str, Any]:
        """Create comprehensive learning insights"""
        
        topic_progress = user_progress.get("topic_progress", [])
        level_progress = user_progress.get("level_progress", [])
        user_info = user_progress.get("user", {})
        
        insights = {
            "overall_performance": "developing",
            "learning_style": "balanced",
            "motivation_level": "moderate",
            "areas_of_excellence": [],
            "improvement_opportunities": [],
            "personalized_tips": [],
            "next_steps": []
        }
        
        if not topic_progress:
            return insights
        
        # Analyze overall performance
        scores = [p.get("best_score", 0) for p in topic_progress if p.get("best_score") is not None]
        
        if scores:
            avg_score = sum(scores) / len(scores)
            
            if avg_score >= 80:
                insights["overall_performance"] = "excellent"
            elif avg_score >= 70:
                insights["overall_performance"] = "good"
            elif avg_score >= 60:
                insights["overall_performance"] = "developing"
            else:
                insights["overall_performance"] = "needs_support"
        
        # Identify areas of excellence and improvement
        all_strengths = []
        all_struggles = []
        
        for progress in topic_progress:
            if progress.get("best_score", 0) >= 80:
                all_strengths.extend(progress.get("strength_areas", []))
            elif progress.get("best_score", 0) < 60:
                all_struggles.extend(progress.get("struggle_areas", []))
        
        insights["areas_of_excellence"] = list(set(all_strengths))[:3]
        insights["improvement_opportunities"] = list(set(all_struggles))[:3]
        
        # Generate personalized tips
        insights["personalized_tips"] = self._generate_personalized_tips(user_progress)
        
        # Suggest next steps
        insights["next_steps"] = self._suggest_next_steps(user_progress)
        
        return insights
    
    def _calculate_detailed_metrics(self, user_progress: Dict, level_id: str = None) -> Dict[str, Any]:
        """Calculate detailed progress metrics"""
        
        topic_progress = user_progress.get("topic_progress", [])
        level_progress = user_progress.get("level_progress", [])
        
        metrics = {
            "completion_rate": 0,
            "average_score": 0,
            "topics_completed": 0,
            "topics_in_progress": 0,
            "topics_not_started": 0,
            "time_spent_estimate": 0,
            "mastery_level": "beginner"
        }
        
        if topic_progress:
            completed = len([p for p in topic_progress if p.get("status") == "completed"])
            in_progress = len([p for p in topic_progress if p.get("status") == "in_progress"])
            total_topics = len(topic_progress)
            
            metrics.update({
                "completion_rate": (completed / total_topics) * 100 if total_topics > 0 else 0,
                "topics_completed": completed,
                "topics_in_progress": in_progress,
                "topics_not_started": total_topics - completed - in_progress
            })
            
            # Calculate average score
            scores = [p.get("best_score", 0) for p in topic_progress if p.get("best_score") is not None]
            if scores:
                metrics["average_score"] = sum(scores) / len(scores)
        
        # Determine mastery level
        if metrics["average_score"] >= 85 and metrics["completion_rate"] >= 80:
            metrics["mastery_level"] = "advanced"
        elif metrics["average_score"] >= 70 and metrics["completion_rate"] >= 60:
            metrics["mastery_level"] = "intermediate"
        else:
            metrics["mastery_level"] = "beginner"
        
        return metrics
    
    def _analyze_progress_impact(self, assessment_results: Dict) -> Dict[str, Any]:
        """Analyze the impact of recent assessment on overall progress"""
        
        impact = {
            "immediate_impact": "neutral",
            "long_term_implications": [],
            "recommended_actions": []
        }
        
        score = assessment_results.get("score", 0)
        passed = assessment_results.get("passed", False)
        
        if passed and score >= 80:
            impact["immediate_impact"] = "positive"
            impact["long_term_implications"].append("Strong understanding demonstrated")
            impact["recommended_actions"].append("Ready to advance to next topic")
        elif passed:
            impact["immediate_impact"] = "moderate"
            impact["long_term_implications"].append("Basic understanding achieved")
            impact["recommended_actions"].append("Consider reviewing before advancing")
        else:
            impact["immediate_impact"] = "concerning"
            impact["long_term_implications"].append("Gaps in understanding identified")
            impact["recommended_actions"].append("Review material before retaking")
        
        return impact
    
    def _calculate_variance(self, scores: List[float]) -> float:
        """Calculate variance in scores"""
        if len(scores) < 2:
            return 0
        
        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        return variance
    
    def _generate_personalized_tips(self, user_progress: Dict) -> List[str]:
        """Generate personalized learning tips"""
        
        tips = []
        topic_progress = user_progress.get("topic_progress", [])
        
        if not topic_progress:
            return ["Start with the basics and take your time to understand each concept"]
        
        # Analyze patterns and generate tips
        scores = [p.get("best_score", 0) for p in topic_progress if p.get("best_score") is not None]
        
        if scores:
            avg_score = sum(scores) / len(scores)
            
            if avg_score < 60:
                tips.append("Focus on understanding concepts before moving to practice")
                tips.append("Don't hesitate to review previous topics if needed")
            elif avg_score > 85:
                tips.append("You're doing great! Challenge yourself with harder problems")
                tips.append("Consider exploring real-world applications of these concepts")
            else:
                tips.append("You're making good progress! Keep practicing regularly")
                tips.append("Try explaining concepts to reinforce your understanding")
        
        return tips[:3]  # Limit to 3 tips
    
    def _suggest_next_steps(self, user_progress: Dict) -> List[str]:
        """Suggest next steps based on current progress"""
        
        steps = []
        topic_progress = user_progress.get("topic_progress", [])
        
        # Find next available topic
        available_topics = [p for p in topic_progress if p.get("status") == "available"]
        in_progress_topics = [p for p in topic_progress if p.get("status") == "in_progress"]
        
        if in_progress_topics:
            steps.append("Complete your current in-progress topics")
        
        if available_topics:
            steps.append("Start the next available topic in your learning path")
        
        steps.append("Review and practice concepts you've learned")
        steps.append("Take assessments to test your understanding")
        
        return steps[:3]  # Limit to 3 steps