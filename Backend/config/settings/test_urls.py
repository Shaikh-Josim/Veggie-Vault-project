from django.urls import path, include
from app_orders import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns = [
    path("api/token/", TokenObtainPairView.as_view(), name="get_token"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="refresh-token"),
    path("", include("app_users.urls")),
    path("", include("app_products.urls")),
    path("", include("app_orders.urls")),
    path("razorpay/webhook", views.RazorpayWebhookAPIView.as_view(), name="razorpay-webhook"),
]
