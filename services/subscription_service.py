async def is_user_subscribed(bot, user_id, channel_id):
    try:
        chat_member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return chat_member.status in ["member", "creator", "administrator"]
    except Exception as e:
        print(f"Subscription check failed for user {user_id}: {e}")
        return False