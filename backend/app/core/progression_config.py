"""
Progression Configuration for ViperMind
Centralized configuration for all progression requirements
"""

from typing import Dict, Any
from pydantic import BaseModel
import os

class ProgressionThresholds(BaseModel):
    """Configuration for progression thresholds"""
    
    # Quiz pass thresholds (by assessment type)
    quiz_pass_threshold: float = 10.0
    section_test_pass_threshold: float = 15.0
    level_final_pass_threshold: float = 10.0
    
    # Section completion requirements
    section_average_requirement: float = 15.0  # Average quiz score needed to complete section
    section_test_requirement: float = 15.0     # Section test score needed
    
    # Level completion requirements
    level_section_average_requirement: float = 15.0  # All sections must have this average
    level_final_requirement: float = 10.0            # Level final score needed
    
    # Topic completion requirements
    topic_quiz_requirement: float = 10.0  # Quiz score needed to complete topic
    
    # Advanced settings
    require_all_topics_completed: bool = True      # Must complete all topics in section
    require_all_section_tests_passed: bool = True  # Must pass all section tests
    require_level_final_passed: bool = True        # Must pass level final
    
    # Retake limits
    quiz_max_attempts: int = 999        # Unlimited quiz attempts
    section_test_max_attempts: int = 2  # 1 initial + 1 retake
    level_final_max_attempts: int = 2   # 1 initial + 1 retake

class ProgressionConfig:
    """Centralized progression configuration"""
    
    def __init__(self):
        self.thresholds = self._load_config()
    
    def _load_config(self) -> ProgressionThresholds:
        """Load configuration from environment variables or defaults"""
        
        # Load from environment variables with defaults
        config_data = {
            "quiz_pass_threshold": float(os.getenv("QUIZ_PASS_THRESHOLD", "70.0")),
            "section_test_pass_threshold": float(os.getenv("SECTION_TEST_PASS_THRESHOLD", "75.0")),
            "level_final_pass_threshold": float(os.getenv("LEVEL_FINAL_PASS_THRESHOLD", "80.0")),
            
            "section_average_requirement": float(os.getenv("SECTION_AVERAGE_REQUIREMENT", "75.0")),
            "section_test_requirement": float(os.getenv("SECTION_TEST_REQUIREMENT", "75.0")),
            
            "level_section_average_requirement": float(os.getenv("LEVEL_SECTION_AVERAGE_REQUIREMENT", "75.0")),
            "level_final_requirement": float(os.getenv("LEVEL_FINAL_REQUIREMENT", "80.0")),
            
            "topic_quiz_requirement": float(os.getenv("TOPIC_QUIZ_REQUIREMENT", "70.0")),
            
            "require_all_topics_completed": os.getenv("REQUIRE_ALL_TOPICS_COMPLETED", "true").lower() == "true",
            "require_all_section_tests_passed": os.getenv("REQUIRE_ALL_SECTION_TESTS_PASSED", "true").lower() == "true",
            "require_level_final_passed": os.getenv("REQUIRE_LEVEL_FINAL_PASSED", "true").lower() == "true",
            
            "quiz_max_attempts": int(os.getenv("QUIZ_MAX_ATTEMPTS", "999")),
            "section_test_max_attempts": int(os.getenv("SECTION_TEST_MAX_ATTEMPTS", "2")),
            "level_final_max_attempts": int(os.getenv("LEVEL_FINAL_MAX_ATTEMPTS", "2")),
        }
        
        return ProgressionThresholds(**config_data)
    
    def get_pass_threshold(self, assessment_type: str) -> float:
        """Get pass threshold for assessment type"""
        thresholds = {
            "quiz": self.thresholds.quiz_pass_threshold,
            "section_test": self.thresholds.section_test_pass_threshold,
            "level_final": self.thresholds.level_final_pass_threshold,
        }
        return thresholds.get(assessment_type, 70.0)
    
    def get_max_attempts(self, assessment_type: str) -> int:
        """Get max attempts for assessment type"""
        attempts = {
            "quiz": self.thresholds.quiz_max_attempts,
            "section_test": self.thresholds.section_test_max_attempts,
            "level_final": self.thresholds.level_final_max_attempts,
        }
        return attempts.get(assessment_type, 2)
    
    def update_thresholds(self, **kwargs) -> None:
        """Update thresholds dynamically"""
        current_data = self.thresholds.dict()
        current_data.update(kwargs)
        self.thresholds = ProgressionThresholds(**current_data)
    
    def get_section_requirements(self) -> Dict[str, float]:
        """Get all section-level requirements"""
        return {
            "average_requirement": self.thresholds.section_average_requirement,
            "test_requirement": self.thresholds.section_test_requirement,
            "topic_quiz_requirement": self.thresholds.topic_quiz_requirement,
        }
    
    def get_level_requirements(self) -> Dict[str, float]:
        """Get all level-level requirements"""
        return {
            "section_average_requirement": self.thresholds.level_section_average_requirement,
            "final_requirement": self.thresholds.level_final_requirement,
        }

# Global configuration instance
progression_config = ProgressionConfig()

# Convenience functions
def get_pass_threshold(assessment_type: str) -> float:
    """Get pass threshold for assessment type"""
    return progression_config.get_pass_threshold(assessment_type)

def get_max_attempts(assessment_type: str) -> int:
    """Get max attempts for assessment type"""
    return progression_config.get_max_attempts(assessment_type)

def get_section_average_requirement() -> float:
    """Get section average requirement"""
    return progression_config.thresholds.section_average_requirement

def get_level_final_requirement() -> float:
    """Get level final requirement"""
    return progression_config.thresholds.level_final_requirement

def update_progression_config(**kwargs) -> None:
    """Update progression configuration"""
    progression_config.update_thresholds(**kwargs)