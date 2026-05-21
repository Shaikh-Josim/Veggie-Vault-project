from django.test import TestCase
from django.core import mail
from app_users.models import User, Profile
from app_locations.models import Location
from app_users.serializers import UserSerializer, ProfileSerializer
from typing import Any, cast
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import APIClient

#run test with
#python .\manage.py test <app-name>.<test-folder>.<test-file-name>
#python .\manage.py test app_users.tests.test_cases
class UserOperationsTest(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        user = User.objects.create(email = "jhon@domain.com", password = "jhon1234")
        user.save()
        location = Location( staddr="123 Baker Street", city="Springfield", state="California", hno="42", landmark="Near Central Park", is_homeaddress = True )
        location.save()
        profile = Profile( user=user, fname="John", lname="Doe", role=Profile.Role.CONSUMER, mobile_no="9876543210", user_Img=None)
        profile.save()
        profile.location.add(location)
        

        self.create_user_data = {
            "email" : "jhon23@domain.com",
            "password" : "jhon12323"
            }
        
        self.login_user_data = {
            "email" : "jhon@domain.com",
            "password" : "jhon1234"
            }
        
        self.refresh_token_data = {
            "refresh" : ""
            }
        
        self.forget_password_data = {
            "email" : "jhon@domain.com",
            "v_code" : "",
            "password" : "12345678"
        }

        self.change_password_data = {
            "email" : "jhon@domain.com",
            "password" : "jhon1234",
            "new_pass" : "nigga787"
        }

        self.profile_update_data = {
            "fname" :"jhon2",
            "lname" :"",
            "location" :"",
            "role" :"",
            "mobile_no" :"0007000700",
            "user_Img" :"",
    }

    def atest_create_users(self):
        print("entering into create user test")
        url = reverse('create-user')
        response = self.client.post(url, self.create_user_data)
        response = cast(Response, response)
        print(response)
        print(response.data)

    def atest_list_users(self):
        print("entering into list test")
        url = reverse('list-users')
        response = self.client.get(url)
        response = cast(Response, response)
        print(response)
        print(response.data)

    def atest_login(self):
        print("entering into login test")
        url = reverse('login')
        response = self.client.post(url, self.login_user_data)
        response = cast(Response, response)
        print(response)
        print(response.data)

    def atest_refersh_token(self):
        print("entering into refresh toke test")
        url = reverse('refresh-token')
        self.atest_login()
        rft = input("refresh token:\t")
        self.refresh_token_data["refresh"] = rft
        response = self.client.post(url, self.refresh_token_data)
        response = cast(Response, response)
        print(response)
        print(response.data)

    def atest_change_password(self):
        print("entering into change password test")
        url = reverse('change-password')
        self.atest_login()
        access_token = input('access_token:\t')

        response = self.client.post(url, data=self.change_password_data, HTTP_AUTHORIZATION="Bearer " + access_token)
        response = cast(Response, response)
        print(response)
        print(response.data)

    def atest_forget_password(self):
        print("entering forget password test")
        url = reverse('forget-password')
        print(self.forget_password_data)
        response = self.client.post(url, data=self.forget_password_data)
        response = cast(Response, response)
        print(response, "\n", response.data)
        print(len(mail.outbox), 1)
        print(mail.outbox[0].subject,mail.outbox[0].body)
        v_code = input()
        self.forget_password_data["v_code"] = v_code
        response = self.client.post(url, self.forget_password_data)
        response = cast(Response, response)
        print(response.data)

    def test_profile_update(self):
        print("entering profile updation test")
        url = reverse('profile')
        self.atest_login()
        access_token = input('access_token:\t')

        response_get = self.client.get(url, HTTP_AUTHORIZATION = 'Bearer '+ access_token)
        response = self.client.put(url,data=self.profile_update_data,HTTP_AUTHORIZATION="Bearer " + access_token)
        #response = self.client.post(url, self.forget_password_data)
        response = cast(Response, response)
        response_get = cast(Response, response_get)
        print(response)
        print("response-get: ", response_get.data)
        print("response-put: ", response.data)

    
