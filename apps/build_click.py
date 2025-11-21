import hashlib
from django.conf import settings


def build_click_sign(data: dict) -> str:
    amount = data.get("merchant_trans_amount") or data.get("amount") or ""

    sign_source = (
        str(data.get("click_trans_id", "")) +
        str(data.get("service_id", "")) +
        str(settings.CLICK_SECRET_KEY) +
        str(data.get("merchant_trans_id", "")) +
        str(amount) +
        str(data.get("action", "")) +
        str(data.get("sign_time", ""))
    )

    return hashlib.md5(sign_source.encode()).hexdigest()
