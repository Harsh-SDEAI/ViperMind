#!/usr/bin/env python3
"""
Debug script to test assessment generation directly
"""

from dotenv import load_dotenv
load_dotenv()

from app.agents.vipermind_agent import create_quiz

def test_quiz_generation():
    """Test quiz generation directly"""
    print("🔧 Testing Quiz Generation Directly")
    print("=" * 40)
    
    try:
        result = create_quiz(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            topic_id="5116b38c-5032-42f8-9927-9749d4aa6c1b"
        )
        
        print(f"Result: {result}")
        
        if result.get("success"):
            print("✓ Quiz generation successful")
            questions = result.get("questions", [])
            print(f"Questions generated: {len(questions)}")
        else:
            print(f"✗ Quiz generation failed: {result.get('error')}")
            
    except Exception as e:
        print(f"✗ Quiz generation error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_quiz_generation()