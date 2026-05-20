from django.test import TestCase
from app_users.serializers import UserSerializer, ProfileSerializer
from app_users.models import User, Profile
from typing import Any, cast

class UserSerializerTest(TestCase):
    
    def test_serialization(self):
        user = User.objects.create(email = "abc@domain.com", password = 'abc123456')
        serializer = UserSerializer(user)
        data = cast(dict[str, Any], serializer.data)
        print(serializer.data)
        self.assertEqual(data['email'], "abc@domain.com")
