from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ChatMemberHandler
from telegram.constants import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import logging

from services.user_service import get_user_by_id
from services.invoice_service import create_click_invoice
from client.utils.click_utils import get_payment_status

logger = logging.getLogger("group_controller")

# Group IDs per duration
GROUP_CHAT_IDS = {
    14: -1002455748953,
    30: -1002650518167,
    90: -1002679985012,
    180: -1002364265871
}

DURATION_MAP = {
    "subscribe_14": {"days": 14, "amount": 109000},
    "subscribe_30": {"days": 30, "amount": 249000},
    "subscribe_90": {"days": 90, "amount": 449000},
    "subscribe_180": {"days": 180, "amount": 799000}
}

# Start the scheduler globally
scheduler = AsyncIOScheduler()

async def handle_paid_group_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🗕 2 Hafta – 109,000 so'm", callback_data="subscribe_14")],
        [InlineKeyboardButton("🔙 Ortga", callback_data="go_back")]
    ]
    await query.edit_message_text("To'lov muddatimiz quyidagilardan iborat:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_subscription_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    key = query.data

    if key not in DURATION_MAP:
        await query.edit_message_text("❌ Invalid selection.")
        return

    duration = DURATION_MAP[key]["days"]
    amount = DURATION_MAP[key]["amount"]
    user = await get_user_by_id(user_id)

    if not user:
        await query.edit_message_text("❌ User not found. Please share your contact first.")
        return

    phone = user.get("phone")
    if not phone:
        await query.edit_message_text("❌ Phone number is missing in your profile.")
        return

    try:
        result = await create_click_invoice(phone, user_id, amount, duration_days=duration)
        merchant_trans_id = result["merchant_trans_id"]
        payment_url = result["payment_link"]

        context.user_data["merchant_trans_id"] = merchant_trans_id
        context.user_data["duration_days"] = duration

        keyboard = [
            [InlineKeyboardButton("💳 To'lov qilish!", url=payment_url)],
            [InlineKeyboardButton("✅ To'lovni tasdiqlash", callback_data="verify_payment")],
            [InlineKeyboardButton("🔙 Ortga", callback_data="go_back")]
        ]

        await query.edit_message_text(
            f"💰 Siz {duration} kunlik obunani tanladingiz.\nNarx: {amount} so'm.\n\nTo'lov uchun quyidagi tugmani bosing:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logger.error(f"Payment link generation failed: {e}")
        keyboard = [[InlineKeyboardButton("🔄 Try Again", callback_data="paid_group")]]
        await query.edit_message_text("❌ Failed to generate payment link.", reply_markup=InlineKeyboardMarkup(keyboard))

async def verify_paid_group_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer("To'lov holati tekshirilmoqda...")

    merchant_trans_id = context.user_data.get("merchant_trans_id")
    duration = context.user_data.get("duration_days")

    if not merchant_trans_id or not duration:
        await query.edit_message_text("❌ Payment or subscription data not found. Please try again.")
        return

    payment_status = await get_payment_status(merchant_trans_id)

    if payment_status == "completed":
        context.user_data.pop("merchant_trans_id", None)
        context.user_data.pop("duration_days", None)

        group_id = GROUP_CHAT_IDS.get(duration)

        try:
            # ✅ Create one-time link (expires in 5 mins)
            invite = await context.bot.create_chat_invite_link(
                chat_id=group_id,
                member_limit=1,
                expire_date=datetime.utcnow() + timedelta(minutes=5),
                creates_join_request=False
            )

            # ✅ FOR TESTING 2-DAY access only for 2-week group
            if duration == 14:
                test_expire_time = datetime.utcnow() + timedelta(days=2)

                scheduler.add_job(
                    kick_user_after,
                    trigger='date',
                    run_date=test_expire_time,
                    args=[context, group_id, user_id],
                    id=f"kick_{user_id}_{group_id}"
                )

            await query.edit_message_text(
                f"✅ To'lov tasdiqlandi!\n\n👉 Guruhga kirish havolasi (5 daqiqa amal qiladi):\n{invite.invite_link}",
                parse_mode=ParseMode.MARKDOWN
            )

        except Exception as e:
            logger.error(f"Invite link error: {e}")
            await query.edit_message_text("❌ Guruhga havola yaratib bo‘lmadi.")
    else:
        await query.edit_message_text("❌ To'lov topilmadi yoki hali yakunlanmagan. Qayta urinib ko‘ring.")

# Kick user after duration expires
async def kick_user_after(context, chat_id: int, user_id: int):
    try:
        await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
        await context.bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
        logger.info(f"Kicked user {user_id} from group {chat_id}")
    except Exception as e:
        logger.error(f"Kick failed: {e}")

# Track when user joins
async def track_user_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.chat_member.new_chat_member.status == "member":
        user = update.chat_member.from_user
        chat_id = update.chat_member.chat.id
        logger.info(f"User {user.id} joined group {chat_id}")
        # Optionally save join info to DB
