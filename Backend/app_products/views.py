import logging
from typing import cast, Dict, Any

# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, generics,  views, filters, status
from rest_framework.response import Response
import sentry_sdk

from .models import Product, Cart
from app_users.models import Profile
from .serializers import ProductSerializer, CartSerializer, CartSerializer
from app_products import services



logger = logging.getLogger('app_products')  # will use your JSON config

class ListProductView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter] 
    filterset_fields = { 'category': ['exact'],
                        'price': ['gte', 'lte', 'gt', 'lt']}
    search_fields = ['name', 'description'] 

class RetrieveProductView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ProductSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

class ListCreateCartView(generics.ListCreateAPIView):
    #serializer_class = CartListSerializer
    serializer_class = CartSerializer
    permission_classes = [permissions.AllowAny]
        
    def get_queryset(self):
        queryset = Cart.objects.filter(profile__user = self.request.user)
        return queryset
    
    def create(self, request, *args, **kwargs):
        try:
            cart_serializer = cast(CartSerializer,CartSerializer(data = request.data))
            cart_serializer.is_valid(raise_exception=True)
            cart_serializer_data = cast(Dict[str,Any], cart_serializer.validated_data)
            cart_serializer.save()
            
            return Response(
                {
                    "message": "Product added to cart successfully!",
                    "data": CartSerializer(Cart.objects.filter(profile__user = self.request.user), many=True).data
                },
                    status=status.HTTP_201_CREATED
            )

        except (services.NotFound, services.CreateError) as e:
            return Response({"error":str(e)}, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e: 
            sentry_sdk.capture_exception(e)
            logger.exception(e)
            return Response({"error": "server error occured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UpdateDestroyCartView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "uid"
    lookup_url_kwarg = "uid"
    def get_queryset(self):
        queryset = Cart.objects.filter(profile__user = self.request.user)
        return queryset
    

