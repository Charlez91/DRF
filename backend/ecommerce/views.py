from json import JSONDecodeError

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import GenericViewSet
from rest_framework.parsers import JSONParser
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import ListModelMixin, UpdateModelMixin, RetrieveModelMixin

from .models import Order, Item
from .serializers import ItemSerializer, OrderSerializer

# Create your views here.
class ItemViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    A Simple ViewSet for listing or retrieving items
    """
    permission_classes = (IsAuthenticated,)
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class OrderViewSet(ListModelMixin, UpdateModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    This view should return A List of all orders
    for the currently authenticated user.
    """
    permission_classes = (IsAuthenticated, )
    serializer_class = OrderSerializer

    def get_queryset(self) -> Order:
        """
        This View should return a list of all the orders
        for the currently authenticated user.
        """
        user = self.request.user
        return Order.objects.filter(user = user)
    
    def create(self, request) -> Response or JsonResponse:
        """
        For handling update/creating of orders
        """
        try:
            data = JSONParser().parse(request)
            get_object_or_404(Item, pk=data["item"])#data.get() will return none if not found and raise no exceptions
            serializer = OrderSerializer(data = data)# actually the serializer handles the not found by setting is valid to false and redirecting to else statement which has status of 400
            if serializer.is_valid(raise_exception=True):
                item: Item =  Item.objects.get(pk= data["item"])#data.get() will return none if not found and raise no exceptions
                order = item.place_order(request.user, data["quantity"])
                return Response(OrderSerializer(order).data)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return JsonResponse({"result":"error", "message":"Json Decode Error"}, status=400)

