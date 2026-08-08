
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager 
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password, check_password

from base.models import BaseModel
from app_locations.models import Location
from app_products.models import Product


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

name_validator = RegexValidator(
    regex = r'^[A-Za-z]+',
    message = "only letters are valid")

mobile_no_validator = RegexValidator(
    regex = r'^[0-9]{10,}',
    message = "only numbers are valid and only 10 digits are allowed")

email_validator = RegexValidator(
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
    message = 'invalid email')

email_verification_code_validator = RegexValidator(
    regex = r'^[A-Za-z0-9]{6,}',
    message = "only numbers and letters are valid")

class User(BaseModel, AbstractBaseUser, PermissionsMixin):    
    class Meta:
        verbose_name = "user"
    email = models.EmailField(verbose_name='email',max_length=50, unique=True, null= False, validators=[email_validator])
    password = models.CharField(verbose_name='password',max_length=128, null= False)

    
    is_staff = models.BooleanField(default=False) 
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    USERNAME_FIELD = "email"              
    REQUIRED_FIELDS = []      

    objects = UserManager()

    def set_password(self, raw_password: str):
        self.password = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        # Hash only if it's not already hashed (naive check: hashed strings start with 'pbkdf2_...')
        if self.password and not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"user-email:{self.email}"

class Profile(BaseModel):

    class Meta:
        verbose_name = "profile"

    class Role(models.IntegerChoices):
        WORKER = 2, "Worker"
        CONSUMER = 3, "Consumer"
        ADMIN = 1, "Admin"

    user = models.OneToOneField(User,verbose_name='user', on_delete=models.CASCADE, related_name= 'profile', related_query_name= 'user_profile')

    fname = models.CharField(verbose_name='first name',max_length=30, null= False , default='', validators=[name_validator])
    lname = models.CharField(verbose_name='last name',max_length=30, null= False, default= '', validators=[name_validator])
    location = models.ManyToManyField(Location,verbose_name='location', related_name="location", blank = True, default=None)

    role = models.IntegerField(verbose_name='role',choices=Role.choices,default=Role.CONSUMER)
    mobile_no = models.CharField(verbose_name='mobile no.',max_length=10, unique=True, null = True, blank=True, validators=[mobile_no_validator])

    user_Img = models.ImageField(verbose_name='profile image',upload_to='images/users/', null=True, blank=True)
    cart = models.ManyToManyField(Product, through= 'app_products.Cart', related_name= 'profiles', blank=True, default= None)

    def __str__(self) -> str:
        return f"user name: {self.fname} {self.lname}\n user-email: {self.user.email}"

    def __debug_str__(self) -> str:
        return f"Profile obj | firstname: {self.fname}, lastname: {self.lname}, role: {self.role} role-name: {self.get_role_display()}, mobile no: {self.mobile_no}, user-img: {self.user_Img},\n User obj| user: {self.user}\n Location obj| location: {list(self.location.all()[:3])}\n Cart obj| cart {list(self.cart.all()[:3])}" #type: ignore[attr-defined]


class EmailVerificationCode(BaseModel):
    class Meta:
        verbose_name = "emailverificationcode"
    user = models.ForeignKey(User, on_delete= models.CASCADE, related_name= 'emailvrcode', related_query_name='email_vrcode')
    code = models.CharField(verbose_name='verification code', max_length=6, null= False,  validators=[email_verification_code_validator])
    expires_at = models.DateTimeField() 
    is_used = models.BooleanField(default=False)

    def is_valid(self): 
        return not self.is_used and timezone.now() < self.expires_at

    def __str__(self) -> str:
        return f"email code: {self.code}, expires at {self.expires_at}"

    def __debug_str__(self) -> str:
        return f"Email obj| email code: {self.code}, expires at {self.expires_at}, is_used {self.is_used}\n User obj| {self.user}"
