"""Groq LLM client wrapper for consistent API usage."""
from typing import Optional, List, Dict, Any
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential
import config


class GroqClient:
    """Wrapper for Groq API client with retry logic and error handling."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize Groq client.
        
        Args:
            api_key: Groq API key. If None, uses config.GROQ_API_KEY
            model: Model name. If None, uses config.GROQ_MODEL
        """
        self.api_key = api_key or config.GROQ_API_KEY
        self.model = model or config.GROQ_MODEL
        self.client = Groq(api_key=self.api_key)
    
    @retry(
        stop=stop_after_attempt(config.MAX_RETRIES),
        wait=wait_exponential(multiplier=config.RETRY_DELAY, min=1, max=10)
    )
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False
    ) -> str:
        """Generate text using Groq API.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream the response
            
        Returns:
            Generated text string
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            # Groq client uses httpx internally, timeout is handled by the client
            # Set a reasonable timeout to prevent hanging
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or config.MAX_RESPONSE_TOKENS,
                temperature=temperature or config.TEMPERATURE,
                stream=stream
            )
            
            if stream:
                # For streaming, collect chunks
                full_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                return full_response
            else:
                return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")
    
    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate JSON response from LLM.
        
        Args:
            prompt: User prompt requesting JSON
            system_prompt: System prompt
            
        Returns:
            Parsed JSON dictionary
        """
        json_prompt = f"{prompt}\n\nRespond with valid JSON only, no markdown formatting."
        response = self.generate(json_prompt, system_prompt)
        
        # Try to extract JSON from response
        import json
        import re
        
        # Remove markdown code blocks if present
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            response = json_match.group(1)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON object in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            raise ValueError(f"Could not parse JSON from response: {response[:200]}")

