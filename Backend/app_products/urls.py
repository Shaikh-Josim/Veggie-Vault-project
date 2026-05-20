from django.urls import path
from . import views

urlpatterns = [
    path("products/", views.ListProductView.as_view(), name="list-products"),
    path("cart/", views.ListCreateCartView.as_view(), name = 'cart-list')

]
