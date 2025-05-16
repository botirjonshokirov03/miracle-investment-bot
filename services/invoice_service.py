import asyncio
import os
import time
import logging
from urllib.parse import urlencode
from database import get_collection
from typing import Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("invoice_service")

SERVICE_ID = os.getenv("CLICK_SERVICE_ID")
MERCHANT_ID = os.getenv("CLICK_MERCHANT_ID")
MERCHANT_USER_ID = os.getenv("CLICK_MERCHANT_USER_ID")
SECRET_KEY = os.getenv("CLICK_SECRET_KEY")
CLICK_API_URL = os.getenv("CLICK_API_URL", "https://my.click.uz/services/pay")

async def create_click_invoice(phone: str, user_id: int, amount: float, duration_days: int) -> Dict[str, Any]:
    timestamp = int(time.time())
    merchant_trans_id = f"TG_{user_id}_{timestamp}"

    query_params = {
        "service_id": SERVICE_ID,
        "merchant_id": MERCHANT_ID,
        "amount": amount,
        "transaction_param": merchant_trans_id,
        "return_url": f"https://t.me/{os.getenv('BOT_USERNAME', 'your_bot_username')}"
    }

    payment_url = f"{CLICK_API_URL}?{urlencode(query_params)}"

    logger.info(f"Generated Click Shop API link: {payment_url}")

    payments = get_collection("payments")
    await payments.insert_one({
        "merchant_trans_id": merchant_trans_id,
        "user_id": user_id,
        "amount": amount,
        "duration_days": duration_days,
        "status": "created",
        "created_at": {"$date": {"$numberLong": str(int(time.time() * 1000))}}
    })

    return {
        "invoice_id": None,
        "merchant_trans_id": merchant_trans_id,
        "payment_link": payment_url
    }
