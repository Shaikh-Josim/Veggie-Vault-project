import json, logging
import copy
from typing import cast, Any
from decimal import Decimal

from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase
from django.urls import reverse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.test import APIClient

from app_users.models import User, Profile
from app_products.models import Product, Cart
from app_locations.models import Location
from base.tests.test_data import user1_data, user2_data, location1_data, location2_data, profile1_data, profile2_data, product1_data, product2_data, product3_data, product4_data, get_test_img, cart1_data, cart2_data, cart3_data, cart4_data
from base.helpers import pop_update_dict_data

logger = logging.getLogger('app_products')

#run tests with
##$env:PYTHONUNBUFFERED=1; python .\manage.py test app_products.tests.test_views.ProductsViewTest --debug-mode
class ProductsViewTest(TestCase):

    def setUp(self) -> None:
        self.setUser()
        self.setProducts()
        self.refresh_token, self.access_token = self.get_tokens()

    def get_tokens(self):
        url = reverse('login')
        response = cast(Response, self.client.post(url, user1_data))
        data = response.data or {}
        return data['refresh'], data['access'] 

    def setProducts(self):
        self.p1 = Product.objects.create(**pop_update_dict_data(copy.deepcopy(product1_data), overrides={'product_Img': get_test_img(product1_data['name'])}))
        self.p2 = Product.objects.create(**pop_update_dict_data(copy.deepcopy(product2_data), overrides={'product_Img': get_test_img(product1_data['name'])}))
        self.p3 = Product.objects.create(**pop_update_dict_data(copy.deepcopy(product3_data), overrides={'product_Img': get_test_img(product1_data['name'])}))
        self.p4 = Product.objects.create(**pop_update_dict_data(copy.deepcopy(product4_data), overrides={'product_Img': get_test_img(product1_data['name'])}))
        
    def setUser(self)   -> None:
        self.client = APIClient()
        self.user = User.objects.create(**user1_data)
        self.location1, self.location2 = Location.objects.create(**location1_data), Location.objects.create(**location2_data)
        self.profile = Profile.objects.create(user = self.user, **profile1_data)
        self.profile.location.add(self.location1, self.location2)

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_products.tests.test_views.ProductsViewTest.test_list_products --debug-mode
    def test_list_products(self):
        logger.info("\n---------- PRODUCT LIST VIEW TEST----------")

        print("\n========== LIST OF PRODUCTS ==========")
        url = reverse('list-products')
        response1 = cast(Response, self.client.get(url))
        print(f"response: {response1}, data: {json.dumps(response1.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder)}")

        print("\n========== SEARCH OF PRODUCTS NAME CONTAINING 'Tom' ==========")
        response2 = cast(Response, self.client.get("/products/?search=tomato"))
        print(f"response: {response2}, data: {json.dumps(response2.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder)}")

        print("\n========== FILTERING PRODUCTS WITH CATEGORY OF FRUITE AND PRICE LESS THAN 100 ==========")
        response3 = cast(Response, self.client.get("/products/?category=2&price__lt=100"))
        print(f"response: {response3}, data: {json.dumps(response3.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder)}")


        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response1.data), 4) #type:ignore
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response2.data), 1) #type:ignore
        self.assertEqual(response2.data[0]['product']['name'], 'Tomato')#type:ignore
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        self.assertEqual(response3.data[0]['product']['category']['value'], 2)#type:ignore
        self.assertTrue(Decimal(response3.data[0]['product']['price'])< 100)#type:ignore
        self.assertEqual(len(response3.data), 1) #type:ignore
        print('TEST PASSED SUCCESSFULLY!!')

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_products.tests.test_views.ProductsViewTest.test_retrieve_products --debug-mode
    def test_retrieve_products(self):
        logger.info("\n---------- RETRIEVE PRODUCT VIEW TEST----------")
        url = reverse("retrieve-product", args=["tomato"])
        response = cast(Response, self.client.get(url))

        print(f"response: {response}, data: {json.dumps(response.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder)}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['product']['name'], 'Tomato')#type:ignore
        print('TEST PASSED SUCCESSFULLY!!')

#run tests with
## $env:PYTHONUNBUFFERED=1; python .\manage.py test app_products.tests.test_views.CartViewTest --debug-mode
class CartViewTest(TestCase):
    
    def setUp(self) -> None:
        self.setUser()
        self.setProducts()
        self.setCart()
        self.refresh_token, self.access_token = self.get_tokens()
        self.add_product_data = pop_update_dict_data(copy.deepcopy(cart1_data), overrides={'profile_id':self.profile1.uid, 'product_id': self.p1.uid})
        self.update_product_data = pop_update_dict_data(copy.deepcopy(cart1_data), overrides={'quantity':10})

    def get_tokens(self):
        url = reverse('login')
        response = cast(Response, self.client.post(url, user1_data))
        data = response.data or {}
        return data['refresh'], data['access'] 
               
    def setUser(self)   -> None:
        self.client = APIClient()
        self.user1 = User.objects.create(**user1_data)
        self.user2 = User.objects.create(**user2_data)
        self.location1 = Location.objects.create(**location1_data)
        self.location2 = Location.objects.create(**location2_data)
        self.profile1 = Profile.objects.create(user=self.user1, **profile1_data)
        self.profile1.location.add(self.location1, self.location2)
        self.profile2 = Profile.objects.create(user=self.user2, **profile2_data)

    def setProducts(self):
        self.p1 = Product.objects.create(**pop_update_dict_data(copy.deepcopy(product1_data), overrides={'product_Img': get_test_img(product1_data['name'])}))
        self.p2 = Product.objects.create(**pop_update_dict_data(copy.deepcopy(product2_data), overrides={'product_Img': get_test_img(product1_data['name'])}))
        self.p3 = Product.objects.create(**pop_update_dict_data(copy.deepcopy(product3_data), overrides={'product_Img': get_test_img(product1_data['name'])}))
        self.p4 = Product.objects.create(**pop_update_dict_data(copy.deepcopy(product4_data), overrides={'product_Img': get_test_img(product1_data['name'])}))

    def setCart(self):
        #self.c1 = Cart.objects.create(profile=self.profile1, product=self.p1, **cart1_data)
        self.c2 = Cart.objects.create(profile=self.profile2, product=self.p2, **cart2_data)
        self.c3 = Cart.objects.create(profile=self.profile2, product=self.p3, **cart3_data)
        self.c4 = Cart.objects.create(profile=self.profile2, product=self.p4, **cart4_data)

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_products.tests.test_views.CartViewTest.test_cart --debug-mode
    def test_cart(self):
        logger.info("\n---------- CART VIEW TEST----------")
        url_get = reverse("cart")
        url_post = reverse("cart")

        print("\n========== POST CART TEST ==========")
        response2 = cast(Response, self.client.post(url_post, data= self.add_product_data, format = 'json', HTTP_AUTHORIZATION = 'Bearer '+ self.access_token))
        print(f"response: {response2}, data: {json.dumps(response2.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder)}")

        print("\n========== GET CART TEST ==========")
        response1 = cast(Response, self.client.get(url_get, HTTP_AUTHORIZATION = 'Bearer '+ self.access_token))
        print(f"response: {response1}, data: {json.dumps(response1.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder)}")

        print("\n========== PATCH CART TEST ==========")
        cart = Cart.objects.get(profile = self.profile1)
        url_up = reverse("cart-update",args=[cart.uid])
        response3 = cast(Response, self.client.patch(url_up, data= self.update_product_data, format = 'json', HTTP_AUTHORIZATION = 'Bearer '+ self.access_token))
        cart_up = Cart.objects.get(profile = self.profile1)
        print(f"response: {response3}, data: {json.dumps(response3.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder)}")

        print("\n========== DELETE CART TEST ==========")
        url_del = reverse("cart-update", args=[cart.uid])
        response4 = cast(Response, self.client.delete(url_del, data= self.update_product_data, format = 'json', HTTP_AUTHORIZATION = 'Bearer '+ self.access_token))
        print(f"response: {response4}, data: {json.dumps(response4.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder)}")

        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data[0]['product']['name'], 'Tomato') #type:ignore
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.data['message'], "Product added to cart successfully!") #type:ignore
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        self.assertEqual(cart_up.quantity, 10)
        self.assertEqual(response4.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Cart.objects.filter(profile = self.profile1).exists())        

        print('TEST PASSED SUCCESSFULLY!!')
        
