import copy


from django.test import TestCase
from django.core.exceptions import ValidationError
from app_users.models import User, Profile, EmailVerificationCode, Location
from base.tests.test_data import *
from base.helpers import pop_update_dict_data
import logging


logger = logging.getLogger('app_users')

# run class test using
# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_models.UserModelTest --debug-mode
class UserModelTest(TestCase):

    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_models.UserModelTest.test_user_obj --debug-mode
    def test_user_obj(self):
        logger.info("\n---------- USER OBJ MODEL TEST----------")
        logger.info('Testing user obj..')
        user = User.objects.create(**user1_data) 
        print(f'user:{str(user)}')
 
        bad_user_data = pop_update_dict_data(copy.deepcopy(user1_data), overrides= {'email': 'abc@examplecom'})
        bad_user = User.objects.create(**bad_user_data) 

        self.assertEqual('abc@example.com', user.email, msg= 'user email is not matching')
        self.assertTrue(user.password.startswith('pbkdf2_'), msg= 'password is not hashed')
        self.assertRaises(ValidationError, bad_user.full_clean)

        print('TEST PASSED SUCCESSFULLY!!')        

# run this class test with command:
# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_models.ProfileModelTest --debug-mode
class ProfileModelTest(TestCase):

    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_models.ProfileModelTest.test_profile_obj --debug-mode
    def test_profile_obj(self):
        logger.info("\n---------- PROFILE OBJ MODEL TEST----------")
        logger.info('Testing profile obj..')
        user = User.objects.create(**user1_data) 
        location1 , location2 = Location.objects.create(**location1_data), Location.objects.create(**location2_data)
        
        profile = Profile.objects.create( user = user, **profile1_data )

        profile.location.add(location1, location2)
        print("profile:",profile.debug_str())

        bad_user_data = pop_update_dict_data(copy.deepcopy(user1_data), overrides= {'email': 'bad@example.com'})
        bad_user = User.objects.create(**bad_user_data)
        bad_profile_data = pop_update_dict_data(copy.deepcopy(profile1_data), overrides= {'mobile_no': '1234567890a'})
        bad_profile = Profile.objects.create(user = bad_user, **bad_profile_data )

        self.assertEqual('abc xyz', profile.fname+' '+profile.lname, msg= 'profile full name is not matching')
        self.assertRaises(ValidationError, bad_profile.full_clean)
        print('TEST PASSED SUCCESSFULLY!!')        

# run this class test with command:
# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_models.EmailVerificationCodeModelTest --debug-mode
class  EmailVerificationCodeModelTest(TestCase):
    # run this func test with command:
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_users.tests.test_models.EmailVerificationCodeModelTest.test_email_vc_obj --debug-mode
    def test_email_vc_obj(self):
        logger.info("\n---------- EMAIL-VERIFICATION-CODE OBJ MODEL TEST----------")
        user = User.objects.create(**user1_data)

        email_vc_obj = EmailVerificationCode.objects.create(user = user, **email_vc_data)
        print("email vc obj: ",email_vc_obj.debug_str())

        bad_user_data = pop_update_dict_data(copy.deepcopy(user1_data), overrides= {'email': 'bad@example.com'})
        bad_user = User.objects.create(**bad_user_data)
        bad_email_vc_data = pop_update_dict_data(copy.deepcopy(email_vc_data), overrides= {'code': '-dsfs-3-'})
        bad_email_vc = EmailVerificationCode.objects.create(user = bad_user, **bad_email_vc_data)

        self.assertIsNotNone(email_vc_obj)
        self.assertRaises(ValidationError, bad_email_vc.full_clean)
        print('TEST PASSED SUCCESSFULLY!!') 
