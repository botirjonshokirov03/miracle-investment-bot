from telegram import Update
from telegram.ext import ContextTypes
from client.keyboards.menu import get_user_keyboard
from admin.handlers.start import admin_start
from services.user_service import get_user_by_id, save_user, is_admin
from services.subscription_service import is_user_subscribed

REQUIRED_CHANNEL_ID = "@miracle_investment_fx"

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    user_id = contact.user_id or update.effective_user.id
    name = contact.first_name
    phone = contact.phone_number

    # 1. Save or update user info
    user = await get_user_by_id(user_id)
    if not user:
        await save_user({"user_id": user_id, "name": name, "phone": phone})

    # 2. Check if user is subscribed to the required channel
    subscribed = await is_user_subscribed(context.bot, user_id, REQUIRED_CHANNEL_ID)
    if not subscribed:
        await update.message.reply_text(
            f"❗ Please subscribe to {REQUIRED_CHANNEL_ID} and press /start again to continue."
        )
        return

    # 3. Show admin or user menu
    if await is_admin(user_id):
        await admin_start(update, context)
    else:
        await update.message.reply_text(
            "✅ You're subscribed! Please choose an option:",
            reply_markup=get_user_keyboard()
        )
