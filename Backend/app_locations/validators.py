from django.core.validators import RegexValidator

address_text_validator = RegexValidator(
    regex = r"^[A-Za-z0-9.,\-/#' ]+",
    message = "only letters and .,'/# and space are valid"
)

location_name_validator = RegexValidator(
    regex = r"^[A-Za-z.\-' ]+",
    message = "only letters and .-' and space are valid"
)

hno_validator = RegexValidator(
    regex = r"^[A-Za-z0-9-/., ]+",
    message = "only letters, numbers and .-/, and space are valid"
)
