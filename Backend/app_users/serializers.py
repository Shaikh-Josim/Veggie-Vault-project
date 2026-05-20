import re
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, Profile
from app_locations.models import Location
from app_locations.serializers import LocationSerializer
from django.core.validators import RegexValidator
from typing import cast

password_validator = RegexValidator( 
    regex = r'^[A-Za-z0-9@#$%&_]{8,}$',
    message = "Password must be at least 8 characters long and contain only letters, numbers, or @#$%%&_"
    )

class EmailPasswordSerializer(serializers.Serializer):
    """
    Serializer for handling user password change requests.

    Fields:
        email (str): Required. The user's email address.
        password (str): Required. The user's current plain-text password. Write-only field with custom validation.
        new_pass (str): Required. The new plain-text password to set for the user. Write-only field with custom validation.

    Returns:
        dict: Validated data containing 'email', 'password', and 'new_pass'.

    Raises:
        ValidationError: If any of the fields fail validation (e.g., invalid email format or password rules).
    """
    email = serializers.EmailField()
    password = serializers.CharField( write_only=True,
    validators=[password_validator])
    new_pass = serializers.CharField( write_only=True)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators = [password_validator])

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user authentication and account management.

    Fields:
        password (str): Required. The user's plain-text password. Write-only field with custom validation.

    Methods:
        create(self, validated_data: dict) -> User:
            Creates a new User instance and securely sets the password.

        update(self, instance: User, validated_data: dict) -> User:
            Updates an existing User instance.
            - Prevents modification of the email field.
            - Updates the password if provided, ensuring it is hashed.

    Returns:
        User: The created or updated User object.

    Raises:
        ValidationError: If password validation fails.
    """

    password = serializers.CharField( write_only=True,
    validators=[password_validator])
    
    class Meta:
        model = User
        fields = ["email","password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data:dict):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data["password"])
        Profile.objects.create(user = user)
        return user
    
    def update(self, instance:User, validated_data:dict):  
        validated_data.pop("email", None) 
        password = validated_data.get("password", None) 
        if password: 
            instance.set_password(password)
        return super().update(instance, validated_data)
    
class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile data, including nested location details and custom email retrieval.

    Nested Serializers:
        LocationSerializer: Handles location fields such as street address, city, state, house number, and landmark.

    Fields:
        uid (int): Unique identifier for the profile.
        fname (str): First name of the user.
        lname (str): Last name of the user.
        email (str): Read-only field retrieved from the related User model.
        location (LocationSerializer): Nested serializer for location details.
        role (str): Role assigned to the user.
        mobile_no (str): Mobile number of the user.
        user_Img (ImageField): Profile image of the user.

    Methods:
        get_email(obj: Profile) -> Optional[str]:
            Returns the email of the associated User object if available.

        create(validated_data: dict) -> Profile:
            Creates a new Profile instance along with a related Location object.
            - Extracts and creates/gets the Location from validated_data.
            - Associates the Location with the new Profile.
            - Returns the created Profile instance.

    Returns:
        Profile: The created or serialized Profile object.
    """
    

    email = serializers.SerializerMethodField(source="user.email", read_only=True)
    location = LocationSerializer(required=False, allow_null=True)
    class Meta:
        model = Profile
        fields = ["fname","lname","email","location","role","mobile_no", "user_Img"]

    def get_email(self,obj):
        obj = cast(Profile, obj) #typehint
        return obj.user.email if obj.user else None
    
    def create(self, validated_data):
        print(validated_data)
        validated_data = cast(dict, validated_data)
        location_data = validated_data.pop('location')
        location_serializer = LocationSerializer(location_data)
        location_serializer.is_valid(raise_exception= True)
        location, _ = Location.objects.get_or_create(**location_data)
        user_profile = Profile.objects.create(location = location,**validated_data)
        return user_profile
    
    
 