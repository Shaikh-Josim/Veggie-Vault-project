import json
import logging
import copy
from typing import Any, cast

from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase

from app_users.models import  User, Profile
from app_products.serializers import  CartSerializer, ProductSerializer, ProductNestedSerializer
from app_products.models import Product, Cart 
from base.helpers import pop_update_dict_data
from base.tests.test_data import cart1_data, profile1_data, user1_data, product1_data, get_test_img

logger = logging.getLogger('app_products')


# run this class test with command:
# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_products.tests.test_serializers.ProductSerializerTest --debug-mode
class ProductSerializerTest(TestCase):

    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_products.tests.test_serializers.ProductSerializerTest.test_product_serializer --debug-mode
    def test_product_serializer(self):
        logger.info("\n-----------PRODUCT SERIALIZER TEST-----------")

        
        product_serializer = ProductNestedSerializer(data = pop_update_dict_data(copy.deepcopy(product1_data), overrides={'product_Img': get_test_img(product1_data['name'])}))
        print("Serialization|  valid data: ",product_serializer.is_valid(), "\n serialized data:", product_serializer.validated_data)
        print(product_serializer.errors)

        product = Product.objects.create(**pop_update_dict_data(copy.deepcopy(product1_data), overrides={'product_Img': get_test_img(product1_data['name'])}))
        product_deserializer = ProductNestedSerializer(product)
        print("Deserialization| valid data: ", product_deserializer.data )

        bad_product_data = pop_update_dict_data(copy.deepcopy(product1_data), overrides={'product_Img': get_test_img(product1_data['name']), 'name':1231})
        bad_product_serializer = ProductNestedSerializer(data = bad_product_data)
        
        self.assertTrue(product_serializer.is_valid())
        self.assertFalse(product_serializer.errors)
        self.assertFalse(bad_product_serializer.is_valid())
        self.assertTrue(bad_product_serializer.errors)
        print('TEST PASSED SUCCESSFULLY!!')

    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_products.tests.test_serializers.ProductSerializerTest.test_product_with_product_tag_serializer --debug-mode
    def test_product_with_product_tag_serializer(self):
        logger.info("\n-----------PRODUCT-TAG PRODUCT SERIALIZER TEST-----------")
        
        product_serializer = ProductSerializer(data = {"product": pop_update_dict_data(copy.deepcopy(product1_data), overrides={'product_Img': get_test_img(product1_data['name'])})})
        print("Serialization|  valid data: ",product_serializer.is_valid(), "\n serialized data:", product_serializer.validated_data)
        print(product_serializer.errors)

        product = Product.objects.create(**pop_update_dict_data(copy.deepcopy(product1_data), overrides={'product_Img': get_test_img(product1_data['name'])}))
        product_deserializer = ProductSerializer(product)
        print("Deserialization| valid data: ", product_deserializer.data )

        bad_product_data = pop_update_dict_data(copy.deepcopy(product1_data), overrides={'product_Img': get_test_img(product1_data['name']), 'name':7373})
        bad_product_serializer = ProductNestedSerializer(data = bad_product_data)
        
        self.assertTrue(product_serializer.is_valid())
        self.assertFalse(product_serializer.errors)
        self.assertTrue(product_deserializer.data.__contains__('product'))
        self.assertFalse(bad_product_serializer.is_valid())
        self.assertTrue(bad_product_serializer.errors)
        print('TEST PASSED SUCCESSFULLY!!')

# run test with
# python .\manage.py test <app-name>.<test-folder>.<test-file-name>
# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_products.tests.test_serializers.CartSerializerTest --debug-mode
class CartSerializerTest(TestCase):
        
    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_products.tests.test_serializers.CartSerializerTest.test_cart_serializer --debug-mode
    def test_cart_serializer(self):
        logger.info("\n----------- CART SERIALIZER TEST -----------")

        user = User.objects.create(**user1_data)
        profile = Profile.objects.create(user = user, **profile1_data)
        product = Product.objects.create(**pop_update_dict_data(copy.deepcopy(product1_data), overrides={'product_Img': get_test_img(product1_data['name'])}))

        cart_data = pop_update_dict_data(copy.deepcopy(cart1_data), overrides= {'profile_id': profile.uid, 'product_id':product.uid})
        cart_serializer = CartSerializer(data = cart_data)
        print("Serialization|  valid data: ",cart_serializer.is_valid(), "\n serialized data:", cart_serializer.validated_data)
        print(cart_serializer.errors)

        cart = Cart.objects.create(profile = profile, product = product, **cart1_data)
        cart_deserializer = CartSerializer(cart)
        print("Deserialization| valid data: ", cart_deserializer.data )

        bad_cart_data = pop_update_dict_data(copy.deepcopy(cart1_data), overrides= {'quantity':'abc'})
        bad_cart_serializer = ProductNestedSerializer(data = bad_cart_data)

        self.assertTrue(cart_serializer.is_valid())
        self.assertFalse(cart_serializer.errors)
        self.assertFalse(bad_cart_serializer.is_valid())
        self.assertTrue(bad_cart_serializer.errors)
        print('TEST PASSED SUCCESSFULLY!!')