"""
LLM Service - Safe, Lazy Init, Production Ready
- No crash on import
- Works without .env
- Initializes Groq ONLY when needed
"""

import os
from typing import Optional

# 🚨 Remove proxy env vars BEFORE importing groq
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

# Load .env if exists (harmless if not)
load_dotenv()

# Global state
_groq_client = None
_llm_model: Optional[str] = None
_llm_temperature: Optional[float] = None
_llm_max_tokens: Optional[int] = None


def _initialize_groq():
    """
    Initialize Groq client ONCE.
    Safe: does NOT crash app if key is missing.
    """
    global _groq_client, _llm_model, _llm_temperature, _llm_max_tokens

    if _groq_client is not None:
        return

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("⚠️ GROQ_API_KEY not found → LLM disabled")
        return

    try:
        from groq import Groq

        _groq_client = Groq(api_key=api_key)

        _llm_model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
        _llm_temperature = float(os.getenv("LLM_TEMPERATURE", "0.3"))
        _llm_max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2048"))

        print("✅ Groq initialized")
        print(f"   Model: {_llm_model}")

    except Exception as e:
        print(f"❌ Groq init failed: {e}")
        _groq_client = None


def ask_llm(question: str, system_prompt: Optional[str] = None) -> str:
    """
    Ask the LLM safely.
    Never crashes the app.
    """

    if _groq_client is None:
        _initialize_groq()

    if _groq_client is None:
        return "LLM is disabled (API key not configured)"

    messages = [
        {
            "role": "system",
            "content": system_prompt or "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": question,
        },
    ]

    try:
        completion = _groq_client.chat.completions.create(
            model=_llm_model,
            messages=messages,
            temperature=_llm_temperature,
            max_tokens=_llm_max_tokens,
        )

        return completion.choices[0].message.content

    except Exception as e:
        print(f"❌ LLM runtime error: {e}")
        return "LLM error occurred"


# Backwards compatibility
class LLMService:
    def ask(self, question: str, system_prompt: Optional[str] = None, **_) -> str:
        return ask_llm(question, system_prompt)


def get_llm_service():
    return LLMService()
