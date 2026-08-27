from uuid import uuid4
import json
import copy 
from typing import cast
import hmac, hashlib
from config.settings.settings_test import RAZORPAY_TEST_KEY_SECRET, RAZORPAY_WEBHOOK_SECRET

from django.test import TestCase
from django.utils import timezone
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO

from app_locations.models import Location
from app_users.models import User, Profile, EmailVerificationCode
from app_products.models import Product, Cart
from app_orders.models import Orders, OrderedItem, Payment, Refund
from base.helpers import pop_update_dict_data

def get_test_img(name):
    image_obj = Image.new("RGB", (100, 100), "red")
    buffer = BytesIO()
    image_obj.save(buffer, format="JPEG")
    buffer.seek(0)  # rewind to start!
    return SimpleUploadedFile(
        f"{name}.jpg",
        buffer.read(),
        content_type="image/jpeg"
    )

def get_payment_signature(razorpay_order_id, razorpay_payment_id):
    secret = cast(str,RAZORPAY_TEST_KEY_SECRET)
    signature = hmac.new(
        secret.encode(),
        f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
        hashlib.sha256
    ).hexdigest()
    return signature

def get_webhook_signature(webhook_data):
    secret = cast(str, RAZORPAY_WEBHOOK_SECRET)
    payload = webhook_data
    
    body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)

    signature = hmac.new(
        key= secret.encode(),
        msg= body.encode(),
        digestmod= hashlib.sha256
        ).hexdigest()
    
    print(signature)

    return signature
        

user1_data = {"email": "abc@example.com", "password": "abc12345"}
user2_data = {"email": "xyz@example.com", "password": "xyz12345"}

location1_data = { "staddr": "123 Baker Street", "city": "Springfield", "state": "California", "hno": "42", "landmark": "Near Central Park", "is_homeaddress": True }
location2_data = {"staddr":"12 main Street","city":"Autumnfield", "state":"California", "hno":"2", "landmark":"Near Dolphin Park", "is_homeaddress": True }
location3_data = {'staddr': '34 circle road', 'city': 'Autumnfield', 'state': 'California', 'hno': '2', 'landmark': 'Near Dolphin Park', 'is_homeaddress': True}

profile1_data = { "fname" : 'abc', "lname" : 'xyz', "role" : 3, "mobile_no" : '1234567890', "user_Img" : None} 
profile2_data = { "fname" : 'xyz', "lname" : 'abc', "role" : 3, "mobile_no" : '0987654321', "user_Img" : None} 

email_vc_data = {"code": 'abc123', "expires_at": timezone.now()+timezone.timedelta(minutes= 2)}

product1_data = {'name':"Tomato", 'description':"A juicy, red fruit often treated as a vegetable, tomatoes are rich in vitamin C and lycopene. They are versatile in cooking, used fresh in salads, sauces, and soups", "price": 20, "stock": 100, 'product_Img': ''}
product2_data = {'name':"Potato", 'description':"A starchy tuber native to South America, potatoes are one of the world’s staple foods. They come in many varieties and are used boiled, mashed, fried, or baked", "price": 25, "stock": 200, 'product_Img': ''}
product3_data = { "name":"Apple", "category":2, "description": "A crisp, sweet fruit from the rose family, apples are one of the most widely cultivated fruits worldwide. They are eaten fresh, baked, or juiced, and are rich in fiber and vitamin C.", "price":100, "stock":50, "product_Img": ''}
product4_data = { "name":"Banana", "category": 2, "description" : "A long, curved tropical fruit with soft, sweet flesh and a yellow peel when ripe. Bananas are high in potassium and energy, making them a popular snack and smoothie ingredient.", "price":50, "stock":120, "product_Img": ''}

cart1_data = {'quantity': 25}
cart2_data = {'quantity': 20}
cart3_data = {'quantity': 5}
cart4_data = {'quantity': 10}

order1_data = {'amount': 500, 'razorpay_order_id': 'order_1', 'order_status':'paid', 'payment_mode': 'offline'}
order2_data = {'amount': 500, 'razorpay_order_id': 'order_2', 'order_status':'not_paid', 'payment_mode': 'offline'}
order3_data = {'amount': 500, 'razorpay_order_id': 'order_3', 'order_status':'paid', 'payment_mode': 'online'}
order4_data = {'amount': 500, 'razorpay_order_id': 'order_4', 'order_status':'not_paid', 'payment_mode': 'online'}

ordereditem1_data = {'quantity': 25, 'total_price': 500, 'item_status':'delivered'}
ordereditem2_data = {'quantity': 20, 'total_price': 500, 'item_status':'pending'}
ordereditem3_data = {'quantity': 5,  'total_price': 500, 'item_status':'pending'}
ordereditem4_data = {'quantity': 10, 'total_price': 500, 'item_status':'pending'}

payment1_data = {'razorpay_payment_id': 'payment_1', 'razorpay_signature':'signature1', 'payment_status':'captured'}
payment2_data = {'razorpay_payment_id': 'payment_2', 'razorpay_signature':'signature2', 'payment_status':'captured'}
payment3_data = {'razorpay_payment_id': 'payment_3', 'razorpay_signature':'signature3', 'payment_status':'captured'}
payment4_data = {'razorpay_payment_id': 'payment_4', 'razorpay_signature':'signature4', 'payment_status':'created'}

refund1_data = {'razorpay_refund_id': 'rfnd_1', 'refund_amount':'500', 'refund_status':'processed'}

class UserModelTests(TestCase):
    def tearDown(self):
        for product in Product.objects.all():
            if product.product_Img:
                product.product_Img.delete(save=False)

        super().tearDown()
    def test_create_user_with_uuid(self):
        u = User.objects.create(**user1_data)
        print(u.debug_str())
        p = Profile.objects.create(user = u, **profile1_data)
        print(p.debug_str())
        e = EmailVerificationCode.objects.create(user = u, **email_vc_data)
        print(e.debug_str())
        pd = Product.objects.create(**pop_update_dict_data(copy.deepcopy(product1_data), overrides={'product_Img': get_test_img(product1_data['name'])}))
        print(pd.debug_str())
        c = Cart.objects.create(profile = p, product = pd, **cart1_data)
        print(c.debug_str())
        l = Location.objects.create(**location1_data)
        print(l.debug_str())
        o = Orders.objects.create(consumer = p, **order1_data)
        print(o.debug_str())
        oi = OrderedItem.objects.create(order = o, ordered_item = pd, **ordereditem1_data)
        print(oi.debug_str())
        pt = Payment.objects.create(order = o, **payment1_data)
        print(pt.debug_str())
        r = Refund.objects.create(payment = pt, **refund1_data)
        print(r.debug_str())

        u.full_clean(); p.full_clean(); e.full_clean(); pd.full_clean(); c.full_clean(); l.full_clean(); o.full_clean(); oi.full_clean(); pt.full_clean(); r.full_clean(); 
        
        