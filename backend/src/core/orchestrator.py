"""
Agent Orchestrator - Routes queries to appropriate specialized agents.
"""
from typing import Dict, Any, Optional
import re

from src.services.llm_service import LLMService
from src.agents.analysis_agent import AnalysisAgent
from src.agents.visualization_agent import VisualizationAgent
from src.agents.suggestions_agent import SuggestionsAgent
from src.agents.rag_agent import RAGAgent
from src.tools.python_repl import PythonREPL
from src.services.vector_service import VectorService


class AgentOrchestrator:
    """
    Orchestrates multiple specialized agents.
    Routes queries to the appropriate agent based on intent.
    """
    
    def __init__(
        self,
        llm_service: LLMService,
        repl: PythonREPL,
        vector_service: Optional[VectorService] = None
    ):
        """
        Initialize orchestrator with all agents.
        
        Args:
            llm_service: LLM service for all agents
            repl: Shared Python REPL
            vector_service: Vector store service
        """
        self.llm = llm_service
        self.repl = repl
        self.vector_service = vector_service or VectorService()
        
        # Initialize all specialized agents
        self.agents = {
            'analysis': AnalysisAgent(llm_service, repl),
            'visualization': VisualizationAgent(llm_service, repl),
            'suggestions': SuggestionsAgent(llm_service, repl),
            'rag': RAGAgent(llm_service, repl, vector_service=self.vector_service)
        }
    
    async def route_query(self, query: str, use_rag: bool = False) -> str:
        """
        Determine which agent should handle the query.
        
        Args:
            query: User query
            use_rag: Whether to use RAG agent
            
        Returns:
            Agent type ('analysis', 'visualization', 'suggestions', 'rag')
        """
        # Check for explicit visualization keywords
        viz_keywords = [
            'plot', 'chart', 'graph', 'visualize', 'visualization', 'show',
            'bar chart', 'line chart', 'scatter', 'histogram', 'heatmap',
            'pie chart', 'box plot', 'display'
        ]
        
        query_lower = query.lower()
        
        # Check for visualization intent
        if any(keyword in query_lower for keyword in viz_keywords):
            return 'visualization'
        
        # Check for suggestions request
        if 'suggest' in query_lower or 'recommend' in query_lower or 'what can' in query_lower:
            return 'suggestions'
        
        # Use RAG if requested or if query references "previous" or "past"
        if use_rag or 'previous' in query_lower or 'past' in query_lower or 'before' in query_lower:
            return 'rag'
        
        # Default to analysis
        return 'analysis'
    
    async def execute(
        self,
        query: str,
        dataset_id: Optional[str] = None,
        use_rag: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a query by routing to the appropriate agent.
        
        Args:
            query: User query
            dataset_id: Dataset identifier for RAG context
            use_rag: Force use of RAG agent
            
        Returns:
            Agent response
        """
        # Route to appropriate agent
        agent_type = await self.route_query(query, use_rag)
        agent = self.agents[agent_type]
        
        # Execute query
        if agent_type == 'rag':
            result = await agent.run_with_context(query, dataset_id)
        else:
            result = await agent.run(query)
        
        # Store in vector database if analysis or visualization
        if agent_type in ['analysis', 'visualization'] and dataset_id:
            self.vector_service.add_analysis(
                query=query,
                result=result.get('final_answer', ''),
                dataset_id=dataset_id,
                metadata={
                    'agent_type': agent_type,
                    'steps': result.get('total_steps', 0)
                }
            )
        
        return result
    
    def get_agent(self, agent_type: str):
        """Get a specific agent by type."""
        return self.agents.get(agent_type)
    
    def update_dataframe(self, df):
        """Update the dataframe for all agents."""
        self.repl.update_dataframe(df)
