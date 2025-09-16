#!/usr/bin/env python3
"""
Test script to verify the curriculum API endpoints
"""

import requests
import json
from dotenv import load_dotenv
load_dotenv()

BASE_URL = "http://localhost:8000/api/v1"

def test_curriculum_api():
    """Test the curriculum API endpoints"""
    print("📚 Testing ViperMind Curriculum API")
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
    
    # Test 2: Curriculum structure
    print("\n2. Testing curriculum structure...")
    try:
        response = requests.get(f"{BASE_URL}/curriculum/structure")
        if response.status_code == 200:
            structure = response.json()
            levels = structure.get("levels", [])
            print(f"✓ Curriculum structure loaded")
            print(f"  Levels: {len(levels)}")
            
            total_sections = sum(len(level.get("sections", [])) for level in levels)
            total_topics = sum(
                len(section.get("topics", []))
                for level in levels
                for section in level.get("sections", [])
            )
            print(f"  Sections: {total_sections}")
            print(f"  Topics: {total_topics}")
        else:
            print(f"✗ Curriculum structure failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Curriculum structure error: {e}")
        return False
    
    # Test 3: Curriculum with progress
    print("\n3. Testing curriculum with progress...")
    try:
        response = requests.get(f"{BASE_URL}/curriculum/progress", headers=headers)
        if response.status_code == 200:
            progress_data = response.json()
            levels = progress_data.get("levels", [])
            print(f"✓ Curriculum progress loaded")
            
            # Check first level details
            if levels:
                first_level = levels[0]
                print(f"  First level: {first_level['name']} ({first_level['code']})")
                print(f"  Unlocked: {first_level.get('is_unlocked', False)}")
                print(f"  Completion: {first_level.get('completion_percentage', 0):.1f}%")
                
                # Check first section
                sections = first_level.get("sections", [])
                if sections:
                    first_section = sections[0]
                    print(f"  First section: {first_section['name']} ({first_section['code']})")
                    print(f"  Section unlocked: {first_section.get('is_unlocked', False)}")
                    
                    # Check first topic
                    topics = first_section.get("topics", [])
                    if topics:
                        first_topic = topics[0]
                        print(f"  First topic: {first_topic['name']}")
                        print(f"  Topic unlocked: {first_topic.get('is_unlocked', False)}")
        else:
            print(f"✗ Curriculum progress failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Curriculum progress error: {e}")
        return False
    
    # Test 4: Level details
    print("\n4. Testing level details...")
    try:
        if levels:
            level_id = levels[0]["id"]
            response = requests.get(f"{BASE_URL}/curriculum/levels/{level_id}")
            if response.status_code == 200:
                level_details = response.json()
                print(f"✓ Level details loaded")
                print(f"  Level: {level_details['name']}")
                print(f"  Sections: {len(level_details.get('sections', []))}")
            else:
                print(f"✗ Level details failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"✗ Level details error: {e}")
        return False
    
    # Test 5: Section details
    print("\n5. Testing section details...")
    try:
        if levels and levels[0].get("sections"):
            section_id = levels[0]["sections"][0]["id"]
            response = requests.get(f"{BASE_URL}/curriculum/sections/{section_id}")
            if response.status_code == 200:
                section_details = response.json()
                print(f"✓ Section details loaded")
                print(f"  Section: {section_details['name']}")
                print(f"  Topics: {len(section_details.get('topics', []))}")
            else:
                print(f"✗ Section details failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"✗ Section details error: {e}")
        return False
    
    # Test 6: Topic details
    print("\n6. Testing topic details...")
    try:
        if levels and levels[0].get("sections") and levels[0]["sections"][0].get("topics"):
            topic_id = levels[0]["sections"][0]["topics"][0]["id"]
            response = requests.get(f"{BASE_URL}/curriculum/topics/{topic_id}")
            if response.status_code == 200:
                topic_details = response.json()
                print(f"✓ Topic details loaded")
                print(f"  Topic: {topic_details['name']}")
            else:
                print(f"✗ Topic details failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"✗ Topic details error: {e}")
        return False
    
    print("\n🎉 All curriculum API tests passed!")
    print("\n✅ Curriculum Management Features:")
    print("  - Complete curriculum structure with levels, sections, and topics")
    print("  - Progress tracking with unlock/completion status")
    print("  - Individual level, section, and topic detail endpoints")
    print("  - User-specific progress calculation")
    print("  - Hierarchical navigation system")
    
    return True

if __name__ == "__main__":
    success = test_curriculum_api()
    if not success:
        print("\n❌ Curriculum API tests failed!")
        exit(1)
    else:
        print("\n🚀 Curriculum management system is ready!")
        exit(0)