from services.faq_service import get_faqs
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackContext

async def show_faq(update: Update, context: CallbackContext):
    faqs = await get_faqs()
    
    if not faqs:
        text = "❌ No FAQs available."
    else:
        text = "\n\n".join([
            f"❓ {faq['question']}\n💬 {faq['answer']}" for faq in faqs
        ])

    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        text + "\n\n🔙 Ortga",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Ortga", callback_data="go_back")]]
        )
    )
