from typing import cast, Any
from django.test import TestCase
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import APIClient
from app_users.models import User, Profile

class UserViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_user(self):
        url = reverse('create-user')
        data = { 
                "email": "abc@domain.com", 
                "password": "abc123456" 
            }
        response = self.client.post(url, data)
        response = cast(Response, response)
        print(response.data)
        
        
