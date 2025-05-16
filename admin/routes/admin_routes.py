from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
from admin.handlers.start import admin_start
from admin.handlers.actions import handle_admin_action
from admin.handlers.input_handler import handle_admin_input


admin_routes = [
    CallbackQueryHandler(handle_admin_action, pattern="^(send_notification|view_users|add_free_video|add_faq|manage_payments)$"),
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_input)
]

