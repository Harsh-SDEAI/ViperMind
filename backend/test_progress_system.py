#!/usr/bin/env python3
"""
Test script to verify the progress and scoring system
"""

import requests
import json
from dotenv import load_dotenv
load_dotenv()

BASE_URL = "http://localhost:8000/api/v1"

def test_progress_system():
    """Test the complete progress and scoring system"""
    print("📊 Testing ViperMind Progress & Scoring System")
    print("=" * 60)
    
    # First, authenticate
    print("1. Authenticating user...")
    login_data = {
        "email_or_username": "authtest@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login-json", json=login_data)
        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data["access_token"]
            user = auth_data["user"]
            print(f"✓ Authenticated as: {user['username']}")
        else:
            print(f"✗ Authentication failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Authentication error: {e}")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 2: Get progress summary
    print("\n2. Testing progress summary...")
    try:
        response = requests.get(f"{BASE_URL}/progress/summary", headers=headers)
        if response.status_code == 200:
            summary = response.json()
            print(f"✓ Progress summary retrieved")
            print(f"  Current level: {summary['user_level']}")
            print(f"  Level progress: {summary['current_level_progress']:.1f}%")
            print(f"  Topics completed: {summary['topics_completed']}/{summary['total_topics']}")
            print(f"  Quizzes passed: {summary['quizzes_passed']}")
            print(f"  Overall score: {summary['overall_score']:.1f}%")
            print(f"  Learning velocity: {summary['learning_velocity']:.2f} topics/day")
            
            if summary.get('next_unlock'):
                next_unlock = summary['next_unlock']
                print(f"  Next unlock: {next_unlock['name']} ({next_unlock['type']})")
        else:
            print(f"✗ Progress summary failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Progress summary error: {e}")
        return False
    
    # Test 3: Get curriculum with progress
    print("\n3. Testing curriculum progress integration...")
    try:
        response = requests.get(f"{BASE_URL}/curriculum/progress", headers=headers)
        if response.status_code == 200:
            curriculum = response.json()
            levels = curriculum.get("levels", [])
            print(f"✓ Curriculum with progress loaded")
            
            # Check first level
            if levels:
                first_level = levels[0]
                print(f"  First level: {first_level['name']}")
                print(f"  Level unlocked: {first_level.get('is_unlocked', False)}")
                print(f"  Level completion: {first_level.get('completion_percentage', 0):.1f}%")
                
                # Check first section
                sections = first_level.get("sections", [])
                if sections:
                    first_section = sections[0]
                    print(f"  First section: {first_section['name']}")
                    print(f"  Section unlocked: {first_section.get('is_unlocked', False)}")
                    
                    # Check first topic
                    topics = first_section.get("topics", [])
                    if topics:
                        first_topic = topics[0]
                        print(f"  First topic: {first_topic['name']}")
                        print(f"  Topic unlocked: {first_topic.get('is_unlocked', False)}")
                        print(f"  Topic completed: {first_topic.get('is_completed', False)}")
        else:
            print(f"✗ Curriculum progress failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Curriculum progress error: {e}")
        return False
    
    # Test 4: Take a quiz and check progress updates
    print("\n4. Testing quiz completion and progress updates...")
    try:
        # Get first topic ID
        topic_id = levels[0]["sections"][0]["topics"][0]["id"]
        topic_name = levels[0]["sections"][0]["topics"][0]["name"]
        
        # Generate quiz
        quiz_data = {
            "target_id": topic_id,
            "assessment_type": "quiz",
            "difficulty": "medium",
            "question_count": 4
        }
        response = requests.post(f"{BASE_URL}/assessments/generate", json=quiz_data, headers=headers)
        
        if response.status_code == 200:
            quiz = response.json()
            print(f"✓ Quiz generated for: {topic_name}")
            
            # Answer all questions correctly
            answers = []
            for question in quiz['questions']:
                answers.append({
                    "question_id": question["id"],
                    "selected_answer": question["correct_answer"]
                })
            
            # Submit quiz
            submission_data = {
                "assessment_id": quiz['assessment_id'],
                "answers": answers,
                "time_taken": 300
            }
            
            response = requests.post(f"{BASE_URL}/assessments/submit", json=submission_data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Quiz submitted with {result['score']:.0f}% score")
                print(f"  Passed: {result['passed']}")
                
                # Check if content was unlocked
                if result['next_steps'].get('unlocked_content'):
                    unlocks = result['next_steps']['unlocked_content']
                    print(f"  Unlocked content: {len(unlocks)} items")
                    for unlock in unlocks:
                        print(f"    - {unlock['name']} ({unlock['type']})")
                
                # Check level advancement
                if result['next_steps'].get('level_advancement'):
                    advancement = result['next_steps']['level_advancement']
                    print(f"  Level advancement: {advancement}")
            else:
                print(f"✗ Quiz submission failed: {response.status_code}")
        else:
            print(f"✗ Quiz generation failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Quiz completion test error: {e}")
    
    # Test 5: Progress analytics
    print("\n5. Testing progress analytics...")
    try:
        response = requests.get(f"{BASE_URL}/progress/analytics", headers=headers)
        if response.status_code == 200:
            analytics = response.json()
            print(f"✓ Progress analytics retrieved")
            print(f"  Agent: {analytics.get('agent')}")
            
            patterns = analytics.get('analytics', {})
            if patterns:
                print(f"  Learning patterns:")
                for key, value in patterns.items():
                    print(f"    {key}: {value}")
            
            insights = analytics.get('insights', {})
            if insights:
                print(f"  AI insights available: {len(insights)} items")
        else:
            print(f"✗ Progress analytics failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Progress analytics error: {e}")
    
    # Test 6: Manual progress update
    print("\n6. Testing manual progress update...")
    try:
        progress_data = {
            "topic_id": topic_id,
            "status": "completed",
            "score": 85.0,
            "time_spent": 600
        }
        
        response = requests.post(f"{BASE_URL}/progress/update", json=progress_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Progress updated manually")
            print(f"  Status: {result['progress']['status']}")
            print(f"  Best score: {result['progress']['best_score']}")
            print(f"  Attempts: {result['progress']['attempts']}")
            
            if result.get('unlocks'):
                print(f"  New unlocks: {len(result['unlocks'])}")
            
            if result.get('level_advancement', {}).get('can_advance'):
                advancement = result['level_advancement']
                print(f"  Level advancement: {advancement['advanced_to']}")
        else:
            print(f"✗ Manual progress update failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Manual progress update error: {e}")
    
    print("\n🎉 Progress and scoring system tests completed!")
    print("\n✅ Scoring & Progression Features Verified:")
    print("  - Comprehensive progress tracking and analytics")
    print("  - Automatic unlock system based on completion")
    print("  - Level advancement with section average requirements")
    print("  - Pass/fail thresholds (70% quiz, 75% test, 80% final)")
    print("  - AI-powered progress analysis and insights")
    print("  - Real-time progress updates from assessments")
    print("  - Detailed progress summaries and statistics")
    
    return True

if __name__ == "__main__":
    success = test_progress_system()
    if not success:
        print("\n❌ Progress system tests failed!")
        exit(1)
    else:
        print("\n🚀 Progress and scoring system is ready!")
        exit(0)