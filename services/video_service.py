from database import db
from bson import ObjectId

# Get all free videos
async def get_free_videos():
    cursor = db.free_videos.find()
    return await cursor.to_list(length=None)

# Add a new free video
async def add_free_video(title, youtube_link):
    await db.free_videos.insert_one({
        "title": title,
        "youtube_link": youtube_link
    })

# Get a specific video
async def get_free_video_by_id(video_id):
    try:
        _id = ObjectId(video_id)
        return await db.free_videos.find_one({"_id": _id})
    except Exception as e:
        print(f"Invalid video ID: {video_id} - {e}")
        return None
