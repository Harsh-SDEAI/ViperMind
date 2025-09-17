"""
Database optimization utilities including index creation and query optimization.
"""
from sqlalchemy import text, Index
from sqlalchemy.orm import Session
from app.db.session import engine
from app.models.user import User
from app.models.curriculum import Level, Section, Topic, LessonContent
from app.models.progress import UserProgress, LevelProgress, LearningAnalytics
from app.models.assessment import Assessment, Question, Answer
from app.models.remedial import RemedialContent, ReviewSchedule
from app.models.personalization import UserProfile
import logging

logger = logging.getLogger(__name__)

def create_performance_indexes():
    """Create database indexes for optimal query performance."""
    
    indexes_to_create = [
        # User-related indexes
        Index('idx_users_email_active', User.email, User.is_active),
        Index('idx_users_username_active', User.username, User.is_active),
        Index('idx_users_current_level', User.current_level),
        
        # Curriculum indexes
        Index('idx_levels_code_order', Level.code, Level.order),
        Index('idx_sections_level_order', Section.level_id, Section.order),
        Index('idx_topics_section_order', Topic.section_id, Topic.order),
        Index('idx_lesson_contents_topic', LessonContent.topic_id),
        
        # Progress tracking indexes (most critical for performance)
        Index('idx_user_progress_user_status', UserProgress.user_id, UserProgress.status),
        Index('idx_user_progress_user_topic', UserProgress.user_id, UserProgress.topic_id),
        Index('idx_user_progress_user_level_section', UserProgress.user_id, UserProgress.level_id, UserProgress.section_id),
        Index('idx_user_progress_last_accessed', UserProgress.last_accessed),
        Index('idx_user_progress_updated_at', UserProgress.updated_at),
        
        Index('idx_level_progress_user_level', LevelProgress.user_id, LevelProgress.level_id),
        Index('idx_level_progress_user_unlocked', LevelProgress.user_id, LevelProgress.is_unlocked),
        Index('idx_level_progress_user_completed', LevelProgress.user_id, LevelProgress.is_completed),
        
        # Assessment indexes
        Index('idx_assessments_user_type', Assessment.user_id, Assessment.type),
        Index('idx_assessments_user_target', Assessment.user_id, Assessment.target_id),
        Index('idx_assessments_user_type_target', Assessment.user_id, Assessment.type, Assessment.target_id),
        Index('idx_assessments_submitted_at', Assessment.submitted_at),
        Index('idx_assessments_user_attempt', Assessment.user_id, Assessment.attempt_number),
        
        Index('idx_questions_assessment_order', Question.assessment_id, Question.order),
        Index('idx_questions_difficulty', Question.difficulty),
        
        Index('idx_answers_assessment_question', Answer.assessment_id, Answer.question_id),
        Index('idx_answers_assessment_correct', Answer.assessment_id, Answer.is_correct),
        
        # Analytics indexes
        Index('idx_learning_analytics_user_timestamp', LearningAnalytics.user_id, LearningAnalytics.timestamp),
        Index('idx_learning_analytics_user_activity', LearningAnalytics.user_id, LearningAnalytics.activity_type),
        Index('idx_learning_analytics_session', LearningAnalytics.session_id),
        Index('idx_learning_analytics_topic_timestamp', LearningAnalytics.topic_id, LearningAnalytics.timestamp),
        
        # Remedial content indexes
        Index('idx_remedial_content_user_assessment', RemedialContent.user_id, RemedialContent.assessment_id),
        Index('idx_remedial_content_user_completed', RemedialContent.user_id, RemedialContent.completed),
        
        Index('idx_review_schedules_user_due', ReviewSchedule.user_id, ReviewSchedule.due_date),
        Index('idx_review_schedules_user_completed', ReviewSchedule.user_id, ReviewSchedule.completed),
        
        # Personalization indexes
        Index('idx_user_profiles_user', UserProfile.user_id),
        Index('idx_user_profiles_learning_style', UserProfile.learning_style),
    ]
    
    try:
        with engine.begin() as conn:
            for index in indexes_to_create:
                try:
                    # Check if index already exists
                    index_name = index.name
                    result = conn.execute(text(f"""
                        SELECT 1 FROM pg_indexes 
                        WHERE indexname = '{index_name}'
                    """))
                    
                    if not result.fetchone():
                        index.create(conn)
                        logger.info(f"Created index: {index_name}")
                    else:
                        logger.info(f"Index already exists: {index_name}")
                        
                except Exception as e:
                    logger.error(f"Failed to create index {index.name}: {e}")
                    
        logger.info("Database index optimization completed")
        
    except Exception as e:
        logger.error(f"Database optimization failed: {e}")
        raise


