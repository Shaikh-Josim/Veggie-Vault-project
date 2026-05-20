from django.db import models

from base.models import BaseModel
from app_locations.models import Location
from app_users.models import Profile
from app_products.models import Product

# Create your models here.
class Orders(BaseModel):
    consumer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="purchasedby")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="purchaseditem")
    quantity = models.IntegerField(null= False)
    price = models.IntegerField(null= False)
    payment_method = models.CharField(max_length=10, null= False)

    def __str__(self):
        return f"consumer-fname:{self.consumer.fname} {self.consumer.lname}, order: {self.product.name}"
