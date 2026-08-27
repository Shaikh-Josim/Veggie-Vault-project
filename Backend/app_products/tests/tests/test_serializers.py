from django.test import TestCase
from app_users.serializers import UserSerializer, ProfileSerializer, LoginSerializer, LocationSerializer, EmailPasswordSerializer, ProfileUpdateLocationsSerializer
from app_users.models import User, Product, Profile, EmailVerificationCode, Location
from typing import Any, cast


# run this class test with command:
# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_models.UserSerializerTest --debug-mode
class UserSerializerTest(TestCase):
    user_data = {"email": "abc@example.com", "password": "abc12345"}
    location_data = [
    { "staddr": "123 Baker Street", "city": "Springfield", "state": "California", "hno": "42", "landmark": "Near Central Park", "is_homeaddress": True }, 
    {"staddr":"12 main Street","city":"Autumnfield", "state":"California", "hno":"2", "landmark":"Near Dolphin Park", "is_homeaddress": True } ]
    profile_data = { "fname" : 'abc', "lname" : 'xyz', "role" : Profile.Role.CONSUMER, "mobile_no" : '1234567890', "user_Img" : None,} 
        
    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_serializers.UserSerializerTest.test_user_serializer --debug-mode
    def test_user_serializer(self):

        print("\n-----------USER SERIALIZER TEST-----------")

        user = User.objects.create(**self.user_data)

        user_deserializer = UserSerializer(user)
        print("Deserialization|   \n serialized data:", user_deserializer.data)

        user_serializer = UserSerializer(instance = user, data = self.user_data) #passing instance for already created user
        print("Serialization| valid data: ",user_serializer.is_valid(), "\n serialized data:", user_serializer.validated_data)
        print(user_serializer.errors)


        bad_user_data = {"email": "abcexamplecom", "password": "abc12345"}
        bad_user_serializer = UserSerializer(data = bad_user_data)

        self.assertTrue(user_serializer.is_valid())
        self.assertFalse(user_serializer.errors)
        self.assertFalse(bad_user_serializer.is_valid())
        self.assertTrue(bad_user_serializer.errors)

    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_serializers.UserSerializerTest.test_email_password_serializer --debug-mode
    def test_email_password_serializer(self):
            
            print("\n-----------EMAIL PASSWORD SERIALIZER TEST-----------")
            email_pass_data = {"email": "abc@domain.com", "password" : 'abc12343', "new_pass": "def12345"}
    
            email_pass_serializer = EmailPasswordSerializer(data = email_pass_data)
            print("Serialization| valid data: ",email_pass_serializer.is_valid(), "\n serialized data:", email_pass_serializer.validated_data)
    
            bad_email_password_data = {"email": "abcexamplecom", "password": "abc1", "new_pass": "1"}
            bad_email_password_serializer = UserSerializer(data = bad_email_password_data)
    
            self.assertTrue(email_pass_serializer.is_valid())
            self.assertFalse(email_pass_serializer.errors)
            self.assertFalse(bad_email_password_serializer.is_valid())
            self.assertTrue(bad_email_password_serializer.errors)

    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_serializers.UserSerializerTest.test_login_serializer --debug-mode
    def test_login_serializer(self):
            
            print("\n-----------LOGIN SERIALIZER TEST-----------")
                
            login_serializer = LoginSerializer(data = self.user_data)
            print("Serialization|  valid data: ",login_serializer.is_valid(), "\n serialized data:", login_serializer.validated_data)

            user= User.objects.create(**self.user_data)

            login_deserializer = LoginSerializer(user)
            print("Deserialization| valid data: ", login_deserializer.data )
    
            bad_login_data = {"email": "abcexamplecom", "password": "abc12345"}
            bad_login_serializer = LoginSerializer(data = bad_login_data)
    
            self.assertTrue(login_serializer.is_valid())
            self.assertFalse(login_serializer.errors)
            self.assertFalse(bad_login_serializer.is_valid())
            self.assertTrue(bad_login_serializer.errors)

    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_serializers.UserSerializerTest.test_profile_serializer --debug-mode
    def test_profile_serializer(self):
            
        print("\n-----------PROFILE SERIALIZER TEST-----------")
        profile_serializer = ProfileSerializer(data = self.profile_data)
        print("Serialization|  valid data: ",profile_serializer.is_valid(), "\n serialized data:", profile_serializer.validated_data)
        print(profile_serializer.errors)

        user= User.objects.create(**self.user_data)
        profile = Profile.objects.create(user = user, **self.profile_data)
        location1, location2 = Location.objects.create(**self.location_data[0]), Location.objects.create(**self.location_data[1])
        profile.location.add(location1,location2)
        profile = Profile.objects.get(user = user)
        
        profile_deserializer = ProfileSerializer(profile)
        print("Deserialization| valid data: ", profile_deserializer.data )

        bad_profile_data = { "fname" : '123', "lname" : 'x3yz', "role" : Profile.Role.CONSUMER, "mobile_no" : '12d34567890', "user_Img" : None,} 
        bad_profile_serializer = ProfileSerializer(data = bad_profile_data)
        
        self.assertTrue(profile_serializer.is_valid())
        self.assertFalse(profile_serializer.errors)
        self.assertFalse(bad_profile_serializer.is_valid())
        self.assertTrue(bad_profile_serializer.errors)
    
        
    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_serializers.UserSerializerTest.test_profile_location_serializer --debug-mode
    def test_profile_location_serializer(self):
            
        print("\n-----------PROFILE LOCATION SERIALIZER TEST-----------")
        self.location_data[0]["city"] = "3-=-3"
        l_data = {
             "old_location": self.location_data[0],
             "new_location": self.location_data[1]
        }
        profile_location_serializer = ProfileUpdateLocationsSerializer(data = l_data)
        print("Serialization|  valid data: ",profile_location_serializer.is_valid(), "\n serialized data:", profile_location_serializer.validated_data)
        print(profile_location_serializer.errors)

        user= User.objects.create(**self.user_data)
        profile = Profile.objects.create(user = user, **self.profile_data)
        location1, location2 = Location.objects.create(**self.location_data[0]), Location.objects.create(**self.location_data[1])
        profile.location.add(location1,location2)
        profile = Profile.objects.get(user = user)
        
        self.assertTrue(profile_location_serializer.is_valid())
        self.assertFalse(profile_location_serializer.errors)
        
    




    
