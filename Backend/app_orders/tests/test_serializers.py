import logging
import json
import copy
from decimal import Decimal
from typing import Any, cast

from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase

from app_orders.serializers import OrderedItemSerializer, OrderSerializer, RazorOrderIdSerializer, PaymentSerializer, RefundSerializer
from app_orders.models import OrderedItem, Product, Profile, Orders, Payment, Refund
from app_locations.models import Location
from app_users.models import User
from app_products.models import Cart
from base.helpers import pop_update_dict_data
from base.tests.test_data import user1_data, profile1_data, location1_data, product1_data, order1_data, ordereditem1_data, payment1_data, refund1_data

logger = logging.getLogger('app_orders')

# run this class test with command:
# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_serializers.OrderSerializerTest --debug-mode
class OrderSerializerTest(TestCase):

    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_serializers.OrderSerializerTest.test_ordered_item_serializer --debug-mode
    def test_ordered_item_serializer(self):
        logger.info("\n-----------ORDERED ITEM SERIALIZER TEST-----------")

        self.user = User.objects.create(**user1_data)
        self.location = Location.objects.create(**location1_data)
        self.profile = Profile.objects.create(user = self.user, **profile1_data)
        self.profile.location.add(self.location)
        self.product = Product.objects.create(**pop_update_dict_data(copy.deepcopy(product1_data))) 
        self.order = Orders.objects.create(consumer = self.profile, **order1_data)
        oi = OrderedItem.objects.create(order = self.order, ordered_item = self.product, **ordereditem1_data)
        ordered_item_deserializer = OrderedItemSerializer(oi)
        print("Deserialization| valid data: ", ordered_item_deserializer.data )

        ordered_item_serializer = OrderedItemSerializer(data = pop_update_dict_data(copy.deepcopy(ordereditem1_data), overrides= {'order': self.order.uid, 'product_id': self.product.uid}))        
        print("Serialization|  valid data: ",ordered_item_serializer.is_valid(), "\n serialized data:", ordered_item_serializer.validated_data)
        print(ordered_item_serializer.errors)

        bad_ordered_item_data = pop_update_dict_data(copy.deepcopy(ordereditem1_data), overrides={'quantity': 'ahbnc'})
        bad_ordered_item_serializer = OrderedItemSerializer(data = bad_ordered_item_data)

        self.assertTrue(ordered_item_serializer.is_valid())
        self.assertFalse(ordered_item_serializer.errors)
        self.assertFalse(bad_ordered_item_serializer.is_valid())
        self.assertTrue(bad_ordered_item_serializer.errors)


    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_serializers.OrderSerializerTest.test_order_serializer --debug-mode
    def test_order_serializer(self):
        logger.info("\n-----------ORDER SERIALIZER TEST-----------")

        order_serializer = OrderSerializer(data = order1_data)
        print("Serialization|  valid data: ",order_serializer.is_valid(), "\n serialized data:", order_serializer.validated_data)
        print(order_serializer.errors)

        self.user = User.objects.create(**user1_data)
        self.location = Location.objects.create(**location1_data)
        self.profile = Profile.objects.create(user = self.user, **profile1_data)
        self.profile.location.add(self.location)
        self.product = Product.objects.create(**pop_update_dict_data(copy.deepcopy(product1_data))) 
        self.order = Orders.objects.create(consumer = self.profile, **order1_data)
        order_deserializer = OrderSerializer(self.order)
        print("Deserialization| valid data: ", order_deserializer.data )

        bad_order_data = pop_update_dict_data(copy.deepcopy(order1_data), overrides={'order_status': 'abc_mode'})
        bad_order_serializer = OrderSerializer(data = bad_order_data)

        self.assertTrue(order_serializer.is_valid())
        self.assertFalse(order_serializer.errors)
        self.assertFalse(bad_order_serializer.is_valid())
        self.assertTrue(bad_order_serializer.errors)

    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_serializers.OrderSerializerTest.test_razorpay_order_serializer --debug-mode
    def test_razorpay_order_serializer(self):
        logger.info("\n-----------ORDER SERIALIZER TEST-----------")

        razorpay_order_serializer = RazorOrderIdSerializer(data = pop_update_dict_data(copy.deepcopy(order1_data), remove_keys= ['consumer', 'amount', 'order_status', 'payment_mode' ]))
        print("Serialization|  valid data: ",razorpay_order_serializer.is_valid(), "\n serialized data:", razorpay_order_serializer.validated_data)
        print(razorpay_order_serializer.errors)

        bad_razorpay_order_data = pop_update_dict_data(copy.deepcopy(order1_data), remove_keys= ['consumer', 'amount', 'order_status', 'payment_mode' ], overrides={'razorpay_order_id': 'abc'})
        bad_razorpay_order_serializer = RazorOrderIdSerializer(data = bad_razorpay_order_data)

        self.assertTrue(razorpay_order_serializer.is_valid())
        self.assertFalse(razorpay_order_serializer.errors)
        self.assertFalse(bad_razorpay_order_serializer.is_valid())
        self.assertTrue(bad_razorpay_order_serializer.errors)

    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_serializers.OrderSerializerTest.test_payment_serialzer --debug-mode
    def test_payment_serialzer(self):
        logger.info("\n-----------PAYMENT SERIALIZER TEST-----------")

        self.user = User.objects.create(**user1_data)
        self.profile = Profile.objects.create(user = self.user, **profile1_data)
        self.order = Orders.objects.create(consumer = self.profile, **order1_data)

        payment_serializer = PaymentSerializer(data = payment1_data)
        print("Serialization|  valid data: ",payment_serializer.is_valid(), "\n serialized data:", payment_serializer.validated_data)
        print(payment_serializer.errors)

        self.payment = Payment.objects.create(order = self.order, **payment1_data)
        payment_deserializer = PaymentSerializer(self.payment)
        print("Deserialization| valid data: ", payment_deserializer.data )
        

        bad_payment_data = pop_update_dict_data(copy.deepcopy(payment1_data), overrides={'payment_status': 'abc'})
        bad_payment_serializer = RazorOrderIdSerializer(data = bad_payment_data)

        self.assertTrue(payment_serializer.is_valid())
        self.assertFalse(payment_serializer.errors)
        self.assertFalse(bad_payment_serializer.is_valid())
        self.assertTrue(bad_payment_serializer.errors)

    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_serializers.OrderSerializerTest.test_refund_serialzer --debug-mode
    def test_refund_serialzer(self):
        logger.info("\n-----------REFUND SERIALIZER TEST-----------")
        fields = ["payment_id", "payment", "razorpay_refund_id", "refund_amount", "refund_status"]

        self.user = User.objects.create(**user1_data)
        self.profile = Profile.objects.create(user = self.user, **profile1_data)
        self.order = Orders.objects.create(consumer = self.profile, **order1_data)
        self.payment = Payment.objects.create(order = self.order, **payment1_data)

        refund_serializer = RefundSerializer(data = pop_update_dict_data(copy.deepcopy(refund1_data), overrides={'payment': self.payment.uid}))
        print("Serialization|  valid data: ",refund_serializer.is_valid(), "\n serialized data:", refund_serializer.validated_data)
        print(refund_serializer.errors)


        self.refund = Refund.objects.create(payment = self.payment, **refund1_data)
        refund_deserializer = RefundSerializer(self.refund)
        print("Deserialization| valid data: ", refund_deserializer.data )
        

        bad_refund_data = pop_update_dict_data(copy.deepcopy(refund1_data), overrides={'refund_status': 'abc', 'refund_amount': 'abc'})
        bad_refund_serializer = RefundSerializer(data = bad_refund_data)

        self.assertTrue(refund_serializer.is_valid())
        self.assertFalse(refund_serializer.errors)
        self.assertFalse(bad_refund_serializer.is_valid())
        self.assertTrue(bad_refund_serializer.errors)
