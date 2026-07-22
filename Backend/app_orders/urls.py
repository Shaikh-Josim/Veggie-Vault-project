from django.urls import path
from . import views

urlpatterns = [
    path("orders/", views.GetOrderItemView.as_view(), name="list-orders"),
    path("razorpay/order/create", views.CreateOrderView.as_view(), name="create-order"),
    path("razorpay/order/payment/verify", views.VerifyPaymentView.as_view(), name="verify-payment"),
    path("razorpay/webhook", views.RazorpayWebhookAPIView.as_view(), name="razorpay-webhook"),
]
