

# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, generics,  views, filters
from rest_framework.response import Response

from .models import Product, Cart
from .serializers import ProductSerializer, CartSerializer


# Create your views here.
import logging

logger = logging.getLogger('app_products')  # will use your JSON config

class ListProductView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter] 
    filterset_fields = { 'category': ['exact'],
                        'price': ['gte', 'lte']}
    search_fields = ['name', 'description'] 

class ListCreateCartView(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        email = request.user
        print(email)
        self.queryset = Cart.objects.filter(profile__user__email = email)
        print(self.queryset.all())
        return super().get(request, *args, **kwargs)

class ListUpdateDestroyCartView(generics.RetrieveUpdateDestroyAPIView):
    pass

