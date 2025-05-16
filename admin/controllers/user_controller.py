from services.user_service import get_all_users

async def show_all_users(query):
    users = await get_all_users()
    if users:
        text = "\n".join([f"{u.get('name')} ({u.get('phone')})" for u in users])
        await query.edit_message_text(f"\U0001F465 Users:\n{text[:4000]}")
    else:
        await query.edit_message_text("No users found.")