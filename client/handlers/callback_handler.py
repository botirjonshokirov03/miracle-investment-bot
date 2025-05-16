from telegram import Update
from telegram.ext import ContextTypes
from client.controllers.faq_controller import show_faq
from client.controllers.video_controller import show_free_videos, show_free_video_detail

from client.controllers.group_controller import handle_paid_group_join, verify_paid_group_payment

from client.handlers.start import user_start


async def handle_client_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data == "faq":
        await show_faq(update, context)
    elif data == "get_free_videos":
        await show_free_videos(update, context)
    elif data.startswith("free_video:"):
        await show_free_video_detail(update, context)
    elif data == "join_paid_group":
        await handle_paid_group_join(update, context)
    elif data == "verify_payment":
        await verify_paid_group_payment(update, context)
    elif data == "go_back":
        await user_start(update, context)