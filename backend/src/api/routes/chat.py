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

import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Session storage path
SESSIONS_FILE = "data/sessions.json"
if not os.path.exists("data"):
    os.makedirs("data")

# Store active orchestrators in memory (these can't be serialized)
active_orchestrators: Dict[str, AgentOrchestrator] = {}

def load_sessions() -> Dict[str, Any]:
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading sessions: {e}")
    return {}

def save_sessions(sessions_data: Dict[str, Any]):
    try:
        # Only save serializable data (history and metadata)
        serializable_sessions = {}
        for sid, data in sessions_data.items():
            serializable_sessions[sid] = {
                'dataset_id': data.get('dataset_id'),
                'history': data.get('history', [])
            }
        with open(SESSIONS_FILE, 'w') as f:
            json.dump(serializable_sessions, f)
    except Exception as e:
        logger.error(f"Error saving sessions: {e}")

# Initial load
sessions = load_sessions()


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
    
    if session_id not in sessions or session_id not in active_orchestrators:
        # Create or restore session
        dataset_id = request.dataset_id or (sessions.get(session_id, {}).get('dataset_id') if session_id in sessions else None)
        
        if not dataset_id:
            raise HTTPException(
                status_code=400,
                detail="dataset_id required for new session"
            )
        
        # Get dataset
        df = dataset_manager.get_dataset(dataset_id)
        if df is None:
            raise HTTPException(
                status_code=404,
                detail=f"Dataset {dataset_id} not found"
            )
        
        # Initialize orchestrator
        try:
            provider = (str(request.llm_provider).strip().lower() if request.llm_provider else None)
            if provider == "gemini":
                logger.info("Gemini provider requested for chat; falling back to groq")
                provider = "groq"

            llm = get_llm_service(provider=provider)
            repl = PythonREPL(df, save_callback=lambda pid, fig: register_plot(f"{dataset_id}_{pid}", fig))
            orchestrator = AgentOrchestrator(llm, repl)
            active_orchestrators[session_id] = orchestrator
        except Exception as e:
            logger.error(f"Error initializing orchestrator: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to initialize AI agent: {str(e)}")
        
        if session_id not in sessions:
            sessions[session_id] = {
                'dataset_id': dataset_id,
                'history': []
            }
    
    session = sessions[session_id]
    orchestrator = active_orchestrators[session_id]
    
    # Execute query
    try:
        logger.info(f"Executing query for session {session_id}: {request.message}")
        result = await orchestrator.execute(
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
        
        # Save sessions to disk
        save_sessions(sessions)
        
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
        logger.error(f"Error executing agent for session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent execution error: {str(e)}")


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
    if session_id in active_orchestrators:
        del active_orchestrators[session_id]
    
    save_sessions(sessions)
    return {"message": "Session cleared"}
