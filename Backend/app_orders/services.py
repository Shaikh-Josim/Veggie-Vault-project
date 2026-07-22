import logging
import time
from datetime import timedelta
from uuid import UUID
from decimal import Decimal
from typing import cast, Dict, Any, Iterable

import razorpay
from razorpay.errors import ServerError, GatewayError, BadRequestError, SignatureVerificationError

from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from base.exceptions import NotFound, CreateError, UpdateError
from VeggieVault.settings import RAZORPAY_TEST_API_KEY, RAZORPAY_TEST_KEY_SECRET
from app_orders.models import Orders, Payment, Cart, OrderedItem, Product, Refund


logger = logging.getLogger('app_orders')

# Set up the Razorpay client configuration globally
razorpay_client: Any = razorpay.Client(auth=(RAZORPAY_TEST_API_KEY, RAZORPAY_TEST_KEY_SECRET))

class OrderCreationService:
    """
    Service layer class containing core business actions for order processing,
    payment tracking, and error recovery workflow rollbacks.
    """

    @staticmethod
    def create_razorpay_order(amount: float) -> Dict[str, Any]:
        """
        Talks to Razorpay to initialize a unique payment transaction instance.
        """
        try:
            logger.info("Entering razorpay order creation service")
            if not amount:
                raise NotFound("Amount is required to create razorpay order")
            
            # Razorpay expects amounts in paise (multiply by 100)
            razorpay_order = razorpay_client.order.create({
                "amount": int(amount * 100), 
                "currency": "INR", 
                "payment_capture": '1',
            })

            logger.info(f"Razorpay order created successfully with ID: {razorpay_order['id']}")
            logger.info("Leaving razorpay order service")
            return razorpay_order
        except Exception as e:
            logger.exception(str(e))
            raise CreateError("Razorpay order creation failed")
        
    @staticmethod
    def refund_expired_order_payment(razorpay_payment_id:Any):
        """
        
        """
        try:
            logger.info("Entering initiate refund service...")
            logger.info("Arguments validated successfully") if razorpay_payment_id else logger.info("Data missing in arguments")

            if not razorpay_payment_id:
                raise NotFound("payment object needed to do refund")
            
            with transaction.atomic():                
                payment_obj = Payment.objects.select_for_update().get(razorpay_payment_id = razorpay_payment_id)
                
                if Refund.objects.filter(payment= payment_obj, refund_status__in = [Refund.Status.PROCESSED, Refund.Status.PENDING, Refund.Status.INITIATED]).exists():
                    return
                
                # save transaction if razorpay successfully does refund but later transaction fails to add state as processed
                refund_obj = Refund.objects.create(payment = payment_obj, razorpay_refund_id = None, refund_amount = 0, refund_status = Refund.Status.INITIATED)
            
            if refund_obj:
                refund = razorpay_client.payment.refund(razorpay_payment_id) #full refund
                razorpay_refund_id = refund.get('id')
                refund_amount = refund.get('amount')
                refund_status = refund.get('status')
                refund_obj.razorpay_refund_id = razorpay_refund_id; refund_obj.refund_amount = refund_amount
                refund_obj.save()

            with transaction.atomic():
                #create refund obj    
                payment_obj = (Payment.objects.select_for_update().get(uid=payment_obj.uid))
                refund_obj = Refund.objects.select_for_update().get(uid = refund_obj.uid)
                if refund_status == 'processed': #refund complete
                    refund_obj.refund_status = Refund.Status.PROCESSED

                    payment_obj.payment_status = 'refunded'
                    payment_obj.save()
            
                
                elif refund_status == 'pending': # money not received currently by the user
                    refund_obj.refund_status = Refund.Status.PENDING

                elif refund_status == 'failed': 
                    refund_obj.refund_status = Refund.Status.FAILED

                refund_obj.save()
            
            logger.info("leaving initiate refund service...")
        except ValueError as e:
            raise e
        except (ServerError, GatewayError, BadRequestError, SignatureVerificationError) as e:
            print(e)
            raise e
        except Exception as e:
            logger.exception(str(e))
            raise UpdateError("Failed to refund")
    


    @staticmethod
    def process_order_payment(order: Orders, payment: Payment, payment_status: str):
        """
        Updates database records for both Orders and Payments inside 
        an isolated database transaction block based on payment outcome.
        """
        try:
            logger.info("Entering order payment status sync service")
            logger.info("Arguments validated successfully") if order and payment else logger.info("Data missing in arguments")

            if not order:
                raise NotFound("order not found")
            if not payment:
                raise NotFound("payment not found")
            
            # Action: Success pathway
            if payment_status == "captured":
                logger.info("Payment captured successfully. Updating status flags to PAID...")
                if order.order_status != 'paid':
                    with transaction.atomic():
                        payment.payment_status = Payment.Status.CAPTURED
                        payment.save()
                        order.order_status = "paid"
                        order.save()
                        logger.info("Order and Payment records marked as paid successfully")
            
            # Action: Failure pathway
            elif payment_status == "failed":
                logger.info("Payment failure flagged. Updating status flags to UNPAID...")
                with transaction.atomic():
                    payment.payment_status = Payment.Status.FAILED
                    payment.save()
                    order.order_status = "not_paid"
                    order.save()
                    logger.info("Order and Payment records marked as failed successfully")

            logger.info("Leaving order payment status sync service")
        except ValueError as e:
            raise e
        except Exception as e:
            logger.exception(str(e))
            raise CreateError("Payment status update failed")
        
    @staticmethod
    def deduct_stock(cart: Iterable[Cart]):
        """
        deduct cart product's quantity from inventory stock.
        """
        try:
            logger.info("Entering deduct stock service")
            logger.info("Arguments validated successfully") if cart else logger.info("Data missing in arguments")

            if not cart:
                raise NotFound("cart not found")
            
            for item in cart:
                item = cast(Cart, item)
                logger.info(f"product stock before deducting :  {item.product.stock}")
                product = item.product
                product.stock = F('stock') - item.quantity
                #product.stock = product.stock - item.quantity
                product.save()
                #product.refresh_from_db()
                logger.info(f"product stock after deducting :  {product.stock}")

            logger.info("leaving deduct stock service...")
        except ValueError as e:
            raise e
        except Exception as e:
            logger.exception(str(e))
            raise UpdateError("Failed to update stock")
        
    @staticmethod        
    def get_amount_from_cart(cart: Iterable[Cart]) -> tuple[ Decimal, list[UUID]]:
        """
        Takes active cart items and calculates the total price.
        """
        try:
            logger.info("Entering calculate total price of cart's products utility")
            
            # Check if any required data is missing from the arguments
            logger.info("Arguments validated successfully") if cart else logger.info("Required data missing in arguments")
            
            if not cart:
                raise NotFound("cart needed to calculate total amount for order")
            
            #extracting products id from cart
            logger.info(f"Extracting products id...")
            products_id = [item.product.uid for item  in cart]
            logger.info(f"product id extracted \n products_ids: {products_id}")
            
            amount = Decimal(0)
            # calculating total price
            logger.warning(f"cart {cart}")
            for items in cart:
                items = cast(Cart, items)
                amount += items.total_price

            logger.info(f"Source cart instances: {cart}")
            logger.info(f"Generated products amount-> amount: {amount}")
            logger.info("Leaving cart's products total price utility")
            
            return amount, products_id
            
        except ValueError as e:
            raise e
        except Exception as e:
            logger.exception(f"failed to calculate total price of products in cart {e}")
            raise CreateError("failed to calculate total price of products in cart")

    @staticmethod        
    def is_cart_products_stock_available(cart: Iterable[Cart]) -> bool:
        """
        Takes active cart items and check if stock available for purchase.
        """
        try:
            logger.info("Entering checking cart's products stock availability..")
            
            # Check if any required data is missing from the arguments
            logger.info("Arguments validated successfully") if cart else logger.info("Required data missing in arguments")
            
            if not cart:
                raise NotFound("cart needed to check products stock availability for order")
            
            """res = None
            if hasattr(cart, '_result_cache'):
                res =  cart._result_cache

            print("cached queryset:\t", res)                  
            print('\n\n\n\n\n\n\n\n\n\n\n\n')"""
        
            # checking stock of products
            logger.info(f"Source cart instances: {cart}")

            
            for items in cart:
                items = cast(Cart, items)

                stock_available = items.is_stock
                logger.info(f" requested stock quantity: {items.quantity}, product stock: {items.product.stock}")
                logger.info(f"item: {items.product.name}, stock-available: {stock_available}")
                
                if not stock_available:
                    logger.info("Leaving cart's products total price utility")
                    return stock_available
            
            return stock_available
            
        except ValueError as e:
            raise e
        except Exception as e:
            logger.exception(f"failed to check stock availability of products in cart \n{e}")
            raise CreateError("failed to check stock availability of products in cart")
        
    @staticmethod
    def get_products_from_cart(cart: Iterable[Cart], order: Orders) -> list[Dict[str, Any]]:
        """
        Takes active cart items and converts them into a clean list of 
        dictionaries formatted for the OrderedItemSerializer.
        """
        try:
            logger.info("Entering cart data conversion utility")
            
            # Check if any required data is missing from the arguments
            logger.info("Arguments validated successfully") if order and cart else logger.info("Required data missing in arguments")
            
            if not cart:
                raise NotFound("cart needed to add products in order")
            
            if not order:
                raise NotFound("order not found to add products")
            
            products_data = []
            for items in cart:
                items = cast(Cart, items)
                # Format the data into fields matching the OrderedItem model schema
                products_data.append({
                    'order': order.uid,
                    'product_id': items.product.uid,
                    'quantity': items.quantity,
                    'total_price': items.total_price,
                    'item_status': "pending"
                })            

            logger.info(f"Source cart instances: {cart}")
            logger.info(f"Generated product payload -> products: {products_data}")
            logger.info("Leaving cart conversion utility")
            
            return products_data
            
        except ValueError as e:
            raise e
        except Exception as e:
            logger.exception(f"Cart conversion failed due to a system error: {e}")
            raise CreateError("Cart conversion failed")
        
    @staticmethod
    def get_products_from_ordereditem(ordered_items: Iterable[OrderedItem]) -> list[Dict[str, Any]]:
        """
        Takes saved ordered items and converts them back into a clean list 
        of dictionaries formatted for the CartSerializer (used during payment rollbacks).
        """
        try:
            logger.info("Entering ordered items data conversion utility")
            
            # Check if any required data is missing from the arguments
            logger.info("Ordered items found in arguments") if ordered_items else logger.info("Ordered items data missing in arguments")
            
            if not ordered_items:
                raise NotFound("ordered items not found to add products back to cart")
            
            products_data = []
            for items in ordered_items:
                items = cast(OrderedItem, items)
                # Format the data into fields matching the Cart model schema
                products_data.append({
                    "profile_id": str(items.order.consumer.uid),
                    "product_id": str(items.ordered_item.uid), 
                    "quantity": items.quantity
                })            

            logger.info(f"Source ordered item instances: {ordered_items}")
            logger.info(f"Generated cart dictionary payload: {products_data}")
            logger.info("Leaving ordered items conversion utility")
            
            return products_data
            
        except ValueError as e:
            raise e
        except Exception as e:
            logger.exception(f"failed to prepare products data \n {e}")
            raise CreateError("failed to prepare products data")
        

    @staticmethod
    def reroll_stock(products: Iterable[Product], data_containing_quantity:Dict[str, str]):
        """
        rerolls product's quantity from inventory stock.
        """
        try:
            logger.info("Entering reroll stock service")
            logger.info("Arguments validated successfully") if products and data_containing_quantity else logger.info("Data missing in arguments")

            if not products:
                raise NotFound("Products needed to reroll the stock")
            if not data_containing_quantity:
                raise NotFound("data containing products quantity needed to reroll the stock")
            
            with transaction.atomic():
                for product in products:
                    logger.info(f"product stock before restocking :  {product.stock}")
                    product.stock = F('stock') + data_containing_quantity.get(str(product.uid))
                    product.save()
                    logger.info(f"product stock after restocking :  {product.stock}")

            logger.info("leaving reroll stock service...")
        except ValueError as e:
            raise e
        except Exception as e:
            logger.exception(str(e))
            raise UpdateError("Failed to update stock")

    @staticmethod        
    def expire_stale_orders(order_id: str):
        """
        Set Orders status as Expired in Database to handle ghost orders.
        """
        try:
            
            logger.info("Entering expire stale orders service")
            
            current_time = timezone.now()
            with transaction.atomic():

                # 1. filter objs which are 30 min olders ("representing orders were left and wasnt paid") and make order status as expired
                order_obj = cast(Orders,Orders.objects.filter(razorpay_order_id = order_id, order_status = 'not_paid', payment_mode = 'online', created_at__lt = current_time - timedelta(minutes= 30)).first())
                print("order object: ", order_obj)
                if not order_obj:
                    print("There is no order record for expiration..")
                    return
                order_obj.order_status = 'expired'
                order_obj.save()
                
                # 2. fetch items which were ordered 10 min ago and make them expired
                ordered_items_objs = list(OrderedItem.objects.filter(order_id = order_obj.uid, item_status = 'pending' , created_at__lt = timezone.now()- timedelta(minutes= 30)))
                if not ordered_items_objs:
                    print("There is no ordered items record for expiration..")
                    return
                for item in ordered_items_objs:
                    item.item_status = 'expired'
                print("ordered items:", ordered_items_objs)
                OrderedItem.objects.bulk_update( ordered_items_objs, fields=['item_status'], batch_size=500 )
                print("ordered items:", ordered_items_objs)

                # 3. restock products for expired order, 
                #   -> get products details using ordered items, 
                #   -> lock and update stock value of products
                extracted_products_data = OrderCreationService.get_products_from_ordereditem(ordered_items= ordered_items_objs)
                products_data = cast(Dict[str, str], {product.get('product_id'):product.get('quantity') for product in extracted_products_data})
                products_id = list(products_data.keys())

                locked_products = Product.objects.select_for_update().filter(uid__in = sorted(products_id))
                if not len(locked_products) == len(products_id):
                    print("Cant lock every required product for update")
                    return
                print("following products are locked for update: ",locked_products)
                OrderCreationService.reroll_stock(locked_products, products_data)

            logger.info("leaving expire stale orders service")
            
        except ValueError as e:
            raise e
        except Exception as e:
            logger.exception(f"failed to prepare products data \n {e}")
            raise CreateError("failed to prepare products data")

