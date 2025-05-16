from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_user_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📺 Get Paid Videos", callback_data="get_paid_videos")],
        [InlineKeyboardButton("🎁 Get Free Videos", callback_data="get_free_videos")],
        [InlineKeyboardButton("💬 Join Paid Group", callback_data="join_paid_group")],
        [InlineKeyboardButton("❓ FAQ", callback_data="faq")]
    ])
