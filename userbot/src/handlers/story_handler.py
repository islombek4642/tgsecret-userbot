"""Story handler for downloading and saving stories"""
import asyncio
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import hashlib

from pyrogram import Client
from pyrogram.types import Message, Story
from pyrogram.errors import FloodWait, UsernameNotOccupied, UsernameInvalid
import aiofiles

from ..config import STORAGE_PATH, TEMP_PATH, MAX_FILE_SIZE
from ..utils.logger import get_logger

logger = get_logger(__name__)

class StoryHandler:
    def __init__(self, backend_api):
        self.backend = backend_api
        
    async def download_stories(
        self, 
        client: Client, 
        username: str,
        status_message: Message
    ) -> Dict[str, Any]:
        """Download all stories from a user"""
        try:
            # Get user
            try:
                user = await client.get_users(username)
            except (UsernameNotOccupied, UsernameInvalid):
                return {"success": False, "error": f"User @{username} not found"}
            
            # Check if user has stories
            if not user.has_stories:
                return {"success": False, "error": f"@{username} has no active stories"}
            
            # Get stories
            await status_message.edit_text(f"📱 Fetching stories from @{username}...")
            
            stories = []
            async for story in client.get_chat_history(user.id, limit=100):
                if isinstance(story, Story):
                    stories.append(story)
            
            if not stories:
                return {"success": False, "error": "No stories found"}
            
            # Download each story
            downloaded_count = 0
            failed_count = 0
            
            for idx, story in enumerate(stories, 1):
                try:
                    await status_message.edit_text(
                        f"📥 Downloading story {idx}/{len(stories)}..."
                    )
                    
                    # Create temp directory
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    story_id = f"{username}_{story.id}_{timestamp}"
                    temp_dir = TEMP_PATH / story_id
                    temp_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Determine media type and download
                    media_type = None
                    file_path = None
                    
                    if story.photo:
                        media_type = "photo"
                        file_path = await story.download(
                            file_name=str(temp_dir / f"story_photo_{story.id}")
                        )
                    elif story.video:
                        media_type = "video"
                        file_path = await story.download(
                            file_name=str(temp_dir / f"story_video_{story.id}")
                        )
                    
                    if not file_path:
                        failed_count += 1
                        continue
                    
                    # Prepare caption
                    caption = (
                        f"📱 **Story from @{username}**\n"
                        f"Type: {media_type.capitalize()}\n"
                        f"Date: {story.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    )
                    
                    if story.caption:
                        caption += f"\n📝 Caption:\n{story.caption}"
                    
                    # Upload to Saved Messages
                    saved_msg = None
                    if media_type == "photo":
                        saved_msg = await client.send_photo("me", file_path, caption=caption)
                    elif media_type == "video":
                        saved_msg = await client.send_video("me", file_path, caption=caption)
                    
                    # Move to permanent storage
                    permanent_dir = STORAGE_PATH / "stories" / username / datetime.now().strftime("%Y%m")
                    permanent_dir.mkdir(parents=True, exist_ok=True)
                    permanent_path = permanent_dir / f"{story.id}_{os.path.basename(file_path)}"
                    shutil.move(file_path, permanent_path)
                    
                    # Log to backend
                    metadata = {
                        "target_username": username,
                        "story_id": str(story.id),
                        "media_type": media_type,
                        "file_path": str(permanent_path),
                        "file_size": os.path.getsize(permanent_path),
                        "caption": story.caption,
                        "view_count": getattr(story, 'views', None),
                        "expires_at": getattr(story, 'expire_date', None)
                    }
                    
                    await self.backend.log_story(
                        user_id=str(client.me.id),
                        metadata=metadata
                    )
                    
                    downloaded_count += 1
                    
                    # Cleanup temp directory
                    try:
                        shutil.rmtree(temp_dir)
                    except:
                        pass
                    
                    # Add delay to avoid flooding
                    await asyncio.sleep(1)
                    
                except FloodWait as e:
                    logger.warning(f"FloodWait: sleeping for {e.value} seconds")
                    await asyncio.sleep(e.value)
                except Exception as e:
                    logger.error(f"Error downloading story {story.id}: {e}")
                    failed_count += 1
            
            return {
                "success": True,
                "count": downloaded_count,
                "failed": failed_count
            }
            
        except Exception as e:
            logger.error(f"Error in download_stories: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
