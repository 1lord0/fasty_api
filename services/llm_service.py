"""
LLM Service - Simple and Working Version
No config imports, just environment variables
"""

"""
LLM Service - Standalone version without config dependencies
"""

import os

# 🚨 CRITICAL FIX: remove proxy env BEFORE importing groq
for k in [
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "http_proxy",
    "https_proxy",
    "ALL_PROXY",
    "all_proxy",
]:
    os.environ.pop(k, None)

from dotenv import load_dotenv
from groq import Groq
from typing import Optional
import time

import os
from dotenv import load_dotenv

# Load environment ONCE at module level
load_dotenv()

# Global variables
_groq_client = None
_llm_model = None
_llm_temperature = None
_llm_max_tokens = None

def _initialize_groq():
    """Initialize Groq client ONCE"""
    global _groq_client, _llm_model, _llm_temperature, _llm_max_tokens
    
    if _groq_client is not None:
        return  # Already initialized
    
    try:
        from groq import Groq
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")
        
        # Initialize with ONLY api_key (no other parameters!)
        _groq_client = Groq(api_key=api_key)
        
        # Get settings from environment
        _llm_model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
        _llm_temperature = float(os.getenv("LLM_TEMPERATURE", "0.3"))
        _llm_max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2048"))
        
        print(f"✅ Groq client initialized successfully")
        print(f"   Model: {_llm_model}")
        
    except Exception as e:
        print(f"❌ Failed to initialize Groq client: {e}")
        raise

def ask_llm(question: str, system_prompt: str = None) -> str:
    """
    Ask a question to the LLM
    
    Args:
        question: User question
        system_prompt: Optional system prompt
        
    Returns:
        str: LLM response
    """
    # Initialize if needed
    if _groq_client is None:
        _initialize_groq()
    
    try:
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({"role": "system", "content": "You are a helpful assistant."})
        
        messages.append({"role": "user", "content": question})
        
        # Call Groq API
        completion = _groq_client.chat.completions.create(
            model=_llm_model,
            messages=messages,
            temperature=_llm_temperature,
            max_tokens=_llm_max_tokens
        )
        
        response = completion.choices[0].message.content
        print(f"✅ LLM response received")
        
        return response
        
    except Exception as e:
        print(f"❌ LLM error: {e}")
        raise

# For backwards compatibility
class LLMService:
    """Dummy class for compatibility"""
    def ask(self, question: str, system_prompt: str = None, **kwargs) -> str:
        return ask_llm(question, system_prompt)

def get_llm_service():
    """Get LLM service (for compatibility)"""
    if _groq_client is None:
        _initialize_groq()
    return LLMService()

# Initialize on import
_initialize_groq()
