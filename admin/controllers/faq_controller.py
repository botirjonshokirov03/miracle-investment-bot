from services.faq_service import add_faq

async def add_faq_by_text(update, context, text):
    if "|" not in text:
        await update.message.reply_text("❌ Format: `Question | Answer`", parse_mode="Markdown")
        return
    question, answer = map(str.strip, text.split("|", 1))
    await add_faq(question, answer)
    await update.message.reply_text("✅ FAQ added.")