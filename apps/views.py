import hashlib
from decimal import Decimal, InvalidOperation

from click_up import ClickUp
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import views, response
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.models import Order
from apps.serializers import OrderSerializer

click_up = ClickUp(
    service_id=settings.CLICK_SERVICE_ID,
    merchant_id=settings.CLICK_MERCHANT_ID,
)


class OrderCreate(views.APIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        result = {
            "order": serializer.data
        }

        if serializer.data.get("payment_method") == "click":
            payment_link = click_up.initializer.generate_pay_link(
                id=order.id,  # merchant_trans_id
                amount=order.total_cost,  # amount
                return_url="https://xpresstransportation.org/",
            )
            result["payment_link"] = payment_link

        return response.Response(result)

def build_click_sign(data: dict) -> str:
    click_trans_id = str(data.get("click_trans_id", "")).strip()
    service_id = str(data.get("service_id", "")).strip()
    merchant_trans_id = str(data.get("merchant_trans_id", "")).strip()
    amount = str(data.get("amount", "0")).strip()
    action = str(data.get("action", "0")).strip()
    sign_time = str(data.get("sign_time", "")).strip()
    secret_key = str(settings.CLICK_SECRET_KEY).strip()

    sign_source = click_trans_id + service_id + merchant_trans_id + amount + action + sign_time + secret_key
    return hashlib.md5(sign_source.encode()).hexdigest().lower()



def validate_click_request(data):
    service_id = str(data.get("service_id", "")).strip()
    if service_id != str(settings.CLICK_SERVICE_ID):
        return None, Response({"error": -3, "error_note": "SERVICE_ID_NOT_MATCH"})

    received_sign = str(data.get("sign_string", "")).lower().strip()
    if not received_sign:
        return None, Response({"error": -1, "error_note": "SIGN_REQUIRED"})

    expected_sign = build_click_sign(data).lower()
    if expected_sign != received_sign:
        return None, Response({"error": -1, "error_note": "SIGN_CHECK_FAILED"})

    order_id = data.get("merchant_trans_id")
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return None, Response({"error": -5, "error_note": "ORDER_NOT_FOUND"})

    raw_amount = data.get("amount")
    if raw_amount is None:
        return None, Response({"error": -2, "error_note": "AMOUNT_MISMATCH"})

    try:
        amount_dec = Decimal(str(raw_amount))
        order_dec = Decimal(str(order.total_cost))
    except InvalidOperation:
        return None, Response({"error": -2, "error_note": "AMOUNT_MISMATCH"})

    if amount_dec != order_dec:
        return None, Response({"error": -2, "error_note": "AMOUNT_MISMATCH"})

    return order, None


@method_decorator(csrf_exempt, name="dispatch")
class ClickPrepareView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        print("Request: ", data)
        # validate_click_request -> service_id, sign, order, amount tekshiradi
        order, error_response = validate_click_request(data)

        if error_response:
            print(error_response.data)
            return error_response

        merchant_trans_id = str(order.id)

        res = {
            "click_trans_id": data.get("click_trans_id"),
            "merchant_trans_id": merchant_trans_id,
            "merchant_prepare_id": merchant_trans_id,
            "error": 0,
            "error_note": "PREPARE_OK",
        }

        print("Response: ",res)

        return Response(res)


@method_decorator(csrf_exempt, name="dispatch")
class ClickCompleteView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        order, error_response = validate_click_request(data)
        if error_response:
            return error_response

        action = int(data.get("action", 0))
        if action != 1:
            return Response({"error": -6, "error_note": "UNKNOWN_ACTION"})

        if not getattr(order, "is_paid", False):
            order.is_paid = True
            order.save(update_fields=["is_paid"])

        merchant_trans_id = str(order.id)

        return Response({
            "click_trans_id": data.get("click_trans_id"),
            "merchant_trans_id": merchant_trans_id,
            "merchant_confirm_id": merchant_trans_id,
            "error": 0,
            "error_note": "SUCCESS",
        })


@method_decorator(csrf_exempt, name="dispatch")
class ClickWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        service_id = str(data.get("service_id", "")).strip()
        if service_id != str(settings.CLICK_SERVICE_ID):
            return Response({"error": -3, "error_note": "SERVICE_ID_NOT_MATCH"})

        received_sign = str(data.get("sign_string", "")).strip().lower()
        if not received_sign:
            return Response({"error": -1, "error_note": "SIGN_REQUIRED"})

        expected_sign = build_click_sign(data)
        if expected_sign != received_sign:
            return Response({"error": -1, "error_note": "SIGN_CHECK_FAILED"})

        order_id = data.get("merchant_trans_id")
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": -5, "error_note": "ORDER_NOT_FOUND"})

        raw_amount = data.get("merchant_trans_amount") or data.get("amount") or "0"
        try:
            amount_dec = Decimal(str(raw_amount))
            order_dec = Decimal(str(order.total_cost))
        except InvalidOperation:
            return Response({"error": -2, "error_note": "AMOUNT_MISMATCH"})

        if amount_dec != order_dec:
            return Response({"error": -2, "error_note": "AMOUNT_MISMATCH"})

        action = int(data.get("action", 0))

        if action == 0:
            return Response({
                "error": 0,
                "error_note": "PREPARE_OK",
            })

        if action == 1:
            if not getattr(order, "is_paid", False):
                order.is_paid = True
                order.save(update_fields=["is_paid"])

            return Response({
                "error": 0,
                "error_note": "SUCCESS",
            })

        return Response({"error": -6, "error_note": "UNKNOWN_ACTION"})
