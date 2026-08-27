import logging
from unittest.mock import Mock, patch

from django.utils import timezone
from django.test import TestCase, RequestFactory
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework import serializers

from base.helpers import validated_dict, schedule_task, require_idempotency_key

logger = logging.getLogger("base")




# run test with
# python .\manage.py test <app-name>.<test-folder>.<test-file-name>
# $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_helpers.HelpersTest --debug-mode
class HelpersTest(TestCase):
    class TestSerializer(serializers.Serializer):
        email = serializers.EmailField()
    factory = RequestFactory()


    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_helpers.HelpersTest.test_validated_dict --debug-mode    
    def test_validated_dict(self):
        logger.info("\n---------- VALIDATED DICT HELPER TEST ----------")

        data = validated_dict(self.TestSerializer(data={"email": "jhon@domain.com"}))
        print('data: ',data)

        with self.assertRaises(serializers.ValidationError):
                validated_dict(self.TestSerializer(data={"email": "jhondomain.com"}))

        self.assertEqual(data["email"], "jhon@domain.com")

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_helpers.HelpersTest.test_schedule_task --debug-mode    
    def test_schedule_task(self):
        logger.info("\n---------- SCHEDULE TASK HELPER TEST ----------")
        task = Mock()

        before = timezone.now()
        schedule_task(function=task, email="john@domain.com", minutes=15)
        after = timezone.now()

        task.apply_async.assert_called_once()

        kwargs = task.apply_async.call_args.kwargs
        print('kwargs: ', kwargs)

        self.assertEqual(
            kwargs["kwargs"],
            {"email": "john@domain.com"},
        )

        eta = task.apply_async.call_args.kwargs["eta"]

        self.assertGreaterEqual(eta, before + timezone.timedelta(minutes=15))
        self.assertLessEqual(eta, after + timezone.timedelta(minutes=15))
        self.assertIsNotNone(kwargs["eta"])

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_helpers.HelpersTest.test_require_idempotency_key --debug-mode    
    def test_require_idempotency_key(self):
        logger.info("\n---------- REQUIRE IDEMPOTENCY KEY HELPER TEST ----------")

        print("============= TEST MISSING IDEMPOTENCY KEY ==============")

        mock_view1 = Mock(return_value=Response({"success": True}))
        decorated_view = require_idempotency_key()(mock_view1)
        request1 = self.factory.post("/test/")
        response1 = decorated_view(request1)
        print(f"response: {response1}, response-data: {response1.data}")

        print("============= TEST NEW IDEMPOTENCY KEY ALLOWS REQUEST =============")
        mock_view2 = Mock(return_value=Response({"success": True}))
        decorated_view = require_idempotency_key()(mock_view2)
        mock_cache2 = Mock()
        with patch("base.helpers.cache", mock_cache2):
            mock_cache2.add.return_value = True
            request2 = self.factory.post("/test/", HTTP_X_IDEMPOTENCY_KEY="abc-123",)
            request2.user = Mock(is_authenticated=True, uid="user-123")
            response2 = decorated_view(request2)
            print(f"response: {response2}, response-data: {response2.data}")

        print("============= TEST EXISTING IDEMPOTENCY KEY RETURNS 409 =============")
        mock_view3 = Mock(return_value=Response({"success": True}))
        decorated_view = require_idempotency_key()(mock_view3)
        mock_cache3 = Mock()
        with patch("base.helpers.cache", mock_cache3):
            mock_cache3.add.return_value = False
            request3 = self.factory.post("/test/", HTTP_X_IDEMPOTENCY_KEY="abc-123",)
            request3.user = Mock( is_authenticated=True, uid="user-123",)
            response3 = decorated_view(request3)
            print(f"response: {response3}response-data: {response3.data}")

        print("============= TEST LOCK IS DELETED AFTER VIEW =============")
        mock_view4 = Mock(return_value=Response({"success": True}))
        decorated_view = require_idempotency_key()(mock_view4)
        mock_cache4 = Mock()
        with patch("base.helpers.cache", mock_cache4):
            mock_cache4.add.return_value = True
            request4 = self.factory.post("/test/", HTTP_X_IDEMPOTENCY_KEY="abc-123",)
            request4.user = Mock( is_authenticated=True,uid="user-123",)
            response4 = decorated_view(request4)
            print(f"response: {response4}, response-data: {response4.data}")

        print("============= TEST LOCK IS DELETED WHEN VIEW RAISES =============")
        mock_view5 = Mock(side_effect=ValueError("Something failed"))
        decorated_view = require_idempotency_key()(mock_view5)
        mock_cache5 = Mock()
        with patch("base.helpers.cache", mock_cache5):
            mock_cache5.add.return_value = True
            request5 = self.factory.post("/test/", HTTP_X_IDEMPOTENCY_KEY="abc-123",)
            request5.user = Mock(is_authenticated=True, uid="user-123",)
            with self.assertRaises(ValueError):
                decorated_view(request5)

        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST,)
        mock_view1.assert_not_called()
        self.assertEqual(response2.status_code,status.HTTP_200_OK,)

        mock_view2.assert_called_once()
        mock_cache2.add.assert_called_once_with("idempotency_user-123_abc-123", "processing", timeout=10)
        mock_cache2.delete.assert_called_once_with("idempotency_user-123_abc-123")

        self.assertEqual(response3.status_code, status.HTTP_409_CONFLICT,)
        mock_view3.assert_not_called()
        mock_cache3.add.assert_called_once_with("idempotency_user-123_abc-123", "processing", timeout=10,)
        mock_cache3.delete.assert_not_called()

        self.assertEqual(response4.status_code, status.HTTP_200_OK,)
        mock_view4.assert_called_once()
        mock_cache4.delete.assert_called_once_with("idempotency_user-123_abc-123")
        
        mock_view5.assert_called_once()
        mock_cache5.delete.assert_called_once_with("idempotency_user-123_abc-123")
