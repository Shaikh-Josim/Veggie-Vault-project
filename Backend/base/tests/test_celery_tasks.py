import logging
from typing import cast, Any
from unittest.mock import patch

from celery.exceptions import Retry
from django.test import TestCase

from app_users.services import generate_verification_code
from base.tasks import send_email_task, create_index_task

logger = logging.getLogger('base')


# run test with
# python .\manage.py test <app-name>.<test-folder>.<test-file-name>
# $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_celery_tasks.TasksTest --debug-mode
class TasksTest(TestCase):
    vc = generate_verification_code()

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_celery_tasks.TasksTest.test_send_email_task --debug-mode
    def test_send_email_task(self):
        logger.info("\n----------SEND EMAIL CELERY TASK TEST----------")

        with patch("base.tasks.core_services.send_email") as mock_send_email:
            result = cast(Any, send_email_task.delay)( topic="new_password", email="jhon@domain.com", v_code=self.vc)

        with patch("base.tasks.core_services.send_email", side_effect=Exception("Email service failed")):

            with self.assertRaises(Retry): 
                cast(Any, send_email_task.delay)(topic="new_password", email='jhon@domain.com', v_code=self.vc)

        mock_send_email.assert_called_once_with( topic="new_password", email= 'jhon@domain.com', v_code=self.vc)
        self.assertEqual(result.get(), "Email sent successfully to jhon@domain.com")

        logger.info("TEST PASSED SUCCESSFULLY!!!")


    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_celery_tasks.TasksTest.test_index_log_file_task --debug-mode
    def test_index_log_file_task(self):
        from pathlib import Path
        from base.log_reader import LogFile

        log_dir = Path("try_programs")
        files = list(log_dir.glob("*.jsonl"))
        for file in files:
            LogFile.objects.create(path = file.as_posix())
        log_file  = LogFile.objects.get(path = r"try_programs/django_errors.log.jsonl")


        logger.info("\n----------CREATE INDEX CELERY TASK TEST----------")
        log_file_id = log_file.uid
        indexing_attributes = ["request_id", "user_id"]

        with patch("base.tasks.LogReader.create_index_in_db") as mock_create_index:
            result = cast(Any, create_index_task.delay)( log_file_id, indexing_attributes)

        mock_create_index.assert_called_once_with( log_file_id, indexing_attributes)
        self.assertEqual(result.get(), f"Index created on {indexing_attributes}")

        logger.info("TEST PASSED SUCCESSFULLY!!!")


