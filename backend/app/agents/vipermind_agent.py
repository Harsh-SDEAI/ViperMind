"""
ViperMind LangGraph Agent - Main orchestrator for all AI agents
"""

from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
from datetime import datetime
import json

from app.agents.nodes.tutor_agent import TutorAgent
from app.agents.nodes.assessment_agent import AssessmentAgent
from app.agents.nodes.content_agent import ContentAgent
from app.agents.nodes.progress_agent import ProgressAgent


class AgentState(TypedDict):
    """State shared between all agents"""
    messages: List[Dict[str, Any]]
    user_id: str
    request_type: str
    agent: Optional[str]
    success: bool
    error: Optional[str]
    # Dynamic fields based on request type
    topic_id: Optional[str]
    level_id: Optional[str]
    section_id: Optional[str]
    assessment_results: Optional[Dict[str, Any]]
    lesson_content: Optional[Dict[str, Any]]
    questions: Optional[List[Dict[str, Any]]]
    user_answers: Optional[List[Dict[str, Any]]]
    concept: Optional[str]
    topic_name: Optional[str]
    difficulty: Optional[str]
    content: Optional[Dict[str, Any]]
    # Agent response fields
    explanation: Optional[str]
    hint: Optional[str]
    question: Optional[str]
    learning_patterns: Optional[Dict[str, Any]]
    pattern_insights: Optional[Dict[str, Any]]
    topic_info: Optional[Dict[str, Any]]


class ViperMindAgent:
    """Main LangGraph agent orchestrator for ViperMind"""
    
    def __init__(self):
        self.tutor_agent = TutorAgent()
        self.assessment_agent = AssessmentAgent()
        self.content_agent = ContentAgent()
        self.progress_agent = ProgressAgent()
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("router", self._route_request)
        workflow.add_node("tutor", self.tutor_agent.process)
        workflow.add_node("assessment", self.assessment_agent.process)
        workflow.add_node("content_generator", self.content_agent.process)
        workflow.add_node("progress", self.progress_agent.process)
        workflow.add_node("finalizer", self._finalize_response)
        
        # Set entry point
        workflow.set_entry_point("router")
        
        # Add routing logic
        workflow.add_conditional_edges(
            "router",
            self._determine_agent,
            {
                "tutor": "tutor",
                "assessment": "assessment", 
                "content": "content_generator",
                "progress": "progress",
                "error": "finalizer"
            }
        )
        
        # All agents go to finalizer
        workflow.add_edge("tutor", "finalizer")
        workflow.add_edge("assessment", "finalizer")
        workflow.add_edge("content_generator", "finalizer")
        workflow.add_edge("progress", "finalizer")
        
        # Finalizer ends the workflow
        workflow.add_edge("finalizer", END)
        
        return workflow.compile()
    
    def _route_request(self, state: AgentState) -> AgentState:
        """Route incoming requests to appropriate agents"""
        
        request_type = state.get("request_type", "")
        
        # Validate required fields
        if not state.get("user_id"):
            return {
                **state,
                "error": "User ID is required",
                "success": False
            }
        
        if not request_type:
            return {
                **state,
                "error": "Request type is required",
                "success": False
            }
        
        # Add routing metadata
        return {
            **state,
            "routed": True,
            "timestamp": str(datetime.now()) if 'datetime' in globals() else "unknown"
        }
    
    def _determine_agent(self, state: AgentState) -> str:
        """Determine which agent should handle the request"""
        
        if state.get("error"):
            return "error"
        
        request_type = state.get("request_type", "")
        
        # Tutor agent requests
        tutor_requests = [
            "generate_lesson", "explain_concept", "provide_hint", 
            "personalize_content", "create_explanation"
        ]
        
        # Assessment agent requests
        assessment_requests = [
            "generate_quiz", "generate_test", "generate_final", "evaluate_assessment", 
            "analyze_performance", "create_questions"
        ]
        
        # Content agent requests
        content_requests = [
            "generate_examples", "create_practice_problems", "generate_analogies",
            "create_visual_explanations", "generate_remedial_content"
        ]
        
        # Progress agent requests
        progress_requests = [
            "analyze_patterns", "predict_outcomes", "recommend_difficulty",
            "generate_insights", "calculate_progress", "update_progress"
        ]
        
        if request_type in tutor_requests:
            return "tutor"
        elif request_type in assessment_requests:
            return "assessment"
        elif request_type in content_requests:
            return "content"
        elif request_type in progress_requests:
            return "progress"
        else:
            return "error"
    
    def _finalize_response(self, state: AgentState) -> AgentState:
        """Finalize the response and prepare for return"""
        
        # Clean up the state for response
        response_state = {
            **state,
            "completed": True,
            "processing_agent": state.get("agent", "unknown")
        }
        
        # Remove internal fields that shouldn't be in the response
        internal_fields = ["messages", "routed", "timestamp"]
        for field in internal_fields:
            response_state.pop(field, None)
        
        return response_state
    
    async def invoke(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point for agent invocation"""
        
        try:
            # Prepare initial state
            initial_state = AgentState(
                messages=[],
                user_id=request.get("user_id", ""),
                request_type=request.get("request_type", ""),
                agent=None,
                success=False,
                error=None,
                **{k: v for k, v in request.items() if k not in ["user_id", "request_type"]}
            )
            
            # Run the workflow
            result = await self.workflow.ainvoke(initial_state)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Agent workflow error: {str(e)}",
                "agent": "workflow_error"
            }
    
    def invoke_sync(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous version of invoke"""
        
        try:
            # Prepare initial state
            initial_state = AgentState(
                messages=[],
                user_id=request.get("user_id", ""),
                request_type=request.get("request_type", ""),
                agent=None,
                success=False,
                error=None,
                **{k: v for k, v in request.items() if k not in ["user_id", "request_type"]}
            )
            
            # Run the workflow synchronously
            result = self.workflow.invoke(initial_state)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Agent workflow error: {str(e)}",
                "agent": "workflow_error"
            }


