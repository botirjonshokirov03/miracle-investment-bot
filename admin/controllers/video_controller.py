from services.video_service import add_free_video

async def add_video_by_text(update, context, text):
    if "|" not in text:
        await update.message.reply_text("❌ Format: `Title | Link`", parse_mode="Markdown")
        return
    title, link = map(str.strip, text.split("|", 1))
    await add_free_video(title, link)
    await update.message.reply_text("✅ Video added.")