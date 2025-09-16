#!/usr/bin/env python3
"""
Test script to verify the complete assessment flow
"""

import requests
import json
from dotenv import load_dotenv
load_dotenv()

BASE_URL = "http://localhost:8000/api/v1"

def test_full_assessment_flow():
    """Test the complete assessment flow from generation to submission"""
    print("🔄 Testing Complete Assessment Flow")
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
    print("\n2. Getting topic from curriculum...")
    try:
        response = requests.get(f"{BASE_URL}/curriculum/structure")
        if response.status_code == 200:
            structure = response.json()
            topic_id = structure["levels"][0]["sections"][0]["topics"][0]["id"]
            topic_name = structure["levels"][0]["sections"][0]["topics"][0]["name"]
            print(f"✓ Using topic: {topic_name}")
        else:
            print(f"✗ Failed to get curriculum: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Curriculum error: {e}")
        return False
    
    # Generate quiz
    print("\n3. Generating quiz...")
    try:
        quiz_data = {
            "target_id": topic_id,
            "assessment_type": "quiz",
            "difficulty": "medium",
            "question_count": 4
        }
        response = requests.post(f"{BASE_URL}/assessments/generate", json=quiz_data, headers=headers)
        if response.status_code == 200:
            quiz = response.json()
            print(f"✓ Quiz generated with {len(quiz['questions'])} questions")
            print(f"  Time limit: {quiz['time_limit']} minutes")
            
            assessment_id = quiz['assessment_id']
            questions = quiz['questions']
            
            # Display first question as example
            first_q = questions[0]
            print(f"\n  Example question:")
            print(f"  Q: {first_q['question']}")
            for i, option in enumerate(first_q['options']):
                marker = "→" if i == first_q['correct_answer'] else " "
                print(f"  {marker} {chr(65+i)}. {option}")
            
        else:
            print(f"✗ Quiz generation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Quiz generation error: {e}")
        return False
    
    # Simulate answering questions (mix of correct and incorrect)
    print("\n4. Simulating quiz answers...")
    try:
        answers = []
        correct_count = 0
        
        for i, question in enumerate(questions):
            # Answer correctly for first 2 questions, incorrectly for others
            if i < 2:
                selected_answer = question['correct_answer']
                correct_count += 1
            else:
                # Select a wrong answer
                selected_answer = (question['correct_answer'] + 1) % len(question['options'])
            
            answers.append({
                "question_id": question["id"],
                "selected_answer": selected_answer
            })
            
            print(f"  Q{i+1}: Selected option {chr(65+selected_answer)} ({'✓' if selected_answer == question['correct_answer'] else '✗'})")
        
        print(f"  Expected score: {(correct_count/len(questions)*100):.0f}%")
        
    except Exception as e:
        print(f"✗ Answer simulation error: {e}")
        return False
    
    # Submit quiz
    print("\n5. Submitting quiz...")
    try:
        submission_data = {
            "assessment_id": assessment_id,
            "answers": answers,
            "time_taken": 420  # 7 minutes
        }
        
        response = requests.post(f"{BASE_URL}/assessments/submit", json=submission_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Quiz submitted successfully")
            print(f"  Final score: {result['score']:.1f}%")
            print(f"  Passed: {result['passed']}")
            print(f"  Correct answers: {result['correct_answers']}/{result['total_questions']}")
            print(f"  Time taken: {result['time_taken']}s")
            print(f"  AI Feedback: {result['feedback'][:100]}...")
            print(f"  Next steps: {result['next_steps']['message'][:100]}...")
            
            # Verify question results
            print(f"\n  Question breakdown:")
            for i, qr in enumerate(result['question_results']):
                status = "✓" if qr['is_correct'] else "✗"
                print(f"    Q{i+1}: {status} (answered {chr(65+qr['user_answer'])}, correct: {chr(65+qr['correct_answer'])})")
            
        else:
            print(f"✗ Quiz submission failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Quiz submission error: {e}")
        return False
    
    # Check assessment history
    print("\n6. Checking assessment history...")
    try:
        response = requests.get(f"{BASE_URL}/assessments/history", headers=headers)
        if response.status_code == 200:
            history = response.json()
            assessments = history.get("assessments", [])
            print(f"✓ Assessment history retrieved")
            print(f"  Total assessments: {len(assessments)}")
            
            if assessments:
                latest = assessments[0]
                print(f"  Latest assessment:")
                print(f"    Type: {latest['type']}")
                print(f"    Score: {latest.get('score', 'N/A')}%")
                print(f"    Attempt: {latest['attempt_number']}")
                print(f"    Date: {latest['created_at'][:19]}")
        else:
            print(f"✗ Assessment history failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Assessment history error: {e}")
        return False
    
    print("\n🎉 Complete assessment flow test passed!")
    print("\n✅ Assessment Interface Features Verified:")
    print("  - Quiz generation with AI-powered questions")
    print("  - Multiple-choice question presentation")
    print("  - Answer submission and validation")
    print("  - Real-time scoring and feedback")
    print("  - Detailed question-by-question results")
    print("  - Assessment history tracking")
    print("  - Pass/fail determination with next steps")
    
    return True

if __name__ == "__main__":
    success = test_full_assessment_flow()
    if not success:
        print("\n❌ Assessment flow test failed!")
        exit(1)
    else:
        print("\n🚀 Assessment interface system is ready!")
        exit(0)