"""
Multi-provider LLM service for agent communication.
Supports Groq, OpenAI, Anthropic, Ollama, and Gemini.
"""
from typing import Optional, List, Dict, Any, AsyncGenerator
import os
from config import settings

# Import LLM clients
try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

try:
    from groq import AsyncGroq
except ImportError:
    AsyncGroq = None

try:
    from anthropic import AsyncAnthropic
except ImportError:
    AsyncAnthropic = None


class LLMService:
    """Multi-provider LLM service."""
    
    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize LLM service.
        
        Args:
            provider: LLM provider (groq, openai, anthropic, ollama, gemini)
            api_key: API key for the provider
            model: Model name to use
        """
        self.provider = provider or settings.default_llm_provider
        self.model = model
        self.api_key = api_key
        
        # Initialize client based on provider
        if self.provider == "groq":
            if AsyncGroq is None:
                raise ImportError("groq package not installed")
            api_key = api_key or settings.groq_api_key or os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("Groq API key not found")
            self.client = AsyncGroq(api_key=api_key)
            if not self.model:
                self.model = settings.default_model or "llama-3.3-70b-versatile"
                
        elif self.provider == "openai":
            if AsyncOpenAI is None:
                raise ImportError("openai package not installed")
            api_key = api_key or settings.openai_api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not found")
            self.client = AsyncOpenAI(api_key=api_key)
            if not self.model:
                self.model = "gpt-4o-mini"
                
        elif self.provider == "anthropic":
            if AsyncAnthropic is None:
                raise ImportError("anthropic package not installed")
            api_key = api_key or settings.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("Anthropic API key not found")
            self.client = AsyncAnthropic(api_key=api_key)
            if not self.model:
                self.model = "claude-3-5-sonnet-20241022"
        elif self.provider == "ollama":
            if AsyncOpenAI is None:
                raise ImportError("openai package not installed (needed for Ollama compatibility)")
            # Ollama doesn't need a real API key
            self.client = AsyncOpenAI(
                base_url=f"{settings.ollama_base_url}/v1",
                api_key="ollama"
            )
            if not self.model:
                self.model = "llama3.1"
        elif self.provider == "gemini":
            if AsyncOpenAI is None:
                raise ImportError("openai package not installed (needed for Gemini OpenAI-compatible API)")
            api_key = api_key or settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("Gemini API key not found")
            self.client = AsyncOpenAI(
                base_url=settings.gemini_base_url,
                api_key=api_key
            )
            if not self.model:
                self.model = "gemini-1.5-flash"
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """
        Generate completion from LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Generated text
        """
        temperature = temperature or settings.temperature
        max_tokens = max_tokens or settings.max_tokens
        
        if self.provider == "anthropic":
            # Anthropic has different API format
            system_message = None
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    user_messages.append(msg)
            
            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": user_messages
            }
            
            if system_message:
                kwargs["system"] = system_message
            
            response = await self.client.messages.create(**kwargs)
            return response.content[0].text
        else:
            # OpenAI and Groq use the same API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                return response  # Return the stream object
            else:
                return response.choices[0].message.content
    
    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming completion from LLM.
        
        Args:
            messages: List of message dicts
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Yields:
            Text chunks
        """
        temperature = temperature or settings.temperature
        max_tokens = max_tokens or settings.max_tokens
        
        if self.provider == "anthropic":
            # Anthropic streaming
            system_message = None
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    user_messages.append(msg)
            
            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": user_messages,
                "stream": True
            }
            
            if system_message:
                kwargs["system"] = system_message
            
            async with self.client.messages.stream(**kwargs) as stream:
                async for text in stream.text_stream:
                    yield text
        else:
            # OpenAI and Groq streaming
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content


# Convenience function to get LLM service
def get_llm_service(
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> LLMService:
    """Get an LLM service instance."""
    return LLMService(provider=provider, api_key=api_key, model=model)
