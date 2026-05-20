from django.test import TestCase
from app_users.models import User, Profile
from app_locations.models import Location
from app_products.models import Product, Cart
from testing_data.fill_dummy_data import fill_database

#run test using
#python manage.py test app_users.tests.test_models

class UserModelTest(TestCase):

    def test_str_representation(self):
        user = User.objects.create(email ="abc@example.com", password ='a1234')
        print(user.email)
        self.assertEqual(str(user), "user-email:abc@example.com")

    def test_user_obj_values(self):
        user = User.objects.create(email ="abc@example.com", password ='a1234')
        print(user.email)
        print(user.password)
        print()
        #self.assertEqual(str(user), "user-email:abc@example.com")

class ProfileModelTest(TestCase):

    def test_str_representation(self):
        user = User.objects.create(email ="abc@example.com", password ='a1234')
        location = Location.objects.create(staddr = 'heien era', city = 'tokyo', state = 'nigga')
        profile = Profile.objects.create(user = user, location = location)
        print(str(profile))
        print()
        self.assertEqual(str(profile), "user name:  \n user-email: abc@example.com")

    def test_user_obj_values(self):
        user = User.objects.create(email ="abc@example.com", password ='a1234')
        location = Location.objects.create(staddr = 'heien era', city = 'tokyo', state = 'nigga')
        print(str(location))
        profile = Profile.objects.create(
        user = user,
        fname = 'thukuna',
        lname = 'ryomen',
        location = location,
        #role = '1',
        mobile_no = '1234567890')
        p = Profile.objects.filter(mobile_no = 1234567890)
        print(p.values())
        print()
        #self.assertEqual(str(user), "user-email:abc@example.com")

    def test_profile_validation(self):
        user = User.objects.create(email ="abc@example.com", password ='a1234')
        p = Profile.objects.create(user = user, mobile_no = 'abc')
        p.full_clean()

