from decimal import Decimal

from django.db import models

from base.models import BaseModel
from app_locations.models import Location
from app_users.models import Profile
from app_products.models import Product , Cart

# Create your models here.

class Orders(BaseModel):
    consumer = models.ForeignKey(Profile, verbose_name= 'Consumer', on_delete=models.CASCADE, related_name="purchasedby")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default= Decimal("0.00"))

    razorpay_order_id = models.CharField(max_length=255, unique=True, blank=True, default='')

    payment_status = models.CharField(
        max_length=20,
        choices=[("paid", "Paid"), ("not_paid", "Not Paid")],
        default="not_paid"
    )

    def __str__(self):
        return f"consumer-fname:{self.consumer.fname} {self.consumer.lname}, order-amount:{self.amount} razorpay_orderid:{self.razorpay_order_id} payment_status: {self.payment_status}"
        return f"consumer-fname:{self.consumer.fname} {self.consumer.lname}, order-amount:{self.amount}"
    
class OrderedItem(BaseModel):
    order = models.ForeignKey(Orders, verbose_name= 'Order', on_delete= models.CASCADE, related_name='ordered_item')
    ordered_item = models.ForeignKey(Product, verbose_name='Ordered Product', on_delete=models.PROTECT, related_name="purchased_item")
    quantity = models.IntegerField(verbose_name='Quantity', null= False)
    total_price = models.IntegerField(verbose_name='total_price', null= False)

    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("delivered", "Delivered"), ("refunded", "Refunded"),("delayed", "Delayed")],
        default="pending"
    )

    def __str__(self):
        return f"order:{self.order} product:{self.ordered_item}, status:{self.status}"
    

 # user -> place order -> create order obj -> ask razorpay for order id ->create payment obj -> 
 #



class Payment(BaseModel):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='payments')
    
    razorpay_payment_id = models.CharField(max_length=100, unique=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    
    class Status(models.TextChoices):
        CREATED = "created", "Created"
        AUTHORIZED = "authorized", "Authorized"
        CAPTURED = "captured", "Captured"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CREATED
    )

    def __str__(self):
        return f"Payment {self.razorpay_payment_id} - {self.status}"
    

