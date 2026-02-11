"""
RAG Agent - Provides context-aware responses using vector store.
"""
from src.agents.base_agent import BaseAgent
from src.services.vector_service import VectorService
from typing import Optional


class RAGAgent(BaseAgent):
    """
    Agent specialized in context-aware responses.
    Uses vector store to retrieve relevant past analyses.
    """
    
    def __init__(self, *args, vector_service: Optional[VectorService] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.vector_service = vector_service or VectorService()
        self.dataset_id = None
    
    def set_dataset_id(self, dataset_id: str):
        """Set the current dataset ID for context retrieval."""
        self.dataset_id = dataset_id
    
    def get_agent_type(self) -> str:
        return "rag"
    
    def get_system_prompt(self) -> str:
        return """You are a RAG (Retrieval-Augmented Generation) Agent. You answer questions using both the current dataset and relevant context from past analyses.

You have access to:
- A pandas DataFrame called 'df'
- Context from similar past analyses (provided in the query)

Your job is to provide context-aware answers that:
1. Reference relevant past analyses when applicable
2. Perform new analysis when needed
3. Combine historical insights with current data

You must follow this format EXACTLY:

Thought: [Your reasoning, considering both context and current data]
Action: Python
```python
# Your analysis code
```

When you have the answer:
Final Answer: [Your answer, referencing context when relevant]

IMPORTANT RULES:
1. Use the provided context to inform your analysis
2. Don't just repeat past analyses - add new insights
3. If context is not relevant, focus on the current query
4. Cite past analyses when they're helpful
5. Always verify insights with current data

Example with context:

Context: "Previous analysis showed sales peak in Q4"
Query: What are the current sales trends?

Thought: The context mentions Q4 peaks. I'll analyze current trends and see if this pattern continues.
Action: Python
```python
monthly_sales = df.groupby('Month')['Sales'].sum()
print(monthly_sales)
```

[After observation]

Final Answer: Current data confirms the Q4 peak pattern observed previously. Sales show a 30% increase in Q4 compared to other quarters, consistent with historical trends.

Now, answer the query using available context and data."""
    
    async def run_with_context(self, query: str, dataset_id: Optional[str] = None) -> dict:
        """
        Run the agent with context retrieval.
        
        Args:
            query: User query
            dataset_id: Dataset ID for context filtering
            
        Returns:
            Agent response with context
        """
        # Get relevant context
        context = self.vector_service.get_context(
            query=query,
            dataset_id=dataset_id or self.dataset_id,
            n_results=3
        )
        
        # Augment query with context
        augmented_query = f"Context from past analyses:\n{context}\n\nCurrent query: {query}"
        
        # Run normal agent loop
        return await self.run(augmented_query)
