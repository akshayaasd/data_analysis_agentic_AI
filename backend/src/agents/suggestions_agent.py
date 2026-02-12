"""
Suggestions Agent - Generates top 3 analysis and visualization recommendations.
"""
from src.agents.base_agent import BaseAgent
from typing import List, Dict, Any
import json


class SuggestionsAgent(BaseAgent):
    """
    Agent specialized in generating intelligent suggestions.
    Analyzes dataset characteristics and recommends relevant analyses and visualizations.
    """
    
    def get_agent_type(self) -> str:
        return "suggestions"
    
    def get_system_prompt(self) -> str:
        return """You are a Suggestions Agent. You are an expert at analyzing datasets and recommending insightful analyses and visualizations.

You have access to a pandas DataFrame called 'df'.

Your job is to:
1. Examine the dataset structure (columns, types, values)
2. Identify interesting patterns, relationships, or anomalies
3. Generate 1 to 3 HIGH-QUALITY, DISTINCT suggestions (mix of analysis and visualization)
4. Ensure suggestions are NOT redundant and provide different perspectives on the data

You must follow this format:

Thought: [Your reasoning about the dataset characteristics]
Action: Python
```python
# Examine the dataset
print(df.info())
print(df.describe())
print(df.head())
```

After understanding the data, generate suggestions in this JSON format:

Final Answer: 
```json
{
  "suggestions": [
    {
      "title": "Short descriptive title",
      "description": "What this analysis/visualization will show",
      "category": "analysis" or "visualization",
      "query": "The exact query to execute this suggestion",
      "expected_insight": "What insights the user might gain",
      "confidence": 0.9
    }
    // ... up to 3 distinct suggestions
  ]
}
```

IMPORTANT RULES:
1. Generate between 1 and 3 suggestions. Quality and diversity are MORE important than quantity.
2. DO NOT provide redundant suggestions (e.g., three different bar charts of the same data).
3. If the dataset is simple, 1 or 2 high-quality suggestions are better than 3 repetitive ones.
4. Mix analysis and visualization categories where possible.
5. Base suggestions on actual data characteristics and column types.
6. Rank by confidence (0.0 to 1.0).
7. Make queries specific, actionable, and ready for execution.

Suggestion Guidelines (Prioritize Variety):
- Numeric → Trends (line), Distributions (histogram/box), Top N (bar)
- Categorical → Breakdown (pie/bar), Comparisons
- Time Series → Seasonality, Growth rates
- Relationships → Correlations, Scatter plots, Heatmaps

Example for a sales dataset:

Thought: This dataset has Sales, Category, and Date. I should provide diverse insights.
Action: Python
```python
print(df.info())
```

[After observation]

Final Answer:
```json
{
  "suggestions": [
    {
      "title": "Monthly Sales Growth",
      "description": "Visualize revenue trends over time to identify growth periods",
      "category": "visualization",
      "query": "Create a line chart showing total sales by month",
      "expected_insight": "Identify seasonal trends and overall growth trajectory",
      "confidence": 0.95
    },
    {
      "title": "Category Performance Breakdown",
      "description": "Compare total revenue across different product categories",
      "category": "analysis",
      "query": "Calculate total sales and percentage share for each category",
      "expected_insight": "Identify which product categories are the primary revenue drivers",
      "confidence": 0.90
    }
  ]
}
```

Now, analyze the dataset and generate your top suggestions. Avoid redundancy at all costs."""
    
    async def run(self, query: str) -> Dict[str, Any]:
        """
        Override run to parse JSON suggestions from final answer.
        
        Args:
            query: User query (usually just "generate suggestions")
            
        Returns:
            Dict with suggestions list
        """
        result = await super().run(query)
        
        # Try to parse JSON from final answer
        try:
            # Extract JSON from final answer
            final_answer = result['final_answer']
            
            # Use regex for better extraction
            import re
            json_pattern = r'```json\n(.*?)\n```'
            json_match = re.search(json_pattern, final_answer, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1).strip()
            else:
                # Fallback: try to find anything that looks like JSON
                json_match = re.search(r'(\{.*\})', final_answer, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1).strip()
                else:
                    json_str = final_answer
            
            suggestions_data = json.loads(json_str)
            result['suggestions'] = suggestions_data.get('suggestions', [])
        except Exception as e:
            # If parsing fails, return empty suggestions
            import logging
            logging.getLogger(__name__).error(f"Failed to parse suggestions JSON: {e}\nRaw answer: {result.get('final_answer')}")
            result['suggestions'] = []
            result['parse_error'] = str(e)
        
        return result
