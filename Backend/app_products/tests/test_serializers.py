from django.test import TestCase
from app_users.serializers import UserSerializer, ProfileSerializer
from app_users.models import User, Profile
from app_products.serializers import CartSerializer, ProductSerializer
from app_products.models import Product, Cart
from testing_data.fill_dummy_data import fill_database
from typing import Any, cast

class CartSerializerTest(TestCase):
    
    def setUp(self) -> None:
        fill_database()
        
    def test_serialization(self):
        cart = Cart.objects.all()
        print(cart)
        serializer = CartSerializer(cart, many = True)
        data = cast(dict[str, Any], serializer.data)
        #print(data)
        print(serializer.data)
        #self.assertEqual(data['email'], "abc@domain.com")
