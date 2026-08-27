import logging
import copy
from decimal import Decimal

from django.test import TestCase
from django.core.exceptions import ValidationError

from app_orders.models import OrderedItem, Product, Profile, Orders, Payment, Refund
from app_locations.models import Location
from app_users.models import User
from app_products.models import Cart
from base.helpers import pop_update_dict_data
from base.tests.test_data import user1_data, profile1_data, location1_data, product1_data, order1_data, ordereditem1_data, payment1_data, refund1_data

logger = logging.getLogger("app_orders")

# run test with
# python .\manage.py test <app-name>.<test-folder>.<test-file-name>
# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_models.OrderModelTest --debug-mode

class OrderModelTest(TestCase):
    

    def setUp(self) -> None:
        """Initializes testing records across required database tables."""
        self.user = User.objects.create(**user1_data)
        self.location = Location.objects.create(**location1_data)
        self.profile = Profile.objects.create(user = self.user, **profile1_data)
        self.profile.location.add(self.location)
        self.order = Orders.objects.create(consumer = self.profile, **order1_data)
        
    
    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_models.OrderModelTest.test_str_representation --debug-mode    
    def test_str_representation(self):
        logger.info("\n---------- STR REPRESENTATION ORDER MODEL TEST----------")
        
        print(self.order.debug_str())
        print(self.order)
        self.assertEqual(str(self.order), "consumer-name:abc xyz, order-amount:500 razorpay_orderid:order_1")
        print(' TEST PASSED SUCCESSFULLY!!')        

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_models.OrderModelTest.test_order_obj_values --debug-mode    
    def test_order_obj_values(self):
        logger.info("\n---------- Order OBJ VALUES MODEL TEST----------")

        self.assertEqual(self.order.amount, 500)
        self.assertEqual(self.order.razorpay_order_id, 'order_1')
        self.assertEqual(self.order.order_status, 'paid')
        self.assertEqual(self.order.payment_mode, 'offline')
        
        print(' TEST PASSED SUCCESSFULLY!!')        
    

# run test with
# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_models.OrderedItemModelTest --debug-mode
class OrderedItemModelTest(TestCase):

    def setUp(self) -> None:
        """Initializes testing records across required database tables."""
        self.user = User.objects.create(**user1_data)
        self.location = Location.objects.create(**location1_data)
        self.profile = Profile.objects.create(user = self.user, **profile1_data)
        self.profile.location.add(self.location)
        self.product = Product.objects.create(**product1_data)
        self.order = Orders.objects.create(consumer = self.profile, **order1_data)
        self.ordered_item = OrderedItem.objects.create(order = self.order, ordered_item = self.product, **ordereditem1_data)
        
    
    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_models.OrderedItemModelTest.test_str_representation --debug-mode    
    def test_str_representation(self):
        logger.info("\n---------- STR REPRESENTATION ORDERED ITEM MODEL TEST----------")
        
        print(self.ordered_item.debug_str())
        print(self.ordered_item)
        self.assertEqual(str(self.ordered_item), "order:consumer-name:abc xyz, order-amount:500 razorpay_orderid:order_1 product:Tomato, item_status:delivered")
        print(' TEST PASSED SUCCESSFULLY!!')        

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_models.OrderedItemModelTest.test_order_obj_values --debug-mode    
    def test_order_obj_values(self):
        logger.info("\n---------- ORDERED ITEM OBJ VALUES MODEL TEST----------")

        self.assertEqual(self.ordered_item.quantity, 25)
        self.assertEqual(self.ordered_item.total_price, 500)
        self.assertEqual(self.ordered_item.item_status, 'delivered')
        
        print(' TEST PASSED SUCCESSFULLY!!')        


# run test with
# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_models.PaymentModelTest --debug-mode
class PaymentModelTest(TestCase):

    def setUp(self) -> None:
        """Initializes testing records across required database tables."""
        self.user = User.objects.create(**user1_data)
        self.location = Location.objects.create(**location1_data)
        self.profile = Profile.objects.create(user = self.user, **profile1_data)
        self.profile.location.add(self.location)
        self.product = Product.objects.create(**product1_data)
        self.order = Orders.objects.create(consumer = self.profile, **order1_data)
        self.payment = Payment.objects.create(order = self.order, **payment1_data)
        
    
    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_models.PaymentModelTest.test_str_representation --debug-mode    
    def test_str_representation(self):
        logger.info("\n---------- STR REPRESENTATION PAYMENT MODEL TEST----------")
        
        print(self.payment.debug_str())
        print(self.payment)
        self.assertEqual(str(self.payment), "payment-id:payment_1 payment-status captured")
        print(' TEST PASSED SUCCESSFULLY!!')        

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_models.PaymentModelTest.test_order_obj_values --debug-mode    
    def test_order_obj_values(self):
        logger.info("\n---------- PAYMENT OBJ VALUES MODEL TEST----------")

        self.assertEqual(self.payment.razorpay_payment_id, 'payment_1')
        self.assertEqual(self.payment.payment_status, 'captured')
        
        print(' TEST PASSED SUCCESSFULLY!!')        


# run test with
# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_models.RefundModelTest --debug-mode
class RefundModelTest(TestCase):

    def setUp(self) -> None:
        """Initializes testing records across required database tables."""
        self.user = User.objects.create(**user1_data)
        self.location = Location.objects.create(**location1_data)
        self.profile = Profile.objects.create(user = self.user, **profile1_data)
        self.profile.location.add(self.location)
        self.product = Product.objects.create(**product1_data)
        self.order = Orders.objects.create(consumer = self.profile, **order1_data)
        self.payment = Payment.objects.create(order = self.order, **payment1_data)
        self.refund = Refund.objects.create(payment = self.payment, **refund1_data)
        
    
    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_models.RefundModelTest.test_str_representation --debug-mode    
    def test_str_representation(self):
        logger.info("\n---------- STR REPRESENTATION REFUND MODEL TEST----------")
        
        print(self.refund.debug_str())
        print(self.refund)
        self.assertEqual(str(self.refund), "refund id: rfnd_1, refund amount: 500, refund_status: processed")
        print(' TEST PASSED SUCCESSFULLY!!')        

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_models.RefundModelTest.test_order_obj_values --debug-mode    
    def test_order_obj_values(self):
        logger.info("\n---------- REFUND OBJ VALUES MODEL TEST----------")

        self.assertEqual(self.refund.razorpay_refund_id, 'rfnd_1')
        self.assertEqual(self.refund.refund_amount, '500')
        self.assertEqual(self.refund.refund_status, 'processed')
        
        print(' TEST PASSED SUCCESSFULLY!!')        

