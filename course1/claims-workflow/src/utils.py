"""Utility functions"""

import os
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Default model
DEFAULT_MODEL = os.getenv("MODEL", "gpt-4.1-nano")


def get_completion(
    messages: Optional[List[Dict[str, str]]] = None,
    system_prompt: Optional[str] = None,
    user_prompt: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0,
    max_tokens: int = 500
) -> str:
    """
    Get completion from OpenAI API.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        system_prompt: Optional system message to prepend
        user_prompt: Optional user message to append
        model: Model to use (defaults to env var MODEL)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        
    Returns:
        str: The completion text
        
    Raises:
        ValueError: If no messages provided
        RuntimeError: If API call fails
    """
    messages_list = list(messages) if messages else []
    
    if system_prompt:
        messages_list.insert(0, {"role": "system", "content": system_prompt})
    if user_prompt:
        messages_list.append({"role": "user", "content": user_prompt})
    
    if not messages_list:
        raise ValueError("Must provide messages, system_prompt, or user_prompt")
    
    try:
        response = client.chat.completions.create(
            model=model or DEFAULT_MODEL,
            messages=messages_list,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"OpenAI API error: {e}") from e