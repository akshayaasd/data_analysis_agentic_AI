import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from config import settings
from services.llm_service import get_llm_service

print(f"ROOT_DIR: {os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}")
print(f"Settings Groq API Key present: {bool(settings.groq_api_key)}")
print(f"OS Env Groq API Key present: {bool(os.getenv('GROQ_API_KEY'))}")
print(f"Default Model: {settings.default_model}")

try:
    llm = get_llm_service()
    print("LLM Service initialized successfully")
except Exception as e:
    print(f"Failed to initialize LLM Service: {e}")
