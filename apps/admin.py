from django.contrib import admin
from django.contrib.admin import ModelAdmin

from apps.models import Order


@admin.register(Order)
class OrderModelAdmin(ModelAdmin):
    list_display = ('id', 'costumer_name', 'address', 'is_paid', 'payment_method')
    list_filter = ('is_paid', 'payment_method',)
