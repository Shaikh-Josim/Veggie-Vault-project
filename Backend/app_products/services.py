import string, random, logging
from typing import cast, Dict, Any, Tuple, Optional

from django.db import transaction, IntegrityError
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework.exceptions import APIException, NotFound

from base.exceptions import *
from .models import Cart, Product
from app_users.models import Profile

logger = logging.getLogger('app_products')




def add_to_cart(profile:Profile, data:Dict[str,Any])-> Cart|None:
    try:
        logger.info("Entering in cart service")
        logger.info(data)
        product = cast(Product,data['product'])
        quantity = data.get("quantity")

        logger.info("Got product") if product else logger.info("Product name missing")

        if not profile:
            raise NotFound("profile not found")
        
        with transaction.atomic():
            product = Product.objects.get(uid = product.uid)
            cart, created = Cart.objects.get_or_create(profile= profile, product= product, quantity = quantity)
            logger.info("Product added to cart successfully")

        logger.info("Leaving service..")
        return cart
    except ValueError as e:
        print(e, flush= True)
    except Product.DoesNotExist:
        raise NotFound("Product which need to be added is not found")
    except Exception as e:
        logger.exception(str(e))
        raise CreateError("Product addation Failed")
    
def remove_from_cart(profile:Profile, data:Dict[str,Any])-> Cart|None:
    try:
        logger.info("Entering in cart service")
        product_id = data['product']
        quantity = data.get("quantity")

        logger.info("Got product id") if product_id else logger.info("Product name missing")

        if not profile:
            raise NotFound("profile not found")
        
        with transaction.atomic():
            product = Product.objects.get(uid = product_id)
            cart, created = Cart.objects.get_or_create(profile= profile, product= product, quantity = quantity)
            logger.info("Product added to cart successfully")

        logger.info("Leaving service..")
        return cart
    except ValueError as e:
        print(e, flush= True)
    except Product.DoesNotExist:
        raise NotFound("Product which need to be added is not found")
    except Exception as e:
        logger.exception(str(e))
        raise CreateError("Product addation Failed")