def create_composite_indexes():
    """Create composite indexes for complex queries."""
    
    composite_indexes = [
        # Multi-column indexes for common query patterns
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_progress_composite_lookup 
        ON user_progress (user_id, level_id, section_id, topic_id, status);
        """,
        
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_assessment_performance_lookup 
        ON assessments (user_id, type, target_id, attempt_number, score);
        """,
        
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_learning_analytics_session_analysis 
        ON learning_analytics (user_id, session_id, activity_type, timestamp);
        """,
        
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_progress_time_tracking 
        ON user_progress (user_id, last_accessed, updated_at) 
        WHERE status IN ('in_progress', 'completed');
        """,
        
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_assessment_retake_eligibility 
        ON assessments (user_id, type, target_id, passed, attempt_number);
        """,
    ]
    
    try:
        with engine.begin() as conn:
            for sql in composite_indexes:
                try:
                    conn.execute(text(sql))
                    logger.info("Created composite index")
                except Exception as e:
                    logger.error(f"Failed to create composite index: {e}")
                    
        logger.info("Composite index creation completed")
        
    except Exception as e:
        logger.error(f"Composite index creation failed: {e}")


def optimize_database_settings():
    """Apply database-level optimizations."""
    
    optimization_queries = [
        # Update table statistics
        "ANALYZE;",
        
        # Set optimal work_mem for complex queries (session-level)
        "SET work_mem = '256MB';",
        
        # Enable parallel query execution
        "SET max_parallel_workers_per_gather = 4;",
        
        # Optimize random page cost for SSD storage
        "SET random_page_cost = 1.1;",
        
        # Increase effective_cache_size
        "SET effective_cache_size = '1GB';",
    ]
    
    try:
        with engine.begin() as conn:
            for query in optimization_queries:
                try:
                    conn.execute(text(query))
                    logger.info(f"Applied optimization: {query}")
                except Exception as e:
                    logger.error(f"Failed to apply optimization {query}: {e}")
                    
        logger.info("Database settings optimization completed")
        
    except Exception as e:
        logger.error(f"Database settings optimization failed: {e}")


def create_materialized_views():
    """Create materialized views for expensive aggregations."""
    
    materialized_views = [
        # User progress summary view
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS user_progress_summary AS
        SELECT 
            up.user_id,
            up.level_id,
            COUNT(*) as total_topics,
            COUNT(CASE WHEN up.status = 'completed' THEN 1 END) as completed_topics,
            AVG(up.best_score) as average_score,
            SUM(up.time_spent) as total_time_spent,
            MAX(up.updated_at) as last_activity
        FROM user_progress up
        GROUP BY up.user_id, up.level_id;
        """,
        
        # Assessment performance view
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS assessment_performance_summary AS
        SELECT 
            a.user_id,
            a.type,
            a.target_id,
            COUNT(*) as total_attempts,
            MAX(a.score) as best_score,
            AVG(a.score) as average_score,
            COUNT(CASE WHEN a.passed = true THEN 1 END) as passed_attempts,
            MAX(a.submitted_at) as last_attempt
        FROM assessments a
        GROUP BY a.user_id, a.type, a.target_id;
        """,
        
        # Learning analytics summary
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS daily_learning_analytics AS
        SELECT 
            la.user_id,
            DATE(la.timestamp) as activity_date,
            la.activity_type,
            COUNT(*) as activity_count,
            SUM(la.time_spent) as total_time,
            AVG(la.engagement_score) as avg_engagement
        FROM learning_analytics la
        GROUP BY la.user_id, DATE(la.timestamp), la.activity_type;
        """,
    ]
    
    try:
        with engine.begin() as conn:
            for view_sql in materialized_views:
                try:
                    conn.execute(text(view_sql))
                    logger.info("Created materialized view")
                except Exception as e:
                    logger.error(f"Failed to create materialized view: {e}")
                    
        logger.info("Materialized views creation completed")
        
    except Exception as e:
        logger.error(f"Materialized views creation failed: {e}")


def refresh_materialized_views():
    """Refresh all materialized views."""
    
    views_to_refresh = [
        "user_progress_summary",
        "assessment_performance_summary", 
        "daily_learning_analytics"
    ]
    
    try:
        with engine.begin() as conn:
            for view_name in views_to_refresh:
                try:
                    conn.execute(text(f"REFRESH MATERIALIZED VIEW {view_name};"))
                    logger.info(f"Refreshed materialized view: {view_name}")
                except Exception as e:
                    logger.error(f"Failed to refresh view {view_name}: {e}")
                    
        logger.info("Materialized views refresh completed")
        
    except Exception as e:
        logger.error(f"Materialized views refresh failed: {e}")


def run_full_optimization():
    """Run complete database optimization."""
    logger.info("Starting full database optimization...")
    
    try:
        create_performance_indexes()
        create_composite_indexes()
        create_materialized_views()
        optimize_database_settings()
        
        logger.info("Full database optimization completed successfully")
        
    except Exception as e:
        logger.error(f"Database optimization failed: {e}")
        raise


if __name__ == "__main__":
    run_full_optimization()