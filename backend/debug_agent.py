#!/usr/bin/env python3
"""
Debug script to test individual agent components
"""

from dotenv import load_dotenv
load_dotenv()

from app.agents.tools.openai_tool import OpenAITool
from app.agents.tools.database_tool import DatabaseTool

def test_openai_tool():
    """Test OpenAI tool directly"""
    print("🔧 Testing OpenAI Tool")
    print("=" * 40)
    
    try:
        openai_tool = OpenAITool()
        print("✓ OpenAI tool initialized")
        
        # Test explanation generation
        result = openai_tool.run(
            "create_explanation",
            concept="Python variables",
            user_level="beginner",
            user_context={}
        )
        
        print(f"OpenAI result: {result}")
        
        if result.get("success"):
            print("✓ OpenAI explanation generated successfully")
            print(f"Explanation length: {len(result.get('explanation', ''))}")
        else:
            print(f"✗ OpenAI explanation failed: {result.get('error')}")
            
    except Exception as e:
        print(f"✗ OpenAI tool error: {e}")

def test_database_tool():
    """Test database tool directly"""
    print("\n🗄️ Testing Database Tool")
    print("=" * 40)
    
    try:
        db_tool = DatabaseTool()
        print("✓ Database tool initialized")
        
        # Test user progress retrieval
        result = db_tool.run("get_user_progress", user_id="550e8400-e29b-41d4-a716-446655440000")
        
        print(f"Database result: {result}")
        
        if "error" not in result:
            print("✓ Database query successful")
        else:
            print(f"✗ Database query failed: {result.get('error')}")
            
    except Exception as e:
        print(f"✗ Database tool error: {e}")

def test_tutor_agent():
    """Test tutor agent directly"""
    print("\n🎓 Testing Tutor Agent")
    print("=" * 40)
    
    try:
        from app.agents.nodes.tutor_agent import TutorAgent
        
        tutor = TutorAgent()
        print("✓ Tutor agent initialized")
        
        # Test concept explanation
        state = {
            "request_type": "explain_concept",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "concept": "Python variables"
        }
        
        result = tutor.process(state)
        
        print(f"Tutor result: {result}")
        
        if result.get("success"):
            print("✓ Tutor agent explanation successful")
            explanation = result.get("explanation")
            if explanation:
                print(f"Explanation length: {len(explanation)}")
            else:
                print("⚠️ Explanation is None or empty")
        else:
            print(f"✗ Tutor agent failed: {result.get('error')}")
            
    except Exception as e:
        print(f"✗ Tutor agent error: {e}")

if __name__ == "__main__":
    test_openai_tool()
    test_database_tool()
    test_tutor_agent()