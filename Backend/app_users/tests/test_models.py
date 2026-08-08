


from django.test import TestCase
from django.core.exceptions import ValidationError
from app_users.models import User, Profile, EmailVerificationCode
from app_locations.models import Location
from app_products.models import Product, Cart
from testing_data.fill_dummy_data import fill_database

import logging


logger = logging.getLogger('app_users')

# run class test using
# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_models.UserModelTest --debug-mode
class UserModelTest(TestCase):

    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_models.UserModelTest.test_user_obj --debug-mode
    def test_user_obj(self):
        logger.info('Testing user obj..')
        user = User.objects.create(email = 'abc@example.com', password = 'abc1234') 
        print(f'CREATED USER INFO:{user.__str__()}')

        bad_user = User.objects.create(email = 'abc@examplecom', password = 'abc1234') 

        self.assertEqual('abc@example.com', user.email, msg= 'user email is not matching')
        self.assertTrue(user.password.startswith('pbkdf2_'), msg= 'password is not hashed')
        self.assertRaises(ValidationError, bad_user.full_clean)

        logger.info('error test succeed')

# run this class test with command:
# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_models.ProfileModelTest --debug-mode
class ProfileModelTest(TestCase):

    user_data = {"email": "abc@example.com", "password": "abc1234"}
    location_data = [
    { "staddr": "123 Baker Street", "city": "Springfield", "state": "California", "hno": "42", "landmark": "Near Central Park", "is_homeaddress": True }, 
    {"staddr":"12 main Street","city":"Autumnfield", "state":"California", "hno":"2", "landmark":"Near Dolphin Park", "is_homeaddress": True } ]
    profile_data = { "fname" : 'abc', "lname" : 'xyz', "role" : Profile.Role.CONSUMER, "mobile_no" : '1234567890', "user_Img" : 'userimg',} 


    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_models.ProfileModelTest.test_profile_obj --debug-mode
    def test_profile_obj(self):
        logger.info('Testing profile obj..')

        user = User.objects.create( **self.user_data )

        location1 , location2 = Location.objects.create(**self.location_data[0] ), Location.objects.create(**self.location_data[1])
        
        profile = Profile.objects.create( user = user, **self.profile_data )

        profile.location.add(location1, location2)
        print("CREATED PROFILE INFO:",profile.__debug_str__())

        bad_user = User.objects.create( email = 'acbe@example.com', password = '12323')
        bad_profile = Profile.objects.create(
                    user = bad_user,
                    fname = 'abc12',
                    lname = 'xyz3',
                    role = Profile.Role.CONSUMER,
                    mobile_no = '1234567890a',
                    user_Img = 'userimg',
                )

        self.assertEqual('abc xyz', profile.fname+' '+profile.lname, msg= 'profile full name is not matching')
        self.assertRaises(ValidationError, bad_profile.full_clean)

# run this class test with command:
# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_models.EmailVerificationCodeModelTest --debug-mode
class  EmailVerificationCodeModelTest(TestCase):
    import random, string
    import datetime
    from django.utils import timezone
    
    user_data = {"email": "abc@example.com", "password": "abc1234"}
    email_vc_data = {"code": ''.join(random.choices(string.ascii_letters + string.digits, k=6)), "expires_at": timezone.now()+datetime.timedelta(minutes= 2)}


    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_models.EmailVerificationCodeModelTest.test_profile_obj --debug-mode
    def test_profile_obj(self):
        logger.info('Testing email verification code obj..')

        user = User.objects.create( **self.user_data )

        email_vc_obj = EmailVerificationCode.objects.create(user = user, **self.email_vc_data)
        print("CREATED EMAILVERIFICATIONCODE INFO:",email_vc_obj.__debug_str__())

        bad_user = User.objects.create( email = 'acbe@example.com', password = '12323')
        bad_email_vc = EmailVerificationCode.objects.create(
                    user = bad_user,
                    code = '-w9e99e',
                    expires_at = self.timezone.now() + self.datetime.timedelta(minutes= 2)
                )

        self.assertIsNotNone(email_vc_obj)
        self.assertRaises(ValidationError, bad_email_vc.full_clean)


class CartModelTest(TestCase):
    def setUp(self):
        fill_database()
        self.profile = Profile.objects.get(user__email = 'priya.sharma@example.com')
        self.profile2 = Profile.objects.get(user__email = 'neha.patel@example.com')
        self.p1 = Product.objects.get(name__contains = 'tomato')
        self.p2 = Product.objects.get(name__contains = 'potato')
        self.p3 = Product.objects.get(name__contains = 'carrot')
    
    def test_cart_objects(self):
        Cart.objects.create(profile= self.profile, product= self.p1, quantity=5)
        Cart.objects.create(profile= self.profile, product= self.p2, quantity=10)
        Cart.objects.create(profile= self.profile, product= self.p3, quantity=15)
        Cart.objects.create(profile= self.profile2, product= self.p3, quantity=16)

        p = Cart.objects.filter(profile = self.profile)
        print(p)

        p2 = Cart.objects.filter(profile__user__email = 'priya.sharma@example.com')

        for product in p:
            print(product.product.name, product.quantity, product.product.price, product.total_price)
        """products = self.profile.cart.all()
        for p in products:
            print(p.name, p.price)"""
        

