from django.urls import path, include
from app_orders import views
urlpatterns = [
    path("", include("app_users.urls")),
    path("", include("app_products.urls")),
    path("", include("app_orders.urls")),
    path("razorpay/webhook", views.RazorpayWebhookAPIView.as_view(), name="razorpay-webhook"),
]
