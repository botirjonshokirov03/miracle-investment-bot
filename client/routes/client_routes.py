from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
from client.handlers.start import user_start
from client.handlers.contact import handle_contact
from client.handlers.callback_handler import handle_client_buttons
from client.controllers.group_controller import handle_subscription_selection

client_routes = [
    CommandHandler("start", user_start),
    MessageHandler(filters.CONTACT, handle_contact),
    CallbackQueryHandler(handle_subscription_selection, pattern="^subscribe_"),
    CallbackQueryHandler(handle_client_buttons)
]