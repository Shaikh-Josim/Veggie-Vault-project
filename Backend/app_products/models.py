from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from django.utils.text import slugify
from django.db.models.functions import TruncDate

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

    name = models.CharField(
        verbose_name='Product Name', max_length=30, null= False, validators=[string_validator])
    slug = models.SlugField(
        max_length=60, unique=True, blank=True)
    category = models.IntegerField(
        verbose_name='Product Category', choices=ProductCategory.choices,default=ProductCategory.VEGETABLE)
    description = models.TextField(
        verbose_name='Product Description', max_length=500, validators=[string_validator])
    price = models.DecimalField(
        verbose_name='Product Price', null= False, max_digits=10,decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.DecimalField(
        verbose_name='Available stock', decimal_places=2, null= False, max_digits=10, validators=[MinValueValidator(0)])
    status = models.IntegerField(
        verbose_name="Product's Status", choices=Status.choices,default= Status.INSTOCK)
    product_Img = models.ImageField(
        verbose_name="Product Image", upload_to='images/products/', null=False, default="images/products/vv.jpg")

    def sulgify_product_name(self):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

    def save(self, *args, **kwargs):
        self.sulgify_product_name()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"
 
    def debug_str(self) -> str:
        return f"Product obj | name: {self.name}, slug: {self.slug}, category: {self.category}, category-name: {self.get_category_display()}, description: {self.description}, price: {self.price}, stock: {self.stock}, status: {self.status}, status-name: {self.get_status_display()}, product-img: {self.product_Img}" #type:ignore
    
class Cart(BaseModel):
    profile = models.ForeignKey(
        'app_users.Profile', verbose_name= 'user', to_field= 'uid' , on_delete= models.CASCADE, null= False, related_name= 'carts')
    product = models.ForeignKey(
        Product, verbose_name= 'product', to_field= 'uid' ,on_delete= models.CASCADE, null= False, related_name= 'cart_items')
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('profile' , 'product', 'created_at')
        constraints = [
            models.UniqueConstraint(
                TruncDate("created_at"),
                "profile",
                'product',
                name="unique_user_per_day",
            )
        ]

    @property 
    def total_price(self): 
        return self.product.price * self.quantity

    @property 
    def is_stock(self): 
        return self.quantity < self.product.stock
    
    def __str__(self) -> str:
        return f"user-email: {self.profile.user.email} product: {self.product.name}"

    def debug_str(self) -> str:
        return f"Cart obj|\n Profile obj| {self.profile}\n Product obj| {self.product}\n quantity: {self.quantity}, total-price: {self.total_price}, is-stock {self.is_stock}"