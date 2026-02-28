import os
import asyncio
from typing import List, Dict, Any
from dotenv import load_dotenv
from google import genai
from tavily import TavilyClient

# Load environment variables
load_dotenv()

class UnstructuredDataHandler:
    """
    Handles unstructured data by scraping using Tavily and processing with Gemini Flash.
    """
    def __init__(self):
        # Initialize Gemini API using the new google-genai SDK
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            print("Warning: GEMINI_API_KEY not found. Please set it in your .env file.")
            self.client = None
        else:
            self.client = genai.Client(api_key=gemini_api_key)
            self.model_id = "gemini-flash-latest"

        # Initialize Tavily client for web scraping and search
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            print("Warning: TAVILY_API_KEY not found. Please set it in your .env file.")
            self.tavily = None
        else:
            self.tavily = TavilyClient(api_key=tavily_api_key)

    async def scrape_and_process(self, query: str):
        """
        Scrapes data based on a query and uses Gemini 1.5 Flash to process it into useful info.
        """
        if not self.tavily:
            return "Tavily client NOT initialized. Check your TAVILY_API_KEY."
        
        if not self.client:
            return "Gemini client NOT initialized. Check your GEMINI_API_KEY."

        print(f"--- Step 1: Scraping and Searching for: '{query}' ---")
        
        # We use Tavily to search and get context.
        # In a real scenario, you could also use 'extract' or 'search(include_raw_content=True)'
        search_result = self.tavily.search(
            query=query, 
            search_depth="advanced", 
            max_results=3
        )
        
        # Combine results into a block of text
        scraped_data = []
        for result in search_result.get('results', []):
            scraped_data.append(f"Title: {result.get('title')}\nURL: {result.get('url')}\nContent: {result.get('content')}")

        unstructured_content = "\n\n".join(scraped_data)

        if not unstructured_content:
            return "No data was found during scraping."

        print(f"--- Step 2: Processing Unstructured Data with Gemini Flash ---")

        # Define a prompt for extraction/summarization
        prompt = f"""
        Objective: Process the following unstructured web-scraped data into a clear, structured summary.
        
        User Query: "{query}"
        
        Scraped Data Blobs:
        {unstructured_content}
        
        Instructions:
        1. Extract the key entities (people, organizations, tech, dates, etc.).
        2. Provide a 3-sentence high-level summary.
        3. Use bullet points for the main technical details or news.
        4. Keep the tone professional.
        5. Provide a 'Final Takeaway' section at the end.

        JSON-like output format preferred for the structured part, but Markdown is fine for the summary.
        """

        # Call Gemini 1.5 Flash using the new SDK
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )
        
        return response.text

async def main():
    """
    Example run function.
    """
    handler = UnstructuredDataHandler()
    
    # Query for something current to see the web search in action
    example_query = "latest major breakthroughs in LLM architectures Feb 2025"
    
    print(f"Starting example for: {example_query}")
    
    result = await handler.scrape_and_process(example_query)
    
    print("\n" + "="*60)
    print("GEMINI FLASH OUTPUT")
    print("="*60)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
