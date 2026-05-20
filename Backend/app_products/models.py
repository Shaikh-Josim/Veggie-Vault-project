from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from base.models import BaseModel


string_validator = RegexValidator(
    regex = r"^[A-Za-z,.']+",
    message = "only letters are valid"
)

# Create your models here.
class Product(BaseModel):

    class ProductCategory(models.IntegerChoices):
        VEGETABLE = 1, "Vegetable"
        FRUIT = 2, "Fruit"
    class Status(models.IntegerChoices):
        INSTOCK = 1, "instock"
        OUTOFSTOCK = 2, "outofstock"

    name = models.CharField(verbose_name='Product Name', max_length=30, null= False, validators=[string_validator])
    category = models.IntegerField(verbose_name='Product Category', choices=ProductCategory.choices,
    default=ProductCategory.VEGETABLE)
    discription = models.TextField(verbose_name='Product Description', max_length=500, validators=[string_validator])
    price = models.DecimalField(verbose_name='Product Price', null= False, max_digits=10,decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.DecimalField(verbose_name='Available stock', decimal_places=2, null= False, max_digits=10, validators=[MinValueValidator(0)])
    status = models.IntegerField(verbose_name="Product's Status", choices=Status.choices,default= Status.INSTOCK)
    product_Img = models.ImageField(verbose_name="Product Image", upload_to='images/products/', null=False, default="images/products/vv.jpg")

    #for orders table
    consumers = models.ManyToManyField('app_users.Profile', through="app_orders.Orders", related_name="consumers")

    def __str__(self):
        return f"{self.name}"
    
class Cart(BaseModel):
    profile = models.ForeignKey('app_users.Profile', verbose_name= 'user', on_delete= models.CASCADE, null= False, related_name= 'carts')
    product = models.ForeignKey(Product, verbose_name= 'product', on_delete= models.CASCADE, null= False, related_name= 'cart_items')
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('profile', 'product')

    @property 
    def total_price(self): 
        return self.product.price * self.quantity
    
    def __str__(self) -> str:
        return f"user-email: {self.profile.user.email} product: {self.product.name}"