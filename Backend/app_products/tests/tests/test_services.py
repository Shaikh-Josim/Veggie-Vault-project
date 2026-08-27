import logging
import re
import datetime
from typing import cast

from django.core import mail
from django.utils import timezone
from django.urls import reverse
from django.test import TestCase
from rest_framework.response import Response
import rest_framework.status as status
from rest_framework.test import APIClient
from freezegun import freeze_time

from app_users.models import User, Profile, Location, EmailVerificationCode
from app_users.services import generate_verification_code, save_user_verification_code, handle_verification, match_user_verification_code, change_user_password, authenticate_user, check_email, add_profile_location, delete_profile_locations, update_profile_location



logger = logging.getLogger("app_users")

# run test with
# python .\manage.py test <app-name>.<test-folder>.<test-file-name>
# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_services.UserServicesTest --debug-mode
class UserServicesTest(TestCase):
    l = { "staddr":"14 main circle road", "city":"Snowfield", "state":"California", "hno":"4", "landmark":"Near Forest Park", "is_homeaddress":True}

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
            'staddr': '123 Baker Street', 'city': 'Springfield', 'state': 'California', 'hno': '42', 'landmark': 'Near Central Park', 'is_homeaddress': True
        }
    ]

    def setUp(self):
        self.client = APIClient()
        self.setObjects()
        

        
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


    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_services.UserServicesTest.test_save_user_verification_code --debug-mode
    def test_save_user_verification_code(self):
        logger.info("\n----------USER VERIFICATION SERVICE TEST----------")
        u = User.objects.get(email = 'jhon@domain.com')
        vc = generate_verification_code()
        
        with freeze_time("2026-08-06 1:00:00") as frozen_datetime:
            save_user_verification_code(u.email , vc)
                    
            frozen_datetime.tick(delta=timezone.timedelta(minutes=10)) #go in future
            e_obj = EmailVerificationCode.objects.get(user__email = 'jhon@domain.com')


        print(EmailVerificationCode.objects.all()[0].debug_str())
        
        self.assertEqual(vc, e_obj.code)
        

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_services.UserServicesTest.test_handle_verification --debug-mode
    def test_handle_verification(self):
        logger.info("\n----------HANDLE VERIFICATION SERVICE TEST----------")
        
        u = User.objects.get(email = 'jhon@domain.com')
        vc = generate_verification_code()
        
        EmailVerificationCode.objects.create(user = u, code = vc, expires_at = timezone.now() + timezone.timedelta(minutes=10) )

        print('\n------test handle verification without verification code------')
        msg1, user_obj1 = handle_verification(u.email, '')
        print(msg1, user_obj1)
        print(f"got mail: {len(mail.outbox)}\nEmail contents\n subject: {mail.outbox[0].subject}\n body: {mail.outbox[0].body}")

        print('\n------test handle verification with verification code------')
        msg2, user_obj2 = handle_verification(u.email, vc)
        print(f'returned data: {msg2}, {user_obj2}')
    
        self.assertEqual(msg1, 'Verification code is sent to the email, check your email!')
        self.assertEqual(msg2, 'Password is changed Successfully')

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_services.UserServicesTest.test_match_user_verification_code --debug-mode
    def test_match_user_verification_code(self):
        logger.info("\n----------MATCH USER VERIFICATION SERVICE TEST----------")
        u = User.objects.get(email = 'jhon@domain.com')
        ev = EmailVerificationCode.objects.create(user = u, code = generate_verification_code(), expires_at = timezone.now() + timezone.timedelta(minutes=10) )

        user = match_user_verification_code(u.email, ev.code)
        print(f'returned data: {user}')

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_services.UserServicesTest.test_change_user_password --debug-mode    
    def test_change_user_password(self):
        logger.info("\n----------CHANGE USER PASSWORD SERVICE TEST----------")

        u,d = change_user_password('jhon@domain.com', 'jhon1234', 'jhon5678')
        print(f'data {d}')

        self.assertEqual(u.email, 'jhon@domain.com') #type:ignore
        self.assertEqual(d['password'], 'jhon5678' )


    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_services.UserServicesTest.test_authenticate_user --debug-mode
    def test_authenticate_user(self):
        logger.info("\n----------AUTHENTICATE USER SERVICE TEST----------")
        u = User.objects.get(email = 'jhon@domain.com')
        d = authenticate_user(u.email, 'jhon1234')
        print(d)

        self.assertIsNotNone(d['refresh'])
        self.assertIsNotNone(d['access'])

        

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_services.UserServicesTest.test_check_email --debug-mode
    def test_check_email(self):
        logger.info("\n----------CHECK EMAIL SERVICE TEST----------")
        u = User.objects.get(email = 'jhon@domain.com')
        obj = check_email(u.email)
        print(f'data: {obj}')

        self.assertIsNotNone(obj)

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_services.UserServicesTest.test_add_profile_location --debug-mode
    def test_add_profile_location(self):
        logger.info("\n----------ADD PROFILE LOCATION SERVICE TEST----------")
        p = Profile.objects.get(user__email = 'jhon@domain.com')
        profile = add_profile_location(p, **self.profile_location_create_data)
        print(profile.debug_str())

        self.assertEqual(profile.user.email, 'jhon@domain.com')
        self.assertTrue(profile.location.filter(**self.profile_location_create_data).exists())
        
    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_services.UserServicesTest.test_delete_profile_locations --debug-mode
    def test_delete_profile_locations(self):
        logger.info("\n----------DELETE PROFILE LOCATION SERVICE TEST----------")
        p = Profile.objects.get(user__email = 'jhon@domain.com')
        profile = delete_profile_locations(p, self.profile_location_delete_data)
        print(profile.debug_str()) 

        self.assertEqual(profile.user.email, 'jhon@domain.com')
        self.assertFalse(profile.location.filter(**self.profile_location_delete_data[0]).exists())


    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_services.UserServicesTest.test_update_profile_location --debug-mode
    def test_update_profile_location(self):
        logger.info("\n----------UPDATE PROFILE LOCATION SERVICE TEST----------")
        p = Profile.objects.get(user__email = 'jhon@domain.com')
        profile = update_profile_location(p, **self.profile_location_update_data)
        print(p.debug_str()) 

        self.assertEqual(profile.user.email, 'jhon@domain.com')
        self.assertTrue(profile.location.filter(**self.profile_location_update_data.pop('new_location')).exists())


        
