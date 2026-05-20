from typing import cast
from rest_framework import serializers

from app_products.models import Product, Cart

class ProductSerializer(serializers.ModelSerializer):
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
    
class CartSerializer(serializers.ModelSerializer):
    
    class ProductSerializer(serializers.ModelSerializer):
        class Meta:
            model = Product
            fields = ["name", "price", "status", "product_Img"]
    
    product = ProductSerializer()

    class Meta:
        model = Cart
        fields = ["product" , "quantity", "total_price"]

    def get_total_price(self,obj):
        obj = cast(Cart, obj) #typehint
        return obj.total_price if obj else None
    
    """def create(self, validated_data):
        print(validated_data)
        validated_data = cast(dict, validated_data)
        location_data = validated_data.pop('location')
        location, _ = Location.objects.get_or_create(**location_data)
        user_profile = Profile.objects.create(location = location,**validated_data)
        return user_profile"""