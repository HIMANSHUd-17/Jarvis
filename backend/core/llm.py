"""
LLM Integration module supporting Groq and Ollama
"""
import json
import asyncio
from typing import Optional, Dict, Any
from core.logger import logger
from config.settings import LLM_PROVIDER, GROQ_API_KEY, GROQ_MODEL, OLLAMA_BASE_URL, OLLAMA_MODEL, JARVIS_SYSTEM_PROMPT

class LLMInterface:
    def __init__(self):
        self.provider = LLM_PROVIDER
        self.system_prompt = JARVIS_SYSTEM_PROMPT
        
        if self.provider == "groq":
            self._init_groq()
        elif self.provider == "ollama":
            self._init_ollama()
    
    def _init_groq(self):
        """Initialize Groq client"""
        try:
            from groq import Groq
            self.client = Groq(api_key=GROQ_API_KEY)
            self.model = GROQ_MODEL
            logger.info(f"Groq initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize Groq: {e}")
            raise
    
    def _init_ollama(self):
        """Initialize Ollama client"""
        try:
            import requests
            self.base_url = OLLAMA_BASE_URL
            self.model = OLLAMA_MODEL
            
            # Test connection
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                logger.info(f"Ollama initialized with model: {self.model}")
            else:
                raise Exception(f"Ollama connection failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            raise
    
    def generate_response(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate LLM response to user input
        
        Args:
            user_input: User's input text
            context: Optional context information
        
        Returns:
            Dictionary with response data
        """
        try:
            if self.provider == "groq":
                return self._generate_groq(user_input, context)
            elif self.provider == "ollama":
                return self._generate_ollama(user_input, context)
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return {
                "response": f"I encountered an error: {str(e)}",
                "action": None,
                "action_params": None,
                "error": True
            }
    
    def _generate_groq(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate response using Groq"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        if context:
            context_str = f"\nContext: {json.dumps(context)}"
            messages[-1]["content"] += context_str
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.7,
                max_tokens=500,
            )
            
            response_text = chat_completion.choices[0].message.content
            logger.info(f"Groq response: {response_text[:100]}...")
            
            return self._parse_response(response_text)
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise
    
    def _generate_ollama(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate response using Ollama"""
        import requests
        
        prompt = self.system_prompt + f"\n\nUser: {user_input}"
        
        if context:
            prompt += f"\n\nContext: {json.dumps(context)}"
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7,
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.status_code}")
            
            result = response.json()
            response_text = result.get("response", "")
            logger.info(f"Ollama response: {response_text[:100]}...")
            
            return self._parse_response(response_text)
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response"""
        try:
            # Try to parse as JSON
            parsed = json.loads(response_text)
            return {
                "response": parsed.get("response", response_text),
                "action": parsed.get("action"),
                "action_params": parsed.get("action_params"),
                "error": False
            }
        except json.JSONDecodeError:
            # If not JSON, return as plain text
            return {
                "response": response_text,
                "action": None,
                "action_params": None,
                "error": False
            }
