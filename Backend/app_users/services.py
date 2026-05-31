import string, random, logging
from typing import cast, Dict, Any, Tuple, Optional
from datetime import timedelta

from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import validate_email 
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, EmailVerificationCode, Profile, Location
#from base import services as core_services
from base.tasks import send_email_task

logger = logging.getLogger('app_users')

class NotFound(Exception): pass
class Invalid(Exception): pass
class AuthenticationError(Exception): pass
class CreateError(Exception):pass
class DeleteError(Exception):pass
class UpdateError(Exception): pass


def generate_verification_code()-> str:
    """
    Generate a random alphanumeric verification code.

    Returns:
        str: A six-character string consisting of uppercase and lowercase letters and digits.

    Raises:
        None
    """

    characters = string.ascii_letters + string.digits
    verification_code = ''.join(random.choices(characters, k=6))
    
    return verification_code

def save_user_verification_code(email: str, vc: str)-> None:
    """
    Save a verification code for a user and set its expiration time.

    Args:
        email (str): The email address of the user to associate with the verification code.
        vc (str): The verification code to be saved.

    Returns:
        None

    Raises:
        NotFound: If no user exists with the given email.
        Exception: For any unexpected errors during code creation.
    """

    try:
        user_obj = User.objects.get(email = email)
        EmailVerificationCode.objects.create( user=user_obj, code=vc, expires_at=timezone.now() + timedelta(minutes=10))
    except User.DoesNotExist:
        raise NotFound("user does not exist")
    except Exception as e:
        raise e

def handle_verification(email:str, v_code: str) -> Tuple[str, Optional[User]]:
    """
    Handle the verification process for password reset by either sending a new code or validating an existing one.

    Args:
        email (str): The email address of the user requesting verification.
        v_code (str | None): The verification code provided by the user, or None to generate a new code.

    Returns:
        tuple: A tuple containing a message string and either None (if a new code was sent) or the verified User object.

    Raises:
        NotFound: If no user exists with the given email. Or If the provided verification code does not exist.
        Invalid: If the verification code is expired or already used.
        Exception: For any unexpected errors during the verification process.
    """

    try:
        if not v_code:
            vc = generate_verification_code()

            #core_services.send_email(subject='new_password', email= email, **{'v_code':vc})
            save_user_verification_code(email = email , vc = vc)
            logger.info("email sent sucsessfully")
            send_email_task.delay(subject='new_password', email= email, v_code=vc) # type: ignore
            return "Verification code is sent to the email, check your email!", None
        else:
            user_obj = match_user_verification_code(email= email, v_code = v_code)
            logger.info("password changed sucsessfully")
            return "Password is changed Successfully", user_obj

    except (NotFound, Invalid) as e:
        raise e
    except Exception as e:
        raise e
    
def match_user_verification_code(email: str, v_code:str)-> Optional[User]:
    """
    Verify a user's email and matching verification code, ensuring validity and marking the verification code as used.

    Args:
        email (str): The email address of the user to verify.
        v_code (str): The verification code provided by the user.

    Returns:
        User: The User object if the verification code is valid and successfully matched.

    Raises:
        NotFound: If no user exists with the given email. or If no verification code is found for the user.
        Invalid: If the verification code is expired or already used.
        Exception: For any unexpected errors encountered during verification.
    """

    try:
        user_obj = User.objects.get(email = email)
        evc_obj = EmailVerificationCode.objects.filter(user = user_obj, code = v_code).first()

        if not evc_obj:
            raise NotFound("Verification Code not found")
        if not evc_obj.is_valid(): 
            raise Invalid("Code expired or already used")

        if evc_obj.code == v_code:
            evc_obj.is_used = True
            evc_obj.save()
            evc_obj.delete()
        return user_obj
    except User.DoesNotExist:
        raise NotFound("Account with this email does not exists")
    except Exception as e:
        raise e
    
def change_user_password(email: str, password: str, new_pass: str)-> Tuple[ Optional[User],dict]:
    """
    Change a user's password by verifying the current password and preparing updated credentials.

    Args:
        email (str): The email address of the user whose password is being changed.
        password (str): The user's current plain-text password.
        new_pass (str): The new plain-text password to set for the user.

    Returns:
        tuple: A tuple containing the User object and a dictionary with updated credentials.

    Raises:
        NotFound: If no user exists with the given email.
        Invalid: If the current password is blank or does not match the stored password.
    """

    try:
        user_obj = User.objects.get(email = email)
            
        if not password:
            raise Invalid("Password can't be blank")
                    
        if not user_obj.check_password(password):
            raise Invalid("Password does not match (unauthorize)")
        
        data = {
            "email": email,
            "password": new_pass
            }
        return user_obj, data
     
    except User.DoesNotExist:
        raise NotFound("Account with this email does not exists")
    
