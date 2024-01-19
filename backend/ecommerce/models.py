from django.db import models
#from django.contrib.auth.models import User
from django_extensions.db.models import (
    TimeStampedModel,
    ActivatorModel,
    TitleSlugDescriptionModel
)
from PIL import Image

from utils.model_abstracts import Model
from core.models import CustomUser

"""
#image class for item images incases of multiple images for an item
class Image(models.Model):
    item = models.ForeignKey('Item', on_delete = models.CASCADE)
    img = image = models.ImageField(default="default.jpg", upload_to="item_images")
    thumbnail = models.ImageField(default="default.jpg", upload_to="item_thumbnails")#still thinking of making optional
"""

def process_item_image(instance)->None:
    """
    to process thumbnail and images
    """
    #open image and makes a copy
    img = Image.open(instance.image.path)
    img_thumbnail = Image.Image.copy(img)
    #logic to resize image
    if img.height > 300 or img.width > 300:
        output_size = (300,300)
        img = img.resize(output_size)
        img.save(instance.image.path)
    #logic to resize thumbnail
    if img_thumbnail.height > 125 or img_thumbnail.width > 125:
        img_thumbnail.thumbnail((125,125))
        img.save(instance.thumbnail.path)


class Category(models.Model):
    """
    `ecommerce.category`
    Stores a single category entry.
    """
    name = models.CharField(max_length= 255, unique=True)
    description = models.TextField(blank=True,null=True)

    def __str__(self) -> str:
        return self.name


class Color(models.Model):
    """
    `ecommerce.color`
    Various Colours for various items
    An `Item` can have more than one colour.
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.name

class Currency(models.Model):
    """
    `ecommerce.currency`
    Currency in which an item was listed and payment transaction carried out in
    """
    name = models.CharField(max_length=50, unique=True)
    symbol = models.CharField(max_length=10, unique=True)
    sign = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return self.name
    

# Create your models here.
class Item(TimeStampedModel, ActivatorModel, TitleSlugDescriptionModel, Model):
    """
    `ecommerce.Item`
    Stores a single item entry for our shop
    related to model: User and model:ecommerce.category and model
    """
    vendor = models.ForeignKey(CustomUser, on_delete= models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete= models.SET_NULL, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete= models.CASCADE, null=True, blank=True)
    stock = models.PositiveIntegerField(default=1)
    price = models.IntegerField(default=0) # normally should be a float field but price here is actually in pence, cents, kobo
    image = models.ImageField(default="default.jpg", upload_to="item_images")# will later make a one to many/many to many relationship cos an item might have multiple images and images can be shared too btw items
    thumbnail = models.ImageField(default="default.jpg", upload_to="item_thumbnails")
    weight = models.DecimalField(max_digits = 10, decimal_places=3, default=0)#in kg
    colors = models.ManyToManyField(Color, related_name='items')

    def __str__(self) -> str:
        return self.title
    
    def save(self) -> None:
        '''
        Image manipulation logic for thumbnail and image logic and saved
        '''
        super().save()
        process_item_image(self)
        
        
    @property
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

    def place_order(self, user:CustomUser, qty:int):
        #used to place an order
        if self.check_stock(qty):
            order:Order = Order.objects.create(
                item = self,
                quantity = qty,
                user = user
            )
            self.manage_stock(qty)# this setup can lead to reentrancy risks. But for development we allow
            return order
        else:
            return None

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"
        ordering = ["id"]

    

class Order(TimeStampedModel, ActivatorModel, Model):
    """
    `ecommerce.order`
    Stores a single order entry related to: model:`ecommerce.Item`
    and model:`auth.User`.
    """
    class OrderStatus(models.TextChoices):
        """An implementation of choices field using Textchoices class"""
        PENDING = "pending", "PENDING"
        CONFIRMED = "confirmed", "CONFIRMED"
        SHIPPED = "shipped", "SHIPPED"
        DELIVERED = "delivered", "DELIVERED"
        CANCELLED = "cancelled", "CANCELLED"
        RETURNED = "returned", "RETURNED"
        REFUNDED = "refunded", "REFUNDED"

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)#buyer
    item = models.ManyToManyField(Item, through="OrderItem")
    quantity = models.PositiveIntegerField(verbose_name="quantity", default=1)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_weight = models.DecimalField(max_digits = 10, decimal_places=3, default=0)
    status = models.CharField(verbose_name="Status", choices = OrderStatus.choices, default=OrderStatus.PENDING, max_length=20)
    transaction = models.OneToOneField("Transaction", on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self) -> str:
        return f'{self.user.username} - {self.item.title}'
    
    def mark_as_delivered(self):
        """
        Method to mark the order as delivered.
        """
        if self.status != Order.OrderStatus.DELIVERED:
            self.status = Order.OrderStatus.DELIVERED
            self.save()

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["id"]


class OrderItem(models.Model):
    """
    intermediary/joining table for the orderitem many to many relationship
    """
    order = models.ForeignKey(Order, on_delete= models.CASCADE)
    item = models.ForeignKey(Item, on_delete= models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f'Order #{self.order.id} - {self.item.title} x {self.quantity}'
    
class Transaction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)#buyer
    amount = models.DecimalField(max_digits=10, decimal_places=2)#in fiat
    paid = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
    currency = models.ForeignKey(Currency, on_delete= models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Transaction {self.pk} - User: {self.user.username}, Amount: {self.amount}"
