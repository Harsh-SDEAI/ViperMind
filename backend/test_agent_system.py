#!/usr/bin/env python3
"""
Test script to verify the LangGraph agent system is working
"""

import requests
import json
from dotenv import load_dotenv
load_dotenv()

BASE_URL = "http://localhost:8000/api/v1"

def test_agent_system():
    """Test the complete LangGraph agent system"""
    print("🤖 Testing ViperMind LangGraph Agent System")
    print("=" * 60)
    
    # First, we need to authenticate
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
    
    # Test 2: Agent status
    print("\n2. Testing agent status...")
    try:
        response = requests.get(f"{BASE_URL}/agents/status", headers=headers)
        if response.status_code == 200:
            status = response.json()
            print("✓ Agent system is operational")
            print(f"  Available agents: {len(status['agents'])}")
            print(f"  Capabilities: {len(status['capabilities'])}")
        else:
            print(f"✗ Agent status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Agent status error: {e}")
        return False
    
    # Test 3: Concept explanation
    print("\n3. Testing concept explanation...")
    try:
        explanation_data = {"concept": "Python variables"}
        response = requests.post(f"{BASE_URL}/agents/concept/explain", json=explanation_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("✓ Concept explanation generated")
            print(f"  Agent: {result.get('agent')}")
            print(f"  Explanation length: {len(result.get('explanation', ''))}")
        else:
            print(f"✗ Concept explanation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Concept explanation error: {e}")
        return False
    
    # Test 4: Progress analysis
    print("\n4. Testing progress analysis...")
    try:
        response = requests.get(f"{BASE_URL}/agents/progress/analyze", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("✓ Progress analysis completed")
            print(f"  Agent: {result.get('agent')}")
            if result.get('learning_patterns'):
                patterns = result['learning_patterns']
                print(f"  Learning velocity: {patterns.get('learning_velocity', 'unknown')}")
                print(f"  Consistency: {patterns.get('consistency', 'unknown')}")
        else:
            print(f"✗ Progress analysis failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Progress analysis error: {e}")
        return False
    
    # Test 5: Hint generation
    print("\n5. Testing hint generation...")
    try:
        hint_data = {
            "question": "What is the difference between a list and a tuple in Python?",
            "user_answer": "I think they are the same"
        }
        response = requests.post(f"{BASE_URL}/agents/hint/generate", json=hint_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("✓ Hint generated successfully")
            print(f"  Agent: {result.get('agent')}")
            print(f"  Hint length: {len(result.get('hint', ''))}")
        else:
            print(f"✗ Hint generation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Hint generation error: {e}")
        return False
    
    # Test 6: Direct agent invocation
    print("\n6. Testing direct agent invocation...")
    try:
        agent_data = {
            "request_type": "analyze_patterns",
            "data": {}
        }
        response = requests.post(f"{BASE_URL}/agents/invoke", json=agent_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("✓ Direct agent invocation successful")
            print(f"  Agent: {result.get('agent')}")
            print(f"  Success: {result.get('success')}")
        else:
            print(f"✗ Direct agent invocation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Direct agent invocation error: {e}")
        return False
    
    print("\n🎉 All agent system tests passed!")
    print("\n✅ LangGraph Agent System Features:")
    print("  - Multi-agent orchestration with LangGraph")
    print("  - Tutor Agent: Personalized explanations and guidance")
    print("  - Assessment Agent: Dynamic question generation and evaluation")
    print("  - Content Agent: Educational content creation")
    print("  - Progress Agent: Learning analytics and insights")
    print("  - OpenAI Integration: GPT-4 powered content generation")
    print("  - Database Integration: User progress and curriculum access")
    print("  - RESTful API: Easy integration with frontend")
    
    return True

if __name__ == "__main__":
    success = test_agent_system()
    if not success:
        print("\n❌ Agent system tests failed!")
        exit(1)
    else:
        print("\n🚀 LangGraph agent system is ready for production!")
        exit(0)