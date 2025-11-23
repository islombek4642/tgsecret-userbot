"""AI handler for .ask command"""
import asyncio
import json
from typing import Dict, Any, Optional
import aiohttp
from datetime import datetime, timedelta

from ..config import AI_ENDPOINTS, DEFAULT_AI_MODELS, AI_RATE_LIMIT
from ..utils.logger import get_logger

logger = get_logger(__name__)

class AIHandler:
    def __init__(self, backend_api):
        self.backend = backend_api
        self.rate_limit_cache = {}
        
    async def process_query(self, user_id: int, prompt: str) -> Dict[str, Any]:
        """Process AI query from user"""
        try:
            # Check rate limit
            if not self._check_rate_limit(user_id):
                return {
                    "success": False,
                    "error": "Rate limit exceeded. Please wait a minute before asking again."
                }
            
            # Get user's API key from backend
            api_config = await self.backend.get_user_api_key(str(user_id))
            
            if not api_config or not api_config.get('key'):
                return {
                    "success": False,
                    "error": "No API key configured. Please add your AI API key in the admin panel."
                }
            
            provider = api_config.get('provider', 'openai')
            api_key = api_config.get('key')
            model = api_config.get('model') or DEFAULT_AI_MODELS.get(provider)
            endpoint = api_config.get('endpoint') or AI_ENDPOINTS.get(provider)
            
            # Call appropriate AI provider
            if provider == 'openai':
                response = await self._call_openai(api_key, prompt, model, endpoint)
            elif provider == 'claude':
                response = await self._call_claude(api_key, prompt, model, endpoint)
            elif provider == 'gemini':
                response = await self._call_gemini(api_key, prompt, model, endpoint)
            else:
                response = await self._call_custom(api_key, prompt, endpoint, api_config)
            
            if response['success']:
                # Log usage to backend
                await self.backend.log_ai_usage(str(user_id), provider, len(prompt), len(response['response']))
                
            return response
            
        except Exception as e:
            logger.error(f"Error processing AI query: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _check_rate_limit(self, user_id: int) -> bool:
        """Check if user has exceeded rate limit"""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old entries
        self.rate_limit_cache = {
            uid: times for uid, times in self.rate_limit_cache.items()
            if times and times[-1] > minute_ago
        }
        
        # Check user's requests
        user_requests = self.rate_limit_cache.get(user_id, [])
        user_requests = [t for t in user_requests if t > minute_ago]
        
        if len(user_requests) >= AI_RATE_LIMIT:
            return False
        
        user_requests.append(now)
        self.rate_limit_cache[user_id] = user_requests
        return True
    
    async def _call_openai(self, api_key: str, prompt: str, model: str, endpoint: str) -> Dict[str, Any]:
        """Call OpenAI API"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4096,
            "temperature": 0.7
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "response": data['choices'][0]['message']['content']
                        }
                    else:
                        error_data = await response.text()
                        return {
                            "success": False,
                            "error": f"OpenAI API error: {response.status} - {error_data}"
                        }
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _call_claude(self, api_key: str, prompt: str, model: str, endpoint: str) -> Dict[str, Any]:
        """Call Claude API"""
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4096
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "response": data['content'][0]['text']
                        }
                    else:
                        error_data = await response.text()
                        return {
                            "success": False,
                            "error": f"Claude API error: {response.status} - {error_data}"
                        }
        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _call_gemini(self, api_key: str, prompt: str, model: str, endpoint: str) -> Dict[str, Any]:
        """Call Gemini API"""
        url = f"{endpoint}/{model}:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "response": data['candidates'][0]['content']['parts'][0]['text']
                        }
                    else:
                        error_data = await response.text()
                        return {
                            "success": False,
                            "error": f"Gemini API error: {response.status} - {error_data}"
                        }
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _call_custom(self, api_key: str, prompt: str, endpoint: str, config: Dict) -> Dict[str, Any]:
        """Call custom AI endpoint"""
        headers = config.get('headers', {})
        headers['Authorization'] = f"Bearer {api_key}"
        
        payload = config.get('payload_template', {})
        payload['prompt'] = prompt
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Try to extract response from common patterns
                        result = data.get('response') or data.get('text') or data.get('output') or str(data)
                        return {
                            "success": True,
                            "response": result
                        }
                    else:
                        error_data = await response.text()
                        return {
                            "success": False,
                            "error": f"Custom API error: {response.status} - {error_data}"
                        }
        except Exception as e:
            logger.error(f"Custom API call failed: {e}")
            return {"success": False, "error": str(e)}
