from django.contrib import admin
from django.urls import path, include

from payment.views import ClickWebhookAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.urls')),
    path("payment/click/update/", ClickWebhookAPIView.as_view()),

]
