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
#$env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_cases --debug-mode
class UserOperationsTest(TestCase):

    def setUp(self) -> None:
        self.setUser()
        

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
            "mobile_no" :"0007000700",
        }

        self.profile_location_update_data = {
            "old_location":{
                'staddr': '123 Baker Street', 'city': 'Springfield',    'state': 'California', 'hno': '42', 'landmark': 'Near Central Park', 'is_homeaddress': True
            }, 
            "new_location":{
                'staddr': '123 Baker Street', 'city': 'Redfield',    'state': 'California', 'hno': '42', 'landmark': 'Near Central Park', 'is_homeaddress': True
            },
        }

        self.profile_location_create_data = {            
            'staddr': '34 circle road', 'city': 'Autumnfield', 'state': 'California', 'hno': '2', 'landmark': 'Near Dolphin Park', 'is_homeaddress': True
        }

        self.profile_location_delete_data = [
            {
                'staddr': '34 circle road', 'city': 'Autumnfield', 'state': 'California', 'hno': '2', 'landmark': 'Near Dolphin Park', 'is_homeaddress': True
            },
            {
                'staddr': '123 Baker Street', 'city': 'Redfield',    'state': 'California', 'hno': '42', 'landmark': 'Near Central Park', 'is_homeaddress': True
            }
        ]
            
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
        


    def atest_create_users(self):
        print("entering into create user test")
        url = reverse('create-user')
        response = self.client.post(url, self.create_user_data)
        response = cast(Response, response)
        print(response)
        print(response.data)

    def atest_list_users(self):
        print("entering into list test")
        url = reverse('list-profiles')
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

    def atest_profile_update(self):
        print("entering profile updation test")
        url = reverse('profile')
        self.atest_login()
        access_token = input('access_token:\t')

        response_get = self.client.get(url, HTTP_AUTHORIZATION = 'Bearer '+ access_token)
        response_put = self.client.put(url, data = self.profile_update_data, format = 'json', HTTP_AUTHORIZATION="Bearer " + access_token)
        response_get = cast(Response, response_get)
        response_put = cast(Response, response_put)
        print(response_put)
        print("response-get: ", response_get.data)
        print("response-put: ", response_put.data)

    def test_profile_location_crud(self):
        print("entering profile locations crud  test")
        url_update = reverse('profile-location-update')
        url_create = reverse("profile-location-create")
        url_get = reverse("profile-locations")
        url_delete = reverse('profile-location-delete')
        self.atest_login()
        access_token = input('access_token:\t')

        response_get = self.client.get(url_get, HTTP_AUTHORIZATION = 'Bearer '+ access_token)
        response_get = cast(Response, response_get)
        print("response-get: ", response_get.data)

        response_put = self.client.put(url_update, data = self.profile_location_update_data, format = 'json' ,HTTP_AUTHORIZATION="Bearer " + access_token)
        response_put = cast(Response, response_put)
        print("response-put: ", response_put.data)

        response_create = self.client.post(url_create, data = self.profile_location_create_data, format = 'json' ,HTTP_AUTHORIZATION="Bearer " + access_token)
        response_create = cast(Response, response_create)
        print("response-create: ", response_create.data)

        response_delete = self.client.delete(url_delete, data = self.profile_location_delete_data, content_type='application/json' ,HTTP_AUTHORIZATION="Bearer " + access_token)
        response_delete = cast(Response, response_delete)
        print("response-delete: ", response_delete.data)
    

    
