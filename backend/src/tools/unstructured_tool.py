import os
import sys
from typing import Optional
from tavily import TavilyClient
from config import settings
from src.services.llm_service import get_llm_service

class UnstructuredDataTool:
    """
    Tool for handling unstructured data by searching the web and processing with Gemini.
    """
    def __init__(self):
        # Use the centralized LLM service, defaulting to gemini
        try:
            self.llm = get_llm_service()
        except Exception as e:
            print(f"Error initializing LLM in UnstructuredDataTool: {e}", file=sys.stderr)
            self.llm = None

        # Initialize Tavily client for web scraping and search
        tavily_api_key = settings.tavily_api_key or os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            self.tavily = None
        else:
            self.tavily = TavilyClient(api_key=tavily_api_key)

    async def search_and_summarize(self, query: str) -> str:
        """
        Searches the web and returns a structured summary.
        """
        if not self.tavily:
            return "Error: Tavily API key not configured. Cannot perform web search."
        
        if not self.llm:
            return "Error: Gemini API key not configured. Cannot process search results."

        try:
            # Search using Tavily
            search_result = self.tavily.search(
                query=query, 
                search_depth="advanced", 
                max_results=3
            )
            
            scraped_data = []
            for result in search_result.get('results', []):
                scraped_data.append(f"Title: {result.get('title')}\nURL: {result.get('url')}\nContent: {result.get('content')}")

            unstructured_content = "\n\n".join(scraped_data)

            if not unstructured_content:
                return "No relevant information found on the web for this query."

            # Process with Gemini Flash
            prompt = f"""
            Objective: Process the following unstructured web-scraped data into a clear, structured summary.
            
            User Query: "{query}"
            
            Scraped Data Blobs:
            {unstructured_content}
            
            Instructions:
            1. Extract the key entities (people, organizations, tech, dates, etc.).
            2. Provide a concise high-level summary.
            3. Use bullet points for the main technical details or news.
            4. Keep the tone professional.
            5. Provide a 'Final Takeaway' section at the end.
            """

            # Process with Gemini using LLMService
            messages = [{"role": "user", "content": prompt}]
            response_text = await self.llm.generate(messages=messages)
            # Sanitize carriage returns to prevent terminal overwrite glitches
            if response_text:
                response_text = response_text.replace('\r\n', '\n').replace('\r', '\n')
            return response_text
        except Exception as e:
            return f"Error during web search/processing: {str(e)}"
