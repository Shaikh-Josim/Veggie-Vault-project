import os, sys
from typing import cast
import django
from django.contrib.auth.hashers import make_password

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "VeggieVault.settings")
django.setup()

from app_locations.models import Location
from app_users.models import User, Profile
from app_products.models import Product, Cart
from app_orders.models import Orders, OrderedItem

def fill_locations():
    locations_data = [
        ("12A", "Main Street", "Near Park", "Ajmer", "Rajasthan"),
        ("45B", "Lake Road", "Opposite Temple", "Jaipur", "Rajasthan"),
        ("78C", "Market Lane", "Beside School", "Udaipur", "Rajasthan"),
        ("101", "Tech Park Road", "Near Mall", "Ajmer", "Rajasthan"),
        ("22D", "Station Road", "Close to Bus Stand", "Kota", "Rajasthan"),
        ("33E", "College Street", "Near Library", "Bikaner", "Rajasthan"),
        ("56F", "Garden Avenue", "Opposite Hospital", "Jodhpur", "Rajasthan"),
        ("89G", "Hill View", "Near Fort", "Mount Abu", "Rajasthan"),
        ("77H", "Airport Road", "Close to Airport", "Jaipur", "Rajasthan"),
        ("99I", "River Side", "Near Bridge", "Chittorgarh", "Rajasthan"),
    ]

    for hno, staddr, landmark, city, state in locations_data:
        Location.objects.create(
            hno=hno,
            staddr=staddr,
            landmark=landmark,
            city=city,
            state=state,
        )
        

    print("✅ Inserted 10 dummy locations into SQLite DB")
def fill_users():
    # Get all locations (assuming you already inserted 10)
    locations = list(Location.objects.all())
    if len(locations) < 10:
        print("❌ Need at least 10 locations before creating users.")
        return

    users_data = [
        ("amit.verma@example.com"),
        ("priya.sharma@example.com"),
        ("ravi.kumar@example.com"),
        ("neha.patel@example.com"),
        ("arjun.mehta@example.com"),
        ("kiran.joshi@example.com"),
        ("deepak.singh@example.com"),
        ("meera.rao@example.com"),
        ("vikram.nair@example.com"),
        ("anita.desai@example.com"),
    ]

    for i, email in enumerate(users_data):
        User.objects.create(
            email=email,
            password=make_password("test1234")
        )

    print("✅ Inserted 10 dummy users into SQLite DB")

def fill_profiles():
    users = list(User.objects.all())
    if len(users) < 10:
        print("❌ Need at least 10 users before creating users.")
        return
    
    locations = list(Location.objects.all())
    if len(locations) < 10:
        print("❌ Need at least 10 Locations before creating users.")
        return
    
    profiles_data = [
        ("Amit", "Verma", "9876500001", Profile.Role.CONSUMER),
        ("Priya", "Sharma", "9876500002", Profile.Role.WORKER),
        ("Ravi", "Kumar", "9876500003", Profile.Role.ADMIN),
        ("Neha", "Patel", "9876500004", Profile.Role.CONSUMER),
        ("Arjun", "Mehta", "9876500005", Profile.Role.WORKER),
        ("Kiran", "Joshi", "9876500006", Profile.Role.CONSUMER),
        ("Deepak", "Singh", "9876500007", Profile.Role.ADMIN),
        ("Meera", "Rao", "9876500008", Profile.Role.CONSUMER),
        ("Vikram", "Nair", "9876500009", Profile.Role.WORKER),
        ("Anita", "Desai", "9876500010", Profile.Role.CONSUMER),
    ]
    for i, (fname, lname, mobile, role) in enumerate(profiles_data):
        profile = Profile.objects.create(
            fname=fname,
            lname=lname,
            mobile_no=mobile,
            role=role,
            user=users[i],  # assign each profile to a different user
        )
        profile.location.add(locations[i])

    print("✅ Inserted 10 dummy profiles into SQLite DB")

