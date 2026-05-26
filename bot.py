#!/usr/bin/env python3
import os
import sys
import logging
import time

# Force stdout to flush immediately
sys.stdout.reconfigure(line_buffering=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("=" * 50)
print("🚀 BOT STARTING...")
print("=" * 50)

# Check for token
TOKEN = os.environ.get("TELEGRAM_TOKEN")
print(f"🔑 Token check: {'✅ FOUND' if TOKEN else '❌ MISSING'}")

if not TOKEN:
    print("❌ CRITICAL: TELEGRAM_TOKEN environment variable not set!")
    print("💡 Please add it in Render Dashboard → Environment Variables")
    sys.exit(1)

print(f"📝 Token starts with: {TOKEN[:5]}...")

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

print("✅ Imports successful")

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"User {user.id} (@{user.username}) started the bot")
    await update.message.reply_text(
        "✅ Bot is alive and working!\n\n"
        "Send me any message and I'll echo it back."
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    logger.info(f"User {user.id} sent: {text[:50]}")
    await update.message.reply_text(f"📢 Echo: {text}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")

# Main function
def main():
    print("🏗️ Building application...")
    app = Application.builder().token(TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_error_handler(error_handler)
    
    print("🤖 Starting polling...")
    print("✅ Bot is now listening for messages!")
    print("💡 Go to Telegram and send /start to your bot")
    print("=" * 50)
    
    # Start the bot
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
