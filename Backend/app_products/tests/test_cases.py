from django.test import TestCase
from django.core import mail
from app_users.models import User, Profile
from app_locations.models import Location
from app_users.serializers import UserSerializer, ProfileSerializer
from typing import Any, cast
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import APIClient


class UserOperationsTest(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        user = User.objects.create(email = "jhon@domain.com", password = "jhon1234")
        user.save()
        location = Location( staddr="123 Baker Street", city="Springfield", state="California", hno="42", landmark="Near Central Park" )
        location.save()
        profile = Profile( user=user, fname="John", lname="Doe", location=location, role=Profile.Role.CONSUMER, mobile_no="9876543210", user_Img=None)
        profile.save()

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
        rft = input()
        self.refresh_token_data["refresh"] = rft
        response = self.client.post(url, self.refresh_token_data)
        response = cast(Response, response)
        print(response)
        print(response.data)

    def test_change_password(self):
        print("entering into change password test")
        url = reverse('change-password')
        response = self.client.post(url, self.change_password_data)
        response = cast(Response, response)
        print(response)
        print(response.data)

    def atest_forget_password(self):
        print("entering forget password test")
        url = reverse('forget-password')
        response = self.client.post(url, self.forget_password_data)
        response = cast(Response, response)
        print(response)
        print(len(mail.outbox), 1)
        print(mail.outbox[0].body)
        v_code = input()
        self.forget_password_data["v_code"] = v_code
        response = self.client.post(url, self.forget_password_data)
        response = cast(Response, response)
        print(response.data)

    