def fill_products():
    # 5 Vegetables
    vegetables = [
        ("Tomato", "A juicy, red fruit often treated as a vegetable, tomatoes are rich in vitamin C and lycopene. They are versatile in cooking, used fresh in salads, sauces, and soups", 20, 100, "images/products/tomato.jpg"),
        ("Potato", "A starchy tuber native to South America, potatoes are one of the world’s staple foods. They come in many varieties and are used boiled, mashed, fried, or baked", 30, 200, "images/products/potato.jpg"),
        ("Onion", "A bulb vegetable with a pungent flavor, onions are widely used to add taste to dishes. They can be eaten raw, sautéed, or caramelized, and are valued for their aromatic oils", 25, 150, "images/products/Onion.png"),
        ("Carrot", "A crunchy root vegetable, typically orange but also found in purple, yellow, or red varieties. Carrots are sweet, nutritious, and high in beta‑carotene, supporting eye health", 40, 120, "images/products/Carrot.png"),
        ("Cabbage", "A leafy vegetable forming dense heads, available in green, red, or savoy varieties. Cabbage is low in calories, high in fiber, and commonly used in salads, stir‑fries, and soups",35, 80, "images/products/Cabbage.png"),
    ]

    # 5 Fruits
    fruits = [
        ("Apple", "A crisp, sweet fruit from the rose family, apples are one of the most widely cultivated fruits worldwide. They are eaten fresh, baked, or juiced, and are rich in fiber and vitamin C.", 100, 50, "images/products/Apple.png"),
        ("Banana", "A long, curved tropical fruit with soft, sweet flesh and a yellow peel when ripe. Bananas are high in potassium and energy, making them a popular snack and smoothie ingredient.",60, 120, "images/products/Banana.png"),
        ("Orange", "A citrus fruit with bright orange skin and juicy flesh, oranges are prized for their refreshing taste and high vitamin C content. They are eaten fresh or juiced.",80, 90, "images/products/orange.jpg"),
        ("Mango", "A tropical stone fruit with sweet, aromatic flesh ranging from golden yellow to orange. Mangoes are rich in vitamins A and C and are widely enjoyed fresh or in desserts.",120, 70, "images/products/mango.jpg"),
        ("Grapes", "Small, juicy berries that grow in clusters on vines, grapes can be eaten fresh, dried (raisins), or used in winemaking. They are rich in antioxidants and natural sugars",90, 100, "images/products/Grapes.png"),
    ]

    # Insert vegetables
    for name, discription, price, stock, product_Img in vegetables:
        Product.objects.create(
            name=name,
            category=Product.ProductCategory.VEGETABLE,
            discription = discription,
            price=price,
            stock=stock,
            product_Img = product_Img
        )

    # Insert fruits
    for name, discription, price, stock, product_Img in fruits:
        Product.objects.create(
            name=name,
            category=Product.ProductCategory.FRUIT,
            discription = discription,
            price=price,
            stock=stock,
            product_Img = product_Img
        )

    print("✅ Inserted 5 vegetables and 5 fruits into Product table")

def fill_carts():
    profiles = list(Profile.objects.all()[:3]) 
    products = list(Product.objects.all())[:3]
    
    if len(profiles) < 3 or len(products) < 3:
        print("❌ Need at least 3 users, 3 products, before creating carts.")
        return
    
    carts_data = [
        # consumer, product, quantity
        (profiles[0], products[0], 2,),
        (profiles[0], products[1], 5, ),
        (profiles[0], products[2], 5, ),
        (profiles[1], products[2], 1, ),
    ]

    for profile, product, qty in carts_data:
        Cart.objects.create(
            profile=profile,
            product=product,
            quantity=qty,
        )

    print("✅ Inserted 4 dummy cart items into Cart table")

def fill_orders():
    # Grab some existing users, products, and locations
    profiles = list(Profile.objects.all()[:3])
    products = list(Product.objects.all()[:3])
    print(products)

    if len(profiles) < 3 or len(products) < 3:
        print("❌ Need at least 3 users, 3 products, and 3 locations before creating orders.")
        return

    orders_data = [
        (profiles[0], (int(products[0].price)*2+ int(products[1].price)*2)),
        (profiles[1], products[2].price*3)
        ]
    
    for consumer, amount in orders_data:
        Orders.objects.create(
            consumer=consumer,
            amount = amount
        )

    print("✅ Inserted 3 dummy orders into Orders table")


def fill_ordered_items():
    orders = list(Orders.objects.all()[:2])
    products = list(Product.objects.all()[:3])
    print(products)
    
    OrderedItem.objects.create(
        order=orders[0],
        ordered_item=products[0],
        quantity=2,
        total_price=products[0].price*2,
        status="delivered"
    )
    OrderedItem.objects.create(
        order=orders[0],
        ordered_item=products[1],
        quantity=2,
        total_price=products[1].price*2,
        status="delivered"
    )

    OrderedItem.objects.create(
        order=orders[1],
        ordered_item=products[2],
        quantity=3,
        total_price=products[2].price*3,
        status="pending"
    )

    print("✅ Inserted 3 dummy ordered item into Orders table")

def fill_database():
    fill_locations()
    fill_users()
    fill_profiles()
    fill_products()
    fill_carts()
    fill_orders()
    fill_ordered_items()
    user = User.objects.create(
        email='admin@example.com',
        password=make_password("admin24"),
        is_superuser = True,
        is_staff = True
        )
    profile = Profile.objects.create(
        fname='admin',
        lname='',
        mobile_no='1232131231',
        role=1,
        user = user
        )
    l = Location.objects.first()
    l = cast(Location, l)
    l.is_homeaddress = True
    l.save()
    profile.location.add(l)
    
def clear_database():
    Location.objects.all().delete()
    User.objects.all().delete()
    Profile.objects.all().delete()
    Product.objects.all().delete()
    Orders.objects.all().delete()
    OrderedItem.objects.all().delete()

if __name__ == "__main__":
    clear_database()
    fill_database()
    