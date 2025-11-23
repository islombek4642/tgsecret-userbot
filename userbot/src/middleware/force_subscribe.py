"""Force subscribe middleware for userbot"""
from typing import List, Dict, Any
from pyrogram import Client
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ForceSubscribeMiddleware:
    def __init__(self, backend_api):
        self.backend = backend_api
        self.channels_cache = []
        self.cache_ttl = 300  # 5 minutes
        self.last_cache_update = 0
    
    async def check_subscription(self, user_id: int) -> bool:
        """Check if user is subscribed to all required channels"""
        try:
            # Get required channels from backend
            channels = await self.get_required_channels()
            
            if not channels:
                return True  # No channels required
            
            # Check subscription status via backend
            return await self.backend.check_subscription(user_id)
            
        except Exception as e:
            logger.error(f"Error checking subscription: {e}")
            return True  # Allow on error to prevent blocking
    
    async def get_required_channels(self) -> List[Dict[str, Any]]:
        """Get list of required channels from backend"""
        try:
            import time
            current_time = time.time()
            
            # Use cache if still valid
            if self.channels_cache and (current_time - self.last_cache_update) < self.cache_ttl:
                return self.channels_cache
            
            # Fetch from backend
            channels = await self.backend.get_required_channels()
            
            # Update cache
            self.channels_cache = channels
            self.last_cache_update = current_time
            
            return channels
            
        except Exception as e:
            logger.error(f"Error getting required channels: {e}")
            return []
    
    async def check_user_in_channel(self, client: Client, user_id: int, channel_id: int) -> bool:
        """Check if a user is member of a specific channel"""
        try:
            member = await client.get_chat_member(channel_id, user_id)
            return member.status in ["creator", "administrator", "member"]
        except UserNotParticipant:
            return False
        except ChatAdminRequired:
            logger.error(f"Bot needs admin rights in channel {channel_id}")
            return False
        except Exception as e:
            logger.error(f"Error checking channel membership: {e}")
            return False
    
    async def get_join_links(self, channels: List[Dict[str, Any]]) -> str:
        """Generate join links for channels"""
        links = []
        for channel in channels:
            username = channel.get('username', '')
            if username:
                links.append(f"https://t.me/{username}")
        return "\n".join(links)
