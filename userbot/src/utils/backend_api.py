"""Backend API client for userbot"""
import aiohttp
import json
from typing import Dict, Any, Optional
from ..config import BACKEND_URL, WEBHOOK_SECRET
from ..utils.logger import get_logger

logger = get_logger(__name__)

class BackendAPI:
    def __init__(self, base_url: str, webhook_secret: str):
        self.base_url = base_url
        self.webhook_secret = webhook_secret
        self.session = None
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to backend"""
        await self._ensure_session()
        
        headers = {
            "X-Webhook-Secret": self.webhook_secret,
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(method, url, json=data, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Backend API error: {response.status} - {error_text}")
                    return {"success": False, "error": f"API error: {response.status}"}
        except Exception as e:
            logger.error(f"Backend API request failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_session_status(self, user_id: str, is_active: bool) -> Dict[str, Any]:
        """Update userbot session status"""
        return await self._request("POST", "/session/status", {
            "userId": user_id,
            "isActive": is_active
        })
    
    async def get_user_api_key(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's AI API key configuration"""
        result = await self._request("GET", f"/api-keys/user/{user_id}")
        return result if result.get("success") else None
    
    async def log_saved_media(self, user_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Log saved media to backend"""
        return await self._request("POST", "/media/log", {
            "userId": user_id,
            **metadata
        })
    
    async def log_story(self, user_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Log downloaded story to backend"""
        return await self._request("POST", "/stories/log", {
            "userId": user_id,
            **metadata
        })
    
    async def log_ai_usage(self, user_id: str, provider: str, prompt_tokens: int, response_tokens: int) -> Dict[str, Any]:
        """Log AI usage to backend"""
        return await self._request("POST", "/ai/usage", {
            "userId": user_id,
            "provider": provider,
            "promptTokens": prompt_tokens,
            "responseTokens": response_tokens
        })
    
    async def get_required_channels(self) -> list:
        """Get list of force-subscribe channels"""
        result = await self._request("GET", "/force-subscribe/channels")
        return result.get("channels", []) if result.get("success") else []
    
    async def check_subscription(self, user_id: int) -> bool:
        """Check if user is subscribed to all required channels"""
        result = await self._request("POST", "/force-subscribe/check", {
            "userId": str(user_id)
        })
        return result.get("isSubscribed", False) if result.get("success") else False
    
    async def close(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
