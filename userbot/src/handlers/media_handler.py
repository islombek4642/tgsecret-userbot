"""Media handler for saving disappearing media"""
import asyncio
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import hashlib

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import FloodWait, MediaEmpty
import aiofiles

from ..config import STORAGE_PATH, TEMP_PATH, MAX_FILE_SIZE
from ..utils.logger import get_logger

logger = get_logger(__name__)

class MediaHandler:
    def __init__(self, backend_api):
        self.backend = backend_api
        self.downloads_in_progress = {}
        
    async def save_disappearing_media(
        self, 
        client: Client, 
        media_message: Message,
        command_message: Message
    ) -> Dict[str, Any]:
        """Save disappearing/view-once media to Saved Messages"""
        try:
            # Determine media type and file
            media_type = None
            media_file = None
            file_size = 0
            
            if media_message.photo:
                media_type = "photo"
                media_file = media_message.photo
                file_size = media_file.file_size if hasattr(media_file, 'file_size') else 0
            elif media_message.video:
                media_type = "video"
                media_file = media_message.video
                file_size = media_file.file_size
            elif media_message.document:
                media_type = "document"
                media_file = media_message.document
                file_size = media_file.file_size
            elif media_message.audio:
                media_type = "audio"
                media_file = media_message.audio
                file_size = media_file.file_size
            elif media_message.voice:
                media_type = "voice"
                media_file = media_message.voice
                file_size = media_file.file_size
            else:
                return {"success": False, "error": "Unsupported media type"}
            
            # Check file size
            if file_size > MAX_FILE_SIZE:
                return {"success": False, "error": f"File too large (max {MAX_FILE_SIZE/1024/1024/1024:.1f}GB)"}
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_id = hashlib.md5(f"{media_message.id}_{timestamp}".encode()).hexdigest()[:8]
            
            # Create temp file path
            temp_dir = TEMP_PATH / file_id
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Download media
            logger.info(f"Downloading {media_type} from message {media_message.id}")
            await command_message.edit_text(f"⬇️ Downloading {media_type}...")
            
            try:
                file_path = await media_message.download(
                    file_name=str(temp_dir / f"{media_type}_{file_id}"),
                    progress=self._download_progress,
                    progress_args=(command_message, media_type)
                )
            except FloodWait as e:
                logger.warning(f"FloodWait: sleeping for {e.value} seconds")
                await asyncio.sleep(e.value)
                file_path = await media_message.download(
                    file_name=str(temp_dir / f"{media_type}_{file_id}")
                )
            
            if not file_path:
                return {"success": False, "error": "Failed to download media"}
            
            # Prepare caption
            caption = (
                f"💾 **Saved Media**\n"
                f"Type: {media_type.capitalize()}\n"
                f"From: {media_message.from_user.mention if media_message.from_user else 'Unknown'}\n"
                f"Date: {media_message.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            
            if media_message.caption:
                caption += f"\n📝 Original caption:\n{media_message.caption}"
            
            # Upload to Saved Messages
            await command_message.edit_text(f"📤 Saving to Saved Messages...")
            
            saved_msg = None
            if media_type == "photo":
                saved_msg = await client.send_photo("me", file_path, caption=caption)
            elif media_type == "video":
                saved_msg = await client.send_video("me", file_path, caption=caption)
            elif media_type == "document":
                saved_msg = await client.send_document("me", file_path, caption=caption)
            elif media_type == "audio":
                saved_msg = await client.send_audio("me", file_path, caption=caption)
            elif media_type == "voice":
                saved_msg = await client.send_voice("me", file_path, caption=caption)
            
            # Move file to permanent storage
            permanent_dir = STORAGE_PATH / "saved_media" / datetime.now().strftime("%Y%m")
            permanent_dir.mkdir(parents=True, exist_ok=True)
            permanent_path = permanent_dir / f"{file_id}_{os.path.basename(file_path)}"
            shutil.move(file_path, permanent_path)
            
            # Log to backend
            metadata = {
                "media_type": media_type,
                "original_chat_id": media_message.chat.id,
                "original_msg_id": media_message.id,
                "saved_msg_id": saved_msg.id if saved_msg else None,
                "file_path": str(permanent_path),
                "file_size": file_size,
                "sender_username": media_message.from_user.username if media_message.from_user else None,
                "sender_name": media_message.from_user.first_name if media_message.from_user else None,
                "is_view_once": True,  # Assuming it's view-once if using .ok command
                "caption": media_message.caption
            }
            
            await self.backend.log_saved_media(
                user_id=str(client.me.id),
                metadata=metadata
            )
            
            # Cleanup temp directory
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
            
            return {
                "success": True,
                "file_id": file_id,
                "saved_msg_id": saved_msg.id if saved_msg else None,
                "file_path": str(permanent_path)
            }
            
        except Exception as e:
            logger.error(f"Error saving media: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def _download_progress(self, current: int, total: int, message: Message, media_type: str):
        """Show download progress"""
        try:
            if total > 0:
                percentage = (current / total) * 100
                bar_length = 20
                filled = int(bar_length * current // total)
                bar = "█" * filled + "░" * (bar_length - filled)
                
                text = (
                    f"⬇️ **Downloading {media_type}**\n\n"
                    f"{bar} {percentage:.1f}%\n"
                    f"{current/1024/1024:.1f}MB / {total/1024/1024:.1f}MB"
                )
                
                # Update every 5%
                if int(percentage) % 5 == 0:
                    await message.edit_text(text)
        except MessageNotModified:
            pass
        except Exception as e:
            logger.error(f"Error updating progress: {e}")
