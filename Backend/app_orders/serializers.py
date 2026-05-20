
from rest_framework import serializers

from app_orders.models import Orders
from app_products.serializers import ProductSerializer

class OrdersSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = Orders
        fields = ["consumer","product","location","quantity","price", "payment_method"]