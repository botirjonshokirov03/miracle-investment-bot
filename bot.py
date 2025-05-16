# bot.py
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from telegram.ext import Application, ContextTypes, CommandHandler, ChatMemberHandler
from telegram import Update
from route import setup_routes
from client.controllers.group_controller import track_user_join, scheduler  # ✅ combined import

load_dotenv()

async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Chat ID: {chat_id}")

# ✅ Run scheduler AFTER event loop is active
async def on_startup(application: Application):
    scheduler.start()
    print("✅ APScheduler started")

def main():
    application = Application.builder()\
        .token(os.getenv("BOT_TOKEN"))\
        .post_init(on_startup)\
        .build()

    setup_routes(application)
    application.add_handler(CommandHandler("debug", debug))
    application.add_handler(ChatMemberHandler(track_user_join, chat_member_types=["member"]))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
