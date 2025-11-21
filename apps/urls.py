from django.urls import path

from .views import OrderCreate, ClickPrepareView, ClickCompleteView, ClickWebhookView

urlpatterns = [
    path("order/create/", OrderCreate.as_view(), name="order-create"),
    path("click/webhook/", ClickWebhookView.as_view(), name="click-webhook"),

    # CLICK webhooks:
    path("api/v1/webhook/click/prepare", ClickPrepareView.as_view(), name="click-prepare"),
    path("api/v1/webhook/click/complete", ClickCompleteView.as_view(), name="click-complete"),

]
