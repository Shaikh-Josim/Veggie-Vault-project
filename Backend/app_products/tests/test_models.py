import logging
import copy
import shutil
import tempfile

from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError

from app_users.models import User, Profile
from app_locations.models import Location
from app_products.models import Product, Cart
from base.tests.test_data import user1_data, location1_data, profile1_data, product1_data, get_test_img
from base.helpers import pop_update_dict_data

logger = logging.getLogger("app_products")

# run test with
# python .\manage.py test <app-name>.<test-folder>.<test-file-name>
# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_products.tests.test_models.ProductModelTest --debug-mode
class ProductModelTest(TestCase):
    
    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_products.tests.test_models.ProductModelTest.test_str_representation --debug-mode    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_media = tempfile.mkdtemp()
        cls.media_override = override_settings(
            MEDIA_ROOT=cls.test_media
        )
        cls.media_override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.media_override.disable()
        shutil.rmtree(cls.test_media, ignore_errors=True)

        super().tearDownClass()

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_products.tests.test_models.ProductModelTest.test_str_representation --debug-mode    
    def test_str_representation(self):
        logger.info("\n---------- STR REPRESENTATION PRODUCT MODEL TEST----------")
        product_data = pop_update_dict_data(copy.deepcopy(product1_data), overrides={'product_Img': get_test_img(product1_data['name'])})
        product = Product.objects.create(**product_data)
        print(product.debug_str())
        
        self.assertEqual(str(product), "Tomato")
        print(' TEST PASSED SUCCESSFULLY!!')        

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_products.tests.test_models.ProductModelTest.test_product_obj_values --debug-mode    
    def test_product_obj_values(self):
        logger.info("\n---------- PRODUCT OBJ VALUES MODEL TEST----------")
        product = Product.objects.create(**pop_update_dict_data(copy.deepcopy(product1_data), overrides={'product_Img': get_test_img(product1_data['name'])}))

        bad_product = pop_update_dict_data(copy.deepcopy(product1_data), overrides={'product_Img': get_test_img(product1_data['name']), 'name':1234})
        bp = Product.objects.create(**bad_product)
        
        self.assertEqual(product.slug, "tomato")
        self.assertEqual(product.price, 20)
        self.assertEqual(product.stock, 100)
        self.assertEqual(product.get_category_display(), 'Vegetable')#type:ignore
        self.assertRaises(ValidationError, bp.full_clean)
        print(' TEST PASSED SUCCESSFULLY!!')        

# run test with
# python .\manage.py test <app-name>.<test-folder>.<test-file-name>
# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_products.tests.test_models.CartModelTest --debug-mode
class CartModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_media = tempfile.mkdtemp()
        cls.media_override = override_settings(
            MEDIA_ROOT=cls.test_media
        )
        cls.media_override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.media_override.disable()
        shutil.rmtree(cls.test_media, ignore_errors=True)

        super().tearDownClass()

    # run this func test with 
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_products.tests.test_models.CartModelTest.test_str_representation --debug-mode    
    def test_str_representation(self):
        

        logger.info("\n---------- STR REPRESENTATION CART MODEL TEST ----------")
        user = User.objects.create(**user1_data)
        location = Location.objects.create(**location1_data)
        profile = Profile.objects.create(user = user, **profile1_data)
        profile.location.add(location)
        product = Product.objects.create(**pop_update_dict_data(copy.deepcopy(product1_data), overrides={'product_Img': get_test_img(product1_data['name'])}))
        cart = Cart.objects.create(profile= profile, product= product, quantity = 5)

        print(str(cart))
        print(cart.debug_str()) 

        self.assertEqual(str(cart), "user-email: abc@example.com product: Tomato")
        print(' TEST PASSED SUCCESSFULLY!!')        

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_products.tests.test_models.CartModelTest.test_cart_obj_values --debug-mode    
    def test_cart_obj_values(self):
        logger.info("\n---------- CART OBJ VALUES MODEL TEST----------")
        
        user = User.objects.create(**user1_data)
        location = Location.objects.create(**location1_data)
        profile = Profile.objects.create(user = user, **profile1_data)
        profile.location.add(location)
        product = Product.objects.create(**pop_update_dict_data(copy.deepcopy(product1_data), overrides={'product_Img': get_test_img(product1_data['name'])}))
        cart = Cart.objects.create(profile= profile, product= product, quantity = 5)

        
        self.assertEqual(cart.quantity, 5)
        self.assertEqual(cart.total_price, 100)
        self.assertTrue(cart.is_stock)
        self.assertIsNotNone(cart.product)
        self.assertIsNotNone(cart.profile)
        with self.assertRaises(ValueError):
            Cart.objects.create(profile= profile, product= product, quantity = 'ADB')
        print(' TEST PASSED SUCCESSFULLY!!')
        


