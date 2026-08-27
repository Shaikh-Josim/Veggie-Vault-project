import logging

from django.core import mail
from django.test import TestCase

from base.services import prepare_dynamic_email_contents, send_email



logger = logging.getLogger("base")

# run test with
# python .\manage.py test <app-name>.<test-folder>.<test-file-name>
# $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_services.ServicesTest --debug-mode
class ServicesTest(TestCase):
    vc = "code12"


    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_services.ServicesTest.test_prepare_dynamic_email_contents --debug-mode    
    def test_prepare_dynamic_email_contents(self):
        logger.info("\n----------DYNAMIC EMAIL CONTENTS SERVICE TEST----------")

        email_contents = prepare_dynamic_email_contents(topic = 'new_password', v_code = self.vc)

        print(email_contents)
        self.assertEqual(email_contents['message'], 'Verify yourself by using this verification code to make your new password. your verification code is\ncode12')

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_services.ServicesTest.test_send_email --debug-mode    
    def test_send_email(self):
        logger.info("\n----------SEND EMAIL SERVICE TEST----------")

        send_email(topic= 'new_password', email='jhon@domain.com', v_code= '1242cd')

        subject = mail.outbox[0].subject
        message = mail.outbox[0].body
        print(f"got mail: {len(mail.outbox)}\nEmail contents\n subject: {subject}\n body: {message}")

        self.assertEqual(subject, 'making new password')
        self.assertEqual(message, 'Verify yourself by using this verification code to make your new password. your verification code is\n1242cd')
        

