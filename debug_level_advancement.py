#!/usr/bin/env python3
"""
Debug script to check why level advancement is not working
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"

def get_user_token():
    """Get user token - you'll need to provide your login credentials"""
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    
    response = requests.post(f"{BASE_URL}/auth/login", data={
        "username": email,
        "password": password
    })
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Login failed: {response.text}")

def debug_level_advancement():
    """Debug why level advancement is not working"""
    print("🔍 Debugging Level Advancement Issue")
    print("=" * 60)
    
    # Get user token
    token = get_user_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get user info
    print("\n1. Checking user information...")
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    if response.status_code == 200:
        user = response.json()
        print(f"   User: {user['username']} ({user['email']})")
        print(f"   Current Level: {user['current_level']}")
    else:
        print(f"   ❌ Failed to get user info: {response.text}")
        return
    
    # Get curriculum with progress
    print("\n2. Checking curriculum progress...")
    response = requests.get(f"{BASE_URL}/curriculum/progress", headers=headers)
    if response.status_code != 200:
        print(f"   ❌ Failed to get curriculum: {response.text}")
        return
    
    curriculum = response.json()
    beginner_level = next((l for l in curriculum["levels"] if l["code"] == "B"), None)
    intermediate_level = next((l for l in curriculum["levels"] if l["code"] == "I"), None)
    
    if not beginner_level:
        print("   ❌ Beginner level not found")
        return
    
    print(f"   Beginner Level Unlocked: {beginner_level['is_unlocked']}")
    print(f"   Beginner Completion: {beginner_level['completion_percentage']:.1f}%")
    print(f"   Intermediate Level Unlocked: {intermediate_level['is_unlocked']}")
    
    # Check beginner level requirements
    print("\n3. Checking beginner level requirements...")
    
    # Check all topics completion
    all_topics_completed = True
    total_topics = 0
    completed_topics = 0
    
    for section in beginner_level["sections"]:
        print(f"\n   Section {section['code']}: {section['name']}")
        section_topics = len(section["topics"])
        section_completed = sum(1 for t in section["topics"] if t.get("is_completed", False))
        
        print(f"     Topics: {section_completed}/{section_topics} completed")
        print(f"     Section Completion: {section.get('completion_percentage', 0):.1f}%")
        
        total_topics += section_topics
        completed_topics += section_completed
        
        for topic in section["topics"]:
            status = "✅" if topic.get("is_completed", False) else "❌"
            score = topic.get("progress_percentage", 0)
            print(f"     {status} {topic['name']} - {score:.1f}%")
            
            if not topic.get("is_completed", False):
                all_topics_completed = False
    
    print(f"\n   Overall Topics: {completed_topics}/{total_topics} completed")
    print(f"   All Topics Completed: {'✅' if all_topics_completed else '❌'}")
    
    # Check section test scores
    print("\n4. Checking section test requirements...")
    response = requests.get(f"{BASE_URL}/assessments/history?assessment_type=section_test", headers=headers)
    if response.status_code == 200:
        section_tests = response.json().get("assessments", [])
        
        # Group by target_id (section_id)
        section_scores = {}
        for test in section_tests:
            if test.get("passed") and test.get("score"):
                section_id = test["target_id"]
                if section_id not in section_scores or test["score"] > section_scores[section_id]:
                    section_scores[section_id] = test["score"]
        
        print(f"   Section Tests Passed: {len(section_scores)}")
        for section in beginner_level["sections"]:
            section_id = section["id"]
            score = section_scores.get(section_id, 0)
            status = "✅" if score >= 75 else "❌"
            print(f"   {status} {section['code']}: {score:.1f}% (need 75%)")
    else:
        print(f"   ❌ Failed to get section test history: {response.text}")
    
    # Check level final
    print("\n5. Checking level final requirement...")
    response = requests.get(f"{BASE_URL}/assessments/history?assessment_type=level_final", headers=headers)
    if response.status_code == 200:
        level_finals = response.json().get("assessments", [])
        
        beginner_final = None
        for final in level_finals:
            if final["target_id"] == beginner_level["id"]:
                if not beginner_final or final["score"] > beginner_final["score"]:
                    beginner_final = final
        
        if beginner_final:
            status = "✅" if beginner_final.get("passed") else "❌"
            score = beginner_final.get("score", 0)
            print(f"   {status} Beginner Level Final: {score:.1f}% (need 80%)")
        else:
            print("   ❌ No level final attempt found")
    else:
        print(f"   ❌ Failed to get level final history: {response.text}")
    
    # Check what's preventing advancement
    print("\n6. Diagnosing advancement blockers...")
    
    # Try to manually trigger level advancement check
    print("   Attempting to check level advancement...")
    response = requests.get(f"{BASE_URL}/progress/summary", headers=headers)
    if response.status_code == 200:
        summary = response.json()
        print(f"   Current Level Progress: {summary.get('current_level_progress', 0):.1f}%")
        print(f"   Topics Completed: {summary.get('topics_completed', 0)}")
        print(f"   Quizzes Passed: {summary.get('quizzes_passed', 0)}")
        print(f"   Section Tests Passed: {summary.get('section_tests_passed', 0)}")
        print(f"   Level Finals Passed: {summary.get('level_finals_passed', 0)}")
        
        next_unlock = summary.get('next_unlock')
        if next_unlock:
            print(f"   Next Unlock: {next_unlock['type']} - {next_unlock['name']}")
        else:
            print("   Next Unlock: None available")
    
    # Recommendations
    print("\n7. Recommendations:")
    print("   To advance to Intermediate level, you need:")
    print("   1. ✅ Complete all beginner topics")
    print("   2. ✅ Pass all section tests with 75%+ average")
    print("   3. ✅ Pass beginner level final with 80%+")
    print("\n   If all requirements are met but level is still locked:")
    print("   - Try refreshing the page")
    print("   - Check if there are any failed assessments to retake")
    print("   - Contact support if the issue persists")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        debug_level_advancement()
    except Exception as e:
        print(f"❌ Debug failed: {e}")