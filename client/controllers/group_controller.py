from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import logging
from services.user_service import get_user_by_id
from services.invoice_service import create_click_invoice
from client.utils.click_utils import get_payment_status

logger = logging.getLogger("group_controller")

GROUP_CHAT_ID = -4685484218
GROUP_INVITE_LINK = "https://t.me/+uzz7lKNXKaIxODYy"

DURATION_MAP = {
    "subscribe_14": {"days": 14, "amount": 109000},
    "subscribe_30": {"days": 30, "amount": 249000},
    "subscribe_90": {"days": 90, "amount": 449000},
    "subscribe_180": {"days": 180, "amount": 799000}
}

async def handle_paid_group_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📅 2 Hafta – 109,000 so'm", callback_data="subscribe_14")],
        [InlineKeyboardButton("📅 1 Oy – 249,000 so'm", callback_data="subscribe_30")],
        [InlineKeyboardButton("📅 3 Oy – 449,000 so'm", callback_data="subscribe_90")],
        [InlineKeyboardButton("📅 6 Oy – 799,000 so'm", callback_data="subscribe_180")],
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

        keyboard = [
            [InlineKeyboardButton("💳 To'lov qilish!", url=payment_url)],
            [InlineKeyboardButton("✅ To'lovni tasdiqlash", callback_data="verify_payment")],
            [InlineKeyboardButton("🔙 Ortga", callback_data="go_back")]
        ]

        await query.edit_message_text(
            f"💰 You selected a {duration}-day subscription for {amount} so'm.\n\nClick below to pay:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        keyboard = [[InlineKeyboardButton("🔄 Try Again", callback_data="paid_group")]]
        await query.edit_message_text("❌ Failed to generate payment link.", reply_markup=InlineKeyboardMarkup(keyboard))

async def verify_paid_group_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer("Checking payment status...")

    merchant_trans_id = context.user_data.get("merchant_trans_id")

    if not merchant_trans_id:
        await query.edit_message_text(
            "❌ Payment information not found. Please try again.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Ortga", callback_data="go_back")]])
        )
        return

    payment_status = await get_payment_status(merchant_trans_id)

    if payment_status == "completed":
        if "merchant_trans_id" in context.user_data:
            del context.user_data["merchant_trans_id"]

        await query.edit_message_text(
            f"✅ To'lov tasdiqlandi, gruppa linki: \n\n👉 {GROUP_INVITE_LINK}",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await query.edit_message_text(
            "❌ Payment not found or still processing. Please complete payment or wait a moment and try again.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Qaytadan Tekshirish", callback_data="verify_payment")],
                [InlineKeyboardButton("🔙 Ortga", callback_data="go_back")]
            ])
        )
