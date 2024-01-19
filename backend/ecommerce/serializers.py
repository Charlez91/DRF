from collections import OrderedDict
from .models import Order, Item
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.exceptions import APIException
from rest_framework_json_api.serializers import (
    ModelSerializer,
    PrimaryKeyRelatedField,
    )


class NotEnoughStockException(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_detail: str = "There is not enough stock"
    default_code: str = "invalid"


class ItemSerializer(ModelSerializer):
    """
    Item serializer class from Item model
    with field as shown
    """
    class Meta:
        model: Item = Item
        fields: list = [
            'title',
            'description',
            'stock',
            'price',
            'image',
        ]

class ItemCreateSerializer(ModelSerializer):
    """
    Item serializer class from Item model
    TO create new items and update
    """
    class Meta:
        model: Item = Item
        fields: tuple = (
            'title',
            'description',
            'stock',
            'price',
            "image",
        )


class OrderSerializer(ModelSerializer):
    """
    Order serializer from OrderModel
    with field as shown below
    """
    item = PrimaryKeyRelatedField(queryset = Item.objects.all(), many=False)

    def validate(self, res: OrderedDict) -> OrderedDict or NotEnoughStockException:
        """
        Used to validate Item stock levels
        """
        item: Item = res.get("item")
        qty: int = res.get("quantity")
        if not item.check_stock(qty):
            raise NotEnoughStockException
        return res

    class Meta:
        model: Order = Order
        fields: tuple = (
            'item',
            'quantity',
        )


