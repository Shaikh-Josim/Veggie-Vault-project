from django.db import models
from base.models import BaseModel
from app_locations.validators import address_text_validator, location_name_validator, hno_validator

# Create your models here.
class Location(BaseModel):
    staddr = models.CharField(verbose_name='Street-address', max_length=100, null= False, blank=True, default= '', validators=[address_text_validator])
    city = models.CharField(verbose_name='City', max_length=100, null = False, blank=True, default= '', validators=[location_name_validator])
    state = models.CharField(verbose_name='State', max_length=100, null = False, blank=True, default= '', validators= [location_name_validator])
    hno = models.CharField(verbose_name='House no.', max_length=5, null = False, blank=True, default= '', validators=[hno_validator])
    landmark = models.CharField(verbose_name='Landmark', max_length=100, null = False, blank=True, default= '', validators=[address_text_validator])
    is_homeaddress = models.BooleanField(verbose_name='is home address', null=False, blank = True, default= False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["staddr", "city", "state", "hno", "landmark"], name="unique_full_location")
        ]

    def __str__(self):
        return f"address:{self.staddr},{self.city},{self.state}"

    def debug_str(self) -> str:
        return f'Location obj| staddr: {self.staddr}, city: {self.city}, state: {self.state}, hno: {self.hno}, landmark: {self.landmark}, is_homeaddress {self.is_homeaddress}'