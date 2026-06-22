import json
from decimal import Decimal
from typing import Any, cast

from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase

from app_orders.serializers import OrderedItemSerializer, OrderSerializer
from app_orders.models import OrderedItem, Product, Profile, Orders
from app_locations.models import Location
from app_users.models import User
from app_products.models import Cart

# Run this specific test suite with:
# $env:PYTHONUNBUFFERED=1; python .\manage.py test app_orders.tests.test_serializers.OrderedItemSerializerTest --debug-mode

class OrderedItemSerializerTest(TestCase):
    """
    Test suite to validate serialization and deserialization patterns 
    for Orders and OrderedItem schemas.
    """
    
    def setUp(self) -> None:
        """Initializes testing records across required database tables."""
        self.setUser()
        self.setProducts()
        self.setCart()
        self.setOrders()
        self.setOrderedItem()

    def setUser(self) -> None:
        """Generates mock User, Location, and User Profile data."""
        user = User.objects.create(email="john@domain.com", password="john1234")
        user.save()
        user2 = User.objects.create(email="brian@domain.com", password="brian1234")
        user2.save()
        
        location1 = Location(staddr="123 Baker Street", city="Springfield", state="California", hno="42", landmark="Near Central Park", is_homeaddress=True)
        location2 = Location(staddr="12 main Street", city="Autumnfield", state="California", hno="2", landmark="Near Dolphin Park", is_homeaddress=False)
        location1.save()
        location2.save()
        
        self.profile = Profile(user=user, fname="John", lname="Doe", role=Profile.Role.CONSUMER, mobile_no="9876543210", user_Img=None)
        self.profile.save()
        self.profile.location.add(location1, location2)

        self.profile2 = Profile(user=user2, fname="Brian", lname="Doe", role=Profile.Role.CONSUMER, mobile_no="98576543210", user_Img=None)
        self.profile2.save()

    def setProducts(self) -> None:
        """Populates temporary test product catalog instances."""
        self.p1 = Product.objects.create(
            name="Tomato",
            category=Product.ProductCategory.VEGETABLE,
            discription="A juicy, red fruit often treated as a vegetable...",
            price=20,
            stock=100,
            product_Img="images/products/tomato.jpg"
        )
        self.p2 = Product.objects.create(
            name="Potato",
            category=Product.ProductCategory.VEGETABLE,
            discription="A starchy tuber native to South America...",
            price=30,
            stock=200,
            product_Img="images/products/potato.jpg"
        )
        self.p3 = Product.objects.create(
            name="Apple",
            category=Product.ProductCategory.FRUIT,
            discription="A crisp, sweet fruit from the rose family...",
            price=100,
            stock=50,
            product_Img="images/products/Apple.png"
        )
        self.p4 = Product.objects.create(
            name="Banana",
            category=Product.ProductCategory.FRUIT,
            discription="A long, curved tropical fruit...",
            price=60,
            stock=120,
            product_Img="images/products/Banana.png"
        )

    def setCart(self) -> None:
        """Sets up mock active shopping sessions items."""
        self.c3 = Cart.objects.create(profile=self.profile, product=self.p3, quantity=5)

        self.c1 = Cart.objects.create(profile=self.profile2, product=self.p1, quantity=2)
        self.c2 = Cart.objects.create(profile=self.profile2, product=self.p2, quantity=5)
        self.c4 = Cart.objects.create(profile=self.profile2, product=self.p4, quantity=1)

    def setOrders(self) -> None:
        """Saves base root orders calculated from cart prices."""
        self.o1 = Orders.objects.create(
            consumer=self.profile,
            amount=Decimal(self.c3.total_price),
            razorpay_order_id='orderid1',
            payment_status="not_paid"
        )

        self.o2 = Orders.objects.create(
            consumer=self.profile2,
            amount=Decimal(self.c1.total_price + self.c2.total_price + self.c4.total_price),
            razorpay_order_id='orderid2',
            payment_status="not_paid"
        )

    def setOrderedItem(self) -> None:
        """Binds structured line items matching historical orders."""
        self.oi2 = OrderedItem.objects.create(order=self.o2, ordered_item=self.p1, quantity=2, total_price=self.c1.total_price, status="pending")
        self.oi3 = OrderedItem.objects.create(order=self.o2, ordered_item=self.p2, quantity=5, total_price=self.c2.total_price, status="pending")
        self.oi4 = OrderedItem.objects.create(order=self.o2, ordered_item=self.p4, quantity=1, total_price=self.c4.total_price, status="pending")

    def test_serialization_post(self) -> None:
        """Validates incoming client dictionary conversion to data rows."""
        oi_post_data = {
            'order': self.o1.uid,
            'product_id': self.p3.uid,
            'quantity': 5,
            'total_price': self.c3.total_price,
            'status': "pending"
        }

        serializer = OrderedItemSerializer(data=oi_post_data)
        
        print("\n--- [TEST] Executing Deserialization (POST payload validation) ---")
        serializer.is_valid(raise_exception=True)
        print("Validated Data Schema Output:", serializer.validated_data)
        
        order_item = serializer.save()
        print("Saved Model Instance Object:", order_item)
        print("Serialized Output Payload:\n", json.dumps(serializer.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder))

    def test_serialization_get(self) -> None:
        """Validates outgoing raw data parsing for model collections."""
        orders = Orders.objects.all()
        serializer_orders = OrderSerializer(orders, many=True)
        
        print("\n--- [TEST] Executing Serializer Output (GET Collections) ---")
        print("All High-Level Orders Array Payload:\n", json.dumps(serializer_orders.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder))
        print("-" * 50)

        ordered_items = OrderedItem.objects.filter(order=self.o1)
        serializer_items = OrderedItemSerializer(ordered_items, many=True)
        print("Detailed Single Order Nested Items Payload:\n", json.dumps(serializer_items.data, indent=2, sort_keys=False, cls=DjangoJSONEncoder))
        print("-" * 50)