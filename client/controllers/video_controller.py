from services.video_service import get_free_videos, get_free_video_by_id
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

# Show free videos list
async def show_free_videos(update: Update, context: CallbackContext):
    videos = await get_free_videos()
    buttons = [
        [InlineKeyboardButton(video["title"], callback_data=f"free_video:{str(video['_id'])}")]
        for video in videos
    ]
    buttons.append([InlineKeyboardButton("🔙 Ortga", callback_data="go_back")])

    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "🎁 Free Videos:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Show detail for a selected free video
async def show_free_video_detail(update: Update, context: CallbackContext):
    video_id = update.callback_query.data.split(":")[1]
    video = await get_free_video_by_id(video_id)
    
    if video:
        await update.callback_query.edit_message_text(
            f"🎞 {video['title']}\n🔗 {video['youtube_link']}",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Ortga", callback_data="get_free_videos")]]
            )
        )
    else:
        await update.callback_query.edit_message_text("❌ Video not found.")
