from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Send Notification", callback_data="send_notification")],
        [InlineKeyboardButton("👥 View Users", callback_data="view_users")],
        [InlineKeyboardButton("➕ Add Free Video", callback_data="add_free_video")],
        [InlineKeyboardButton("❓ Add FAQ", callback_data="add_faq")],
        [InlineKeyboardButton("💳 Manage Payments", callback_data="manage_payments")]
    ])

async def admin_start(update, context):
    await update.message.reply_text(
        "\U0001F451 Welcome, Admin! Please choose an option:",
        reply_markup=get_admin_keyboard()
    )
