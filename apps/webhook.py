from django.conf import settings
from paytechuz.gateways.click.webhook import ClickWebhookHandler

webhook_handler = ClickWebhookHandler(
    service_id=settings.CLICK_SERVICE_ID,
    secret_key=settings.CLICK_SECRET_KEY,
)


def process_webhook(request_data):
    response = webhook_handler.handle_webhook(request_data)

    if response['error'] == 0:
        # Payment successful
        print("Payment successful!")

    return response


def build_click_sign_complete(data):
    click_trans_id = str(data.get("click_trans_id"))
    service_id = str(data.get("service_id"))
    secret_key = settings.CLICK_SECRET_KEY
    merchant_trans_id = str(data.get("merchant_trans_id"))
    merchant_prepare_id = str(data.get("merchant_prepare_id"))
    amount = str(data.get("amount"))
    action = str(data.get("action"))
    sign_time = str(data.get("sign_time"))

    source = (
        click_trans_id +
        service_id +
        secret_key +
        merchant_trans_id +
        merchant_prepare_id +
        amount +
        action +
        sign_time
    )

    return hashlib.md5(source.encode()).hexdigest()
