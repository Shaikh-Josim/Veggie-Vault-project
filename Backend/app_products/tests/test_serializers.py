import json
from typing import Any, cast

from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase

from app_users.models import  Profile
from app_products.serializers import  CartSerializer
from app_products.models import Product, Cart
from testing_data.fill_dummy_data import fill_database


class CartSerializerTest(TestCase):
    
    def setUp(self) -> None:
        fill_database()
        
    def test_serialization(self):

        carts = Cart.objects.all()
        profiles = Profile.objects.all()
        products = Product.objects.all()

        first_profile = cast(Profile, profiles.first())
        first_product = cast(Product, products.first())
        
        print(carts)
        serializer = CartSerializer(carts, many=True)
        print("------------------for get------------")
        print(json.dumps(serializer.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder))
        print("-------------------------------------")

        print(first_profile)
        print(first_product)
        cart_data = {
            "profile_id":   str(first_profile.uid),
            "product_id": str(first_product.uid),
            "quantity":"100",
        }
        print(cart_data)
        serializer = CartSerializer(data=cart_data)
        print("------------------for post------------")

        # Validate input
        serializer.is_valid(raise_exception=True)
        print("Validated data:", serializer.validated_data)
        cart = serializer.save()
        print("Serialized output:", json.dumps(serializer.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder))

        serializer = CartSerializer(Cart.objects.all(), many=True)
        print("------------------for get------------")
        print(json.dumps(serializer.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder))
        print("-------------------------------------")

        cart_data = {
            "quantity":"50",
        }
        serializer = CartSerializer(instance=cart, data=cart_data, partial = True)
        print("------------------for update------------")

        # Validate input
        serializer.is_valid(raise_exception=True)
        print("Validated data:", serializer.validated_data)
        cart = serializer.save()
        print("Serialized output:", json.dumps(serializer.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder))

        serializer = CartSerializer(Cart.objects.all(), many=True)
        print("------------------for get------------")
        print(json.dumps(serializer.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder))

        serializer = CartSerializer(instance=cart, data=cart_data, partial = True)
        


        