from database import db

# Check if the user is an admin
async def is_admin(user_id):
    user = await db.users.find_one({"user_id": user_id})
    return user and user.get("is_admin", False)

# Get user by ID
async def get_user_by_id(user_id):
    return await db.users.find_one({"user_id": user_id})

# Save or update user
async def save_user(data):
    await db.users.update_one(
        {"user_id": data["user_id"]},
        {"$set": data},
        upsert=True
    )

async def get_all_users():
    cursor = db.users.find()
    return await cursor.to_list(length=None)