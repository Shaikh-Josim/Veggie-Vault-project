from typing import Any, cast
import json

from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase
from django.core import mail
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import APIClient

from app_users.models import User, Profile
from app_products.models import Product, Cart
from app_locations.models import Location


#run tests with
##$env:PYTHONUNBUFFERED=1; python .\manage.py test app_products.tests.test_cases --debug-mode

class ProductsOperationsTest(TestCase):

    def setUp(self) -> None:
        self.setUser()
        self.setProducts()
        
        self.login_user_data = {
            "email" : "jhon@domain.com",
            "password" : "jhon1234"
            }

    def setProducts(self):
        p1 = Product.objects.create(
            name="Tomato",
            category=Product.ProductCategory.VEGETABLE,
            discription = "A juicy, red fruit often treated as a vegetable, tomatoes are rich in vitamin C and lycopene. They are versatile in cooking, used fresh in salads, sauces, and soups,",
            price=20,
            stock=100,
            product_Img = "images/products/tomato.jpg"
        )
        p2 = Product.objects.create(
            name="Potato",
            category=Product.ProductCategory.VEGETABLE,
            discription = "A starchy tuber native to South America, potatoes are one of the world’s staple foods. They come in many varieties and are used boiled, mashed, fried, or baked",
            price=30,
            stock=200,
            product_Img = "images/products/potato.jpg"
        )
        p3 = Product.objects.create(
            name="Apple",
            category=Product.ProductCategory.FRUIT,
            discription = "A crisp, sweet fruit from the rose family, apples are one of the most widely cultivated fruits worldwide. They are eaten fresh, baked, or juiced, and are rich in fiber and vitamin C.",
            price=100,
            stock=50,
            product_Img = "images/products/Apple.png"
        )
        p3 = Product.objects.create(
            name="Banana",
            category=Product.ProductCategory.FRUIT,
            discription = "A long, curved tropical fruit with soft, sweet flesh and a yellow peel when ripe. Bananas are high in potassium and energy, making them a popular snack and smoothie ingredient.",
            price=60,
            stock=120,
            product_Img = "images/products/Banana.png"
        )
        

    def setUser(self)   -> None:
        self.client = APIClient()
        user = User.objects.create(email = "jhon@domain.com", password = "jhon1234")
        user.save()
        location1 = Location( staddr="123 Baker Street", city="Springfield", state="California", hno="42", landmark="Near Central Park", is_homeaddress = True )
        location2 = Location( staddr="12 main Street", city="Autumnfield", state="California", hno="2", landmark="Near Dolphin Park", is_homeaddress = False )
        location1.save()
        location2.save()
        profile = Profile( user=user, fname="John", lname="Doe", role=Profile.Role.CONSUMER, mobile_no="9876543210", user_Img=None)
        profile.save()
        profile.location.add(location1,location2)
 
    def atest_login(self):
        print("entering into login test")
        url = reverse('login')
        response = self.client.post(url, self.login_user_data)
        response = cast(Response, response)
        print(response)
        print(response.data)

    def test_list_products(self):
        print("entering into list products test")
        url = reverse('list-products')
        response = self.client.get(url)
        response = cast(Response, response)
        print(response)
        print(response.data)

    def test_retrieve_products(self):
        print("entering into retrieve product test")
        url = reverse("retrieve-product", args=["tomato"])

        response = self.client.get(url)
        response = cast(Response, response)
        print(response)
        print(response.data)

#$env:PYTHONUNBUFFERED=1; python .\manage.py test app_products.tests.test_cases.CartOperationsTest --debug-mode
class CartOperationsTest(TestCase):

    def setUp(self) -> None:
        self.setUser()
        self.setProducts()
        self.setCart()
        
        self.login_user_data = [
            {
            "email" : "jhon@domain.com",
            "password" : "jhon1234"},
            {
            "email" : "brian@domain.com",
            "password" : "brian1234"},
        ]

        self.add_product_data = {
            "profile_id": str(self.profile.uid),
            "product_id" : str(self.p1.uid), #"Tomato"
            "quantity" : "5"
        }

        self.update_product_data = {
            "quantity" : "10"
        }

               
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
        
        self.c1 = Cart.objects.create(profile=self.profile2,product=self.p1,quantity=2)
        self.c2 = Cart.objects.create(profile=self.profile2,product=self.p2,quantity=5)
        self.c3 = Cart.objects.create(profile=self.profile,product=self.p3,quantity=5)
        self.c4 = Cart.objects.create(profile=self.profile2,product=self.p4,quantity=1)

    
    def atest_login(self):
        print("entering into login test")
        url = reverse('login')
        response = self.client.post(url, self.login_user_data[0])
        response = cast(Response, response)
        print(response)
        print(response.data)

    def atest_list_products(self):
        print("entering into list products test")
        url = reverse('list-products')
        response = self.client.get(url)
        response = cast(Response, response)
        print(response)
        print(response.data)

    def atest_retrieve_products(self):
        print("entering into retrieve product test")
        url = reverse("retrieve-product", args=["tomato"])

        response = self.client.get(url)
        response = cast(Response, response)
        print(response)
        print(response.data)   

    def test_cart(self):
        print("entering into cart test")
        url_get = reverse("cart")
        url_post = reverse("cart")
        url_up = reverse("cart",args=[self.c3.uid])
        url_del = reverse("cart")

        self.atest_login()
        access_token = input('access_token:\t')

        response_get = self.client.get(url_get, HTTP_AUTHORIZATION = 'Bearer '+ access_token)
        response_get = cast(Response, response_get)
        print(response_get)
        print(json.dumps(response_get.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder))

        response_post = self.client.post(url_post, data= self.add_product_data, format = 'json', HTTP_AUTHORIZATION = 'Bearer '+ access_token)
        response_post = cast(Response, response_post)
        print(response_post)
        print(json.dumps(response_post.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder))

        response_up = self.client.patch(url_up, data= self.update_product_data, format = 'json', HTTP_AUTHORIZATION = 'Bearer '+ access_token)
        response_up = cast(Response, response_up)
        print(response_up)
        print(json.dumps(response_up.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder))

        response_get = self.client.get(url_get, HTTP_AUTHORIZATION = 'Bearer '+ access_token)
        response_get = cast(Response, response_get)
        print(response_get)
        print(json.dumps(response_get.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder))

        response_delete = self.client.delete(url_up, data= self.update_product_data, format = 'json', HTTP_AUTHORIZATION = 'Bearer '+ access_token)
        response_delete = cast(Response, response_delete)
        print(response_delete)
        print(json.dumps(response_delete.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder))

        response_get = self.client.get(url_get, HTTP_AUTHORIZATION = 'Bearer '+ access_token)
        response_get = cast(Response, response_get)
        print(response_get)
        print(json.dumps(response_get.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder))
    
