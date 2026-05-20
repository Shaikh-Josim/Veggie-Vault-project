from typing import cast, Dict, Any
import logging

from rest_framework import permissions, generics, status, views
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
import sentry_sdk

from .models import User, Profile
from .serializers import UserSerializer, ProfileSerializer, EmailPasswordSerializer, LoginSerializer
from app_users import services

from dotenv import load_dotenv 

# Create your views here.
load_dotenv()

logger = logging.getLogger('app_users')  # will use JSON config


          
class CreateUserView(generics.ListCreateAPIView):
    """
    API endpoint for listing all users and creating new user accounts.

    Inherits:
        ListCreateAPIView: Provides GET (list) and POST (create) functionality.

    Queryset:
        User.objects.all(): Returns all User instances.

    Permissions:
        AllowAny: Accessible to all users without authentication.

    Methods:
        create(self, request, *args, **kwargs) -> Response:
            - Validates incoming request data using UserSerializer.
            - Calls serializer.save() to create a new User instance.
            - Returns a success message with HTTP 201 status if creation succeeds.
            - Captures and logs unexpected exceptions, returning a 500 error response.

    Request Body:
        {
            "email": str,      # Required. User's email address.
            "password": str    # Required. User's plain-text password.
        }

    Responses:
        201 Created:
            {"message": "New user created successfully"}

        500 Internal Server Error:
            {"error": "server error occured"}

    Raises:
        ValidationError: If the provided data is invalid (handled automatically by DRF).
        Exception: For any unexpected errors during user creation.
    """

    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            user_serializer = UserSerializer(data=request.data)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()   # calls serializer.create(), returns User instance
            return Response(
                {"message": "New user created successfully"},
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e: 
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e: 
            sentry_sdk.capture_exception(e)
            logger.exception(e)
            return Response({"error": "server error occured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
class CheckUserView(views.APIView):
    """
    API endpoint for checking whether a user exists by email.

    Permissions:
        AllowAny: Accessible to all users without authentication.

    Methods:
        get(self, request, *args, **kwargs) -> Response:
            - Reads the 'email' query parameter from the request.
            - Validates the email using EmailSerializer.
            - Calls the check_email service to determine if a user exists.
            - Returns HTTP 409 Conflict if a user already exists with the given email.
            - Returns HTTP 200 OK if no user exists with the given email.
            - Handles validation errors and unexpected exceptions gracefully.

    Query Parameters:
        email (str): Required. The email address of the user to check.

    Responses:
        200 OK:
            {}  # Empty body, indicates no user exists with the given email.

        409 Conflict:
            {"detail": "User already exists with the given email"}

        400 Bad Request:
            {"detail": "<validation error message>"}

        500 Internal Server Error:
            {"error": "server error occured"}

    Raises:
        ValidationError: If the email format is invalid.
        Exception: For any unexpected errors during processing.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request: Request, *args, **kwargs) -> Response:
        try:        
            email = str(request.query_params.get('email'))
            if email and '@' in email:
                exist = services.check_email(email = email)

                if exist:
                    return Response(
                    {"detail": "User already exists with the given email"},
                        status=status.HTTP_409_CONFLICT
                    )
            return Response(
                status=status.HTTP_200_OK
            )
        except services.ValidationError as e: 
            return Response({"detail": e}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e: 
            sentry_sdk.capture_exception(e)
            logger.exception(e)
            return Response({"error": "server error occured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(views.APIView):
    """
    API endpoint for authenticating users and issuing JWT access/refresh tokens.

    Methods:
        post(self, request, *args, **kwargs) -> Response:
            - Validates request data using UserSerializer (email + password).
            - Calls the authenticate_user service to verify credentials.
            - If authentication succeeds, returns a Response containing access and refresh tokens,
              along with user details.
            - Sets the refresh token in an HttpOnly, Secure, SameSite=Strict cookie with a 7-day expiry.
            - Handles authentication errors and unexpected exceptions gracefully.

    Request Body:
        {
            "email": str,      # Required. User's email address.
            "password": str    # Required. User's plain-text password.
        }

    Responses:
        200 OK:
            {
                "refresh": "<refresh_token>",
                "access": "<access_token>",
                "email": "<user_email>",
                "role": "<user_role>",
                "user_Img": "<profile_image_url or empty string>"
            }
            - Also sets 'refreshToken' cookie with HttpOnly, Secure, SameSite=Strict attributes.

        400 Bad Request:
            {"error": "<invalid credentials or user not found>"}

        500 Internal Server Error:
            {"error": "server error occured"}

    Raises:
        UserNotFound: If no user exists with the given email.
        AuthenticationError: If the provided password is invalid.
        Exception: For any unexpected errors during login.
    """
    permission_classes = [permissions.AllowAny]
    def post(self, request: Request, *args, **kwargs) -> Response:
        login_serializer = LoginSerializer(data = request.data)
        login_serializer.is_valid(raise_exception=True)
        data = cast(Dict[str,Any],login_serializer.validated_data)
        try:
            res = services.authenticate_user(
                email= data['email'],  
                password = data['password']
            )

            print(res)
            
            #refresh_token = request.COOKIES.get("refreshToken")
            if isinstance(res, dict):
                res = Response({**res})
                data = cast(Dict[str,Any],res.data)
                res.set_cookie(
                    key="refreshToken",
                    value= data["refresh"],
                    httponly=True,   
                    secure=True,     
                    samesite="Strict",
                    max_age=7*24*60*60 
                )
            return res
        except (services.UserNotFound, services.AuthenticationError) as e:
            return Response({"error":str(e)}, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e: 
            sentry_sdk.capture_exception(e)
            logger.exception(e)
            return Response({"error": "server error occured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
class ForgetPasswordView(views.APIView):
    """
    API endpoint for handling password reset requests via email verification codes.

    Permissions:
        AllowAny: Accessible to all users without authentication.

    Methods:
        post(self, request):
            - Validates request data using VerificationCodeSerializer and UserSerializer.
            - If no verification code is provided, generates and sends a new code to the user's email.
            - If a verification code is provided, validates it and resets the user's password.
            - Saves the user object if verification succeeds.
            - Returns a success message or error response depending on the outcome.

    Request Body:
        {
            "email": str,          # Required. User's email address.
            "v_code": str | None,  # Optional. Verification code for password reset.
            "password": str,       # Required. New password to set.
        }

    Responses:
        200 OK:
            {"message": "Verification code is sent to the email, check your email!"}
            {"message": "Password is changed Successfully"}

        400 Bad Request:
            {"error": "<validation or verification error message>"}

        500 Internal Server Error:
            {"error": "<unexpected error message>"}

    Raises:
        UserNotFound: If no user exists with the given email.
        CodeNotFound: If the provided verification code does not exist.
        InvalidCode: If the verification code is expired or already used.
        Exception: For any unexpected errors during processing.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):   
        try:
            msg, user_obj = services.handle_verification(
                email= request.data.get('email'),
                v_code= request.data.get('v_code')
             )
            if user_obj:
                user_serializer = UserSerializer(user_obj,data=request.data)
                user_serializer.is_valid(raise_exception=True)
                user_serializer.save()
            return Response(
                {"message": msg},
                status=status.HTTP_200_OK
                )   
                    
        except (services.UserNotFound, services.CodeNotFound, services.InvalidCode) as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e: 
            sentry_sdk.capture_exception(e)
            logger.exception(e)
            print(e)
            return Response({"error": str(e)}, status= status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class ChangePasswordView(views.APIView):
    """
    API endpoint for authenticated users to change their password.

    Permissions:
        IsAuthenticated: Only accessible to logged-in users.

    Methods:
        post(self, request):
            - Validates request data using EmailPasswordSerializer.
            - Calls the change_user_password service to verify the current password
              and prepare updated credentials.
            - Updates the User object with the new password using UserSerializer.
            - Returns a success message if the password change is successful.
            - Handles and reports errors gracefully.

    Request Body:
        {
            "email": str,       # Required. The user's email address.
            "password": str,    # Required. The user's current password.
            "new_pass": str     # Required. The new password to set.
        }

    Responses:
        200 OK:
            {"message": "Password Changed Successfully!"}

        400 Bad Request:
            {"error": "<validation or user not found error message>"}

        500 Internal Server Error:
            {"error": "server error occured"}

    Raises:
        UserNotFound: If no user exists with the given email.
        InvalidCode: If the provided password or code is invalid.
        Exception: For any unexpected errors during processing.
    """

    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):      
         
        try: 
            print(request.data)
            ep_serializer = EmailPasswordSerializer(data = request.data)
            ep_serializer.is_valid(raise_exception=True)
            ep_serializer_data = cast(Dict[str,Any], ep_serializer.validated_data)

            user_obj,data = services.change_user_password(
            email = ep_serializer_data['email'], 
            password= ep_serializer_data['password'], 
            new_pass= ep_serializer_data['new_pass']
            )

            serializer = UserSerializer(user_obj, data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {"message": "Password Changed Successfully!"},
                status=status.HTTP_200_OK
            )
        
        except (services.UserNotFound, services.InvalidCode) as e:
            return Response({"error":str(e)}, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e: 
            sentry_sdk.capture_exception(e)
            logger.exception(e)
            return Response({"error": "server error occured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListUserProfileView(generics.ListAPIView):
    """
    API endpoint for listing all user profiles.

    Inherits:
        ListAPIView: Provides GET (list) functionality for Profile objects.

    Queryset:
        Profile.objects.all(): Returns all Profile instances.

    Serializer:
        ProfileSerializer: Serializes Profile model data for output.

    Permissions:
        AllowAny: Accessible to all users without authentication.

    Methods:
        get(self, request, *args, **kwargs) -> Response:
            - Returns a list of all user profiles in the system.
            - Uses ProfileSerializer to format the response data.
            - Supports pagination and filtering if configured globally in DRF.

    Responses:
        200 OK:
            [
                {
                    "id": int,
                    "user": int,
                    "bio": str,
                    "website": str,
                    "avatar": str
                },
                ...
            ]

        500 Internal Server Error:
            {"error": "server error occured"}  # If unexpected errors occur

    Raises:
        Exception: For any unexpected errors during profile retrieval.
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.AllowAny]

class UpdateProfileView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_object(self):
        profile = Profile.objects.get(user = self.request.user)
        return profile

    