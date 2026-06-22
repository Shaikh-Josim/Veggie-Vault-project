from typing import Any, cast, Dict
import json
import hmac , hashlib
from unittest.mock import patch

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.crypto import get_random_string
from django.test import TestCase
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework.test import APIClient


from app_users.models import User, Profile
from app_products.models import Product, Cart
from app_locations.models import Location
from app_orders.models import Orders, OrderedItem, Payment
from VeggieVault.settings import RAZORPAY_TEST_API_KEY, RAZORPAY_TEST_KEY_SECRET

from django.test import TestCase, Client  # <-- Add Client here


import logging

logger = logging.getLogger('app_orders')



# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_cases.OrderOperationsTest --debug-mode

class OrderOperationsTest(TestCase):

    def setUp(self) -> None:
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

        self.razorpay_create_order_data = {
            "consumer": self.profile.uid,
            "amount": 500,
        }

        self.update_product_data = {
            "quantity" : "10"
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
        
        self.razorpay_after_payment_data = self.get_razorpay_mock_payment_data()
        self.access_token = str(self.atest_login().get('access'))

               
    def setUser(self)   -> None:
        self.client = APIClient()
        user = User.objects.create(email = "jhon@domain.com", password = "jhon1234")
        user.save()
        user2 = User.objects.create(email = "brian@domain.com", password = "brian1234")
        user2.save()
        location1 = Location( staddr="123 Baker Street", city="Springfield", state="California", hno="42", landmark="Near Central Park", is_homeaddress = True )
        location2 = Location( staddr="12 main Street", city="Autumnfield", state="California", hno="2", landmark="Near Dolphin Park", is_homeaddress = False )
        location1.save()
        location2.save()
        self.profile = Profile( user=user, fname="John", lname="Doe", role=Profile.Role.CONSUMER, mobile_no="9876543210", user_Img=None)
        self.profile.save()
        self.profile.location.add(location1,location2)

        self.profile2 = Profile( user=user2, fname="Brian", lname="Doe", role=Profile.Role.CONSUMER, mobile_no="98576543210", user_Img=None)
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
            stock=50,
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
        self.c1 = Cart.objects.create(profile=self.profile2,product=self.p1,quantity=2)
        self.c2 = Cart.objects.create(profile=self.profile2,product=self.p2,quantity=5)
        self.c4 = Cart.objects.create(profile=self.profile2,product=self.p4,quantity=1)

    def setOrder(self):
        print(Orders.objects.all())
        self.o1 = Orders.objects.create(
            consumer=self.profile,
            amount = self.c3.total_price,
            razorpay_order_id = 'order_'+ get_random_string(14)
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
            secret = cast(str,RAZORPAY_TEST_KEY_SECRET)
            order_obj = Orders.objects.filter(consumer = self.profile).first()
            if order_obj is not None:
                order_id =  order_obj.razorpay_order_id
            payment_id = "pay_" + get_random_string(14)
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
        

    
    def atest_login(self) -> Dict[str, Any]:
        print("entering into login test")
        url = reverse('login')
        response = self.client.post(url, self.login_user_data[0])
        response = cast(Response, response)
        print(response)
        print(response.data)
        return cast(Dict[str, Any],response.data)

    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_cases.OrderOperationsTest.test_razorpay_create_order --debug-mode
    def test_razorpay_create_order(self, mock_client = None):
        logger.info("entering into razorpay create order test...")
        url_post = reverse("create-order")

        response = self.client.post(url_post, data= self.razorpay_create_order_data,  content_type='application/json', HTTP_AUTHORIZATION = 'Bearer '+ self.access_token)

        logger.info(f"response data: {json.dumps(response.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder)}") #type: ignore
        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(response.json()['order_id'], None)
        self.assertEqual(response.json()['merchant_key'], 'rzp_test_SzX0yI8GDc7TL1')
    
    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_cases.OrderOperationsTest.test_razorpay_verify_payment --debug-mode
    @patch('app_orders.views.client') 
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

        # Send the successful payment data to our view using the user's login token
        response = self.client.post(
            url, 
            data=self.razorpay_after_payment_data, 
            format='json', 
            HTTP_AUTHORIZATION='Bearer ' + self.access_token
        )
        response = cast(Response, response)
        
        # Log the response in the terminal so we can see what the view sent back
        logger.info(f"Response data:{json.dumps(response.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder)}")
        
        # Make sure the view returns a 202 status (Accepted) and the right success message
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json()['msg'], 'order payment is done successfully')
        