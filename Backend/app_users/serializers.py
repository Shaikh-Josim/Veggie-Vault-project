from typing import cast

from rest_framework import serializers
from app_users.models import User, Profile, Location
from app_locations.serializers import LocationSerializer
from app_users.validators import password_validator



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
    password = serializers.CharField( write_only=True, validators=[password_validator])
    new_pass = serializers.CharField( write_only=True, validators=[password_validator])

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

    password = serializers.CharField( write_only=True, validators=[password_validator])
    
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
        LocationSerializer (many=True): Handles multiple location objects related to the profile.
            - Fields: street address, city, state, house number, landmark.

    Fields:
        fname (str): First name of the user.
        lname (str): Last name of the user.
        email (str): Read-only field retrieved from the related User model via get_email().
        location (LocationSerializer): Nested serializer for one or more location records.
        role (str): Role assigned to the user (choice field).
        mobile_no (str): Mobile number of the user.
        user_Img (ImageField): Profile image of the user.

    Methods:
        get_email(obj: Profile) -> Optional[str]:
            Returns the email of the associated User object if available.

        get_location(obj: Profile) -> LocationSerializer:
            Serializes all related Location objects for the profile using the nested LocationSerializer.

    Returns:
        Profile: The serialized Profile object with nested location and custom email field.
    """

    email = serializers.SerializerMethodField(source="user.email", read_only=True)
    location = LocationSerializer(many=True, required=False)

    class Meta:
        model = Profile
        fields = ["fname", "lname", "email", "location", "role", "mobile_no", "user_Img"]

    def get_location(self, obj):
        obj = cast(Profile, obj)
        return LocationSerializer(many=True, data=obj.location.all())

    def get_email(self, obj):
        obj = cast(Profile, obj)
        return obj.user.email if obj.user else None

class ProfileUpdateLocationsSerializer(serializers.Serializer):
    """
    Serializer for updating a user's profile locations by replacing an old location
    with a new one.

    Nested Serializers:
        LocationSerializer:
            - old_location: Represents the existing location record that should be updated or replaced.
            - new_location: Represents the new location data to be applied to the profile.

    Fields:
        old_location (LocationSerializer): The current location details associated with the profile.
        new_location (LocationSerializer): The updated location details to replace the old location.

    Use Cases:
        - Allows clients to send both the old and new location data in a single request.

    Returns:
        dict: A validated dictionary containing both old and new location data.
    """

    old_location = LocationSerializer()
    new_location = LocationSerializer()


    
    
    

    
    
 