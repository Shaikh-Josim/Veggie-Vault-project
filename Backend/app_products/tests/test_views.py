from typing import cast, Any
from django.test import TestCase
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import APIClient
from app_users.models import User, Profile
from app_products.models import Product
from testing_data.fill_dummy_data import fill_database

class UserViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_user(self):
        url = reverse('create-user')
        data = { 
                "email": "abc@domain.com", 
                "password": "abc123456" 
            }
        response = self.client.post(url, data)
        response = cast(Response, response)
        print(response.data)
        
class ProductViewTest(TestCase) :
    def setUp(self):
        self.client = APIClient()
        fill_database()

    def test_get_products(self):
        url = reverse('list-products') #all products
        url_with_category_filter = f"{url}?category=2" #product only fruits (2)
        url_with_price_filter = f"{url}?price__gte=0&price__lte=100" #custom price products
        #response = self.client.get(url) #gives all products
        response = self.client.get(url_with_price_filter) #gives products where categoty is fruits
        response = cast(Response, response)
        print(response.data)

class CartViewTest(TestCase) :
    def setUp(self):
        fill_database()
        self.client = APIClient()
        self.client.login(username = 'amit.verma@example.com', password = 'test1234')

    def test_get_cart(self):
        url = reverse('cart-list') #all products
        response = self.client.get(url)
        response = cast(Response, response)
        print("ngiiga")
        print(response.data)
