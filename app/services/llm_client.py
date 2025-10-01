"""
LLM client for communication with language models.
Handles all LLM API interactions.
"""
import json
from typing import Dict, Any
import litellm
from app.config import settings


class LLMClient:
    """Client for interacting with LLM providers via LiteLLM."""
    
    def __init__(self):
        """Initialize the LLM client with configuration."""
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
    
    async def complete(
        self, 
        system_message: str, 
        user_prompt: str,
        json_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Send a completion request to the LLM.
        
        Args:
            system_message: System role message for context
            user_prompt: User prompt to send to the LLM
            json_mode: Whether to request JSON-formatted response
            
        Returns:
            Parsed JSON response from the LLM
            
        Raises:
            json.JSONDecodeError: If response is not valid JSON
            Exception: For other LLM-related errors
        """
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt}
        ]
        
        # Build request parameters
        request_params = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature
        }
        
        # Add JSON mode if requested
        if json_mode:
            request_params["response_format"] = {"type": "json_object"}
        
        # Call LLM
        response = await litellm.acompletion(**request_params)
        
        # Extract content
        content = response.choices[0].message.content
        
        # Parse JSON if in JSON mode
        if json_mode:
            return json.loads(content)
        
        return {"content": content}
