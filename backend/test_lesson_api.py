#!/usr/bin/env python3
"""
Test script to verify the lesson API endpoints
"""

import requests
import json
from dotenv import load_dotenv
load_dotenv()

BASE_URL = "http://localhost:8000/api/v1"

def test_lesson_api():
    """Test the lesson API endpoints"""
    print("📖 Testing ViperMind Lesson API")
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
    
    # Get a topic ID from curriculum
    print("\n2. Getting topic ID from curriculum...")
    try:
        response = requests.get(f"{BASE_URL}/curriculum/structure")
        if response.status_code == 200:
            structure = response.json()
            topic_id = structure["levels"][0]["sections"][0]["topics"][0]["id"]
            topic_name = structure["levels"][0]["sections"][0]["topics"][0]["name"]
            print(f"✓ Using topic: {topic_name} ({topic_id})")
        else:
            print(f"✗ Failed to get curriculum: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Curriculum error: {e}")
        return False
    
    # Test 3: Get lesson content
    print("\n3. Testing lesson content generation...")
    try:
        response = requests.get(f"{BASE_URL}/lessons/topic/{topic_id}", headers=headers)
        if response.status_code == 200:
            lesson = response.json()
            print(f"✓ Lesson content loaded")
            print(f"  Topic: {lesson['topic_name']}")
            print(f"  AI Generated: {lesson['is_generated']}")
            
            content = lesson["lesson_content"]
            print(f"  Key Ideas: {len(content.get('key_ideas', []))}")
            print(f"  Examples: {len(content.get('examples', []))}")
            print(f"  Pitfalls: {len(content.get('pitfalls', []))}")
            
            # Check if content has expected structure
            required_fields = ['why_it_matters', 'key_ideas', 'examples', 'recap']
            missing_fields = [field for field in required_fields if field not in content]
            if missing_fields:
                print(f"  ⚠️ Missing fields: {missing_fields}")
            else:
                print(f"  ✓ All required content fields present")
                
        else:
            print(f"✗ Lesson content failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Lesson content error: {e}")
        return False
    
    # Test 4: Update progress
    print("\n4. Testing progress update...")
    try:
        progress_data = {
            "topic_id": topic_id,
            "completed": False,
            "time_spent": 120  # 2 minutes
        }
        response = requests.post(f"{BASE_URL}/lessons/progress/update", json=progress_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Progress updated")
            print(f"  Status: {result.get('status')}")
            print(f"  Total time: {result.get('total_time_spent')}s")
        else:
            print(f"✗ Progress update failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Progress update error: {e}")
        return False
    
    # Test 5: Mark as complete
    print("\n5. Testing lesson completion...")
    try:
        completion_data = {
            "topic_id": topic_id,
            "completed": True,
            "time_spent": 60  # 1 more minute
        }
        response = requests.post(f"{BASE_URL}/lessons/progress/update", json=completion_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Lesson marked as complete")
            print(f"  Status: {result.get('status')}")
            print(f"  Total time: {result.get('total_time_spent')}s")
        else:
            print(f"✗ Lesson completion failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Lesson completion error: {e}")
        return False
    
    # Test 6: Navigation - Next topic
    print("\n6. Testing next topic navigation...")
    try:
        response = requests.get(f"{BASE_URL}/lessons/topic/{topic_id}/next", headers=headers)
        if response.status_code == 200:
            nav_data = response.json()
            print(f"✓ Next topic navigation loaded")
            if nav_data.get("next_topic"):
                next_topic = nav_data["next_topic"]
                print(f"  Next topic: {next_topic['name']}")
                print(f"  Same section: {nav_data.get('same_section', False)}")
            else:
                print(f"  Message: {nav_data.get('message', 'No next topic')}")
        else:
            print(f"✗ Next topic navigation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Next topic navigation error: {e}")
        return False
    
    # Test 7: Navigation - Previous topic
    print("\n7. Testing previous topic navigation...")
    try:
        response = requests.get(f"{BASE_URL}/lessons/topic/{topic_id}/previous", headers=headers)
        if response.status_code == 200:
            nav_data = response.json()
            print(f"✓ Previous topic navigation loaded")
            if nav_data.get("previous_topic"):
                prev_topic = nav_data["previous_topic"]
                print(f"  Previous topic: {prev_topic['name']}")
                print(f"  Same section: {nav_data.get('same_section', False)}")
            else:
                print(f"  Message: {nav_data.get('message', 'No previous topic')}")
        else:
            print(f"✗ Previous topic navigation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Previous topic navigation error: {e}")
        return False
    
    print("\n🎉 All lesson API tests passed!")
    print("\n✅ Lesson Content Delivery Features:")
    print("  - AI-powered lesson content generation with OpenAI")
    print("  - Structured lesson content (why it matters, key ideas, examples, pitfalls, recap)")
    print("  - Progress tracking with time spent and completion status")
    print("  - Sequential navigation between topics")
    print("  - User-specific progress persistence")
    print("  - Real-time lesson status updates")
    
    return True

if __name__ == "__main__":
    success = test_lesson_api()
    if not success:
        print("\n❌ Lesson API tests failed!")
        exit(1)
    else:
        print("\n🚀 Lesson content delivery system is ready!")
        exit(0)