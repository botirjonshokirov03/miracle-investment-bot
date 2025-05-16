from telegram import Update
from telegram.ext import ContextTypes
from admin.controllers.faq_controller import add_faq_by_text
from admin.controllers.video_controller import add_video_by_text
from admin.controllers.broadcast_controller import broadcast_message

import asyncio
from admin.handlers.start import get_admin_keyboard
from services.faq_service import add_faq
from services.video_service import add_free_video

async def handle_admin_input(update, context):
    if not update.message:
        return

    text = update.message.text
    user_data = context.user_data

    if user_data.get("awaiting_faq"):
        if "|" not in text:
            await update.message.reply_text("❌ Format: `Question | Answer`", parse_mode="Markdown")
            return

        question, answer = map(str.strip, text.split("|", 1))
        await add_faq(question, answer)
        user_data["awaiting_faq"] = False

        await update.message.reply_text("✅ FAQ saved.", reply_markup=get_admin_keyboard())


    elif user_data.get("awaiting_video"):
        if "|" not in text:
            await update.message.reply_text("❌ Format: `Title | Link`", parse_mode="Markdown")
            return

        title, link = map(str.strip, text.split("|", 1))
        await add_free_video(title, link)
        user_data["awaiting_video"] = False

        await update.message.reply_text("✅ Video saved.", reply_markup=get_admin_keyboard())


    elif user_data.get("awaiting_broadcast"):
            await broadcast_message(update, context, text)
            user_data["awaiting_broadcast"] = False

    # ✅ After any action, show admin panel again
    await update.message.reply_text(
        "\U0001F451 Admin Menu:",
        reply_markup=get_admin_keyboard()
    )

