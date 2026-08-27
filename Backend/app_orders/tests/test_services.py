import copy


from unittest.mock import patch
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from django.db import connection
from django.db.models import Q
from freezegun import freeze_time



from django.utils.crypto import get_random_string
from django.test import TestCase
from rest_framework.test import APIClient


from app_users.models import User, Profile
from app_products.models import Product, Cart
from app_locations.models import Location
from app_orders.models import Orders, OrderedItem, Payment, Refund
from base.tests.test_data import user1_data, profile1_data, location1_data, product1_data, product2_data, cart1_data, cart2_data, order1_data, order4_data, ordereditem1_data, ordereditem2_data, payment1_data
from base.helpers import pop_update_dict_data

import logging

logger = logging.getLogger('app_orders')

from app_orders.services import OrderCreationService

# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_cases.OrderOperationsTest --debug-mode
class OrderServiceTest(TestCase):

    dummy_razorpay_order = {
            "id": "order_test123456789",
            "entity": "order",
            "amount": 50000,
            "amount_paid": 0,
            "amount_due": 50000,
            "currency": "INR",
            "receipt": "receipt_test_123",
            "status": "created",
            "attempts": 0,
            "notes": {},
            "created_at": 1755840000,
            }
    
    dummy_razorpay_refund = {
        "id": "rfnd_test123456789",
        "entity": "refund",
        "amount": 50000,
        "currency": "INR",
        "payment_id": "payment_1",
        "notes": {},
        "receipt": None,
        "acquirer_data": {},
        "created_at": 1755889200,
        "status": "processed",
    }

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_services.OrderServiceTest.test_create_razorpay_order --debug-mode
    def test_create_razorpay_order(self):
        logger.info("\n----------CREATE RAZORPAY ORDER SERVICE TEST----------")

        with patch("app_orders.services.razorpay_client") as mock_client:
            mock_client.order.create.return_value = self.dummy_razorpay_order
            data = OrderCreationService.create_razorpay_order(amount= 500) 

            self.assertEqual(data['id'], self.dummy_razorpay_order.get('id'))
            print(' TEST PASSED SUCCESSFULLY!!')  

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_services.OrderServiceTest.test_refund_expired_order_payment --debug-mode
    def test_refund_expired_order_payment(self):
        logger.info("\n----------REFUND EXPIRED ORDER PAYMENT SERVICE TEST----------")
        self.user = User.objects.create(**user1_data)
        self.location = Location.objects.create(**location1_data)
        self.profile = Profile.objects.create(user = self.user, **profile1_data)
        self.profile.location.add(self.location)
        self.product = Product.objects.create(**product1_data)
        self.order = Orders.objects.create(consumer = self.profile, **order1_data)
        self.payment = Payment.objects.create(order = self.order, **payment1_data)
        

        with patch("app_orders.services.razorpay_client") as mock_client:
            mock_client.payment.refund.return_value = self.dummy_razorpay_refund
            OrderCreationService.refund_expired_order_payment(razorpay_payment_id= self.payment.razorpay_payment_id)
            print(Refund.objects.all())
            refund = Refund.objects.get(razorpay_refund_id = self.dummy_razorpay_refund['id'])

            self.assertTrue(refund.razorpay_refund_id, self.dummy_razorpay_refund['id'])
            self.assertTrue(refund.refund_status, 'processed')

        print(' TEST PASSED SUCCESSFULLY!!')  

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_services.OrderServiceTest.test_process_order_payment --debug-mode
    def test_process_order_payment(self):
        logger.info("\n----------PROCESS ORDER PAYMENT SERVICE TEST----------")
        self.user = User.objects.create(**user1_data)
        self.location = Location.objects.create(**location1_data)
        self.profile = Profile.objects.create(user = self.user, **profile1_data)
        self.profile.location.add(self.location)
        self.product = Product.objects.create(**product1_data)
        self.order = Orders.objects.create(consumer = self.profile, **order4_data)
        self.payment = Payment.objects.create(order = self.order, **pop_update_dict_data(copy.deepcopy(payment1_data), remove_keys=['payment_status']))
        print(Payment.objects.all())
        OrderCreationService.process_order_payment(order= self.order, payment= self.payment, payment_status = 'captured')
        print(Payment.objects.all())

        print(Payment.objects.filter(razorpay_payment_id = 'payment_1', payment_status = 'created', order__order_status = 'paid'))
        self.assertFalse(Payment.objects.filter(razorpay_payment_id = 'payment_1', payment_status = 'created', order__order_status = 'paid').exists())

        print(' TEST PASSED SUCCESSFULLY!!')  
        
    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_services.OrderServiceTest.test_deduct_stock --debug-mode
    def test_deduct_stock(self):
        logger.info("\n----------DEDUCT STOCK ORDER SERVICE TEST----------")
        self.user = User.objects.create(**user1_data)
        self.location = Location.objects.create(**location1_data)
        self.profile = Profile.objects.create(user = self.user, **profile1_data)
        self.profile.location.add(self.location)
        self.product = Product.objects.create(**product1_data)
        self.cart = Cart.objects.create(profile = self.profile, product = self.product, **cart1_data)

        OrderCreationService.deduct_stock(cart= Cart.objects.filter(profile = self.profile))

        product = Product.objects.get(uid = self.product.uid)

        self.assertEqual(product.stock, 75) #deducted stock is 75 from 100
        print(' TEST PASSED SUCCESSFULLY!!')  

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_services.OrderServiceTest.test_get_amount_from_cart --debug-mode
    def test_get_amount_from_cart(self):
        logger.info("\n----------GET AMOUNT FROM CART ORDER SERVICE TEST----------")
        self.user = User.objects.create(**user1_data)
        self.location = Location.objects.create(**location1_data)
        self.profile = Profile.objects.create(user = self.user, **profile1_data)
        self.profile.location.add(self.location)
        self.product = Product.objects.create(**product1_data)
        self.product2 = Product.objects.create(**product2_data)
        Cart.objects.create(profile = self.profile, product = self.product, **cart1_data)
        Cart.objects.create(profile = self.profile, product = self.product2, **cart2_data)
        
        total_price_of_cart_items, product_ids = OrderCreationService.get_amount_from_cart(Cart.objects.filter(profile = self.profile))
        self.assertEqual(total_price_of_cart_items, 1000)
        
        print(' TEST PASSED SUCCESSFULLY!!')  

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_services.OrderServiceTest.test_is_cart_products_stock_available --debug-mode
    def test_is_cart_products_stock_available(self):
        logger.info("\n---------IS CART PRODUCTS IN STOCK ORDER SERVICE TEST----------")
        self.user = User.objects.create(**user1_data)
        self.location = Location.objects.create(**location1_data)
        self.profile = Profile.objects.create(user = self.user, **profile1_data)
        self.profile.location.add(self.location)
        self.product = Product.objects.create(**pop_update_dict_data(copy.deepcopy(product1_data), overrides={'stock': 10})) #making product out of stock
        self.product2 = Product.objects.create(**product2_data)
        Cart.objects.create(profile = self.profile, product = self.product, **cart1_data)
        Cart.objects.create(profile = self.profile, product = self.product2, **cart2_data)
        
        is_stock = OrderCreationService.is_cart_products_stock_available(Cart.objects.filter(profile = self.profile) )
        self.assertFalse(is_stock)
        
        print(' TEST PASSED SUCCESSFULLY!!')  

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_services.OrderServiceTest.test_get_products_from_cart --debug-mode
    def test_get_products_from_cart(self):
        logger.info("\n---------GET PRODUCTS FROM CART ORDER SERVICE TEST----------")
        self.user = User.objects.create(**user1_data)
        self.location = Location.objects.create(**location1_data)
        self.profile = Profile.objects.create(user = self.user, **profile1_data)
        self.profile.location.add(self.location)
        self.product = Product.objects.create(**product1_data) #making product out of stock
        self.product2 = Product.objects.create(**product2_data) 
        Cart.objects.create(profile = self.profile, product = self.product, **cart1_data)
        Cart.objects.create(profile = self.profile, product = self.product2, **cart2_data)
        self.order = Orders.objects.create(consumer = self.profile, **order1_data)

        products_data = OrderCreationService.get_products_from_cart(Cart.objects.filter(profile = self.profile).order_by('-quantity'), order= self.order )
        print(products_data)
        self.assertEqual(products_data[0]['product_id'], self.product.uid)
        self.assertEqual(products_data[1]['product_id'], self.product2.uid)
        print(' TEST PASSED SUCCESSFULLY!!')  
            
    
    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_services.OrderServiceTest.test_get_products_from_ordereditem --debug-mode
    def test_get_products_from_ordereditem(self):
        logger.info("\n---------GET PRODUCTS FROM ORDEREDITEMS ORDER SERVICE TEST----------")
        self.user = User.objects.create(**user1_data)
        self.location = Location.objects.create(**location1_data)
        self.profile = Profile.objects.create(user = self.user, **profile1_data)
        self.profile.location.add(self.location)
        self.product = Product.objects.create(**product1_data) #making product out of stock
        self.product2 = Product.objects.create(**product2_data) 
        Cart.objects.create(profile = self.profile, product = self.product, **cart1_data)
        Cart.objects.create(profile = self.profile, product = self.product2, **cart2_data)
        self.order = Orders.objects.create(consumer = self.profile, **order1_data)
        OrderedItem.objects.create(order = self.order, ordered_item = self.product, **ordereditem1_data)
        OrderedItem.objects.create(order = self.order, ordered_item = self.product2, **ordereditem2_data)

        cart_data = OrderCreationService.get_products_from_ordereditem(OrderedItem.objects.filter(order = self.order).order_by('-quantity'))
        print(cart_data)
        self.assertEqual(cart_data[0]['profile_id'], self.profile.uid)
        self.assertEqual(cart_data[0]['product_id'], self.product.uid)
        self.assertEqual(cart_data[1]['product_id'], self.product2.uid)
        print(' TEST PASSED SUCCESSFULLY!!')  

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_services.OrderServiceTest.test_reroll_stock --debug-mode
    def test_reroll_stock(self):
        logger.info("\n---------REROLL STOCK ORDER SERVICE TEST----------")
        self.user = User.objects.create(**user1_data)
        self.location = Location.objects.create(**location1_data)
        self.profile = Profile.objects.create(user = self.user, **profile1_data)
        self.profile.location.add(self.location)
        self.product = Product.objects.create(**pop_update_dict_data(copy.deepcopy(product1_data), overrides={'stock': 75})) #making product out of stock
        self.product2 = Product.objects.create(**product2_data) 
        Cart.objects.create(profile = self.profile, product = self.product, **cart1_data)
        Cart.objects.create(profile = self.profile, product = self.product2, **cart2_data)
        self.order = Orders.objects.create(consumer = self.profile, **order1_data)
        OrderedItem.objects.create(order = self.order, ordered_item = self.product, **ordereditem1_data)
        OrderedItem.objects.create(order = self.order, ordered_item = self.product2, **ordereditem2_data)

        
        products = Product.objects.filter(Q( uid = self.product.uid) | Q( uid = self.product2.uid))
        data_containing_quantity = {self.product.uid: cart1_data['quantity'], self.product2.uid: cart2_data['quantity']}

        OrderCreationService.reroll_stock(products= products, data_containing_quantity= data_containing_quantity)

        self.assertEqual(Product.objects.get(uid = self.product.uid).stock, 100)
        self.assertEqual(Product.objects.get(uid = self.product2.uid).stock, 220)
        print(' TEST PASSED SUCCESSFULLY!!')  

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_services.OrderServiceTest.test_expire_stale_orders --debug-mode
    def test_expire_stale_orders (self):
        logger.info("\n---------EXPIRE STALE ORDER SERVICE TEST----------")

        with freeze_time("2026-07-16 1:00:00") as frozen_datetime:
            self.user = User.objects.create(**user1_data)
            self.location = Location.objects.create(**location1_data)
            self.profile = Profile.objects.create(user = self.user, **profile1_data)
            self.profile.location.add(self.location)
            self.product = Product.objects.create(**pop_update_dict_data(copy.deepcopy(product1_data), overrides={'stock': 75})) #making product out of stock
            self.product2 = Product.objects.create(**pop_update_dict_data(copy.deepcopy(product2_data), overrides={'stock': 80}))
            Cart.objects.create(profile = self.profile, product = self.product, **cart1_data)
            Cart.objects.create(profile = self.profile, product = self.product2, **cart2_data)
            self.order = Orders.objects.create(consumer = self.profile, **pop_update_dict_data(copy.deepcopy(order1_data), overrides= {'amount': 1000, 'order_status' : 'not_paid', 'payment_mode' : 'online'}))
            OrderedItem.objects.create(order = self.order, ordered_item = self.product, **pop_update_dict_data(copy.deepcopy(ordereditem1_data), overrides={'item_status': 'pending'}))
            OrderedItem.objects.create(order = self.order, ordered_item = self.product2, **ordereditem2_data)

            frozen_datetime.tick(delta=timezone.timedelta(minutes=31)) #go in future
            OrderCreationService.expire_stale_orders(order_id= str(self.order.razorpay_order_id)) 

        self.assertEqual(Orders.objects.get(uid = self.order.uid).order_status, 'expired')
        self.assertEqual(Product.objects.get(uid = self.product.uid).stock, 100)
        self.assertEqual(Product.objects.get(uid = self.product2.uid).stock, 100)
        print(' TEST PASSED SUCCESSFULLY!!')  