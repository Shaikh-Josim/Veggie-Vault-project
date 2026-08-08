import logging
from typing import cast, Any
from unittest.mock import patch

from celery.exceptions import Retry
from django.test import TestCase

from app_users.services import generate_verification_code
from base.tasks import send_email_task

logger = logging.getLogger('app_users')


# run test with
# python .\manage.py test <app-name>.<test-folder>.<test-file-name>
# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_services.UserServicesTest --debug-mode
class TasksTest(TestCase):
    vc = generate_verification_code()

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_celery_tasks.TasksTest.test_send_email_task --debug-mode
    def test_send_email_task(self):
        logger.info("\n----------SEND EMAIL CELERY TASK TEST----------")

        result = cast(Any, send_email_task.delay)(subject="new_password", email="jhon@domain.com", v_code=self.vc)

        with patch("base.tasks.core_services.send_email") as mock_send_email:
            result = cast(Any, send_email_task.delay)( subject="new_password", email="jhon@domain.com", v_code=self.vc)

        with patch("base.tasks.core_services.send_email", side_effect=Exception("Email service failed")):

            with self.assertRaises(Retry): 
                cast(Any, send_email_task.delay)(subject="new_password", email='jhon@domain.com', v_code=self.vc)

        mock_send_email.assert_called_once_with( subject="new_password", email= 'jhon@domain.com', v_code=self.vc)
        self.assertEqual(result.get(), "Email sent successfully to jhon@domain.com")

        # Verify side effects in DB
        #self.order.refresh_from_db()
        #self.assertEqual(self.order.status, "processed")
