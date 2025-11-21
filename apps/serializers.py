from rest_framework.serializers import ModelSerializer

from apps.models import Order


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'costumer_name', 'address', 'total_cost', 'payment_method')
