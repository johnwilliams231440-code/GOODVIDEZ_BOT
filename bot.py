#!/usr/bin/env python3
import os
import sys
import logging
import asyncio
from datetime import datetime

# Force immediate log output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

print(f"[{datetime.now().isoformat()}] 🚀 BOT INITIALIZING...")
print(f"[{datetime.now().isoformat()}] 📍 Working directory: {os.getcwd()}")
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

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    print(f"[{datetime.now().isoformat()}] ✅ Telegram imports successful")
except Exception as e:
    print(f"[{datetime.now().isoformat()}] ❌ Import error: {e}")
    sys.exit(1)

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"📨 /start from {user.id} (@{user.username})")
    await update.message.reply_text(
        "✅ **Bot is Alive!**\n\n"
        "Send me any message and I'll echo it back.\n"
        "Send /help for commands.",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 **Available Commands:**\n"
        "/start - Start the bot\n"
        "/help - Show this help\n"
        "/ping - Check if bot is responsive\n\n"
        "Or just send any text message!",
        parse_mode="Markdown"
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong! Bot is responsive.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    logger.info(f"📨 Echo from {user.id}: {text[:50]}")
    await update.message.reply_text(f"📢 **You said:** {text}", parse_mode="Markdown")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"❌ Error: {context.error}", exc_info=True)
    if update and update.effective_message:
        await update.effective_message.reply_text("⚠️ Sorry, an error occurred.")

# Main function
async def main_async():
    print(f"[{datetime.now().isoformat()}] 🏗️ Building application...")
    app = Application.builder().token(TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_error_handler(error_handler)
    
    print(f"[{datetime.now().isoformat()}] 🤖 Starting polling...")
    print(f"[{datetime.now().isoformat()}] ✅ Bot is now listening for messages!")
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
            await asyncio.sleep(3600)  # Sleep for 1 hour, keep alive
            print(f"[{datetime.now().isoformat()}] 💓 Heartbeat: Bot still running")
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
    print(f"[{datetime.now().isoformat()}] 🎯 Bot starting in BACKGROUND WORKER mode")
    main()
