
from rest_framework import serializers

from app_locations.models import Location
from app_locations.validators import location_name_validator, address_text_validator, hno_validator




class LocationSerializer(serializers.Serializer):
    """
    Serializer for user authentication and account management.

    Fields:
        email (str): Required. The user's email address.
        password (str): Required. The user's plain-text password. Write-only field with custom validation.

    Methods:
        create(self, validated_data: dict) -> User:
            Creates a new User instance and securely sets the password.

        update(self, instance: User, validated_data: dict) -> User:
            Updates an existing User instance.
            - Prevents modification of the email field.
            - Upda=tes the password if provided, ensuring it is hashed.

    Returns:
        User: The created or updated User object.

    Raises:
        ValidationError: If password validation fails.
    """
    staddr = serializers.CharField(validators = [address_text_validator])
    city = serializers.CharField(validators = [location_name_validator])
    state = serializers.CharField(validators = [location_name_validator])
    hno = serializers.CharField(validators = [hno_validator])
    landmark = serializers.CharField(validators = [address_text_validator])
    is_homeaddress = serializers.BooleanField()

class LocationModelSerializer(serializers.ModelSerializer):
    """
    Serializer for user authentication and account management.

    Fields:
        email (str): Required. The user's email address.
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

    class Meta:
        model = Location
        fields = ["staddr","city", "state", "hno", "landmark", "is_homeaddress"]

        