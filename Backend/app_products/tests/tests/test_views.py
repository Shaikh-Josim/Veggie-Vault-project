import logging
import re
from typing import cast

from django.core import mail
from django.urls import reverse
from django.test import TestCase
from rest_framework.response import Response
import rest_framework.status as status
from rest_framework.test import APIClient

from app_users.models import User, Profile, Location



logger = logging.getLogger("app_users")
# run test with
# python .\manage.py test <app-name>.<test-folder>.<test-file-name>
# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_views.UserViewsTest --debug-mode
class UserViewsTest(TestCase):


    create_user_data = {
        "email" : "jhon23@domain.com",
        "password" : "jhon12323"
    
    }

    login_user_data = {
        "email" : "jhon@domain.com",
        "password" : "jhon1234"
    }

    refresh_token_data = {
        "refresh": ""
    }   

    change_password_data = {
        "email" : "jhon@domain.com",
        "password" : "jhon1234",
        "new_pass" : "jhon1787"
    }

    forget_password_data = {
        "email" : "jhon@domain.com",
        "v_code" : "",
        "password" : "12345678"
    }

    profile_update_data = {
        "fname" :"jhon2",
        "mobile_no" :"0007000700",
    }

    profile_location_update_data = {
        "old_location":{
            'staddr': '123 Baker Street', 'city': 'Springfield',    'state': 'California', 'hno': '42', 'landmark': 'Near Central Park', 'is_homeaddress': True
        }, 
        "new_location":{
            'staddr': '123 Baker Street', 'city': 'Redfield',    'state': 'California', 'hno': '42', 'landmark': 'Near Central Park', 'is_homeaddress': True
        },
    }
    
    profile_location_create_data = {            
        'staddr': '34 circle road', 'city': 'Autumnfield', 'state': 'California', 'hno': '2', 'landmark': 'Near Dolphin Park', 'is_homeaddress': True
    }
    
    profile_location_delete_data = [
        {
            'staddr': '34 circle road', 'city': 'Autumnfield', 'state': 'California', 'hno': '2', 'landmark': 'Near Dolphin Park', 'is_homeaddress': True
        },
        {
            'staddr': '123 Baker Street', 'city': 'Redfield',    'state': 'California', 'hno': '42', 'landmark': 'Near Central Park', 'is_homeaddress': True
        }
    ]

    def setUp(self):
        self.client = APIClient()
        self.setObjects()
        self.refresh_token, self.access_token = self.get_tokens()

    def get_tokens(self):
        url = reverse('login')
        response = cast(Response, self.client.post(url, self.login_user_data))
        data = response.data or {}
        self.refresh_token_data["refresh"] = data['refresh']
        return data['refresh'], data['access'] 
        
    def setObjects(self):
        user = User.objects.create(email = "jhon@domain.com", password = "jhon1234")
        user.save()

        location1 = Location( staddr="123 Baker Street", city="Springfield", state="California", hno="42", landmark="Near Central Park", is_homeaddress = True )
        location2 = Location( staddr="12 main Street", city="Autumnfield", state="California", hno="2", landmark="Near Dolphin Park", is_homeaddress = False )
        location1.save()
        location2.save()

        profile = Profile( user=user, fname="John", lname="Doe", role=Profile.Role.CONSUMER, mobile_no="9876543210", user_Img=None)
        profile.save()
        profile.location.add(location1,location2)

    def test_get_user(self):
        url = reverse('create-user')
        data = { 
                "email": "abc@domain.com", 
                "password": "abc123456" 
            }
        response = self.client.post(url, data)
        response = cast(Response, response)
        print(response.data)

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_views.UserViewsTest.test_create_users --debug-mode
    def test_create_users(self):
        logger.info("\n----------CREATE USER VIEW TEST----------")
        url = reverse('create-user')
        response = cast(Response, self.client.post(url, self.create_user_data))
        data = response.data or {}
        print(f"response: {response}, data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data["message"], "New user created successfully")    
        
    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_views.UserViewsTest.test_login --debug-mode
    def test_login(self):
        logger.info("\n----------LOGIN VIEW TEST----------")
        url = reverse('login')
        response = cast(Response, self.client.post(url, self.login_user_data))
        data = response.data or {}
        print(f"response: {response}, data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(data.__contains__("access"))
        self.assertTrue(data.__contains__("refresh"))

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_views.UserViewsTest.test_refersh_token_view --debug-mode
    def test_refersh_token_view(self):
        logger.info("\n----------REFRESH TOKEN VIEW TEST----------")
        url = reverse('refresh-token')
        response = cast(Response, self.client.post(url, self.refresh_token_data))
        data = response.data or {}
        print(f"response: {response}, data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(data.__contains__("access"))

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_views.UserViewsTest.test_list_user_view --debug-mode
    def test_list_user_view(self):
        logger.info("\n----------LIST USER VIEW TEST----------")
        url = reverse('list-profiles')
        response = cast(Response, self.client.get(url))
        data = response.data or {}
        print(f"response: {response}, data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(data[0].__contains__('email'))

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_views.UserViewsTest.test_change_password --debug-mode
    def test_change_password(self):
        logger.info("\n----------CHANGE PASSWORD VIEW TEST----------")
        print("entering into change password test")
        url = reverse('change-password')

        response = cast(Response, self.client.post(url, data=self.change_password_data, HTTP_AUTHORIZATION="Bearer " + self.access_token))
        data  = response.data or {}
        print(f"response: {response}, data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["message"], 'Password Changed Successfully!')
        

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_views.UserViewsTest.test_forget_password --debug-mode
    def test_forget_password(self):
        logger.info("\n----------FORGET PASSWORD VIEW TEST----------")
        url = reverse('forget-password')

        response = cast(Response, self.client.post(url, data=self.forget_password_data, HTTP_AUTHORIZATION="Bearer " + self.access_token))
        data  = response.data or {}
        print(f"response: {response}, data: {response.data}")
        print(f"got mail: {len(mail.outbox)}\nEmail contents\n subject: {mail.outbox[0].subject}\n body: {mail.outbox[0].body}")
        email = str( mail.outbox[0].body)
        
        matches = re.findall(r"\bverification code is\s+(\w+)", email, re.IGNORECASE)
        self.forget_password_data["v_code"] = matches[0]
        response = cast(Response, self.client.post(url, data=self.forget_password_data, HTTP_AUTHORIZATION="Bearer " + self.access_token))
        data  = response.data or {}
        print(f"response: {response}, data:  {response.data}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["message"], 'Password is changed Successfully')

    
    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_views.UserViewsTest.test_profile_update --debug-mode
    def test_profile_update(self):
        logger.info("\n----------PROFILE UPDATE VIEW TEST----------")
        url = reverse('profile')


        response_get = cast(Response, self.client.get(url, HTTP_AUTHORIZATION="Bearer " + self.access_token))
        get_data  = response_get.data or {}
        print(f"response-get: {response_get}, data: {response_get.data}\n")

        response_put = cast(Response, self.client.put(url, data = self.profile_update_data, format = 'json', HTTP_AUTHORIZATION="Bearer " + self.access_token))
        put_data  = response_put.data or {}
        print(f"response-put: {response_put}, data: {response_put.data}")

        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        self.assertTrue(get_data.__contains__('email'))
        self.assertEqual(response_put.status_code, status.HTTP_200_OK)
        self.assertEqual(put_data["message"], 'Profile Updated Successfully!')

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_views.UserViewsTest.test_profile_location_crud --debug-mode
    def test_profile_location_crud(self):
        logger.info("\n----------PROFILE LOCATION CRUD VIEW TEST----------")
        url_update = reverse('profile-location-update'); url_create = reverse("profile-location-create")
        url_get = reverse("profile-locations"); url_delete = reverse('profile-location-delete')

        response_get = cast(Response, self.client.get(url_get, HTTP_AUTHORIZATION = 'Bearer '+ self.access_token))
        get_data  = response_get.data or {}
        print(f"response-get: {response_get}, data: {response_get.data}\n")

        response_put = cast(Response, self.client.put(url_update, data = self.profile_location_update_data, format = 'json' ,HTTP_AUTHORIZATION="Bearer " + self.access_token))
        put_data  = response_put.data or {}
        print(f"response-put: {response_put}, data: {response_put.data}\n")
        
        response_create = cast(Response, self.client.post(url_create, data = self.profile_location_create_data, format = 'json' ,HTTP_AUTHORIZATION="Bearer " + self.access_token))
        create_data  = response_create.data or {}
        print(f"response-create: {response_create}, data: {response_create.data}\n")

        response_delete = cast(Response, self.client.delete(url_delete, data = self.profile_location_delete_data, content_type='application/json' ,HTTP_AUTHORIZATION="Bearer " + self.access_token))
        delete_data  = response_delete.data or {}
        print(f"response-delete: {response_delete}, data: {response_delete.data}\n")

        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        self.assertEqual(response_create.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_put.status_code, status.HTTP_200_OK)
        self.assertEqual(response_delete.status_code, status.HTTP_200_OK)
        self.assertTrue(get_data[0].__contains__('state'))
        self.assertEqual(put_data['message'], 'Location Updated Successfully!')
        self.assertEqual(create_data['message'], 'Location added successfully!')
        self.assertEqual(delete_data['message'], 'Locations deleted Successfully!')
