from django.test import TestCase
from app_users.models import User, Profile
from app_locations.models import Location
from app_products.models import Product, Cart
from testing_data.fill_dummy_data import fill_database
#run test using
#python manage.py test app_users.tests.test_models
#python .\manage.py test app_users.tests.test_models.ProfileModelTest.test_profile_location

class UserModelTest(TestCase):

    def test_str_representation(self):
        user = User.objects.create(email ="abc@example.com", password ='a1234')
        print(user.email)
        self.assertEqual(str(user), "user-email:abc@example.com")

    def test_user_obj_values(self):
        user = User.objects.create(email ="abc@example.com", password ='a1234')
        print(user.email)
        print(user.password)
        print()
        #self.assertEqual(str(user), "user-email:abc@example.com")

class ProfileModelTest(TestCase):

    def test_str_representation(self):
        user = User.objects.create(email ="abc@example.com", password ='a1234')
        location = Location.objects.create(staddr = 'heien era', city = 'tokyo', state = 'nigga')
        profile = Profile.objects.create(user = user, location = location)
        print(str(profile))
        print()
        self.assertEqual(str(profile), "user name:  \n user-email: abc@example.com")

    def test_user_obj_values(self):
        user = User.objects.create(email ="abc@example.com", password ='a1234')
        location = Location.objects.create(staddr = 'heien era', city = 'tokyo', state = 'nigga')
        print(str(location))
        profile = Profile.objects.create(
        user = user,
        fname = 'thukuna',
        lname = 'ryomen',
        location = location,
        #role = '1',
        mobile_no = '1234567890')
        p = Profile.objects.filter(mobile_no = 1234567890)
        print(p.values())
        print()
        #self.assertEqual(str(user), "user-email:abc@example.com")

    def test_profile_validation(self):
        user = User.objects.create(email ="abc@example.com", password ='a1234')
        p = Profile.objects.create(user = user, mobile_no = 'abc')
        p.full_clean()

    def test_profile_location(self):
        user = User.objects.create(email = "jhon@domain.com", password = "jhon1234")
        user.save()
        location1 = Location( staddr="123 Baker Street", city="Springfield", state="California", hno="42", landmark="Near Central Park", is_homeaddress = True )
        location2 = Location( staddr="12 main Street", city="Autumnfield", state="California", hno="2", landmark="Near Dolphin Park", is_homeaddress = True )
        location1.save()
        location2.save()
        profile = Profile( user=user, fname="John", lname="Doe", role=Profile.Role.CONSUMER, mobile_no="9876543210", user_Img=None)
        profile.save()
        profile.location.add(location1,location2)
        l = profile.location.filter(is_homeaddress=True)
        print(l)

    def test_location_M2M(self):
        user = User.objects.create(email = "jhon@domain.com", password = "jhon1234")
        user.save()
        location1 = Location( staddr="123 Baker Street", city="Springfield", state="California", hno="42", landmark="Near Central Park", is_homeaddress = True )
        location2 = Location( staddr="12 main Street", city="Autumnfield", state="California", hno="2", landmark="Near Dolphin Park", is_homeaddress = True )
        location1.save()
        location2.save()
        location3, _ = Location.objects.get_or_create( staddr="12 main Street", city="Autumnfield", state="California", hno="2", landmark="Near Dolphin Park", is_homeaddress = True )
        print("newly created: ", _)
        profile = Profile( user=user, fname="John", lname="Doe", role=Profile.Role.CONSUMER, mobile_no="9876543210", user_Img=None)
        profile.save()
        print("before adding same 3rd location to profile")
        profile.location.add(location1,location2)
        l = profile.location.all()
        print(l)
        print("after adding same 3rd location to profile")
        profile.location.add(location3)
        l = profile.location.all()
        print(l)


class CartModelTest(TestCase):
    def setUp(self):
        fill_database()
        self.profile = Profile.objects.get(user__email = 'priya.sharma@example.com')
        self.profile2 = Profile.objects.get(user__email = 'neha.patel@example.com')
        self.p1 = Product.objects.get(name__contains = 'tomato')
        self.p2 = Product.objects.get(name__contains = 'potato')
        self.p3 = Product.objects.get(name__contains = 'carrot')
    
    def test_cart_objects(self):
        Cart.objects.create(profile= self.profile, product= self.p1, quantity=5)
        Cart.objects.create(profile= self.profile, product= self.p2, quantity=10)
        Cart.objects.create(profile= self.profile, product= self.p3, quantity=15)
        Cart.objects.create(profile= self.profile2, product= self.p3, quantity=16)

        p = Cart.objects.filter(profile = self.profile)
        print(p)

        p2 = Cart.objects.filter(profile__user__email = 'priya.sharma@example.com')

        for product in p:
            print(product.product.name, product.quantity, product.product.price, product.total_price)
        """products = self.profile.cart.all()
        for p in products:
            print(p.name, p.price)"""
        

