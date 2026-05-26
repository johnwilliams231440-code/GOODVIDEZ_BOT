#!/usr/bin/env python3
"""
TEXT-TO-SPEECH TELEGRAM BOT
Converts any text message to speech audio
No external APIs - uses offline TTS engine
"""

import os
import sys
import logging
import tempfile
from datetime import datetime

# Force immediate log output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

print(f"[{datetime.now().isoformat()}] 🎤 TEXT-TO-SPEECH BOT INITIALIZING...")
print(f"[{datetime.now().isoformat()}] 🐍 Python version: {sys.version}")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get bot token
TOKEN = os.environ.get("TELEGRAM_TOKEN")
print(f"[{datetime.now().isoformat()}] 🔑 Token present: {'YES' if TOKEN else 'NO'}")

if not TOKEN:
    print(f"[{datetime.now().isoformat()}] ❌ CRITICAL ERROR: TELEGRAM_TOKEN not set!")
    print(f"[{datetime.now().isoformat()}] 💡 Add it in Render Dashboard → Environment")
    sys.exit(1)

print(f"[{datetime.now().isoformat()}] ✅ Token found (first 5 chars): {TOKEN[:5]}...")

# Import Telegram libraries
try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    print(f"[{datetime.now().isoformat()}] ✅ Telegram imports successful")
except Exception as e:
    print(f"[{datetime.now().isoformat()}] ❌ Telegram import error: {e}")
    sys.exit(1)

# Import TTS library
try:
    import pyttsx3
    print(f"[{datetime.now().isoformat()}] ✅ pyttsx3 import successful")
except Exception as e:
    print(f"[{datetime.now().isoformat()}] ❌ pyttsx3 import error: {e}")
    print(f"[{datetime.now().isoformat()}] 💡 This usually works on Render. Continuing...")
    pyttsx3 = None

# Initialize TTS engine (will be created per message to avoid issues)
def create_tts_engine():
    """Create and configure TTS engine"""
    try:
        engine = pyttsx3.init()
        # Configure voice properties
        engine.setProperty('rate', 150)    # Speed of speech
        engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
        
        # Get available voices and set to first available
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)
        
        return engine
    except Exception as e:
        logger.error(f"Failed to create TTS engine: {e}")
        return None

def text_to_speech(text, filename):
    """Convert text to speech and save to file"""
    try:
        engine = create_tts_engine()
        if not engine:
            return False
        
        # Save to file
        engine.save_to_file(text, filename)
        engine.runAndWait()
        engine.stop()
        return True
    except Exception as e:
        logger.error(f"TTS conversion error: {e}")
        return False

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"📨 /start from {user.id} (@{user.username})")
    
    welcome_text = (
        "🎤 *Welcome to Text-to-Speech Bot!*\n\n"
        "Send me any text, and I'll convert it to speech.\n\n"
        "*Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this help\n"
        "/info - Bot information\n\n"
        "*Features:*\n"
        "✅ No external APIs needed\n"
        "✅ Works entirely offline\n"
        "✅ Supports any language\n"
        "✅ Fast conversion\n\n"
        "Just type any message and I'll send you an audio file!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 *How to use this bot:*\n\n"
        "1️⃣ Send any text message (max 1000 characters)\n"
        "2️⃣ Bot converts text to speech\n"
        "3️⃣ You receive an audio file (.mp3)\n\n"
        "*Tips:*\n"
        "• Keep messages under 500 characters for best results\n"
        "• The bot works with multiple languages\n"
        "• You can use emojis and punctuation\n\n"
        "*Commands:*\n"
        "/start - Restart the bot\n"
        "/info - Technical information"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info_text = (
        "ℹ️ *Bot Information*\n\n"
        f"🤖 *Bot Status:* Active\n"
        f"🔊 *TTS Engine:* pyttsx3 (offline)\n"
        f"🐍 *Python Version:* {sys.version.split()[0]}\n"
        f"📦 *Library:* python-telegram-bot v20.8\n\n"
        "*Note:* This bot runs entirely on Render using free open-source libraries. No external APIs required."
    )
    await update.message.reply_text(info_text, parse_mode="Markdown")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    text_length = len(text)
    
    logger.info(f"📨 Text from {user.id}: {text[:50]}... (length: {text_length})")
    
    # Limit text length to prevent abuse
    if text_length > 1000:
        await update.message.reply_text("⚠️ Text too long! Please keep under 1000 characters.")
        return
    
    # Send processing message
    processing_msg = await update.message.reply_text("🎵 Converting text to speech... Please wait.")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        audio_file = tmp_file.name
    
    try:
        # Convert text to speech
        success = text_to_speech(text, audio_file)
        
        if success and os.path.exists(audio_file) and os.path.getsize(audio_file) > 0:
            # Send audio file to user
            with open(audio_file, 'rb') as audio:
                await update.message.reply_audio(
                    audio=audio,
                    filename=f"speech_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
                    caption=f"🎤 Converted: \"{text[:100]}{'...' if text_length > 100 else ''}\"",
                    title="Text-to-Speech Audio",
                    performer="TTS Bot"
                )
            
            # Delete processing message
            await processing_msg.delete()
            logger.info(f"✅ Audio sent to user {user.id}")
        else:
            await processing_msg.edit_text("❌ Failed to convert text to speech. Please try again with shorter text.")
            logger.error(f"Audio generation failed for user {user.id}")
            
    except Exception as e:
        logger.error(f"Error in handle_text: {e}")
        await processing_msg.edit_text("❌ An error occurred. Please try again.")
    
    finally:
        # Clean up temporary file
        try:
            if os.path.exists(audio_file):
                os.unlink(audio_file)
        except:
            pass

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"❌ Error: {context.error}", exc_info=True)
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ Sorry, an error occurred. Please try again later."
        )

# Main function
async def main_async():
    print(f"[{datetime.now().isoformat()}] 🏗️ Building TTS bot application...")
    
    # Create application
    app = Application.builder().token(TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_error_handler(error_handler)
    
    print(f"[{datetime.now().isoformat()}] 🤖 Starting polling...")
    print(f"[{datetime.now().isoformat()}] ✅ TTS Bot is now listening for messages!")
    print(f"[{datetime.now().isoformat()}] 💡 Go to Telegram and send /start to your bot")
    print("=" * 60)
    
    # Start the bot
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    # Keep running
    print(f"[{datetime.now().isoformat()}] 🟢 Bot polling loop active")
    try:
        while True:
            await asyncio.sleep(3600)  # Keep alive
            print(f"[{datetime.now().isoformat()}] 💓 Heartbeat: TTS Bot still running")
    except KeyboardInterrupt:
        print(f"[{datetime.now().isoformat()}] 🛑 Shutting down...")
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print(f"[{datetime.now().isoformat()}] 👋 Bot stopped by user")
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] ❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    print(f"[{datetime.now().isoformat()}] 🎤 TEXT-TO-SPEECH BOT STARTING...")
    main()
