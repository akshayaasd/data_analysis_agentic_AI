# Handle Unstructured Data with Gemini Flash & Tavily

This folder contains a solution for handling unstructured data by combining web scraping (via Tavily) and advanced text processing (via Gemini 1.5 Flash).

## Features
- **Tavily for Web Scraping**: Efficiently searches and extracts data from the web based on a query.
- **Gemini 1.5 Flash for Logic**: Processes the resulting unstructured blobs of text into a clean, structured summary or JSON format.
- **Asynchronous Execution**: Uses Python's `asyncio` for faster non-blocking calls.

## Prerequisites
1.  **GEMINI_API_KEY**: Get it from [Google AI Studio](https://aistudio.google.com/).
2.  **TAVILY_API_KEY**: Get it from [Tavily AI](https://tavily.com/).

## Setup & Installations
Install the required packages:
```bash
pip install -r requirements.txt
```

Ensure your `.env` file in the root directory (or in this folder) contains:
```env
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

## How to Run
Run the example script:
```bash
python handle_unstructured_data.py
```

## Custom Usage
You can import the `UnstructuredDataHandler` class in your own projects:
```python
from handle_unstructured_data import UnstructuredDataHandler
# ... initialize and use await handler.scrape_and_process(query)
```
