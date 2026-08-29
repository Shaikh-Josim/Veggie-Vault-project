from django.core.validators import RegexValidator

name_validator = RegexValidator(
    regex = r'^[A-Za-z ]+',
    message = "only letters and spaces are valid")

mobile_no_validator = RegexValidator(
    regex = r'^[0-9]{10,}',
    message = "only numbers are valid and only 10 digits are allowed")

email_validator = RegexValidator(
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
    message = 'invalid email')

email_verification_code_validator = RegexValidator(
    regex = r'^[A-Za-z0-9]{6,}',
    message = "only numbers and letters are valid")

password_validator = RegexValidator( 
    regex = r'^[A-Za-z0-9@#$%&_]{8,}$',
    message = "Password must be at least 8 characters long and contain only letters, numbers, or @#$%%&_"
    )