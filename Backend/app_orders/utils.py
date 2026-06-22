import logging
from typing import cast, Dict, Any

from base.exceptions import NotFound, CreateError
from app_orders.models import OrderedItem, Orders
from app_products.models import Cart

logger = logging.getLogger('app_orders')

# ==========================================
# DATA TRANSFORMATION UTILITIES
# ==========================================

def get_products_from_cart(cart, order: Orders) -> list[Dict[str, Any]]:
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
                'status': "pending"
            })            

        logger.info(f"Source cart instances: {cart}")
        logger.info(f"Generated product dictionary payload: {products_data}")
        logger.info("Leaving cart conversion utility")
        
        return products_data
        
    except ValueError as e:
        raise e
    except Exception as e:
        logger.exception(str(e))
        raise CreateError("failed to prepare products data")


def get_products_from_ordereditem(ordered_items) -> list[Dict[str, Any]]:
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
        logger.exception(str(e))
        raise CreateError("failed to prepare products data")