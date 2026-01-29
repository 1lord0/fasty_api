"""
LLM Service - Standalone version without config dependencies
"""
import os
from dotenv import load_dotenv
from groq import Groq
from typing import Optional
import time

# Load environment variables
load_dotenv()

class LLMService:
    """LLM Service with Groq API"""
    
    def __init__(self):
        # Get API key from environment
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("❌ GROQ_API_KEY not found in .env file")
        
        # Initialize Groq client - ONLY with api_key
        try:
            self.client = Groq(api_key=api_key)
        except Exception as e:
            print(f"❌ Error initializing Groq client: {e}")
            raise
        
        # Get settings from environment or use defaults
        self.model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.3"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2048"))
        
        print(f"✅ LLM Service initialized")
        print(f"   Model: {self.model}")
        print(f"   Temperature: {self.temperature}")
    
    def ask(
        self,
        question: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Ask a question to the LLM
        
        Args:
            question: User question
            system_prompt: System prompt (optional)
            temperature: Temperature override (optional)
            max_tokens: Max tokens override (optional)
            
        Returns:
            str: LLM response
        """
        try:
            start_time = time.time()
            
            # Build messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            else:
                messages.append({"role": "system", "content": "You are a helpful assistant."})
            
            messages.append({"role": "user", "content": question})
            
            # Call Groq API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature if temperature is not None else self.temperature,
                max_tokens=max_tokens if max_tokens is not None else self.max_tokens
            )
            
            response = completion.choices[0].message.content
            elapsed = time.time() - start_time
            
            print(f"✅ LLM responded in {elapsed:.2f}s")
            
            return response
            
        except Exception as e:
            print(f"❌ LLM error: {e}")
            import traceback
            traceback.print_exc()
            raise

# Global instance
_llm_service = None

def get_llm_service() -> LLMService:
    """Get or create LLM service singleton"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

def ask_llm(question: str, system_prompt: Optional[str] = None) -> str:
    """
    Convenience function for asking LLM
    
    Args:
        question: User question
        system_prompt: System prompt (optional)
        
    Returns:
        str: LLM response
    """
    try:
        service = get_llm_service()
        return service.ask(question, system_prompt)
    except Exception as e:
        print(f"❌ ask_llm error: {e}")
        raise

# Test on import (optional - comment out if not needed)
if __name__ == "__main__":
    print("Testing LLM Service...")
    try:
        response = ask_llm("Say hello!")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Test failed: {e}")