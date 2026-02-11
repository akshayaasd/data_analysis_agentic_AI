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
2. Identify interesting patterns or relationships
3. Generate exactly 3 suggestions (mix of analysis and visualization)
4. Rank them by potential insight value

You must follow this format EXACTLY:

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
    },
    ... (exactly 3 suggestions)
  ]
}
```

IMPORTANT RULES:
1. Generate EXACTLY 3 suggestions
2. Mix analysis and visualization suggestions
3. Base suggestions on actual data characteristics
4. Rank by confidence (0.0 to 1.0)
5. Make queries specific and actionable
6. Focus on insights that would be valuable to a business user

Suggestion Guidelines:
- Look for numeric columns → suggest aggregations, trends, distributions
- Look for categorical columns → suggest breakdowns, comparisons
- Look for time columns → suggest time series analysis
- Look for correlations → suggest scatter plots, heatmaps
- Look for outliers → suggest box plots, statistical analysis

Example for a sales dataset:

Thought: This dataset has Sales, Region, Product, and Date columns. I should suggest analyses that reveal business insights.
Action: Python
```python
print(df.columns.tolist())
print(df.dtypes)
print(df.describe())
```

[After observation]

Final Answer:
```json
{
  "suggestions": [
    {
      "title": "Sales Performance by Region",
      "description": "Compare total sales across different regions to identify top performers",
      "category": "visualization",
      "query": "Create a bar chart showing total sales by region",
      "expected_insight": "Identify which regions are generating the most revenue and which may need attention",
      "confidence": 0.95
    },
    {
      "title": "Product Profitability Analysis",
      "description": "Calculate profit margins for each product category",
      "category": "analysis",
      "query": "Calculate the average profit margin by product and show the top 5",
      "expected_insight": "Understand which products are most profitable and should be prioritized",
      "confidence": 0.90
    },
    {
      "title": "Sales Trends Over Time",
      "description": "Visualize how sales have changed over the time period",
      "category": "visualization",
      "query": "Create a line chart showing sales trends over time",
      "expected_insight": "Identify seasonal patterns, growth trends, or concerning declines",
      "confidence": 0.85
    }
  ]
}
```

Now, analyze the dataset and generate your top 3 suggestions."""
    
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
            json_match = final_answer.find('```json')
            if json_match != -1:
                json_start = json_match + 7
                json_end = final_answer.find('```', json_start)
                json_str = final_answer[json_start:json_end].strip()
            else:
                json_str = final_answer
            
            suggestions_data = json.loads(json_str)
            result['suggestions'] = suggestions_data.get('suggestions', [])
        except Exception as e:
            # If parsing fails, return empty suggestions
            result['suggestions'] = []
            result['parse_error'] = str(e)
        
        return result
