from django.urls import path
from . import views

urlpatterns = [
    path("products/", views.ListProductView.as_view(), name="list-products"),
    path("product/<slug:slug>", views.RetrieveProductView.as_view(), name="retrieve-product"),
    path("profile/cart/", views.ListCreateCartView.as_view(), name = 'cart'),
    path("profile/cart/<uuid:uid>/", views.UpdateDestroyCartView.as_view(), name = 'cart'),

]
