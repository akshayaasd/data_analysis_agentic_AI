"""
Chat API routes for conversational interface.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import uuid

from src.models.schemas import ChatRequest, ChatResponse, MessageRole
from src.core.orchestrator import AgentOrchestrator
from src.services.llm_service import get_llm_service
from src.tools.python_repl import PythonREPL
from src.tools.data_tools import dataset_manager
from src.api.routes.visualization import register_plot

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Store active sessions
sessions: Dict[str, Dict[str, Any]] = {}


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a chat message and get agent response.
    
    Args:
        request: Chat request with message and optional session_id
        
    Returns:
        Chat response with agent's answer
    """
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    
    if session_id not in sessions:
        # Create new session
        if not request.dataset_id:
            raise HTTPException(
                status_code=400,
                detail="dataset_id required for new session"
            )
        
        # Get dataset
        df = dataset_manager.get_dataset(request.dataset_id)
        if df is None:
            raise HTTPException(
                status_code=404,
                detail=f"Dataset {request.dataset_id} not found"
            )
        
        # Initialize orchestrator
        llm = get_llm_service(provider=request.llm_provider)
        # Prefix plot_ids with dataset_id to avoid collisions
        dataset_id = request.dataset_id
        repl = PythonREPL(df, save_callback=lambda pid, fig: register_plot(f"{dataset_id}_{pid}", fig))
        orchestrator = AgentOrchestrator(llm, repl)
        
        sessions[session_id] = {
            'orchestrator': orchestrator,
            'dataset_id': request.dataset_id,
            'history': []
        }
    
    session = sessions[session_id]
    
    # Execute query
    try:
        result = await session['orchestrator'].execute(
            query=request.message,
            dataset_id=session['dataset_id'],
            use_rag=False
        )
        
        # Store in history
        session['history'].append({
            'role': MessageRole.USER,
            'content': request.message
        })
        session['history'].append({
            'role': MessageRole.ASSISTANT,
            'content': result['final_answer']
        })
        
        # Build response
        response = ChatResponse(
            session_id=session_id,
            message=result['final_answer'],
            agent_type=result.get('agent_type'),
            code_executed=None,
            plots=[f"{session['dataset_id']}_{pid}" for pid in result.get('plots', [])],
            metadata={
                'steps': result.get('total_steps'),
                'execution_time': result.get('execution_time')
            }
        )
        
        # Include code if available
        if result.get('steps'):
            last_step = result['steps'][-1]
            if last_step.get('action_input'):
                response.code_executed = last_step['action_input']
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_history(session_id: str):
    """Get conversation history for a session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"session_id": session_id, "history": sessions[session_id]['history']}


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a session."""
    if session_id in sessions:
        del sessions[session_id]
    
    return {"message": "Session cleared"}
