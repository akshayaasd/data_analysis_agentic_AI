"""
Image Analysis Agent - Specialized agent for analyzing image content.
In this mock implementation, it uses filename mapping to provide realistic data insights.
"""
import asyncio
import time
from typing import Dict, Any

class ImageAnalysisAgent:
    """
    Lightweight agent for image analysis.
    Provides insights based on image filename mapping with simulated delay.
    """
    
    def __init__(self):
        # Predefined insights based on filename patterns
        self.insights = {
            "image_2": (
                "Regional Sales Analysis (Q1 2026)\n\n"
                "• North Region: 5,600 units - Top performing category, driven by recent marketing campaigns.\n"
                "• West Region: 3,200 units - Stable growth, matching year-over-year projections.\n"
                "• East Region: 2,100 units - Slight decline due to inventory logistics issues in February.\n"
                "• South Region: 1,900 units - Significantly below target; requires immediate strategic intervention.\n\n"
                "Recommended Action: Reallocate 15% of marketing budget from North to South to improve penetration."
            ),
            "image - market share breakdown": (
                "Competitive Market Landscape Analysis\n\n"
                "• Stass Wears: 25.5% share (Market Leader) - Strongest in urban demographics.\n"
                "• Retail Giants: 19.2% share - Heavy competition in price-conscious segments.\n"
                "• Boutique Brands: 15.8% share - Growing rapidly in premium artisanal categories.\n"
                "• Others (Cumulative): 39.5% share - Highly fragmented tail end.\n\n"
                "Insight: Stass Wears maintains lead through superior supply chain efficiency, but premium boutique brands are gaining 2% share annually."
            )
        }

    async def analyze_image(self, filename: str) -> Dict[str, Any]:
        """
        Analyze an image by its filename and return insights.
        Simulates AI processing delay.
        """
        start_time = time.time()
        
        # Simulate 3-second AI processing delay
        await asyncio.sleep(3)
        
        # Clean filename for matching (lower case, remove extension)
        clean_name = filename.lower()
        if '.' in clean_name:
            clean_name = clean_name.rsplit('.', 1)[0]
            
        # Try finding a match (exact or substring)
        final_answer = None
        for pattern, insight in self.insights.items():
            if pattern in clean_name or clean_name in pattern:
                final_answer = insight
                break
                
        if not final_answer:
            # Default fallback message
            final_answer = (
                f"Image analysis for '{filename}' is complete.\n\n"
                "Insights detected: General business document with text and charts.\n"
                "Specific metrics could not be extracted with high confidence.\n\n"
                "Note: For detailed regional or competitive insights, try filenames like 'Image_2' or 'Market Share Breakdown'."
            )
            
        return {
            "final_answer": final_answer,
            "execution_time": time.time() - start_time,
            "success": True
        }
