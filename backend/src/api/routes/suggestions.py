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


import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


from src.api.routes.visualization import register_plot

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
    try:
        provider = (llm_provider or "").strip().lower() or None
        if provider == "gemini":
            logger.info("Gemini provider requested for suggestions; falling back to groq")
            provider = "groq"

        llm = get_llm_service(provider=provider)
        repl = PythonREPL(df, save_callback=lambda pid, fig: register_plot(f"{dataset_id}_{pid}", fig))
        agent = SuggestionsAgent(llm, repl)
    except Exception as e:
        logger.error(f"Error initializing SuggestionsAgent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize suggestions: {str(e)}")
    
    # Generate suggestions
    try:
        logger.info(f"Generating suggestions for dataset {dataset_id}")
        result = await agent.run("Generate top 3 suggestions for this dataset")
        
        # Parse suggestions
        suggestions_list = result.get('suggestions', [])
        
        if not suggestions_list:
            logger.warning(f"No suggestions generated for dataset {dataset_id}. Raw result: {result.get('final_answer')}")
        
        # Convert to Suggestion objects
        suggestions = []
        # Support variable number of suggestions (1-3)
        for i, sug in enumerate(suggestions_list[:3]):
            suggestions.append(Suggestion(
                suggestion_id=f"{dataset_id}_sug_{i+1}",
                title=sug.get('title', 'Analysis Suggestion'),
                description=sug.get('description', 'No description available'),
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
        logger.error(f"Failed to generate suggestions for dataset {dataset_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate suggestions: {str(e)}"
        )
