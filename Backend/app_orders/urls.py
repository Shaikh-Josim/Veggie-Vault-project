from django.urls import path
from . import views

urlpatterns = [
    path("orders/", views.GetOrderView.as_view(), name="list-orders"),
]
