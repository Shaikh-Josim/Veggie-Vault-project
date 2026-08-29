
import copy
from typing import Any, cast

from django.test import TestCase

from app_users.serializers import UserSerializer, ProfileSerializer, LoginSerializer, EmailPasswordSerializer, ProfileUpdateLocationsSerializer
from app_users.models import User, Profile, Location
from base.tests.test_data import user1_data, location1_data, location2_data, profile1_data
from base.helpers import pop_update_dict_data 


# run this class test with command:
# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_models.UserSerializerTest --debug-mode
class UserSerializerTest(TestCase):
        
    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_serializers.UserSerializerTest.test_user_serializer --debug-mode
    def test_user_serializer(self):

        print("\n-----------USER SERIALIZER TEST-----------")

        user = User.objects.create(**user1_data)

        user_deserializer = UserSerializer(user)
        print("Deserialization|   \n serialized data:", user_deserializer.data)

        user_serializer = UserSerializer(instance = user, data = user1_data) #passing instance for already created user
        print("Serialization| valid data: ",user_serializer.is_valid(), "\n serialized data:", user_serializer.validated_data)
        print(user_serializer.errors)


        bad_user_data = pop_update_dict_data(copy.deepcopy(user1_data), overrides= {'email': 'abcexamplecom', 'password':'abc'})
        bad_user_serializer = UserSerializer(data = bad_user_data)

        self.assertTrue(user_serializer.is_valid())
        self.assertFalse(user_serializer.errors)
        self.assertFalse(bad_user_serializer.is_valid())
        self.assertTrue(bad_user_serializer.errors)
        print('TEST PASSED SUCCESSFULLY!!')

    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_serializers.UserSerializerTest.test_email_password_serializer --debug-mode
    def test_email_password_serializer(self):
            
        print("\n-----------EMAIL PASSWORD SERIALIZER TEST-----------")
            
        email_pass_data = pop_update_dict_data(copy.deepcopy(user1_data), overrides={"new_pass": "def12345"})
    
        email_pass_serializer = EmailPasswordSerializer(data = email_pass_data)
        print("Serialization| valid data: ",email_pass_serializer.is_valid(), "\n serialized data:", email_pass_serializer.validated_data)

        bad_email_password_data = pop_update_dict_data(copy.deepcopy(user1_data), overrides={"email": "abcexamplecom", "password": "abc1", "new_pass": "1"})
        bad_email_password_serializer = UserSerializer(data = bad_email_password_data)
        
        self.assertTrue(email_pass_serializer.is_valid())
        self.assertFalse(email_pass_serializer.errors)
        self.assertFalse(bad_email_password_serializer.is_valid())
        self.assertTrue(bad_email_password_serializer.errors)
        print('TEST PASSED SUCCESSFULLY!!')

    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_serializers.UserSerializerTest.test_login_serializer --debug-mode
    def test_login_serializer(self):
            
            print("\n-----------LOGIN SERIALIZER TEST-----------")
                
            login_serializer = LoginSerializer(data = user1_data)
            print("Serialization|  valid data: ",login_serializer.is_valid(), "\n serialized data:", login_serializer.validated_data)

            user= User.objects.create(**user1_data)
            login_deserializer = LoginSerializer(user)
            print("Deserialization| valid data: ", login_deserializer.data )
    
            bad_login_data = pop_update_dict_data(copy.deepcopy(user1_data), overrides={"email": "abcexamplecom", "password": "abc"})
            bad_login_serializer = LoginSerializer(data = bad_login_data)
    
            self.assertTrue(login_serializer.is_valid())
            self.assertFalse(login_serializer.errors)
            self.assertFalse(bad_login_serializer.is_valid())
            self.assertTrue(bad_login_serializer.errors)
            print('TEST PASSED SUCCESSFULLY!!')

    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_serializers.UserSerializerTest.test_profile_serializer --debug-mode
    def test_profile_serializer(self):
            
        print("\n-----------PROFILE SERIALIZER TEST-----------")
        profile_serializer = ProfileSerializer(data = profile1_data)
        print("Serialization|  valid data: ",profile_serializer.is_valid(), "\n serialized data:", profile_serializer.validated_data)
        print(profile_serializer.errors)

        user= User.objects.create(**user1_data)
        profile = Profile.objects.create(user = user, **profile1_data)
        location1, location2 = Location.objects.create(**location1_data), Location.objects.create(**location2_data)
        profile.location.add(location1,location2)
        
        profile_deserializer = ProfileSerializer(profile)
        print("Deserialization| valid data: ", profile_deserializer.data )

        bad_profile_data = pop_update_dict_data(copy.deepcopy(profile1_data), overrides={ "fname" : '123', "lname" : 'x3yz', "role" : Profile.Role.CONSUMER, "mobile_no" : '12d34567890', "user_Img" : None})
        bad_profile_serializer = ProfileSerializer(data = bad_profile_data)
        
        self.assertTrue(profile_serializer.is_valid())
        self.assertFalse(profile_serializer.errors)
        self.assertFalse(bad_profile_serializer.is_valid())
        self.assertTrue(bad_profile_serializer.errors)
        print('TEST PASSED SUCCESSFULLY!!')
    
        
    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_serializers.UserSerializerTest.test_profile_location_serializer --debug-mode
    def test_profile_location_serializer(self):
            
        print("\n-----------PROFILE LOCATION SERIALIZER TEST-----------")
        
        l_data = {
            "old_location": copy.deepcopy(location1_data),
            "new_location": copy.deepcopy(location2_data)
        }
        profile_location_serializer = ProfileUpdateLocationsSerializer(data = l_data)
        print("Serialization|  valid data: ",profile_location_serializer.is_valid(), "\n serialized data:", profile_location_serializer.validated_data)
        print(profile_location_serializer.errors)

        bad_l_data = {
            "old_location": pop_update_dict_data(copy.deepcopy(location1_data), overrides={"staddr": "=="}),
            "new_location": pop_update_dict_data(copy.deepcopy(location2_data), overrides={"city": "@"})
        }
        bad_profile_location_serializer = ProfileUpdateLocationsSerializer(data = bad_l_data)
        
        self.assertTrue(profile_location_serializer.is_valid())
        self.assertFalse(profile_location_serializer.errors)
        self.assertFalse(bad_profile_location_serializer.is_valid())
        self.assertTrue(bad_profile_location_serializer.errors)
        print('TEST PASSED SUCCESSFULLY!!')
        
    
 



    
