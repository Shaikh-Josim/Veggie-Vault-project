
from rest_framework import permissions, generics
from .models import  Orders
from .serializers import OrdersSerializer
import logging

logger = logging.getLogger('app_orders')  # will use your JSON config
    
class GetOrderView(generics.ListAPIView):
    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer
    permission_classes = [permissions.AllowAny]

    