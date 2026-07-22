import logging
from rest_framework import serializers
from django.core.validators import RegexValidator

from app_orders.models import Orders, OrderedItem, Product, Payment, Refund
from app_products.serializers import ProductNestedSerializer

logger = logging.getLogger('app_orders')

# ==========================================
# CUSTOM VALIDATORS
# ==========================================

razorpay_orderid_validator = RegexValidator( 
    regex=r'^order_[A-Za-z0-9_]+$',
    message="Invalid Razorpay Order ID format. Must start with 'order_' followed by alphanumeric characters."
)

# ==========================================
# SERIALIZERS
# ==========================================

class OrderedItemSerializer(serializers.ModelSerializer):
    """
    Serializer to map individual items saved inside a completed order.
    """
    ordered_item_id = serializers.UUIDField(source="uid", read_only=True)
    ordered_item = ProductNestedSerializer(read_only=True)
    
    # Accept the raw database product ID from incoming cart dictionaries
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='ordered_item'
    )

    class Meta:
        model = OrderedItem
        fields = ["ordered_item_id", "order", "product_id", "ordered_item", "quantity", "total_price", "item_status"]
        extra_kwargs = {
            'product_id': {'write_only': True, 'many': True},
        }


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer to handle the core high-level Checkout Order record creation.
    """
    order_id = serializers.UUIDField(source="uid", read_only=True)

    class Meta:
        model = Orders
        fields = ["order_id", "consumer", "amount", "razorpay_order_id", "order_status", "payment_mode"]
        extra_kwargs = {
            "consumer": {"read_only": True},
            "razorpay_order_id": {"required": False},  
            "payment_mode": {"required": True},
        }


class RazorOrderIdSerializer(serializers.Serializer):
    """
    Standalone serializer used to parse and validate incoming Razorpay ID tokens 
    during webhook actions or signature checking loops.
    """
    razorpay_order_id = serializers.CharField(validators=[razorpay_orderid_validator])

    class Meta:
        model = Orders
        fields = ["razorpay_order_id"]
        extra_kwargs = {
            "razorpay_order_id": {"required": True}
        }


class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer to log and maintain transaction history details linked to checkout orders.
    """
    payment_id = serializers.UUIDField(source="uid", read_only=True)

    class Meta:
        model = Payment
        fields = ["payment_id", "order", "razorpay_payment_id", "razorpay_signature", "payment_status"]
        extra_kwargs = {
            "razorpay_signature": {"required": False},  
            "order": {"read_only": True}
        }

class RefundSerializer(serializers.ModelSerializer):
    """
    """
    payment_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='ordered_item'
    )

    class Meta:
        model = Refund
        fields = ["payment_id", "payment", "razorpay_refund_id", "refund_amount", "refund_status"]
        extra_kwargs = {              
            'payment_id': {'write_only': True, 'many': True},
        }