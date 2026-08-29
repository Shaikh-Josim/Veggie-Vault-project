from django.core.validators import RegexValidator

product_name_validator = RegexValidator(
    regex = r"^[A-Za-z-' ]+",
    message = "only letters and (- ') and space are allowed")

text_validator = RegexValidator(
    regex = r"^[A-Za-z-'!#%&(), ]+",
    message = "only letters and (,-'!#%&()) and space are allowed")