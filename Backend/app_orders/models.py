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
    razorpay_order_id = models.CharField(max_length=255, unique=True, blank=True, null= True)

    order_status = models.CharField(
        max_length=20,
        choices=[("paid", "Paid"), ("not_paid", "Not Paid"), ("expired", "Expired")],
        default="not_paid"
    )

    payment_mode = models.CharField(
        max_length=20,
        choices=[("offline", "Offline"), ("online", "Online")],
        default="online"
    )

    def save(self, *args, **kwargs):
        if self.razorpay_order_id == "":
            self.razorpay_order_id = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"consumer-name:{self.consumer.fname} {self.consumer.lname}, order-amount:{self.amount} razorpay_orderid:{self.razorpay_order_id}"

    def debug_str(self) -> str:
        return f"Order obj: (order-amount:{self.amount} razorpay_orderid:{self.razorpay_order_id}, order-status: {self.order_status}. payment-mode: {self.payment_mode}\n| consumer: Profile obj| {self.consumer} )"
        
    
class OrderedItem(BaseModel):
    order = models.ForeignKey(Orders, verbose_name= 'Order', on_delete= models.CASCADE, related_name='ordered_item')
    ordered_item = models.ForeignKey(Product, verbose_name='Ordered Product', on_delete=models.PROTECT, related_name="purchased_item")
    quantity = models.IntegerField(verbose_name='Quantity', null= False)
    total_price = models.IntegerField(verbose_name='total_price', null= False)

    item_status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("delivered", "Delivered"), ("refunded", "Refunded"),("delayed", "Delayed"), ("expired", "Expired")],
        default="pending"
    )

    def __str__(self):
        return f"order:{self.order} product:{self.ordered_item}, item_status:{self.item_status}"

    def debug_str(self) -> str:
        return f"OrderItem obj: (quantity:{self.quantity} total-price:{self.total_price}, item-status: {self.item_status}\n| consumer: Order obj| {self.order}\n order-item: Product obj| {self.ordered_item})"



class Payment(BaseModel):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='payments')
    
    razorpay_payment_id = models.CharField(max_length=100, unique=True, null = True, blank = True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    
    class Status(models.TextChoices):
        CREATED = "created", "Created"
        AUTHORIZED = "authorized", "Authorized"
        CAPTURED = "captured", "Captured"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    payment_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CREATED
    )

    def __str__(self):
        return f"payment-id:{self.razorpay_payment_id} payment-status {self.payment_status}"

    def debug_str(self) -> str:
        return f"Payment obj: (razorpay-payment-id:{self.razorpay_payment_id} razorpay-signature:{self.razorpay_signature}, payment-status: {self.payment_status}\n| order: Order obj| {self.order})"

class Refund(BaseModel):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    
    razorpay_refund_id = models.CharField(max_length=100, unique=True, null= True, blank=True)
    refund_amount = models.PositiveIntegerField(verbose_name='refunded_amount', blank = False, null= False, default= 0)
    
    class Status(models.TextChoices):
        PROCESSED = "processed", "Processed"
        PENDING = "pending", "Pending"
        FAILED = "failed", "Failed"    
        INITIATED = "initiated", "Initiated"

    refund_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    def __str__(self):
        return f"refund id: {self.razorpay_refund_id}, refund amount: {self.refund_amount}, refund_status: {self.refund_status}"

    def debug_str(self) -> str:
            return f"Refund obj: (razorpay-refund-id: {self.razorpay_refund_id} refund-amount:{self.refund_amount}, refund-status: {self.refund_status}\n| payment: Payment obj| {self.payment})"
    
    def save(self, *args, **kwargs):
        if self.razorpay_refund_id == "":
            self.razorpay_refund_id = None
        super().save(*args, **kwargs)


