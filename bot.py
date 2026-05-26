#!/usr/bin/env python3
"""
TEXT-TO-SPEECH TELEGRAM BOT
Converts any text to speech audio
No API keys needed - uses gTTS
"""

import os
import sys
import logging
import tempfile
import asyncio
from datetime import datetime
from gtts import gTTS
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Force log output
sys.stdout.reconfigure(line_buffering=True)

print(f"[{datetime.now().isoformat()}] 🎤 TTS BOT STARTING...")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get bot token
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    print("❌ TELEGRAM_TOKEN not set!")
    sys.exit(1)

print(f"✅ Token found: {TOKEN[:5]}...")

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎤 *Text-to-Speech Bot*\n\n"
        "Send me any text and I'll convert it to speech!\n\n"
        "Commands:\n"
        "/start - Start bot\n"
        "/help - Show help\n\n"
        "Just type any message and get audio!",
        parse_mode="Markdown"
    )

# Command: /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *How to use:*\n\n"
        "1. Send any text message\n"
        "2. Bot converts to speech\n"
        "3. Receive audio file\n\n"
        "Works with any language!",
        parse_mode="Markdown"
    )

# Handle text messages
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    
    logger.info(f"User {user.id}: {text[:50]}")
    
    # Limit text length
    if len(text) > 500:
        await update.message.reply_text("⚠️ Text too long! Max 500 characters.")
        return
    
    # Send processing message
    msg = await update.message.reply_text("🎵 Converting to speech...")
    
    try:
        # Create temporary audio file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            audio_file = tmp.name
        
        # Convert text to speech
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(audio_file)
        
        # Send audio
        with open(audio_file, 'rb') as f:
            await update.message.reply_audio(
                audio=f,
                filename=f"speech_{user.id}.mp3",
                caption=f"🎤 {text[:100]}"
            )
        
        # Cleanup
        os.unlink(audio_file)
        await msg.delete()
        
        logger.info(f"✅ Audio sent to user {user.id}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await msg.edit_text("❌ Failed to convert. Please try again.")

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update error: {context.error}")

# Main function
async def main():
    app = Application.builder().token(TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_error_handler(error_handler)
    
    print("🤖 Bot is running!")
    print("💡 Send /start on Telegram")
    
    # Start polling
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    # Keep alive
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
