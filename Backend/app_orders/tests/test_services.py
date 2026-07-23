
from django.test.utils import CaptureQueriesContext
from django.db import connection

from django.utils.crypto import get_random_string
from django.test import TestCase
from rest_framework.test import APIClient


from app_users.models import User, Profile
from app_products.models import Product, Cart
from app_locations.models import Location
from app_orders.models import Orders, OrderedItem, Payment

import logging

logger = logging.getLogger('app_orders')

from app_orders.services import OrderCreationService




# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_cases.OrderOperationsTest --debug-mode
class InspectServiceTest(TestCase):
    def setUp(self) -> None:
        self.setUser()
        self.setProducts()
        self.setCart()
        self.setOrder()
        self.setOrderedItem()
               
    def setUser(self)   -> None:
        self.client = APIClient()
        self.user = User.objects.create(email = "jhon@domain.com", password = "jhon1234")
        self.user.save()
        self.user2 = User.objects.create(email = "brian@domain.com", password = "brian1234")
        self.user2.save()
        location1 = Location( staddr="123 Baker Street", city="Springfield", state="California", hno="42", landmark="Near Central Park", is_homeaddress = True )
        location2 = Location( staddr="12 main Street", city="Autumnfield", state="California", hno="2", landmark="Near Dolphin Park", is_homeaddress = False )
        location1.save()
        location2.save()
        self.profile = Profile( user=self.user, fname="John", lname="Doe", role=Profile.Role.CONSUMER, mobile_no="9876543210", user_Img=None)
        self.profile.save()
        self.profile.location.add(location1,location2)

        self.profile2 = Profile( user=self.user2, fname="Brian", lname="Doe", role=Profile.Role.CONSUMER, mobile_no="98576543210", user_Img=None)
        self.profile2.save()

    def setProducts(self):
        self.p1 = Product.objects.create(
            name="Tomato",
            category=Product.ProductCategory.VEGETABLE,
            discription = "A juicy, red fruit often treated as a vegetable, tomatoes are rich in vitamin C and lycopene. They are versatile in cooking, used fresh in salads, sauces, and soups,",
            price=20,
            stock=100,
            product_Img = "images/products/tomato.jpg"
        )
        self.p2 = Product.objects.create(
            name="Potato",
            category=Product.ProductCategory.VEGETABLE,
            discription = "A starchy tuber native to South America, potatoes are one of the world’s staple foods. They come in many varieties and are used boiled, mashed, fried, or baked",
            price=30,
            stock=200,
            product_Img = "images/products/potato.jpg"
        )
        self.p3 = Product.objects.create(
            name="Apple",
            category=Product.ProductCategory.FRUIT,
            discription = "A crisp, sweet fruit from the rose family, apples are one of the most widely cultivated fruits worldwide. They are eaten fresh, baked, or juiced, and are rich in fiber and vitamin C.",
            price=100,
            stock=50,
            product_Img = "images/products/Apple.png"
        )
        self.p4 = Product.objects.create(
            name="Banana",
            category=Product.ProductCategory.FRUIT,
            discription = "A long, curved tropical fruit with soft, sweet flesh and a yellow peel when ripe. Bananas are high in potassium and energy, making them a popular snack and smoothie ingredient.",
            price=60,
            stock=120,
            product_Img = "images/products/Banana.png"
        )

    def setCart(self):
        self.c3 = Cart.objects.create(profile=self.profile,product=self.p3,quantity=5)
        self.c1 = Cart.objects.create(profile=self.profile2,product=self.p1,quantity=2)
        self.c2 = Cart.objects.create(profile=self.profile2,product=self.p2,quantity=5)
        self.c4 = Cart.objects.create(profile=self.profile2,product=self.p4,quantity=1)

    def setOrder(self):
        print(Orders.objects.all())
        self.o1 = Orders.objects.create(
            consumer=self.profile,
            amount = self.c3.total_price,
            razorpay_order_id = 'order_'+ get_random_string(14),
            payment_status = 'paid'

        )
        print(Orders.objects.all())

    def setOrderedItem(self):
        pass
        OrderedItem.objects.create(
        order=self.o1,
        ordered_item=self.p3,
        quantity=5,
        total_price=self.p3.price*5,
    )

    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_services.InspectServiceTest.test_inspect_service_queries --debug-mode
    def test_inspect_service_queries(self):
        logger.info("Entering in 'get_amount_from_cart' query test")
        
        with CaptureQueriesContext(connection) as ctx:
            # unoptimized query
            #get_amount_from_cart(cart= Cart.objects.filter(profile=self.profile))
            
            # optimized query
            OrderCreationService.get_amount_from_cart(cart= Cart.objects.select_related('profile__user', 'product').filter(profile=self.profile))

        # 2. Get the total number of database hits
        total_queries = len(ctx)
        logger.info(f"total executed queries: {total_queries}")

        print("\n--- EXECUTED SQL QUERIES---")
        for index, query in enumerate(ctx.captured_queries, start=1):
            print(f"\nQuery #{index}:")
            print(query['sql'])  # This prints the raw SQL string
            
        print("\n--- EXECUTED SQL QUERIES END ---")
        
        # 3. Fail the test if it hits the N+1 problem
        self.assertLess(
            total_queries, 
            5, 
            f"Alert! Service made {total_queries} queries. It is likely unoptimized!"
        )
    
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_services.InspectServiceTest.test_amount_fetcher --debug-mode
    """def test_amount_fetcher(self):
    OrderCreationService.expire_stale_orders(order_id= order_id)"""