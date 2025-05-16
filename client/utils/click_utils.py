import hashlib
import logging
import os
from typing import Optional
from datetime import datetime, timedelta
from database import get_collection

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("click_utils")

SECRET_KEY = os.getenv("CLICK_SECRET_KEY")
SERVICE_ID = os.getenv("CLICK_SERVICE_ID")
MERCHANT_ID = os.getenv("CLICK_MERCHANT_ID")

def verify_sign_string(data: dict, is_complete: bool = False) -> bool:
    try:
        if is_complete:
            raw = (
                str(data["click_trans_id"]) +
                str(data["service_id"]) +
                SECRET_KEY +
                str(data["merchant_trans_id"]) +
                str(data["merchant_prepare_id"]) +
                str(data["amount"]) +
                str(data["action"]) +
                data["sign_time"]
            )
        else:
            raw = (
                str(data["click_trans_id"]) +
                str(data["service_id"]) +
                SECRET_KEY +
                str(data["merchant_trans_id"]) +
                str(data["amount"]) +
                str(data["action"]) +
                data["sign_time"]
            )
        calc_sign = hashlib.md5(raw.encode()).hexdigest()
        is_valid = calc_sign == data.get("sign_string")
        if not is_valid:
            logger.warning(f"Invalid signature: expected {calc_sign}, got {data.get('sign_string')}")
        return is_valid
    except Exception as e:
        logger.error(f"Error verifying signature: {str(e)}")
        return False

async def get_payment_status(merchant_trans_id: str) -> Optional[str]:
    try:
        payments = get_collection("payments")
        payment = await payments.find_one({"merchant_trans_id": merchant_trans_id})
        if payment:
            return payment.get("status")
        return None
    except Exception as e:
        logger.error(f"Error getting payment status: {str(e)}")
        return None

async def update_user_subscription(user_id: int, merchant_trans_id: str) -> bool:
    try:
        payments = get_collection("payments")
        payment = await payments.find_one({"merchant_trans_id": merchant_trans_id})
        duration_days = payment.get("duration_days", 30)

        users = get_collection("users")
        user = await users.find_one({"user_id": user_id})
        if not user:
            logger.error(f"User {user_id} not found when updating subscription")
            return False

        current_date = datetime.now()
        current_end_date = user.get("subscription_end")
        if current_end_date and current_end_date > current_date:
            new_end_date = current_end_date + timedelta(days=duration_days)
        else:
            new_end_date = current_date + timedelta(days=duration_days)

        await users.update_one(
            {"user_id": user_id},
            {"$set": {
                "has_paid_access": True,
                "subscription_end": new_end_date,
                "last_payment_date": current_date
            }}
        )

        logger.info(f"Updated subscription for user {user_id} until {new_end_date}")
        return True
    except Exception as e:
        logger.error(f"Error updating user subscription: {str(e)}")
        return False

async def extract_user_id_from_merchant_trans_id(merchant_trans_id: str) -> Optional[int]:
    try:
        parts = merchant_trans_id.split('_')
        if len(parts) >= 2 and parts[0] == "TG":
            return int(parts[1])
        return None
    except Exception as e:
        logger.error(f"Error extracting user ID from {merchant_trans_id}: {str(e)}")
        return None