def authenticate_user(email:str, password:str)-> dict:
    """
    Authenticate a user by verifying email and password credentials, and issue JWT tokens upon success.

    Args:
        email (str): The user's email address.
        password (str): The user's plain-text password.

    Returns:
        dict: A dictionary containing the refresh token, access token and user details.

    Raises:
        NotFound: If no user exists with the given email.
        AuthenticationError: If the provided password is invalid or authentication fails.
    """

    try:
        logger.info("Entering in service")
        logger.info("Authenticating User")
        user_obj = User.objects.get(email = email)
        user = authenticate(email= email, password= password)
        if not user:
            raise AuthenticationError("Authentication Failed")
        refresh = RefreshToken.for_user(user)
        res = {'refresh': str(refresh),
                'access': str(refresh.access_token),
        }
        return res
    except User.DoesNotExist as e:
        raise NotFound("Unable to find user")
    
def check_email(email:str)-> User|None:
    """
    Validate the format of an email address and check if it exists in the User model.

    Args:
        email (str): The email address to validate.

    Returns:
        User | None: The User object if a matching email exists, otherwise None.

    Raises:
        ValidationError: If the provided email string is not in a valid format.
    """
    try:
        #validate_email(email) 
        exist_email = User.objects.filter(email = email).first()
        return exist_email
    except ValidationError:
        raise ValidationError("Invalid email format")



def update_profile_location(profile:Profile, **location_data)-> Profile:
    """
    Authenticate a user by verifying email and password credentials, and issue JWT tokens upon success.

    Args:
        email (str): The user's email address.
        password (str): The user's plain-text password.

    Returns:
        dict: A dictionary containing the refresh token, access token and user details.

    Raises:
        NotFound: If no user exists with the given email.
        AuthenticationError: If the provided password is invalid or authentication fails.
    """
    try:
        logger.info("Entering in user service")
        logger.info(" creating new Location or fetching existing one ")

        old_location = location_data.pop('old_location')
        new_location = location_data.pop('new_location')

        location_obj, created = Location.objects.get_or_create(**new_location)
        old_location_obj = Location.objects.get(**old_location)

        if created:
            logger.info("New location has been created")
        else:
            logger.info("Location already exists")

        logger.info("Removing Old location from profile")
        profile.location.remove(old_location_obj)
        logger.info("Old location removed from profile")
        logger.info("Adding Location to profile")
        profile.location.add(location_obj)
        logger.info("Location Added successfully")
        

        logger.info("Location added to Profile")


        return profile
    except Location.DoesNotExist:
        raise NotFound("Location which need to update is not found")
    except Exception as e:
        logger.exception(str(e))
        raise UpdateError("Update Failed")

def delete_profile_locations(profile:Profile, locations_data:list[Dict[str,Any]])-> Profile:
    try:
        logger.info("Entering in user service")
        locations_data if logger.info("Got locations data from request") else logger.info("locations data missing from request")
        print(locations_data, "\t", type(locations_data))
        with transaction.atomic():
            for location in locations_data:
                location_obj = Location.objects.get(**location)
                profile.location.remove(location_obj)
            logger.info("locations removed from profile successfully")

        logger.info("Leaving service..")
        return profile
    except Location.DoesNotExist:
        raise NotFound("Location which need to delete is not found")
    except Exception as e:
        logger.exception(str(e))
        raise DeleteError("delete Failed")

def add_profile_location(profile:Profile, **location_data)-> Profile:
    try:
        logger.info("Entering in user service")
        print(location_data)
        location_data if logger.info("Got location data from request") else logger.info("location data missing from request")

        with transaction.atomic():
            location_obj, _ = Location.objects.get_or_create(**location_data)
            profile.location.add(location_obj)
            logger.info("location added to profile successfully")

        logger.info("Leaving service..")
        return profile
    except Location.DoesNotExist:
        raise NotFound("Location which need to be added is not found")
    except Exception as e:
        logger.exception(str(e))
        raise CreateError("Location addation Failed")
