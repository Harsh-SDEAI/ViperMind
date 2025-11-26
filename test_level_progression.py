#!/usr/bin/env python3
"""
Test script to verify level progression works correctly
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER = {
    "email": "test_progression@example.com",
    "username": "test_progression",
    "password": "testpass123"
}

def register_user():
    """Register a test user"""
    response = requests.post(f"{BASE_URL}/auth/register", json=TEST_USER)
    if response.status_code == 200:
        return response.json()["access_token"]
    elif response.status_code == 400 and "already registered" in response.json().get("detail", ""):
        # User already exists, try to login
        return login_user()
    else:
        raise Exception(f"Registration failed: {response.text}")

def login_user():
    """Login the test user"""
    response = requests.post(f"{BASE_URL}/auth/login", data={
        "username": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Login failed: {response.text}")

def get_headers(token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {token}"}

def test_level_progression():
    """Test the complete level progression flow"""
    print("🧪 Testing Level Progression Fix")
    print("=" * 50)
    
    # Step 1: Register/Login user
    print("1. Registering/logging in test user...")
    token = register_user()
    headers = get_headers(token)
    print("✅ User authenticated")
    
    # Step 2: Get initial curriculum state
    print("\n2. Getting initial curriculum state...")
    response = requests.get(f"{BASE_URL}/curriculum/progress", headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to get curriculum: {response.text}")
    
    curriculum = response.json()
    beginner_level = next((l for l in curriculum["levels"] if l["code"] == "B"), None)
    intermediate_level = next((l for l in curriculum["levels"] if l["code"] == "I"), None)
    
    print(f"✅ Beginner level unlocked: {beginner_level['is_unlocked']}")
    print(f"✅ Intermediate level unlocked: {intermediate_level['is_unlocked']}")
    
    # Step 3: Simulate completing beginner level
    print("\n3. Simulating beginner level completion...")
    
    # For testing, we'll create a mock level final assessment
    # In a real scenario, user would complete all topics and section tests first
    
    # Generate level final for beginner level
    print("   Generating level final assessment...")
    response = requests.post(f"{BASE_URL}/assessments/generate", 
                           json={
                               "target_id": beginner_level["id"],
                               "assessment_type": "level_final"
                           }, 
                           headers=headers)
    
    if response.status_code != 200:
        print(f"⚠️  Assessment generation failed: {response.text}")
        print("   This might be expected if prerequisites aren't met")
        return
    
    assessment = response.json()
    print(f"✅ Level final generated with {len(assessment['questions'])} questions")
    
    # Submit perfect answers to pass the level final
    print("   Submitting perfect answers...")
    answers = []
    for i, question in enumerate(assessment["questions"]):
        answers.append({
            "question_id": f"{assessment['assessment_id']}_{i}",
            "selected_answer": question["correct_answer"]
        })
    
    response = requests.post(f"{BASE_URL}/assessments/submit",
                           json={
                               "assessment_id": assessment["assessment_id"],
                               "answers": answers,
                               "time_taken": 1800  # 30 minutes
                           },
                           headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Assessment submission failed: {response.text}")
    
    result = response.json()
    print(f"✅ Assessment submitted - Score: {result['score']}%, Passed: {result['passed']}")
    
    # Check if level advancement occurred
    if result.get("next_steps", {}).get("level_advancement", {}).get("can_advance"):
        print("🎉 Level advancement detected!")
        advancement = result["next_steps"]["level_advancement"]
        print(f"   Advanced to: {advancement.get('level_name', 'Unknown')}")
    else:
        print("⚠️  No level advancement detected")
        print("   This might be because prerequisites aren't fully met")
    
    # Step 4: Check updated curriculum state
    print("\n4. Checking updated curriculum state...")
    response = requests.get(f"{BASE_URL}/curriculum/progress", headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to get updated curriculum: {response.text}")
    
    updated_curriculum = response.json()
    updated_intermediate = next((l for l in updated_curriculum["levels"] if l["code"] == "I"), None)
    
    print(f"✅ Intermediate level now unlocked: {updated_intermediate['is_unlocked']}")
    
    # Step 5: Verify user level was updated
    print("\n5. Checking user profile...")
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    if response.status_code == 200:
        user = response.json()
        print(f"✅ User current level: {user['current_level']}")
    
    print("\n" + "=" * 50)
    print("🎯 Level Progression Test Complete!")
    
    if updated_intermediate['is_unlocked']:
        print("✅ SUCCESS: Level progression is working correctly!")
    else:
        print("❌ ISSUE: Level progression may still have issues")
        print("   Check that all prerequisites are met:")
        print("   - All beginner topics completed")
        print("   - All beginner section tests passed with 75%+")
        print("   - Beginner level final passed with 80%+")

if __name__ == "__main__":
    try:
        test_level_progression()
    except Exception as e:
        print(f"❌ Test failed: {e}")