import json, logging
import uuid
from typing import cast
from unittest.mock import patch

from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase
from django.urls import reverse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.test import APIClient

from app_users.models import User, Profile
from app_products.models import Product, Cart
from app_locations.models import Location
from app_orders.models import OrderedItem, Orders
from base.tests.test_data import user1_data, location1_data, profile1_data, product1_data, cart1_data, order1_data, order4_data, ordereditem1_data, get_payment_signature, get_webhook_signature
from base.helpers import pop_update_dict_data

logger = logging.getLogger('app_orders')

#run tests with 
##$env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_views.OrderViewTest --debug-mode
class OrderViewTest(TestCase):

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

    dummy_payment_fetch_data = {
        "id": "pay_Test123456789",
        "entity": "payment",
        "amount": 50000,          
        "currency": "INR",
        "status": "captured",     # Can be 'created', 'authorized', 'captured', or 'failed'
        "order_id": "order_4",
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

    dummy_payment_refund_data = {
        "id": "rfnd_R7GTH3oiaXMUQE", # Refund ID (`rfnd_...`)           
        "entity": "refund",
        "amount": 50000, # Refunded amount (paise)          
        "base_amount": 50000,
        "currency": "INR",
        "payment_id": "pay_Test123456789", # Original payment ID              
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

    webhook_response_data = {
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
                "id": 'pay_Test123456789',
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
                "id": 'order_4',
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
    
    payment_verify_data = {
        "razorpay_order_id": "",
        "razorpay_payment_id": "",
        "razorpay_signature": ""
    }

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create(**user1_data)
        self.create_order_idempotency_key = str(uuid.uuid4())
        self.refresh_token, self.access_token = self.get_tokens()

    def get_tokens(self):
        url = reverse('login')
        response = cast(Response, self.client.post(url, user1_data))
        data = response.data or {}
        return data['refresh'], data['access'] 

    


    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_views.OrderViewTest.test_list_ordereditems --debug-mode
    def test_list_ordereditems(self):
        logger.info("\n---------- ORDERED ITEMS LIST VIEW TEST----------")

        print("\n========== LIST OF PRODUCTS ==========")
        url = reverse('list-ordered-items') 
        response1 = cast(Response, self.client.get(url, HTTP_AUTHORIZATION = 'Bearer '+ self.access_token))
        print(f"response: {response1}, data: {json.dumps(response1.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder)}")

        
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        print('TEST PASSED SUCCESSFULLY!!')

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_views.OrderViewTest.test_create_order --debug-mode
    def test_create_order(self):
        logger.info("\n---------- CREATE ORDER VIEW TEST----------")
        location = Location.objects.create(**location1_data)
        profile = Profile.objects.create(user = self.user, **profile1_data)
        profile.location.add(location)
        product = Product.objects.create(**product1_data) 
        cart = Cart.objects.create(profile = profile, product = product, **cart1_data)

        url = reverse('create-order') 
        with patch("app_orders.services.razorpay_client") as mock_client:
            mock_client.order.create.return_value = self.dummy_razorpay_order
            response1 = cast(Response, self.client.post(url, data= order1_data , content_type='application/json', HTTP_AUTHORIZATION = 'Bearer '+ self.access_token, HTTP_X_IDEMPOTENCY_KEY= self.create_order_idempotency_key))
        
        print(f"response: {response1}, data: {json.dumps(response1.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder)}")

        
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response1.data['message'], 'order created successfully') #type: ignore
        print('TEST PASSED SUCCESSFULLY!!')





    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_views.OrderViewTest.test_payment_verify --debug-mode
    def test_payment_verify(self):
        logger.info("\n---------- PAYMENT VERIFY VIEW TEST----------")
        location = Location.objects.create(**location1_data)
        profile = Profile.objects.create(user = self.user, **profile1_data)
        profile.location.add(location)
        product = Product.objects.create(**product1_data) 
        cart = Cart.objects.create(profile = profile, product = product, **cart1_data)
        order = Orders.objects.create(consumer = profile, **order4_data)
        ordereditem = OrderedItem.objects.create(order = order, ordered_item = product, **ordereditem1_data)

        self.payment_verify_data = pop_update_dict_data(self.payment_verify_data,
            overrides= {
                "razorpay_order_id": order.razorpay_order_id,
                "razorpay_payment_id": self.dummy_payment_fetch_data['id'],
                "razorpay_signature": get_payment_signature(order.razorpay_order_id, self.dummy_payment_fetch_data['id'])
            }
        )

        url = reverse('verify-payment') 
        with patch("app_orders.views.razorpay_client") as mock_client:
            mock_client.payment.fetch.return_value = self.dummy_payment_fetch_data

            response1 = cast(Response, self.client.post(url, data= self.payment_verify_data , content_type='application/json', HTTP_AUTHORIZATION = 'Bearer '+ self.access_token, HTTP_X_IDEMPOTENCY_KEY= self.create_order_idempotency_key))
        
        print(f"response: {response1}, data: {json.dumps(response1.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder)}")
        
        self.assertEqual(response1.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response1.data['message'], 'order payment is done successfully') #type: ignore
        print('TEST PASSED SUCCESSFULLY!!')
    
    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_views.OrderViewTest.test_razorpay_webhook --debug-mode
    def test_razorpay_webhook(self):
        logger.info("\n---------- RAZORPAY WEBHOOK VIEW TEST----------")
        location = Location.objects.create(**location1_data)
        profile = Profile.objects.create(user = self.user, **profile1_data)
        profile.location.add(location)
        product = Product.objects.create(**product1_data) 
        cart = Cart.objects.create(profile = profile, product = product, **cart1_data)
        order = Orders.objects.create(consumer = profile, **order4_data)
        ordereditem = OrderedItem.objects.create(order = order, ordered_item = product, **ordereditem1_data)

        url = reverse("razorpay-webhook")
        with patch("app_orders.views.razorpay_client") as mock_client:
            mock_client.payment.fetch.return_value = self.dummy_payment_fetch_data

            response1 = cast(Response, self.client.post(
                    url, 
                    data=self.webhook_response_data, 
                    format='json', 
                    HTTP_AUTHORIZATION='Bearer ' + self.access_token,
                    HTTP_X_IDEMPOTENCY_KEY= self.create_order_idempotency_key,
                    HTTP_X_RAZORPAY_SIGNATURE= get_webhook_signature(webhook_data= self.webhook_response_data), 
                ))
        
        print(f"response: {response1}, data: {json.dumps(response1.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder)}")
        
        self.assertEqual(response1.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response1.data['message'], 'order payment is done successfully') #type: ignore
        print('TEST PASSED SUCCESSFULLY!!')

