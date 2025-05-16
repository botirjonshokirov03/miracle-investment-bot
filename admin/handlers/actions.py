from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from admin.controllers.user_controller import show_all_users
from admin.handlers.start import get_admin_keyboard
import asyncio

async def handle_admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    user_data = context.user_data

    if data == "view_users":
        await show_all_users(query)

    elif data == "send_notification":
        await query.edit_message_text("📝 Please send the message to broadcast (expires in 60s).")
        user_data["awaiting_broadcast"] = True
        asyncio.create_task(admin_timeout(query, user_data, "awaiting_broadcast"))

    elif data == "add_free_video":
        await query.edit_message_text("📹 Send: `Title | Link`\n(You have 60 seconds)", parse_mode="Markdown")
        user_data["awaiting_video"] = True
        asyncio.create_task(admin_timeout(query, user_data, "awaiting_video", action="video"))

    elif data == "add_faq":
        await query.edit_message_text("❓ Send: `Question | Answer`\n(You have 60 seconds)", parse_mode="Markdown")
        user_data["awaiting_faq"] = True
        asyncio.create_task(admin_timeout(query, user_data, "awaiting_faq", action="faq"))

    # Video/FAQ continue/cancel
    elif data == "continue_video":
        await query.edit_message_text("📹 OK, send Title | Link now. You have 60 seconds.")

    elif data == "cancel_video":
        user_data["awaiting_video"] = False
        await query.edit_message_text("❌ Video add cancelled. Returning to admin menu.", reply_markup=get_admin_keyboard())

    elif data == "continue_faq":
        await query.edit_message_text("❓ OK, send `Question | Answer` now. You have 60 seconds.", parse_mode="Markdown")

    elif data == "cancel_faq":
        user_data["awaiting_faq"] = False
        await query.edit_message_text("❌ FAQ add cancelled. Returning to admin menu.", reply_markup=get_admin_keyboard())

    print("✅ Button clicked:", data)


# 🔧 Shared timeout logic for FAQ, Video, Broadcast
async def admin_timeout(query, user_data, flag_key, action=None):
    await asyncio.sleep(60)
    if user_data.get(flag_key):
        # First timeout hit
        if action in ["video", "faq"]:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Yes", callback_data=f"continue_{action}")],
                [InlineKeyboardButton("❌ No", callback_data=f"cancel_{action}")]
            ])
            await query.message.reply_text(f"⏳ Time’s up! Do you still want to add a {action.upper()}?", reply_markup=keyboard)

            # Second timeout
            async def second_timeout():
                await asyncio.sleep(60)
                if user_data.get(flag_key):
                    user_data[flag_key] = False
                    await query.message.reply_text(f"❌ {action.capitalize()} add cancelled. Returning to admin menu.", reply_markup=get_admin_keyboard())

            asyncio.create_task(second_timeout())

        else:
            # For general broadcast or other timeout
            user_data[flag_key] = False
            await query.message.reply_text("⏰ Timeout reached. Returning to admin menu.", reply_markup=get_admin_keyboard())
