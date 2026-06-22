from typing import cast, Dict, Any

from razorpay.errors import ( SignatureVerificationError, BadRequestError, ServerError, GatewayError)


import sentry_sdk
from rest_framework import permissions, generics, views, status
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from base import helpers
from base.exceptions import *
from .models import  Orders, Profile, Payment, Cart, OrderedItem
from .serializers import OrderedItemSerializer, OrderSerializer, PaymentSerializer, RazorOrderIdSerializer
from app_products.serializers import CartSerializer
from app_orders.services import OrderCreationService, RAZORPAY_TEST_API_KEY, razorpay_client

from VeggieVault.settings import RAZORPAY_TEST_KEY_SECRET
from app_orders.utils import *
import logging

logger = logging.getLogger('app_orders')  # will use your JSON config


class GetOrderItemView(generics.ListAPIView):
    queryset = Orders.objects.all()
    serializer_class = OrderedItemSerializer
    permission_classes = [permissions.AllowAny]

logger = logging.getLogger('app_orders')

class CreateOrderView(generics.CreateAPIView):
    """
    View to handle create a new order.
    """
    queryset = Orders.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_profile_obj(self) -> Profile:
        """Helper to get the current user's profile."""
        logger.info(f"Looking up profile for user ID: {self.request.user.pk}")
        profile_obj = Profile.objects.get(user=self.request.user)
        logger.debug(f"Found profile: {profile_obj.uid}")
        return profile_obj
    
    def get_cart(self):
        """Helper to get all active cart items for this profile."""
        profile = self.get_profile_obj()
        logger.info(f"Getting cart items for profile: {profile.uid}")
        return Cart.objects.filter(profile=profile)

    def create(self, request, *args, **kwargs) -> Response:
        """Main method that handles the whole checkout process."""
        logger.info(f"User {request.user.id} clicked checkout button")
        
        try:
            # 1. Check and validate incoming request data
            order_serializer = cast(OrderSerializer, self.get_serializer(data=request.data))
            order_serializer.is_valid(raise_exception=True)
            order_serializer_data = helpers.validated_dict(order_serializer)
            
            amount = order_serializer_data.get("amount")
            logger.info(f"Validated order amount: INR {amount}")

            # 2. Call Razorpay API (Keep this outside the DB transaction because network calls are slow)
            logger.info("Calling Razorpay API to create an order...")
            razorpay_order = OrderCreationService.create_razorpay_order(amount=amount)
            order_id = razorpay_order.get('id')
            logger.info(f"Razorpay order created successfully. ID: {order_id}")

            # 3. Save everything to the database safely
            logger.info("Starting database transaction...")
            with transaction.atomic():
                profile = self.get_profile_obj()
                
                # Create the main Order record
                logger.info("Saving main Order record to database...")
                order = cast(Orders, order_serializer.save(consumer=profile, razorpay_order_id=order_id))
                logger.debug(f"Saved Order ID: {order.uid}")

                # Move items from Cart format into OrderedItem format
                logger.info("Converting cart items into ordered items data...")
                product_data = get_products_from_cart(cart=self.get_cart(), order=order)
                
                logger.info(f"Saving {len(product_data)} items to OrderedItem table...")
                orderitem_serializer = OrderedItemSerializer(data=product_data, many=True)
                orderitem_serializer.is_valid(raise_exception=True)
                orderitem_serializer.save()
                logger.info("All ordered items saved successfully")

                # Delete the user's cart since checkout is done
                logger.info("Deleting items from user's cart...")
                self.get_cart().delete()
                logger.info("User cart cleared successfully")

            # 4. If everything worked, send success response to frontend
            merchant_key = RAZORPAY_TEST_API_KEY
            logger.info(f"Checkout finished successfully for order: {order_id}")
            
            return Response(
                {
                    "order": razorpay_order, 
                    "order_id": order_id, 
                    "merchant_key": merchant_key
                },
                status=status.HTTP_201_CREATED
            )
        
        # Catch normal validation or missing data errors (Bad Requests)
        except (NotFound, ValueError, CreateError, ObjectDoesNotExist) as e:
            logger.warning(f"Validation or data error during checkout: {str(e)}")
            logger.exception(str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        # Catch errors specifically sent by the Razorpay SDK
        except (SignatureVerificationError, BadRequestError, ServerError, GatewayError) as e: 
            logger.error(f"Razorpay API error occurred: {e}")
            logger.exception(f"error: {e}")
            return Response({"error": "razorpay error occurred"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Catch unexpected crashes (Server Errors)
        except Exception as e: 
            logger.critical("The checkout crashed due to an unhandled system error")
            sentry_sdk.capture_exception(e)
            logger.exception(e)
            return Response(
                {"error": "server error occured"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )        

class VerifyPaymentView(generics.CreateAPIView):
    """
    View to confirm Razorpay payment signatures and update order records.
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_profile_obj(self) -> Profile:
        """Helper to get the current user's profile."""
        logger.info(f"Looking up profile for user Primary Key: {self.request.user.pk}")
        profile_obj = Profile.objects.get(user=self.request.user)
        logger.debug(f"Found profile: {profile_obj.uid}")
        return profile_obj

    def get_orders(self):
        """Helper to fetch all orders belonging to this user."""
        profile_obj = self.get_profile_obj()
        orders = Orders.objects.filter(consumer=profile_obj)
        logger.info(f"Found {orders.count()} order records for profile: {profile_obj.uid}")
        return orders
    
    def post(self, request) -> Response:
        """Handles incoming checkout payment verification confirmation."""
        logger.info(f"User {request.user.pk} submitted payment signature verification")
        
        try:
            # 1. Isolate and validate the Razorpay Order ID from the request
            razor_order_id_serializer = RazorOrderIdSerializer(data={"razorpay_order_id": request.data.get("razorpay_order_id")})
            razor_order_id_serializer.is_valid(raise_exception=True)
            razor_order_id_serializer_data = helpers.validated_dict(razor_order_id_serializer)
            order_id = razor_order_id_serializer_data.get("razorpay_order_id")
            
            # Fetch the matching order belonging specifically to this authenticated user
            logger.info(f"Searching for order string matching token: {order_id}")
            order = cast(Orders, self.get_orders().get(razorpay_order_id=order_id))
            
            # 2. Extract and validate signature payload items
            payment_serializer = cast(PaymentSerializer, self.get_serializer(data=request.data))
            payment_serializer.is_valid(raise_exception=True)
            payment_serializer_data = helpers.validated_dict(payment_serializer)
            
            payment_id = payment_serializer_data.get("razorpay_payment_id")
            signature = payment_serializer_data.get("razorpay_signature")
            
            # Look up if this payment item transaction row was created earlier
            payment_obj = Payment.objects.filter(razorpay_payment_id=payment_id).first()
            
            # 3. Security Check: Call Razorpay SDK utility to authenticate the digital signature
            logger.info("Verifying payload signature using Razorpay Client...")
            razorpay_client.utility.verify_payment_signature({
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature
            })
            logger.info("Signature verification passed.")

            # If the payment row already exists, update it instead of creating a duplicate
            if payment_obj:
                logger.info(f"Existing payment record found for ID: {payment_id}. Updating instance.")
                payment_serializer = PaymentSerializer(instance=payment_obj, data=request.data, partial=True)
                payment_serializer.is_valid(raise_exception=True)

            payment = payment_serializer.save(order=order, razorpay_payment_id=payment_id, status=Payment.Status.CREATED)
            
            # 4. Request the direct transaction state status explicitly from Razorpay servers
            logger.info(f"Fetching current payment status from remote server for: {payment_id}")
            payment_status = client.payment.fetch(payment_id)
            current_status = payment_status.get("status")
            logger.info(f"Remote server returned current transaction state status: {current_status}")

            # 5. Handle Action: Success Workflow
            if current_status == "captured":
                logger.info(f"Payment capture confirmed. Updating tracking rows to PAID for Order: {order.uid}")
                OrderCreationService.order_payment(order=order, payment=payment, status="captured")
                return Response({"msg": "order payment is done successfully"}, status=status.HTTP_202_ACCEPTED)
            
            # 6. Handle Action: Failure Reversion Workflow
            elif current_status == "failed":
                logger.warning(f"Payment failed on gateway side for payment ID: {payment_id}. Reverting inventory back to user cart.")
                
                # Wrap database rollback actions inside a safe atomic block
                with transaction.atomic():
                    OrderCreationService.order_payment(order=order, payment=payment, status="failed")
                    
                    # Convert ordered items back into cart items
                    ordered_items = OrderedItem.objects.filter(order=order)
                    products_data = get_products_from_ordereditem(ordered_items)

                    cart_serializer = CartSerializer(data=products_data, many=True)
                    cart_serializer.is_valid(raise_exception=True)
                    cart_serializer.save()
                    
                    # Remove the failed ordered items row logs
                    ordered_items.delete()
                    logger.info("Items restored back to the user's active cart. OrderedItem entries cleaned up.")

                return Response({"msg": "payment failed."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Edge case if status returns something unexpected like 'authorized' or 'refunded'
            else:
                logger.error(f"Unexpected payment status state flagged by remote gateway server: {current_status}")
                return Response({"error": f"Unhandled transaction state: {current_status}"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Catch lookup failures (e.g., user tries verifying an order they don't own)
        except (NotFound, Orders.DoesNotExist) as e:
            logger.warning(f"Order or resource access failure flagged during verification processing: {str(e)}")
            logger.exception(e)
            return Response({"error": "payment failed"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Catch network/signature payload errors raised directly by Razorpay SDK
        except (SignatureVerificationError, BadRequestError, ServerError, GatewayError) as e: 
            logger.error(f"Razorpay integration exception hit during confirmation checking: {e}")
            logger.exception(f"error: {e}")
            return Response({"error": "razorpay error occurred"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Catch unexpected code crashes
        except Exception as e:
            logger.critical("Critical backend code failure hit during verification processing lifecycle")
            logger.exception(e)
            return Response({"error": "payment failed. some server error occured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RazorpayWebhookAPIView(views.APIView):
    """
    Webhook view that listens to background events sent directly by Razorpay servers.
    """
    # Webhooks must be AllowAny because Razorpay servers don't have user tokens
    permission_classes = [permissions.AllowAny]

    def get_order_obj(self, rz_order_id: str) -> Orders:
        """Helper to find an order using its Razorpay order ID string."""
        logger.info(f"Webhook searching for order matching: {rz_order_id}")
        order_obj = Orders.objects.get(razorpay_order_id=rz_order_id)
        logger.debug(f"Found order instance: {order_obj.uid}")
        return order_obj

    def post(self, request, *args, **kwargs) -> Response:
        """Processes incoming event payloads sent by Razorpay."""
        data = cast(Dict[str, Any], request.data)
        event = data.get('event')
        
        logger.info(f"Received Razorpay webhook event: {event}")

        try:
            # 1. Parse the deep JSON structure safely from Razorpay's payload
            order_entity = data['payload']['order']['entity']
            rz_orderid = order_entity['id']
            
            payment_entity = data['payload'].get('payment', {}).get('entity', {})
            rz_paymentid = payment_entity.get('id')
            
            logger.info(f"Extracted Razorpay Order ID: {rz_orderid} and Payment ID: {rz_paymentid}")

            # 2. Validate the extracted order ID
            razor_order_id_serializer = RazorOrderIdSerializer(data={"razorpay_order_id": rz_orderid})
            razor_order_id_serializer.is_valid(raise_exception=True)
            razor_order_id_serializer_data = helpers.validated_dict(razor_order_id_serializer)
            order_id = razor_order_id_serializer_data.get("razorpay_order_id")
            
            # Fetch the actual order model row

            order = self.get_order_obj(rz_order_id= str(order_id)) 

            # 3. Validate and record the payment details
            payment_serializer = PaymentSerializer(data={'razorpay_payment_id': rz_paymentid})
            payment_serializer.is_valid(raise_exception=True)
            payment_serializer_data = helpers.validated_dict(payment_serializer)
            payment_id = payment_serializer_data.get("razorpay_payment_id")
            
            # Check if we already created a payment entry earlier for this ID
            payment_obj = Payment.objects.filter(razorpay_payment_id=payment_id).first()

            if payment_obj:
                logger.info(f"Payment {payment_id} already exists in DB. Updating row.")
                payment_serializer = PaymentSerializer(instance=payment_obj, data=request.data, partial=True)
                payment_serializer.is_valid(raise_exception=True)
            
            # Save the payment record tracking row
            payment = cast(Payment, payment_serializer.save(order=order, status=Payment.Status.CREATED))

            # 4. ACTION: If Razorpay says the order is fully paid
            if event == 'order.paid':    
                logger.info(f"Event matches success state. Updating order {order.uid} to PAID status.")
                OrderCreationService.process_order_payment(order=order, payment=payment, status="captured")
                return Response({"msg": "order payment is done successfully"}, status=status.HTTP_200_OK)
            
            # 5. ACTION: If Razorpay says the payment completely failed
            elif event == 'payment.failed':
                logger.warning(f"Event matches failure state. Reverting cart items for order {order.uid}.")
                
                # Wrap the inventory reversal database tasks inside an isolated safe atomic block
                with transaction.atomic():
                    OrderCreationService.process_order_payment(order=order, payment=payment, status="failed")
                    
                    # Fetch items tied to the order and map them back to standard cart records
                    ordered_items = OrderedItem.objects.filter(order=order)
                    products_data = get_products_from_ordereditem(ordered_items)

                    cart_serializer = CartSerializer(data=products_data, many=True)
                    cart_serializer.is_valid(raise_exception=True)
                    cart_serializer.save()
                    
                    # Delete the dead ordered items from database logs
                    ordered_items.delete()
                    logger.info("Items restored back to active carts. Failed ordered items tracking rows dropped.")
                    
                return Response({"msg": "payment failed."}, status=status.HTTP_400_BAD_REQUEST)
                
            # If Razorpay sent an event type your view isn't tracking yet
            else:
                logger.info(f"Webhook received unhandled event type: {event}. No database changes made.")
                return Response({"msg": "Webhook event acknowledged"}, status=status.HTTP_200_OK)

        # Catch missing target database rows or lookups that failed entirely
        except (NotFound, Orders.DoesNotExist) as e:
            logger.warning(f"Webhook processing halted because a target record was missing: {str(e)}")
            logger.exception(e)
            return Response({"error": "payment failed"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Catch unexpected structural crashes
        except Exception as e:
            logger.critical("Critical background code exception encountered during webhook loop handling")
            logger.exception(e)
            return Response({"error": "payment failed. some server error occured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)