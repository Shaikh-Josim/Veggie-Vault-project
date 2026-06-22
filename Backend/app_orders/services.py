import logging
from typing import cast, Dict, Any

import razorpay
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from base.exceptions import NotFound, CreateError
from VeggieVault.settings import RAZORPAY_TEST_API_KEY, RAZORPAY_TEST_KEY_SECRET
from app_orders.models import Orders, Payment


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
                "payment_capture": '1'
            })

            logger.info(f"Razorpay order created successfully with ID: {razorpay_order['id']}")
            logger.info("Leaving razorpay order service")
            return razorpay_order
        except Exception as e:
            logger.exception(str(e))
            raise CreateError("Razorpay order creation failed")

    @staticmethod
    def process_order_payment(order: Orders, payment: Payment, status: str):
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
            if status == "captured":
                logger.info("Payment captured successfully. Updating status flags to PAID...")
                if order.payment_status != 'paid':
                    with transaction.atomic():
                        payment.status = Payment.Status.CAPTURED
                        payment.save()
                        order.payment_status = "paid"
                        order.save()
                        logger.info("Order and Payment records marked as paid successfully")
            
            # Action: Failure pathway
            elif status == "failed":
                logger.info("Payment failure flagged. Updating status flags to UNPAID...")
                with transaction.atomic():
                    payment.status = Payment.Status.FAILED
                    payment.save()
                    order.payment_status = "not_paid"
                    order.save()
                    logger.info("Order and Payment records marked as failed successfully")

            logger.info("Leaving order payment status sync service")
        except ValueError as e:
            raise e
        except Exception as e:
            logger.exception(str(e))
            raise CreateError("Payment status update failed")
