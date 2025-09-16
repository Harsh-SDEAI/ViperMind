"""
Analytics service for generating learning insights and progress analytics
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.user import User
from app.models.assessment import Assessment, AssessmentType
from app.models.progress import UserProgress, LevelProgress, ProgressStatus
from app.models.remedial import RemedialContent, RemedialStatus
from app.models.curriculum import Level, Section, Topic
from datetime import datetime, timedelta
import statistics

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard data for a user"""
        
        # Get basic user info
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        
        # Get overall progress statistics
        overall_stats = self._get_overall_progress_stats(user_id)
        
        # Get level progress
        level_progress = self._get_level_progress_summary(user_id)
        
        # Get recent activity
        recent_activity = self._get_recent_activity(user_id)
        
        # Get performance trends
        performance_trends = self._get_performance_trends(user_id)
        
        # Get learning insights
        learning_insights = self._generate_learning_insights(user_id)
        
        # Get recommendations
        recommendations = self._generate_recommendations(user_id)
        
        # Get achievement stats
        achievements = self._get_achievement_stats(user_id)
        
        return {
            "user_info": {
                "id": str(user.id),
                "username": user.username,
                "current_level": user.current_level.value,
                "member_since": user.created_at.isoformat()
            },
            "overall_stats": overall_stats,
            "level_progress": level_progress,
            "recent_activity": recent_activity,
            "performance_trends": performance_trends,
            "learning_insights": learning_insights,
            "recommendations": recommendations,
            "achievements": achievements
        }
    
    def _get_overall_progress_stats(self, user_id: str) -> Dict[str, Any]:
        """Get overall progress statistics"""
        
        # Get total topics and completed topics
        total_topics = self.db.query(Topic).count()
        completed_topics = self.db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.status == ProgressStatus.COMPLETED
        ).count()
        
        # Get assessment statistics
        total_assessments = self.db.query(Assessment).filter(
            Assessment.user_id == user_id,
            Assessment.submitted_at.isnot(None)
        ).count()
        
        passed_assessments = self.db.query(Assessment).filter(
            Assessment.user_id == user_id,
            Assessment.submitted_at.isnot(None),
            Assessment.passed == True
        ).count()
        
        # Get average scores by assessment type
        quiz_avg = self.db.query(func.avg(Assessment.score)).filter(
            Assessment.user_id == user_id,
            Assessment.type == AssessmentType.QUIZ,
            Assessment.submitted_at.isnot(None)
        ).scalar() or 0
        
        section_avg = self.db.query(func.avg(Assessment.score)).filter(
            Assessment.user_id == user_id,
            Assessment.type == AssessmentType.SECTION_TEST,
            Assessment.submitted_at.isnot(None)
        ).scalar() or 0
        
        final_avg = self.db.query(func.avg(Assessment.score)).filter(
            Assessment.user_id == user_id,
            Assessment.type == AssessmentType.LEVEL_FINAL,
            Assessment.submitted_at.isnot(None)
        ).scalar() or 0
        
        # Get total study time
        total_study_time = self.db.query(func.sum(UserProgress.time_spent)).filter(
            UserProgress.user_id == user_id
        ).scalar() or 0
        
        # Get remedial content stats
        remedial_assigned = self.db.query(RemedialContent).filter(
            RemedialContent.user_id == user_id
        ).count()
        
        remedial_completed = self.db.query(RemedialContent).filter(
            RemedialContent.user_id == user_id,
            RemedialContent.status == RemedialStatus.COMPLETED
        ).count()
        
        return {
            "topics_completed": completed_topics,
            "total_topics": total_topics,
            "completion_percentage": (completed_topics / total_topics * 100) if total_topics > 0 else 0,
            "assessments_taken": total_assessments,
            "assessments_passed": passed_assessments,
            "pass_rate": (passed_assessments / total_assessments * 100) if total_assessments > 0 else 0,
            "average_scores": {
                "quiz": round(quiz_avg, 1) if quiz_avg else 0,
                "section_test": round(section_avg, 1) if section_avg else 0,
                "level_final": round(final_avg, 1) if final_avg else 0
            },
            "total_study_time_minutes": round(total_study_time / 60),
            "remedial_stats": {
                "assigned": remedial_assigned,
                "completed": remedial_completed,
                "completion_rate": (remedial_completed / remedial_assigned * 100) if remedial_assigned > 0 else 0
            }
        }
    
    def _get_level_progress_summary(self, user_id: str) -> List[Dict[str, Any]]:
        """Get progress summary for each level"""
        
        levels = self.db.query(Level).order_by(Level.order).all()
        level_progress = []
        
        for level in levels:
            # Get sections in this level
            sections = self.db.query(Section).filter(Section.level_id == level.id).all()
            
            level_data = {
                "level_id": str(level.id),
                "level_name": level.name,
                "level_code": level.code,
                "sections": []
            }
            
            total_topics_in_level = 0
            completed_topics_in_level = 0
            
            for section in sections:
                # Get topics in this section
                topics = self.db.query(Topic).filter(Topic.section_id == section.id).all()
                total_topics_in_section = len(topics)
                total_topics_in_level += total_topics_in_section
                
                # Get completed topics in this section
                completed_topics_in_section = self.db.query(UserProgress).filter(
                    UserProgress.user_id == user_id,
                    UserProgress.section_id == section.id,
                    UserProgress.status == ProgressStatus.COMPLETED
                ).count()
                completed_topics_in_level += completed_topics_in_section
                
                # Get section test score
                section_test = self.db.query(Assessment).filter(
                    Assessment.user_id == user_id,
                    Assessment.type == AssessmentType.SECTION_TEST,
                    Assessment.target_id == section.id,
                    Assessment.submitted_at.isnot(None)
                ).order_by(desc(Assessment.score)).first()
                
                section_data = {
                    "section_id": str(section.id),
                    "section_name": section.name,
                    "section_code": section.code,
                    "total_topics": total_topics_in_section,
                    "completed_topics": completed_topics_in_section,
                    "completion_percentage": (completed_topics_in_section / total_topics_in_section * 100) if total_topics_in_section > 0 else 0,
                    "section_test_score": section_test.score if section_test else None,
                    "section_test_passed": section_test.passed if section_test else False
                }
                
                level_data["sections"].append(section_data)
            
            # Get level final score
            level_final = self.db.query(Assessment).filter(
                Assessment.user_id == user_id,
                Assessment.type == AssessmentType.LEVEL_FINAL,
                Assessment.target_id == level.id,
                Assessment.submitted_at.isnot(None)
            ).order_by(desc(Assessment.score)).first()
            
            level_data.update({
                "total_topics": total_topics_in_level,
                "completed_topics": completed_topics_in_level,
                "completion_percentage": (completed_topics_in_level / total_topics_in_level * 100) if total_topics_in_level > 0 else 0,
                "level_final_score": level_final.score if level_final else None,
                "level_final_passed": level_final.passed if level_final else False,
                "is_unlocked": self._is_level_unlocked(user_id, str(level.id)),
                "can_advance": self._can_advance_from_level(user_id, str(level.id))
            })
            
            level_progress.append(level_data)
        
        return level_progress
    
    def _get_recent_activity(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent learning activity"""
        
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Get recent assessments
        recent_assessments = self.db.query(Assessment).filter(
            Assessment.user_id == user_id,
            Assessment.submitted_at >= since_date
        ).order_by(desc(Assessment.submitted_at)).limit(10).all()
        
        # Get recent progress updates
        recent_progress = self.db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.last_accessed >= since_date
        ).order_by(desc(UserProgress.last_accessed)).limit(10).all()
        
        activities = []
        
        # Add assessment activities
        for assessment in recent_assessments:
            activities.append({
                "type": "assessment",
                "timestamp": assessment.submitted_at.isoformat(),
                "description": f"Completed {assessment.type.value.replace('_', ' ')} - {assessment.score}%",
                "score": assessment.score,
                "passed": assessment.passed,
                "assessment_type": assessment.type.value
            })
        
        # Add topic completion activities
        for progress in recent_progress:
            if progress.status == ProgressStatus.COMPLETED:
                topic = self.db.query(Topic).filter(Topic.id == progress.topic_id).first()
                activities.append({
                    "type": "topic_completion",
                    "timestamp": progress.last_accessed.isoformat(),
                    "description": f"Completed topic: {topic.name if topic else 'Unknown'}",
                    "topic_name": topic.name if topic else "Unknown"
                })
        
        # Sort by timestamp and return recent activities
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return activities[:15]
    
    def _get_performance_trends(self, user_id: str) -> Dict[str, Any]:
        """Get performance trends over time"""
        
        # Get assessments from last 30 days
        since_date = datetime.utcnow() - timedelta(days=30)
        
        assessments = self.db.query(Assessment).filter(
            Assessment.user_id == user_id,
            Assessment.submitted_at >= since_date,
            Assessment.submitted_at.isnot(None)
        ).order_by(Assessment.submitted_at).all()
        
        if not assessments:
            return {"trend": "insufficient_data", "message": "Not enough recent data for trend analysis"}
        
        # Calculate trend by assessment type
        trends = {}
        
        for assessment_type in [AssessmentType.QUIZ, AssessmentType.SECTION_TEST, AssessmentType.LEVEL_FINAL]:
            type_assessments = [a for a in assessments if a.type == assessment_type]
            
            if len(type_assessments) >= 3:
                scores = [a.score for a in type_assessments if a.score is not None]
                if scores:
                    # Simple trend calculation
                    first_half = scores[:len(scores)//2]
                    second_half = scores[len(scores)//2:]
                    
                    first_avg = statistics.mean(first_half)
                    second_avg = statistics.mean(second_half)
                    
                    trend_direction = "improving" if second_avg > first_avg else "declining" if second_avg < first_avg else "stable"
                    trend_magnitude = abs(second_avg - first_avg)
                    
                    trends[assessment_type.value] = {
                        "direction": trend_direction,
                        "magnitude": round(trend_magnitude, 1),
                        "current_average": round(second_avg, 1),
                        "previous_average": round(first_avg, 1),
                        "total_assessments": len(type_assessments)
                    }
        
        return trends
    
    def _generate_learning_insights(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate AI-powered learning insights"""
        
        insights = []
        
        # Analyze weak areas
        weak_concepts = self._get_weak_concepts(user_id)
        if weak_concepts:
            insights.append({
                "type": "weak_areas",
                "title": "Areas for Improvement",
                "message": f"You've struggled with {', '.join(weak_concepts[:3])}. Consider reviewing these topics.",
                "action": "review_concepts",
                "concepts": weak_concepts[:5]
            })
        
        # Analyze study patterns
        study_pattern = self._analyze_study_patterns(user_id)
        if study_pattern:
            insights.append(study_pattern)
        
        # Analyze assessment performance
        assessment_insight = self._analyze_assessment_performance(user_id)
        if assessment_insight:
            insights.append(assessment_insight)
        
        return insights
    
    def _generate_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate personalized recommendations"""
        
        recommendations = []
        
        # Check for incomplete remedial content
        incomplete_remedial = self.db.query(RemedialContent).filter(
            RemedialContent.user_id == user_id,
            RemedialContent.status != RemedialStatus.COMPLETED
        ).count()
        
        if incomplete_remedial > 0:
            recommendations.append({
                "type": "remedial_content",
                "priority": "high",
                "title": "Complete Remedial Content",
                "message": f"You have {incomplete_remedial} remedial activities waiting. Complete them to improve your understanding.",
                "action": "view_remedial_content"
            })
        
        # Check for available retakes
        failed_assessments = self.db.query(Assessment).filter(
            Assessment.user_id == user_id,
            Assessment.passed == False,
            Assessment.submitted_at.isnot(None)
        ).count()
        
        if failed_assessments > 0:
            recommendations.append({
                "type": "retake_assessments",
                "priority": "medium",
                "title": "Retake Failed Assessments",
                "message": f"You have {failed_assessments} failed assessments that you can retake to improve your scores.",
                "action": "view_failed_assessments"
            })
        
        # Check for next available content
        next_topic = self._get_next_available_topic(user_id)
        if next_topic:
            recommendations.append({
                "type": "continue_learning",
                "priority": "medium",
                "title": "Continue Learning",
                "message": f"Ready to learn about {next_topic['name']}? Start your next topic!",
                "action": "start_topic",
                "topic_id": next_topic["id"]
            })
        
        return recommendations
    
    def _get_achievement_stats(self, user_id: str) -> Dict[str, Any]:
        """Get achievement and milestone statistics"""
        
        # Get streak information
        current_streak = self._calculate_current_streak(user_id)
        longest_streak = self._calculate_longest_streak(user_id)
        
        # Get perfect scores
        perfect_scores = self.db.query(Assessment).filter(
            Assessment.user_id == user_id,
            Assessment.score == 100,
            Assessment.submitted_at.isnot(None)
        ).count()
        
        # Get first-try passes
        first_try_passes = self.db.query(Assessment).filter(
            Assessment.user_id == user_id,
            Assessment.attempt_number == 1,
            Assessment.passed == True,
            Assessment.submitted_at.isnot(None)
        ).count()
        
        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "perfect_scores": perfect_scores,
            "first_try_passes": first_try_passes,
            "badges_earned": self._calculate_badges_earned(user_id)
        }
    
    def _get_weak_concepts(self, user_id: str) -> List[str]:
        """Get concepts the user struggles with"""
        
        # Get failed assessments and extract weak concepts
        failed_assessments = self.db.query(Assessment).filter(
            Assessment.user_id == user_id,
            Assessment.passed == False,
            Assessment.submitted_at.isnot(None)
        ).all()
        
        weak_concepts = []
        for assessment in failed_assessments:
            if assessment.user_answers:
                for answer in assessment.user_answers:
                    if not answer.get("is_correct", True):
                        # Extract concept from question (simplified)
                        weak_concepts.append("Python Fundamentals")  # Placeholder
        
        # Get from remedial content
        remedial_content = self.db.query(RemedialContent).filter(
            RemedialContent.user_id == user_id
        ).all()
        
        for content in remedial_content:
            if content.weak_concepts:
                weak_concepts.extend(content.weak_concepts)
        
        # Count frequency and return most common
        concept_counts = {}
        for concept in weak_concepts:
            concept_counts[concept] = concept_counts.get(concept, 0) + 1
        
        return sorted(concept_counts.keys(), key=lambda x: concept_counts[x], reverse=True)
    
    def _analyze_study_patterns(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Analyze user's study patterns"""
        
        # Get recent progress data
        recent_progress = self.db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.last_accessed.isnot(None)
        ).order_by(desc(UserProgress.last_accessed)).limit(20).all()
        
        if len(recent_progress) < 5:
            return None
        
        # Analyze time spent patterns
        avg_time_per_topic = statistics.mean([p.time_spent for p in recent_progress if p.time_spent > 0])
        
        if avg_time_per_topic > 1800:  # 30 minutes
            return {
                "type": "study_pattern",
                "title": "Thorough Learner",
                "message": f"You spend an average of {int(avg_time_per_topic/60)} minutes per topic. Great attention to detail!",
                "pattern": "thorough"
            }
        elif avg_time_per_topic < 300:  # 5 minutes
            return {
                "type": "study_pattern",
                "title": "Quick Learner",
                "message": "You move through topics quickly. Consider spending more time on challenging concepts.",
                "pattern": "quick"
            }
        
        return None
    
    def _analyze_assessment_performance(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Analyze assessment performance patterns"""
        
        recent_assessments = self.db.query(Assessment).filter(
            Assessment.user_id == user_id,
            Assessment.submitted_at.isnot(None)
        ).order_by(desc(Assessment.submitted_at)).limit(10).all()
        
        if len(recent_assessments) < 3:
            return None
        
        pass_rate = sum(1 for a in recent_assessments if a.passed) / len(recent_assessments)
        
        if pass_rate >= 0.8:
            return {
                "type": "assessment_performance",
                "title": "Strong Performance",
                "message": f"You're passing {int(pass_rate*100)}% of your recent assessments. Keep up the excellent work!",
                "performance": "excellent"
            }
        elif pass_rate < 0.5:
            return {
                "type": "assessment_performance",
                "title": "Need More Practice",
                "message": f"You're passing {int(pass_rate*100)}% of recent assessments. Consider reviewing material more thoroughly.",
                "performance": "needs_improvement"
            }
        
        return None
    
    def _get_next_available_topic(self, user_id: str) -> Optional[Dict[str, str]]:
        """Get the next available topic for the user"""
        
        next_topic = self.db.query(Topic).join(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.status == ProgressStatus.AVAILABLE
        ).order_by(Topic.order).first()
        
        if next_topic:
            return {
                "id": str(next_topic.id),
                "name": next_topic.name
            }
        
        return None
    
    def _calculate_current_streak(self, user_id: str) -> int:
        """Calculate current learning streak"""
        
        # Get recent assessments ordered by date
        recent_assessments = self.db.query(Assessment).filter(
            Assessment.user_id == user_id,
            Assessment.submitted_at.isnot(None)
        ).order_by(desc(Assessment.submitted_at)).limit(20).all()
        
        streak = 0
        for assessment in recent_assessments:
            if assessment.passed:
                streak += 1
            else:
                break
        
        return streak
    
    def _calculate_longest_streak(self, user_id: str) -> int:
        """Calculate longest learning streak"""
        
        assessments = self.db.query(Assessment).filter(
            Assessment.user_id == user_id,
            Assessment.submitted_at.isnot(None)
        ).order_by(Assessment.submitted_at).all()
        
        max_streak = 0
        current_streak = 0
        
        for assessment in assessments:
            if assessment.passed:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def _calculate_badges_earned(self, user_id: str) -> List[Dict[str, str]]:
        """Calculate badges earned by the user"""
        
        badges = []
        
        # Perfect Score Badge
        perfect_scores = self.db.query(Assessment).filter(
            Assessment.user_id == user_id,
            Assessment.score == 100,
            Assessment.submitted_at.isnot(None)
        ).count()
        
        if perfect_scores >= 5:
            badges.append({"name": "Perfectionist", "description": "Earned 5+ perfect scores"})
        
        # Quick Learner Badge
        first_try_passes = self.db.query(Assessment).filter(
            Assessment.user_id == user_id,
            Assessment.attempt_number == 1,
            Assessment.passed == True,
            Assessment.submitted_at.isnot(None)
        ).count()
        
        if first_try_passes >= 10:
            badges.append({"name": "Quick Learner", "description": "Passed 10+ assessments on first try"})
        
        # Persistent Badge
        total_attempts = self.db.query(Assessment).filter(
            Assessment.user_id == user_id,
            Assessment.submitted_at.isnot(None)
        ).count()
        
        if total_attempts >= 50:
            badges.append({"name": "Persistent", "description": "Completed 50+ assessments"})
        
        return badges
    
    def _is_level_unlocked(self, user_id: str, level_id: str) -> bool:
        """Check if a level is unlocked for the user"""
        # Simplified - would implement proper unlock logic
        return True
    
    def _can_advance_from_level(self, user_id: str, level_id: str) -> bool:
        """Check if user can advance from this level"""
        # Simplified - would implement proper advancement logic
        level_final = self.db.query(Assessment).filter(
            Assessment.user_id == user_id,
            Assessment.type == AssessmentType.LEVEL_FINAL,
            Assessment.target_id == level_id,
            Assessment.passed == True
        ).first()
        
        return level_final is not None