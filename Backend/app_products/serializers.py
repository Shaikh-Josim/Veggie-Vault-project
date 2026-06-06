from typing import cast
from uuid import UUID
from decimal import Decimal

from rest_framework import serializers

from app_users.models import Profile
from app_products.models import Product, Cart

class ProductNestedSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ["name", "discription", "category", "price", "stock", "status", "product_Img"]
        
    def get_category(self, obj):
        return {
                "name":obj.get_category_display(),
                "value": obj.category}
    
    def get_status(self, obj):
        return {
                "type":obj.get_status_display(),
                "value": obj.status}
    
class ProductSerializer(serializers.Serializer):
    product = ProductNestedSerializer(source = '*')
    

class CartSerializer(serializers.ModelSerializer):
    cart_id = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    profile_id = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())
    product = ProductNestedSerializer(read_only = True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = Cart
        fields = ["cart_id","profile_id", "product_id", "product", "quantity", "total_price"]

    def get_cart_id(self, obj: Cart) -> UUID | None:
        return obj.uid if obj else None

    def get_total_price(self, obj: Cart) -> Decimal | None:
        return obj.total_price if obj else None
    
    def create(self, validated_data):
        profile = validated_data.pop('profile_id')
        product = validated_data.pop('product_id')
        cart, created = Cart.objects.update_or_create(profile = profile, product =  product , defaults=validated_data)
        return cart
