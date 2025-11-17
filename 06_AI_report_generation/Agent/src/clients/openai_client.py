"""OpenAI API client"""

import os
from typing import List, Dict, Any
from openai import OpenAI


class OpenAIClient:
    """OpenAI API client for AI analysis"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize OpenAI client
        
        Args:
            api_key: OpenAI API key (if not provided, reads from environment)
        """
        self._api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self._api_key:
            raise ValueError("OPENAI_API_KEY not found")
        
        self._client = OpenAI(api_key=self._api_key)
        self._model = "gpt-4o-mini"
    
    def analyze(self, prompt: str, system_prompt: str = None) -> str:
        """
        Analyze data using OpenAI
        
        Args:
            prompt: User prompt with data to analyze
            system_prompt: Optional system prompt
            
        Returns:
            AI analysis result
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content