# Global agent instance
vipermind_agent = ViperMindAgent()


# Convenience functions for different agent operations
def generate_lesson(user_id: str, topic_id: str) -> Dict[str, Any]:
    """Generate a lesson for a specific topic"""
    return vipermind_agent.invoke_sync({
        "user_id": user_id,
        "request_type": "generate_lesson",
        "topic_id": topic_id
    })


def create_quiz(user_id: str, topic_id: str) -> Dict[str, Any]:
    """Create a quiz for a specific topic"""
    return vipermind_agent.invoke_sync({
        "user_id": user_id,
        "request_type": "generate_quiz",
        "topic_id": topic_id
    })


def evaluate_assessment(user_id: str, assessment: Dict[str, Any], user_answers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Evaluate an assessment submission"""
    return vipermind_agent.invoke_sync({
        "user_id": user_id,
        "request_type": "evaluate_assessment",
        "assessment": assessment,
        "user_answers": user_answers
    })


def explain_concept(user_id: str, concept: str) -> Dict[str, Any]:
    """Get an explanation for a concept"""
    return vipermind_agent.invoke_sync({
        "user_id": user_id,
        "request_type": "explain_concept",
        "concept": concept
    })


def analyze_progress(user_id: str) -> Dict[str, Any]:
    """Analyze user's learning progress"""
    return vipermind_agent.invoke_sync({
        "user_id": user_id,
        "request_type": "analyze_patterns"
    })


def generate_hint(user_id: str, question: str, user_answer: str = None) -> Dict[str, Any]:
    """Generate a hint for a question"""
    return vipermind_agent.invoke_sync({
        "user_id": user_id,
        "request_type": "provide_hint",
        "question": question,
        "user_answer": user_answer
    })