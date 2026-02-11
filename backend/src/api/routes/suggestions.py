"""
Suggestions API routes.
"""
from fastapi import APIRouter, HTTPException

from src.models.schemas import SuggestionsResponse, Suggestion
from src.agents.suggestions_agent import SuggestionsAgent
from src.services.llm_service import get_llm_service
from src.tools.python_repl import PythonREPL
from src.tools.data_tools import dataset_manager

router = APIRouter(prefix="/api/suggestions", tags=["suggestions"])


@router.get("/{dataset_id}", response_model=SuggestionsResponse)
async def get_suggestions(dataset_id: str, llm_provider: str = None):
    """
    Get top 3 suggestions for a dataset.
    
    Args:
        dataset_id: Dataset identifier
        llm_provider: Optional LLM provider
        
    Returns:
        Top 3 suggestions
    """
    # Get dataset
    df = dataset_manager.get_dataset(dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Initialize agent
    llm = get_llm_service(provider=llm_provider)
    repl = PythonREPL(df)
    agent = SuggestionsAgent(llm, repl)
    
    # Generate suggestions
    try:
        result = await agent.run("Generate top 3 suggestions for this dataset")
        
        # Parse suggestions
        suggestions_list = result.get('suggestions', [])
        
        # Convert to Suggestion objects
        suggestions = []
        for i, sug in enumerate(suggestions_list[:3]):  # Ensure only 3
            suggestions.append(Suggestion(
                suggestion_id=f"{dataset_id}_sug_{i+1}",
                title=sug.get('title', ''),
                description=sug.get('description', ''),
                category=sug.get('category', 'analysis'),
                confidence=sug.get('confidence', 0.5),
                query=sug.get('query', ''),
                expected_insight=sug.get('expected_insight', '')
            ))
        
        return SuggestionsResponse(
            dataset_id=dataset_id,
            suggestions=suggestions
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate suggestions: {str(e)}"
        )
