from django.db import models
from django.contrib.auth.models import User
from django_extensions.db.models import (
    TimeStampedModel,
    ActivatorModel,
    TitleSlugDescriptionModel
)

from utils.model_abstracts import Model

# Create your models here.
class Item(TimeStampedModel, ActivatorModel, TitleSlugDescriptionModel, Model):
    '''
    ecommerce.Item
    Stores a single item entry for our shop
    '''
    stock = models.IntegerField(default=1)
    price = models.IntegerField(default=0) # normally should be a float field but price here is actually in pence

    def __str__(self) -> str:
        return self.title

    def amount(self) -> float:
        #converts price from pence to pounds
        amount: float = float(self.price / 100)
        return amount

    def manage_stock(self, qty:int)-> None:
        # used to reduce item stock when an order is made
        new_stock: int = self.stock - int(qty)
        self.stock: int = new_stock
        self.save()

    def check_stock(self, qty:int) -> bool:
        #used to check if order quantity exceeds stock levels
        if int(qty) <= self.stock:
            return True
        return False

    def place_order(self, user:User, qty:int):
        #used to place an order
        if self.check_stock(qty):
            order:Order = Order.objects.create(
                item = self,
                quantity = qty,
                user = user
            )
            self.manage_stock(qty)
            return order
        else:
            return None

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"
        ordering = ["id"]

    

class Order(TimeStampedModel, ActivatorModel, Model):
    """
    ecommerce.order
    Stores a single order entry related to: model:`ecommerce.Item`
    and model:`auth.User`.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f'{self.user.username} - {self.item.title}'

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["id"]