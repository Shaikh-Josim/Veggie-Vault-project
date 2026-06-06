from django.db import models
from django.core.validators import RegexValidator
from base.models import BaseModel


# Create your models here.

address_validator = RegexValidator(
    regex = r"^[A-Za-z0-9,' ]+",
    message = "only letters and ,' space are valid"
)

class Location(BaseModel):
    staddr = models.CharField(verbose_name='Street-address', max_length=100, null= False, blank=True, default= '', validators=[address_validator])
    city = models.CharField(verbose_name='City', max_length=100, null = False, blank=True, default= '', validators=[address_validator])
    state = models.CharField(verbose_name='State', max_length=100, null = False, blank=True, default= '', validators= [address_validator])
    hno = models.CharField(verbose_name='House no.', max_length=5, null = False, blank=True, default= '', validators=[address_validator])
    landmark = models.CharField(verbose_name='Landmark', max_length=100, null = False, blank=True, default= '', validators=[address_validator])
    is_homeaddress = models.BooleanField(verbose_name='is home address', null=False, blank = True, default= False)


    def __str__(self):
        return f"address:{self.staddr},{self.city},{self.state}"