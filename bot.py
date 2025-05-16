# bot.py
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from telegram.ext import Application, ContextTypes, CommandHandler
from telegram import Update
from route import setup_routes

load_dotenv()

async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Chat ID: {chat_id}")

def main():
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    setup_routes(application)
    application.add_handler(CommandHandler("debug", debug))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
