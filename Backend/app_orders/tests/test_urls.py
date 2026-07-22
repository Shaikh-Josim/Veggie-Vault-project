from django.urls import path, include

urlpatterns = [
    path("", include("app_users.urls")),
    path("", include("app_products.urls")),
    path("", include("app_orders.urls")),
]
