"""Initialize Pyrogram session for first-time setup"""
import asyncio
import os
from pyrogram import Client
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

async def init_session():
    """Initialize a new Pyrogram session"""
    api_id = int(os.getenv("API_ID", "0"))
    api_hash = os.getenv("API_HASH", "")
    phone_number = os.getenv("PHONE_NUMBER", "")
    
    if not api_id or not api_hash:
        print("❌ Error: API_ID and API_HASH must be set in .env file")
        print("Get them from: https://my.telegram.org")
        return
    
    if not phone_number:
        phone_number = input("Enter your phone number (with country code, e.g., +1234567890): ")
    
    # Create sessions directory
    sessions_dir = Path(__file__).parent.parent / "sessions"
    sessions_dir.mkdir(exist_ok=True)
    
    print("\n🔐 Initializing Telegram session...")
    print(f"📱 Phone: {phone_number}")
    print(f"🔑 API ID: {api_id}")
    
    # Create client
    app = Client(
        name="tgsecret_session",
        api_id=api_id,
        api_hash=api_hash,
        workdir=str(sessions_dir),
        phone_number=phone_number
    )
    
    try:
        # Start client and authenticate
        await app.start()
        
        # Get session string
        session_string = await app.export_session_string()
        
        # Get user info
        me = await app.get_me()
        
        print("\n✅ Session initialized successfully!")
        print(f"👤 Logged in as: {me.first_name} (@{me.username})")
        print(f"🆔 User ID: {me.id}")
        
        # Save session string to .env
        env_path = Path(__file__).parent.parent / ".env"
        
        # Read existing .env
        env_content = ""
        if env_path.exists():
            with open(env_path, "r") as f:
                lines = f.readlines()
                for line in lines:
                    if not line.startswith("SESSION_STRING="):
                        env_content += line
        
        # Add session string
        env_content += f"\n# Generated session string (DO NOT SHARE!)\n"
        env_content += f'SESSION_STRING="{session_string}"\n'
        
        # Write updated .env
        with open(env_path, "w") as f:
            f.write(env_content)
        
        print("\n📝 Session string saved to .env file")
        print("⚠️  Keep your session string secret! Anyone with it can access your account.")
        
        await app.stop()
        
        print("\n🚀 You can now start the userbot with: python -m src.main")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure your phone number is correct")
        print("2. Check your internet connection")
        print("3. Verify API_ID and API_HASH are correct")
        print("4. Try deleting sessions/*.session file and retry")
        
        if app:
            await app.stop()

if __name__ == "__main__":
    asyncio.run(init_session())
