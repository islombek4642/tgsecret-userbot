"""Main userbot module with core functionality"""
import asyncio
import logging
import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pyrogram.errors import FloodWait, MessageNotModified
import aiohttp
import aiofiles

from config import *
from handlers.media_handler import MediaHandler
from handlers.story_handler import StoryHandler
from handlers.ai_handler import AIHandler
from middleware.force_subscribe import ForceSubscribeMiddleware
from utils.logger import setup_logger
from utils.backend_api import BackendAPI

# Setup logger
logger = setup_logger('TgSecret', LOG_FILE, LOG_LEVEL)

class TgSecretUserbot:
    def __init__(self):
        """Initialize the userbot"""
        self.app: Optional[Client] = None
        self.backend = BackendAPI(BACKEND_URL, WEBHOOK_SECRET)
        self.media_handler = MediaHandler(self.backend)
        self.story_handler = StoryHandler(self.backend)
        self.ai_handler = AIHandler(self.backend)
        self.force_subscribe = ForceSubscribeMiddleware(self.backend)
        self.active_downloads = {}
        self.download_semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)
        
    async def initialize(self):
        """Initialize Pyrogram client"""
        session_name = "tgsecret_session"
        session_file = SESSIONS_PATH / f"{session_name}.session"
        
        # Create client
        self.app = Client(
            name=session_name,
            api_id=API_ID,
            api_hash=API_HASH,
            workdir=str(SESSIONS_PATH),
            session_string=SESSION_STRING if SESSION_STRING else None
        )
        
        # Register handlers
        self._register_handlers()
        
        logger.info("Userbot initialized successfully")
        
    def _register_handlers(self):
        """Register all command handlers"""
        
        # .ok command - Save disappearing media
        @self.app.on_message(filters.me & filters.command("ok", prefixes="."))
        async def save_disappearing_media(client: Client, message: Message):
            try:
                # Check force subscribe
                if not await self.force_subscribe.check_subscription(message.from_user.id):
                    channels = await self.force_subscribe.get_required_channels()
                    links = "\n".join([f"• @{ch['username']}" for ch in channels])
                    await message.edit_text(
                        f"❌ **Subscription Required**\n\n"
                        f"Please join the following channels first:\n{links}"
                    )
                    return
                
                # Check if replying to media
                if not message.reply_to_message:
                    await message.edit_text("❌ Reply to a media message with `.ok` to save it")
                    return
                
                reply = message.reply_to_message
                
                # Check if it's view-once media
                if not (reply.photo or reply.video or reply.document or reply.audio):
                    await message.edit_text("❌ Reply message doesn't contain media")
                    return
                
                # Download and save media
                await message.edit_text("⏳ Downloading media...")
                result = await self.media_handler.save_disappearing_media(client, reply, message)
                
                if result['success']:
                    await message.delete()  # Delete command message
                    logger.info(f"Saved disappearing media: {result['file_id']}")
                else:
                    await message.edit_text(f"❌ Failed to save media: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"Error in .ok handler: {e}")
                await message.edit_text(f"❌ Error: {str(e)}")
        
        # .get/.story command - Save stories
        @self.app.on_message(filters.me & filters.command(["get", "story"], prefixes="."))
        async def save_stories(client: Client, message: Message):
            try:
                # Check force subscribe
                if not await self.force_subscribe.check_subscription(message.from_user.id):
                    channels = await self.force_subscribe.get_required_channels()
                    links = "\n".join([f"• @{ch['username']}" for ch in channels])
                    await message.edit_text(
                        f"❌ **Subscription Required**\n\n"
                        f"Please join the following channels first:\n{links}"
                    )
                    return
                
                # Parse username
                args = message.text.split(maxsplit=1)
                if len(args) < 2:
                    await message.edit_text("❌ Usage: `.get username` or `.story username`")
                    return
                
                username = args[1].strip().replace("@", "")
                await message.edit_text(f"📱 Fetching stories from @{username}...")
                
                # Download stories
                result = await self.story_handler.download_stories(client, username, message)
                
                if result['success']:
                    count = result.get('count', 0)
                    await message.edit_text(
                        f"✅ **Stories Saved**\n\n"
                        f"Downloaded {count} stories from @{username}\n"
                        f"Check your Saved Messages 📥"
                    )
                else:
                    await message.edit_text(f"❌ Failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"Error in .get handler: {e}")
                await message.edit_text(f"❌ Error: {str(e)}")
        
        # .ask command - AI assistant
        @self.app.on_message(filters.me & filters.command("ask", prefixes="."))
        async def ai_assistant(client: Client, message: Message):
            try:
                # Check force subscribe
                if not await self.force_subscribe.check_subscription(message.from_user.id):
                    channels = await self.force_subscribe.get_required_channels()
                    links = "\n".join([f"• @{ch['username']}" for ch in channels])
                    await message.edit_text(
                        f"❌ **Subscription Required**\n\n"
                        f"Please join the following channels first:\n{links}"
                    )
                    return
                
                # Parse prompt
                args = message.text.split(maxsplit=1)
                if len(args) < 2:
                    await message.edit_text("❌ Usage: `.ask your question here`")
                    return
                
                prompt = args[1].strip()
                await message.edit_text("🤔 Thinking...")
                
                # Get AI response
                result = await self.ai_handler.process_query(message.from_user.id, prompt)
                
                if result['success']:
                    response = result['response']
                    
                    # Handle long responses
                    if len(response) > 4096:
                        # Split into multiple messages
                        chunks = [response[i:i+4096] for i in range(0, len(response), 4096)]
                        await message.edit_text(chunks[0])
                        for chunk in chunks[1:]:
                            await message.reply_text(chunk)
                    else:
                        await message.edit_text(response)
                else:
                    error_msg = result.get('error', 'Unknown error')
                    if 'api_key' in error_msg.lower():
                        await message.edit_text(
                            "❌ **API Key Required**\n\n"
                            "Please configure your AI API key in the admin panel:\n"
                            f"{BACKEND_URL.replace('3001', '3000')}/api-keys"
                        )
                    else:
                        await message.edit_text(f"❌ Error: {error_msg}")
                        
            except Exception as e:
                logger.error(f"Error in .ask handler: {e}")
                await message.edit_text(f"❌ Error: {str(e)}")
        
        # .help command
        @self.app.on_message(filters.me & filters.command("help", prefixes="."))
        async def show_help(client: Client, message: Message):
            help_text = """
**🤖 TgSecret Commands**

• `.ok` - Reply to disappearing/view-once media to save it
• `.get username` - Download stories from a user  
• `.story username` - Alternative for .get
• `.ask question` - Ask AI assistant anything

**⚙️ Admin Panel**
Visit http://localhost:3000 to:
- Configure AI API keys
- Manage force-subscribe channels  
- View saved media logs
- Control userbot session

**📝 Notes**
- All saved media goes to Saved Messages
- Story viewing is anonymous (won't show as viewed)
- Configure AI provider in admin panel first
            """
            await message.edit_text(help_text)
            
    async def start(self):
        """Start the userbot"""
        try:
            await self.initialize()
            await self.app.start()
            
            me = await self.app.get_me()
            logger.info(f"Userbot started as @{me.username} (ID: {me.id})")
            
            # Notify backend that bot is online
            await self.backend.update_session_status(str(me.id), True)
            
            # Send startup message
            await self.app.send_message(
                "me",
                "✅ **TgSecret Userbot Started**\n\n"
                "Type `.help` for available commands"
            )
            
            # Keep the bot running
            await idle()
            
        except Exception as e:
            logger.error(f"Failed to start userbot: {e}")
            raise
            
    async def stop(self):
        """Stop the userbot"""
        try:
            if self.app:
                me = await self.app.get_me()
                await self.backend.update_session_status(str(me.id), False)
                await self.app.stop()
                logger.info("Userbot stopped")
        except Exception as e:
            logger.error(f"Error stopping userbot: {e}")
            
async def main():
    """Main entry point"""
    bot = TgSecretUserbot()
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
