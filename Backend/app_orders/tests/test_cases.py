from typing import Any, cast, Dict
import uuid
import copy
import json
import hmac , hashlib
import threading
import time
from unittest.mock import patch

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.crypto import get_random_string
from django.test import TestCase, TransactionTestCase, LiveServerTestCase
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework.test import APIClient


from app_users.models import User, Profile
from app_products.models import Product, Cart
from app_locations.models import Location
from app_orders.models import Orders, OrderedItem, Payment
from VeggieVault.settings import RAZORPAY_TEST_API_KEY, RAZORPAY_TEST_KEY_SECRET, RAZORPAY_WEBHOOK_SECRET
from config.settings import settings_test


import logging

logger = logging.getLogger('app_orders')


MYSQL_DB = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME':'Test',
        'USER':'root',
        'PASSWORD':'',
        'HOST':'127.0.0.1',
        'PORT':'3306',
    }
# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_cases.OrderOperationsTest --debug-mode

class OrderOperationsTest(
        #TestCase
        LiveServerTestCase                     
    ):
    

    def setUp(self) -> None:
        
        self.start_barrier = threading.Barrier(2)
        self.setUser()
        self.setProducts()
        self.setCart()
        self.setOrder()
        self.setOrderedItem()

        
        self.login_user_data = [
            {
            "email" : "jhon@domain.com",
            "password" : "jhon1234"},
            {
            "email" : "brian@domain.com",
            "password" : "brian1234"},
        ]

        self.razorpay_create_order_idempotency_key = str(uuid.uuid4())
        self.razorpay_create_order_idempotency_key2 = str(uuid.uuid4())
        self.razorpay_payment_id = "pay_" + get_random_string(14)
        self.razorpay_after_payment_data = self.get_razorpay_mock_payment_data()
        self.access_token = str(self.atest_login().get('access'))
        self.user2_access_token = str(self.atest_login(i=1).get('access'))

        self.create_order_pm_online_data = {
            "payment_mode" : "online"
        }
        self.create_order_pm_offline_data = {
            "payment_mode" : "offline"
        }
        
        self.razorpay_payment_data = {
            "order_id": "",
            "amount": "500"
        }

        self.razorpay_payment_verify_data = {
            "razorpay_order_id": "",
            "razorpay_payment_id": "",
            "razorpay_signature": "",
        }

        self.razorpay_after_refund_payment_mock_data = {
            "id": "rfnd_R7GTH3oiaXMUQE", # Refund ID (`rfnd_...`)           
            "entity": "refund",
            "amount": 10000, # Refunded amount (paise)          
            "base_amount": 10000,
            "currency": "INR",
            "payment_id": "pay_R7AjczHWEzV2wW", # Original payment ID              
            "receipt": None,
            "notes": {}, # Your metadata                    
            "acquirer_data": {  # Bank reference (ARN/RRN/UTR)     
                "arn": None  # Could also be rrn/utr depending on payment method and processing stage
            },
            "created_at": 1755622126, #Unix timestamp                   
            "batch_id": None,
            "status": "pending", # `pending`, `processed`, `failed` 
            "speed_requested": "optimum", # `normal` or `optimum`            
            "speed_processed": "instant" # Actual processing speed          
        }

        self.razorpay_verify_order_return_data = {
            "id": "pay_T3mdp2569kHOXR",
            "entity": "payment",
            "amount": 50000,          
            "currency": "INR",
            "status": "captured",     # Can be 'created', 'authorized', 'captured', or 'failed'
            "order_id": "order_MOCK123",
            "invoice_id": None,
            "international": False,
            "method": "upi",          # Can be 'card', 'netbanking', 'wallet', 'upi'
            "amount_refunded": 0,
            "refund_status": None,
            "captured": True,
            "description": "Purchase Description",
            "card_id": None,
            "bank": None,
            "wallet": None,
            "vpa": "success@razorpay", # UPI ID if method is upi
            "email": "test@example.com",
            "contact": "+919999999999",
            "notes": [],
            "fee": 1180,
            "tax": 180,
            "error_code": None,
            "error_description": None,
            "created_at": 1618924372
        }

        self.webhook_data = {
            "entity": "event",
            "account_id": "acc_TEST123456789",
            "event": "order.paid",
            "contains": [
                "payment",
                "order"
            ],
            "payload": {
                "payment": {
                "entity": {
                    "id": self.razorpay_payment_id,
                    "entity": "payment",
                    "amount": 50000,
                    "currency": "INR",
                    "status": "captured",
                    "order_id": "order_TEST123456789",
                    "method": "upi"
                }
                },
                "order": {
                "entity": {
                    "id": self.o1.razorpay_order_id,
                    "entity": "order",
                    "amount": 50000,
                    "amount_paid": 50000,
                    "currency": "INR",
                    "status": "paid"
                }
                }
            },
            "created_at": 1750000000
        }
        self.webhook_signature = self.get_webhook_signature()
                
        

    def setUser(self)   -> None:
        self.client = APIClient()
        self.user1 = User.objects.create(email = "jhon@domain.com", password = "jhon1234")
        self.user1.save()
        self.user2 = User.objects.create(email = "brian@domain.com", password = "brian1234")
        self.user2.save()
        location1 = Location( staddr="123 Baker Street", city="Springfield", state="California", hno="42", landmark="Near Central Park", is_homeaddress = True )
        location2 = Location( staddr="12 main Street", city="Autumnfield", state="California", hno="2", landmark="Near Dolphin Park", is_homeaddress = False )
        location1.save()
        location2.save()
        self.profile = Profile( user=self.user1, fname="John", lname="Doe", role=Profile.Role.CONSUMER, mobile_no="9876543210", user_Img=None)
        self.profile.save()
        self.profile.location.add(location1,location2)

        self.profile2 = Profile( user=self.user2, fname="Brian", lname="Doe", role=Profile.Role.CONSUMER, mobile_no="98576543210", user_Img=None)
        self.profile2.save()

    def setProducts(self):
        self.p1 = Product.objects.create(
            name="Tomato",
            category=Product.ProductCategory.VEGETABLE,
            discription = "A juicy, red fruit often treated as a vegetable, tomatoes are rich in vitamin C and lycopene. They are versatile in cooking, used fresh in salads, sauces, and soups,",
            price=20,
            stock=100,
            product_Img = "images/products/tomato.jpg"
        )
        self.p2 = Product.objects.create(
            name="Potato",
            category=Product.ProductCategory.VEGETABLE,
            discription = "A starchy tuber native to South America, potatoes are one of the world’s staple foods. They come in many varieties and are used boiled, mashed, fried, or baked",
            price=30,
            stock=200,
            product_Img = "images/products/potato.jpg"
        )
        self.p3 = Product.objects.create(
            name="Apple",
            category=Product.ProductCategory.FRUIT,
            discription = "A crisp, sweet fruit from the rose family, apples are one of the most widely cultivated fruits worldwide. They are eaten fresh, baked, or juiced, and are rich in fiber and vitamin C.",
            price=100,
            #stock=50,
            stock = 10,
            product_Img = "images/products/Apple.png"
        )
        self.p4 = Product.objects.create(
            name="Banana",
            category=Product.ProductCategory.FRUIT,
            discription = "A long, curved tropical fruit with soft, sweet flesh and a yellow peel when ripe. Bananas are high in potassium and energy, making them a popular snack and smoothie ingredient.",
            price=60,
            stock=120,
            product_Img = "images/products/Banana.png"
        )

    def setCart(self):
        self.c3 = Cart.objects.create(profile=self.profile,product=self.p3,quantity=5)
        self.c5 = Cart.objects.create(profile=self.profile2,product=self.p3,quantity=8)
        self.c1 = Cart.objects.create(profile=self.profile2,product=self.p1,quantity=2)
        self.c2 = Cart.objects.create(profile=self.profile2,product=self.p2,quantity=5)
        self.c4 = Cart.objects.create(profile=self.profile2,product=self.p4,quantity=1)

    def setOrder(self):
        print(Orders.objects.all())
        self.o1 = Orders.objects.create(
            consumer=self.profile,
            amount = self.c3.total_price,
            razorpay_order_id = 'order_test_'+ get_random_string(14)
        )
        print(Orders.objects.all())

    def setOrderedItem(self):
        pass
        OrderedItem.objects.create(
        order=self.o1,
        ordered_item=self.p3,
        quantity=5,
        total_price=self.p3.price*5,
    )
        
    def get_razorpay_mock_payment_data(self):
        try:
            print(self.razorpay_create_order_idempotency_key)
            print(self.razorpay_payment_id)
            secret = cast(str,RAZORPAY_TEST_KEY_SECRET)
            order_obj = Orders.objects.filter(consumer = self.profile).first()
            if order_obj is not None:
                order_id =  order_obj.razorpay_order_id
            order_id = self.o1.razorpay_order_id
            payment_id = self.razorpay_payment_id
            signature = hmac.new(
                secret.encode(),
                f"{order_id}|{payment_id}".encode(),
                hashlib.sha256
            ).hexdigest()

            return {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
        except Exception as e:
            logger.exception(e)

    def get_webhook_signature(self):
        try:
            secret = cast(str,RAZORPAY_WEBHOOK_SECRET)
            payload = self.webhook_data
            
            body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)

            signature = hmac.new(
                key= secret.encode(),
                msg= body.encode(),
                digestmod= hashlib.sha256
                ).hexdigest()
            
            print(body)
            print(signature)

            return signature
        except Exception as e:
            logger.exception(e)
            return ''

    
    def atest_login(self, i = 0) -> Dict[str, Any]:
        print("entering into login test")
        url = reverse('login')
        response = self.client.post(url, self.login_user_data[i])
        response = cast(Response, response)
        print(response)
        print(response.data)
        return cast(Dict[str, Any],response.data)

    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_cases.OrderOperationsTest.test_razorpay_create_order --debug-mode
    def test_razorpay_create_order(self):
        logger.info("entering into razorpay create order test...")
        url_post = reverse("create-order")

        response = self.client.post(url_post, data= self.create_order_pm_online_data, content_type='application/json', HTTP_AUTHORIZATION = 'Bearer '+ self.access_token)
                                            

        logger.info(f"response data: {json.dumps(response.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder)}") #type: ignore
        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(response.json()['order_id'], None)
        self.assertEqual(response.json()['merchant_key'], 'rzp_test_SzX0yI8GDc7TL1')
    
    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_cases.OrderOperationsTest.test_razorpay_verify_payment --debug-mode
    @patch('app_orders.views.razorpay_client') 
    def test_razorpay_verify_payment(self, mock_client):
        """
        Test that a successful Razorpay payment updates our system correctly.
        
        What this test checks:
        1. A logged-in user with a valid token can hit the endpoint.
        2. Instead of calling Razorpay's real servers, we use a fake response.
        3. The view successfully processes the payment and returns a 'success' message.
        """
        logger.info("entering into razorpay verify payment test...")
        url = reverse('verify-payment')
         
        # (This is commented out, but we keep it here in case we want to test a fake/hacked signature later)
        # from razorpay.errors import SignatureVerificationError
        # mock_client.utility.verify_payment_signature.side_effect = SignatureVerificationError("Invalid signature")

        # Tell the fake Razorpay client to return our test data when the view calls it
        mock_client.payment.fetch.return_value = self.razorpay_verify_order_return_data
        logger.info(self.razorpay_after_payment_data)

        # Send the successful payment data to our view using the user's login token
        response = self.client.post(
            url, 
            data=self.razorpay_after_payment_data, 
            format='json', 
            HTTP_AUTHORIZATION='Bearer ' + self.access_token,
            HTTP_X_IDEMPOTENCY_KEY= self.razorpay_create_order_idempotency_key
        )
        response = cast(Response, response)
        
        # Log the response in the terminal so we can see what the view sent back
        logger.info(f"Response data:{json.dumps(response.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder)}")
        
        # Make sure the view returns a 202 status (Accepted) and the right success message
        """self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json()['msg'], 'order payment is done successfully')"""

    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_cases.OrderOperationsTest.test_razorpay_webhook --debug-mode
    def test_razorpay_webhook(self):
        logger.info("entering into razorpay verify payment test...")
        url = reverse("razorpay-webhook")


        # Send the successful payment data to our view using the user's login token
        response = self.client.post(
            url, 
            data=self.webhook_data, 
            format='json', 
            HTTP_AUTHORIZATION='Bearer ' + self.access_token,
            HTTP_X_IDEMPOTENCY_KEY= self.razorpay_create_order_idempotency_key,
            HTTP_X_RAZORPAY_SIGNATURE= self.webhook_signature, 
        )
        response = cast(Response, response)
        
        # Log the response in the terminal so we can see what the view sent back
        logger.info(f"Response data:{json.dumps(response.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder)}")
        

    def send_same_user_order_request(self, thread_id):
        """Worker function executed by each concurrent thread."""
        print(f"[Thread {thread_id}] Waiting at the gate...")

        def razorpay_create_order(self:OrderOperationsTest, thread_id):
            logger.info(f"[Thread {thread_id}] entering into razorpay create order test...")
            url_post = self.live_server_url + reverse("create-order")

            response = self.client.post(url_post, data=self.create_order_pm_online_data ,content_type='application/json', HTTP_AUTHORIZATION = 'Bearer '+ self.access_token, HTTP_X_IDEMPOTENCY_KEY= self.razorpay_create_order_idempotency_key)
                                                
            logger.info(f"[Thread {thread_id}] , response data: {json.dumps(response.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder)}") #type: ignore

        self.start_barrier.wait() # Synced release

        """if thread_id == 2:
            time.sleep(0.1)"""
        
        start_time = time.time()
        try:
            razorpay_create_order(self= self, thread_id= thread_id)
            duration = time.time() - start_time
            print(f"[Thread {thread_id}] | Time taken: {duration:.4f}s\n\n")
        except Exception as e:
            print(f"[Thread {thread_id}] Request failed: {e}")

    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_cases.OrderOperationsTest.test_same_user_double_click --settings=app_orders.tests.settings --debug-mode 
    def test_same_user_double_click(self):
        """Simulates 1 user sending 2 identical requests with the same UUID."""

        logger.info("--- STARTING TEST : SAME USER DOUBLE CLICK SHIELD ---")        

        import sys
        logger.info("--- STARTING TEST : DIFFERENT USER SENDING REQUEST AT SAME TIME ---")
        if len(sys.argv) > 1 and sys.argv[3] != '--settings=app_orders.tests.settings':
            logger.info(f"use mysql database to run test for this function\n you can use '--settings=app_orders.tests.settings' to run this function against mysql")
            return

        t1 = threading.Thread(target=self.send_same_user_order_request, args=(1,))
        t2 = threading.Thread(target=self.send_same_user_order_request, args=(2,))
        
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        product = Product.objects.get(uid = self.p3.uid)
        logger.info(f"Product stock need to be 45.00 after deducting quantity of 5\n Actual Product Stock remained: {product.stock}")

    
    def send_different_user_order_request(self, thread_id):
        """Worker function executed by each concurrent thread."""

        def razorpay_create_order(self:OrderOperationsTest, thread_id):
            logger.info(f"[Thread {thread_id}] entering into razorpay create order test...")
            url_post = self.live_server_url + reverse("create-order")

            if thread_id == 1:
                
                
                    response = self.client.post(url_post, data=self.create_order_pm_online_data ,content_type='application/json', HTTP_AUTHORIZATION = 'Bearer '+ self.access_token, HTTP_X_IDEMPOTENCY_KEY= self.razorpay_create_order_idempotency_key)
            
            elif thread_id == 2:
                
                    response = self.client.post(url_post, data=self.create_order_pm_online_data ,content_type='application/json', HTTP_AUTHORIZATION = 'Bearer '+ self.user2_access_token, HTTP_X_IDEMPOTENCY_KEY= self.razorpay_create_order_idempotency_key2)
                                                
            logger.info(f"[Thread {thread_id}] , response data: {json.dumps(response.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder)}") #type: ignore

        self.start_barrier.wait() # Synced release

        """if thread_id == 2:
            time.sleep(0.1)"""
        
        start_time = time.time()
        try:
            razorpay_create_order(self= self, thread_id= thread_id)
            duration = time.time() - start_time
            print(f"[Thread {thread_id}] | Time taken: {duration:.4f}s\n\n")
        except Exception as e:
            print(f"[Thread {thread_id}] Request failed: {e}")

    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_cases.OrderOperationsTest.test_different_user_click --settings=app_orders.tests.settings --debug-mode 

    @patch('app_orders.views.expire_stale_orders_task.apply_async')
    def test_different_user_click(self, mock_apply_async):
        """Simulates 2 user sending requests at same time."""
        import sys
        from unittest.mock import MagicMock
        logger.info("--- STARTING TEST : DIFFERENT USER SENDING REQUEST AT SAME TIME ---")
        if len(sys.argv) > 1 and sys.argv[3] != '--settings=app_orders.tests.settings':
            logger.info(f"use mysql database to run test for this function\n you can use '--settings=app_orders.tests.settings' to run this function against mysql")
            return

        t1 = threading.Thread(target=self.send_different_user_order_request, args=(1,))
        t2 = threading.Thread(target=self.send_different_user_order_request, args=(2,))
        
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
        print("orderobjs:", Orders.objects.all())

        print("CHECKING IF CELERY TASK GOT THE TASK AND ARGS ELSE RAISE ERROR")
        mock_apply_async = cast(MagicMock, mock_apply_async)
        mock_apply_async.assert_called_once()
        args, kwargs = mock_apply_async.call_args
        print("args:",args, "kwargs:", kwargs)
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
        

        product = Product.objects.get(uid = self.p3.uid)
        logger.info(f"Product Apple has stock 10 \n User A needs: 5\n and User B needs: 8\n one request should be descarded with response of stock unavailable and stock should not be deducted to -ve if both user by pass\n Corrupt result will be -3\n Actual Product Stock remained: {product.stock}")


    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_cases.OrderOperationsTest.test_order_creation_with_celery --settings=app_orders.tests.settings --debug-mode 
    @patch('app_orders.views.expire_stale_orders_task.apply_async')
    def test_order_creation_with_celery(self, mock_apply_async):
        """Simulates 2 user sending requests at same time."""
        import sys
        from unittest.mock import MagicMock
        from datetime import timedelta
        from freezegun import freeze_time
        from app_orders.tasks import expire_stale_orders_task
        logger.info("--- STARTING TEST : DIFFERENT USER SENDING REQUEST AT SAME TIME ---")
        if len(sys.argv) > 1 and sys.argv[3] != '--settings=app_orders.tests.settings':
            logger.info(f"use mysql database to run test for this function\n you can use '--settings=app_orders.tests.settings' to run this function against mysql")
            return

        url_post = self.live_server_url + reverse("create-order")

        with freeze_time("2026-07-16 1:00:00") as frozen_datetime:
            self.access_token = self.atest_login()['access']
            response = self.client.post(url_post, data=self.create_order_pm_online_data ,
            content_type='application/json', HTTP_AUTHORIZATION = 'Bearer '+ self.access_token, HTTP_X_IDEMPOTENCY_KEY= self.razorpay_create_order_idempotency_key)
                                                
            logger.info(f" response data: {json.dumps(response.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder)}") #type: ignore

            
            print("CHECKING IF CELERY TASK GOT THE TASK AND ARGS ELSE RAISE ERROR")
            mock_apply_async = cast(MagicMock, mock_apply_async)
            mock_apply_async.assert_called_once()
            args, kwargs = mock_apply_async.call_args
            print("SUCCESS")
            print("expire_stale_orders_task.apply() called one time and has args and kwargs:\nargs:",args, "kwargs:", kwargs,'\n')
            expire_stale_orders_task_kwargs = kwargs.get('kwargs')

            order_obj = Orders.objects.get(consumer = self.profile, razorpay_order_id = expire_stale_orders_task_kwargs.get('order_id'))
            print(order_obj, order_obj.updated_at)

            frozen_datetime.tick(delta=timedelta(minutes=15)) #go in future
            expire_stale_orders_task = cast(Any, expire_stale_orders_task)
            expire_stale_orders_task.apply(kwargs = expire_stale_orders_task_kwargs) #call task 

            order_obj = Orders.objects.get(consumer = self.profile, razorpay_order_id = expire_stale_orders_task_kwargs.get('order_id'))
            print(order_obj, order_obj.updated_at)
            print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
        
            print("orderobjs:", Orders.objects.all())


        product = Product.objects.get(uid = self.p3.uid)
        logger.info(f"Product Apple has stock 10 \n User A needs: 5\n and User B needs: 8\n one request should be descarded with response of stock unavailable and stock should not be deducted to -ve if both user by pass\n Corrupt result will be -3\n Actual Product Stock remained: {product.stock}")
        

