from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from client.keyboards.menu import get_user_keyboard

async def user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        # /start case
        contact_button = KeyboardButton("📱 Share Phone Number", request_contact=True)
        markup = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_text(
            "Welcome! Please share your phone number to continue:",
            reply_markup=markup
        )

    elif update.callback_query:
        # Button press, like "Go Back"
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "Please choose an option:",
            reply_markup=get_user_keyboard()
        )
