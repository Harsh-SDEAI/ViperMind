#!/usr/bin/env python3
"""
Debug script to test the LangGraph workflow directly
"""

from dotenv import load_dotenv
load_dotenv()

from app.agents.vipermind_agent import vipermind_agent, explain_concept

def test_workflow_direct():
    """Test the workflow directly"""
    print("🔄 Testing LangGraph Workflow")
    print("=" * 40)
    
    try:
        # Test direct workflow invocation
        result = vipermind_agent.invoke_sync({
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "request_type": "explain_concept",
            "concept": "Python variables"
        })
        
        print(f"Workflow result: {result}")
        
        if result.get("success"):
            print("✓ Workflow completed successfully")
            explanation = result.get("explanation")
            if explanation:
                print(f"Explanation length: {len(explanation)}")
                print(f"First 100 chars: {explanation[:100]}...")
            else:
                print("⚠️ Explanation is None or empty")
        else:
            print(f"✗ Workflow failed: {result.get('error')}")
            
    except Exception as e:
        print(f"✗ Workflow error: {e}")
        import traceback
        traceback.print_exc()

def test_convenience_function():
    """Test the convenience function"""
    print("\n📞 Testing Convenience Function")
    print("=" * 40)
    
    try:
        result = explain_concept(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            concept="Python variables"
        )
        
        print(f"Convenience function result: {result}")
        
        if result.get("success"):
            print("✓ Convenience function successful")
            explanation = result.get("explanation")
            if explanation:
                print(f"Explanation length: {len(explanation)}")
            else:
                print("⚠️ Explanation is None or empty")
        else:
            print(f"✗ Convenience function failed: {result.get('error')}")
            
    except Exception as e:
        print(f"✗ Convenience function error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_workflow_direct()
    test_convenience_function()