from services.user_service import get_all_users

async def broadcast_message(update, context, message):
    users = await get_all_users()
    count = 0
    for user in users:
        try:
            await context.bot.send_message(chat_id=user["user_id"], text=message)
            count += 1
        except Exception:
            pass
    await update.message.reply_text(f"✅ Message sent to {count} users.")
