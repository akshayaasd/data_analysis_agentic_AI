"""
Pydantic models for request/response schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    GEMINI = "gemini"


class AgentType(str, Enum):
    """Types of specialized agents."""
    ANALYSIS = "analysis"
    VISUALIZATION = "visualization"
    SUGGESTIONS = "suggestions"
    RAG = "rag"


class MessageRole(str, Enum):
    """Chat message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# Chat Schemas
class ChatMessage(BaseModel):
    """Chat message model."""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    """Request to send a chat message."""
    message: str
    session_id: Optional[str] = None
    dataset_id: Optional[str] = None
    llm_provider: Optional[LLMProvider] = None


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    session_id: str
    message: str
    agent_type: Optional[AgentType] = None
    code_executed: Optional[str] = None
    plots: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


# Data Schemas
class DatasetInfo(BaseModel):
    """Dataset metadata."""
    dataset_id: str
    filename: str
    rows: int
    columns: int
    column_names: List[str]
    column_types: Dict[str, str]
    upload_time: datetime
    file_size: int


class DataUploadResponse(BaseModel):
    """Response after uploading a dataset."""
    dataset_id: str
    info: DatasetInfo
    preview: List[Dict[str, Any]]


# Analysis Schemas
class AnalysisRequest(BaseModel):
    """Request to perform analysis."""
    dataset_id: str
    query: str
    session_id: Optional[str] = None


class AnalysisResult(BaseModel):
    """Result of an analysis."""
    analysis_id: str
    query: str
    code_executed: str
    result: Any
    execution_time: float
    timestamp: datetime


# Visualization Schemas
class VisualizationRequest(BaseModel):
    """Request to generate visualization."""
    dataset_id: str
    query: str
    session_id: Optional[str] = None


class VisualizationResult(BaseModel):
    """Result of visualization generation."""
    plot_id: str
    query: str
    code_executed: str
    plot_type: str
    timestamp: datetime


# Suggestions Schemas
class Suggestion(BaseModel):
    """A single suggestion."""
    suggestion_id: str
    title: str
    description: str
    category: str  # "analysis" or "visualization"
    confidence: float
    query: str
    expected_insight: str


class SuggestionsResponse(BaseModel):
    """Top 3 suggestions for a dataset."""
    dataset_id: str
    suggestions: List[Suggestion]


# Agent Schemas
class AgentStep(BaseModel):
    """A single step in the agent's reasoning loop."""
    step_number: int
    thought: str
    action: Optional[str] = None
    action_input: Optional[str] = None
    observation: Optional[str] = None


class AgentResponse(BaseModel):
    """Complete agent response with reasoning steps."""
    final_answer: str
    steps: List[AgentStep]
    total_steps: int
    execution_time: float
    agent_type: AgentType
