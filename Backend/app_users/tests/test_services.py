import logging

from django.core import mail
from django.utils import timezone
from django.test import TestCase
from rest_framework.test import APIClient
from freezegun import freeze_time

from app_users.models import User, Profile, Location, EmailVerificationCode
from app_users.services import save_user_verification_code, handle_verification, match_user_verification_code, change_user_password, authenticate_user, check_email, add_profile_location, delete_profile_locations, update_profile_location
from base.tests.test_data import user1_data, profile1_data, location1_data, location2_data, email_vc_data
from base.helpers import pop_update_dict_data


logger = logging.getLogger("app_users")

# run test with
# python .\manage.py test <app-name>.<test-folder>.<test-file-name>
# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_services.UserServicesTest --debug-mode
class UserServicesTest(TestCase):
    
    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_services.UserServicesTest.test_save_user_verification_code --debug-mode
    def test_save_user_verification_code(self):
        logger.info("\n----------USER VERIFICATION SERVICE TEST----------")
        u = User.objects.create(**user1_data)
        
        with freeze_time("2026-08-06 1:00:00") as frozen_datetime:
            save_user_verification_code(u.email , 'abc123')
                    
            frozen_datetime.tick(delta=timezone.timedelta(minutes=10)) #go in future
            e_obj = EmailVerificationCode.objects.create(user = u, **email_vc_data)


        print(EmailVerificationCode.objects.all()[0].debug_str())
        
        self.assertEqual(e_obj.code, 'abc123')
        print('TEST PASSED SUCCESSFULLY!!')
        

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_services.UserServicesTest.test_handle_verification --debug-mode
    def test_handle_verification(self):
        logger.info("\n----------HANDLE VERIFICATION SERVICE TEST----------")
        
        u = User.objects.create(email = 'abc@example.com')
        EmailVerificationCode.objects.create(user = u, **email_vc_data)

        print('\n------test handle verification without verification code------')
        msg1, user_obj1 = handle_verification(u.email, '')
        print(msg1, user_obj1)
        print(f"got mail: {len(mail.outbox)}\nEmail contents\n subject: {mail.outbox[0].subject}\n body: {mail.outbox[0].body}")

        print('\n------test handle verification with verification code------')
        msg2, user_obj2 = handle_verification(u.email, 'abc123')
        print(f'returned data: {msg2}, {user_obj2}')
    
        self.assertEqual(msg1, 'Verification code is sent to the email, check your email!')
        self.assertEqual(msg2, 'Password is changed Successfully')
        print('TEST PASSED SUCCESSFULLY!!')

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_services.UserServicesTest.test_match_user_verification_code --debug-mode
    def test_match_user_verification_code(self):
        logger.info("\n----------MATCH USER VERIFICATION SERVICE TEST----------")
        u = User.objects.create(**user1_data)
        ev = EmailVerificationCode.objects.create(user = u, **email_vc_data )

        user = match_user_verification_code(u.email, ev.code)
        print(f'returned data: {user}')

        self.assertEqual(u.email, 'abc@example.com')
        print('TEST PASSED SUCCESSFULLY!!')

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_services.UserServicesTest.test_change_user_password --debug-mode    
    def test_change_user_password(self):
        logger.info("\n----------CHANGE USER PASSWORD SERVICE TEST----------")
        User.objects.create(**user1_data)
        u,d = change_user_password('abc@example.com', 'abc12345', 'abc67890')
        print(f'data {d}')

        self.assertEqual(u.email, 'abc@example.com') #type:ignore
        self.assertEqual(d['password'], 'abc67890')
        print('TEST PASSED SUCCESSFULLY!!')


    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_services.UserServicesTest.test_authenticate_user --debug-mode
    def test_authenticate_user(self):
        logger.info("\n----------AUTHENTICATE USER SERVICE TEST----------")
        u = User.objects.create(**user1_data)
        d = authenticate_user(u.email, 'abc12345')
        print(d)

        self.assertIsNotNone(d['refresh'])
        self.assertIsNotNone(d['access'])
        print('TEST PASSED SUCCESSFULLY!!')

        

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_services.UserServicesTest.test_check_email --debug-mode
    def test_check_email(self):
        logger.info("\n----------CHECK EMAIL SERVICE TEST----------")
        u = User.objects.create(**user1_data)
        obj = check_email(u.email)
        print(f'data: {obj}')

        self.assertIsNotNone(obj)
        print('TEST PASSED SUCCESSFULLY!!')

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_services.UserServicesTest.test_add_profile_location --debug-mode
    def test_add_profile_location(self):
        logger.info("\n----------ADD PROFILE LOCATION SERVICE TEST----------")
        u = User.objects.create(**user1_data)
        p = Profile.objects.create(user = u, **profile1_data)
        profile = add_profile_location(p, **location1_data)
        print(profile.debug_str())

        self.assertEqual(profile.user.email, 'abc@example.com')
        self.assertTrue(profile.location.filter(**location1_data).exists())
        print('TEST PASSED SUCCESSFULLY!!')
        
    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_services.UserServicesTest.test_delete_profile_locations --debug-mode
    def test_delete_profile_locations(self):
        logger.info("\n----------DELETE PROFILE LOCATION SERVICE TEST----------")
        u = User.objects.create(**user1_data)
        p = Profile.objects.create(user = u, **profile1_data)
        l1,l2 = Location.objects.create(**location1_data), Location.objects.create(**location2_data)
        print(Location.objects.all())
        p.location.add(l1,l2)
        
        profile = delete_profile_locations(p, [location1_data])
        print(profile.debug_str()) 

        self.assertEqual(profile.user.email, 'abc@example.com')
        self.assertFalse(profile.location.filter(**location1_data).exists())
        print('TEST PASSED SUCCESSFULLY!!')


    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_services.UserServicesTest.test_update_profile_location --debug-mode
    def test_update_profile_location(self):
        logger.info("\n----------UPDATE PROFILE LOCATION SERVICE TEST----------")
        u = User.objects.create(**user1_data)
        p = Profile.objects.create(user = u, **profile1_data)
        l1= Location.objects.create(**location1_data)
        p.location.add(l1)
        profile_location_update_data = {"old_location": location1_data, "new_location": location2_data}

        print(p.debug_str()) 
        profile = update_profile_location(p, **profile_location_update_data)
        print(profile.debug_str())

        self.assertEqual(profile.user.email, 'abc@example.com')
        self.assertTrue(profile.location.filter(**location2_data).exists())
        print('TEST PASSED SUCCESSFULLY!!')


        
