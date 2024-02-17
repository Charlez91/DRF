from json import JSONDecodeError

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import ListModelMixin, UpdateModelMixin, RetrieveModelMixin, CreateModelMixin

from .models import Order, Item
from .serializers import ItemSerializer, OrderSerializer, ItemCreateSerializer

# Create your views here.
class ItemViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    A Simple ViewSet for listing or retrieving items
    """
    permission_classes = (IsAuthenticated,)
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class ItemCreateViewSet(CreateModelMixin, UpdateModelMixin, GenericViewSet):
    """
    A Simple ViewSet for listing or retrieving items
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = (IsAuthenticated,)
    serializer_class = ItemCreateSerializer

    def create(self, request, *args, **kwargs):
        data = MultiPartParser(request)
        serializer = self.get_serializer(data= data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message":"Item Created Successfully", "data":serializer.data})
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)



class OrderViewSet(ListModelMixin, UpdateModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    This view should return A List of all orders
    for the currently authenticated user.
    """
    permission_classes = (IsAuthenticated, )
    #authentication_classes = (TokenAuthentication,)# it has been defaulted in rest_framework settings
    #parser_classes = [JSONParser] # it has been defaulted too
    serializer_class = OrderSerializer

    def get_queryset(self) -> Order:
        """
        This View should return a list of all the orders
        for the currently authenticated user.
        """
        user = self.request.user
        return Order.objects.filter(user = user)
    
    def create(self, request) -> Response:
        """
        For handling update/creating of orders
        """
        try:
            data = JSONParser().parse(request)#no need for dis cos data is already parsed through default parser in settings
            serializer = OrderSerializer(data = data)
            if serializer.is_valid(raise_exception=True):
                item: Item =  get_object_or_404(Item, pk=serializer.validated_data["item"].id)#validated data for relationship field returns the class instance for that model
                order = item.place_order(request.user, qty= serializer.validated_data["quantity"])
                return Response(OrderSerializer(order).data)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return JsonResponse({"result":"error", "message":"Json Decode Error"}, status=400)

