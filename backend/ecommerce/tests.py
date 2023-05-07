from uuid import uuid4

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.authtoken.models import Token

from .models import Item, Order
from .serializers import NotEnoughStockException

# Create your tests here.
class EcommerceTestCase(APITestCase):
    """
    Test suite for Items and Orders
    """

    def setUp(self) -> None:
        #creating Items
        Item.objects.create(title= "Demo item 1",
                            description= "This is a description for demo 1",
                            price= 500,stock= 20)
        Item.objects.create(title= "Demo item 2",
                            description= "This is a description for demo 2",
                            price= 700,stock= 15)
        Item.objects.create(title= "Demo item 3",
                            description= "This is a description for demo 3",
                            price= 300,stock= 18)
        Item.objects.create(title= "Demo item 4",
                            description= "This is a description for demo 4",
                            price= 400,stock= 14)
        Item.objects.create(title= "Demo item 5",
                            description= "This is a description for demo 5",
                            price= 500,stock= 30)
        self.items = Item.objects.all()
        #creating users
        self.user = User.objects.create_user(
            username="Charlez91",
            password="testing123",
            email="okekecharles91@gmail.com"
        )
        #creating orders
        Order.objects.create(item = Item.objects.first(),
                             user = self.user, quantity = 1)
        Order.objects.create(item = Item.objects.first(),
                             user = User.objects.first(), quantity = 2)
        Order.objects.create(item = Item.objects.last(), 
                             user = User.objects.first(), quantity = 2)
        self.orders = Order.objects.all()
        #the app uses Token Authentication
        self.token = Token.objects.get(user = self.user)
        self.client = APIClient()
        #we pass the token in all calls to the API
        self.client.credentials(HTTP_AUTHORIZATION = "Token "+self.token.key)

    def test_get_all_items(self):
        '''
        test ItemsViewSet list method
        '''
        self.assertEqual(Item.objects.count(), len(self.items), "Numbers of items in db dont match")
        response = self.client.get('/item/')
        self.assertEqual(response.status_code, HTTP_200_OK)
    
    def test_get_one_item(self):
        '''
        test ItemsViewSet retrieve method
        '''
        for item in self.items:
            response = self.client.get(f'/item/{item.id}/')
            self.assertEqual(response.status_code, HTTP_200_OK)
    
    def test_order_is_more_than_stock(self):
        '''
        test `Item.check_stock` when order .quantity>item.stock
        '''
        for i in self.items:
            current_stock = i.stock
            self.assertEqual(i.check_stock(current_stock+1), False, "Stock is <= quantity requested")
    
    def test_order_is_equalto_stock(self):
        '''
        test `Item.check_stock` when order .quantity==item.stock
        '''
        for i in self.items:
            current_stock = i.stock
            self.assertEqual(i.check_stock(current_stock), True, "Stock is > quantity requested")
    
    def test_order_is_less_than_stock(self):
        '''
        test `Item.check_stock` when order .quantity<item.stock
        '''
        for i in self.items:
            current_stock = i.stock
            self.assertEqual(i.check_stock(current_stock-1), True, "Stock is > quantity requested")
    
    def test_create_order_with_more_than_stock(self):
        '''
        test OrdersViewSet create method when `order.quantity`>`item.stock`
        '''
        for i in self.items:
            stock = i.stock
            data = {"item":str(i.id), "quantity":f'{stock+1}'}
            response = self.client.post('/order/', data)
            self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST, 'order.quantity<=item.stock')
            self.assertRaises(NotEnoughStockException)
    
    def test_create_order_with_less_than_stock(self):
        '''
        test OrdersViewSet create method when `order.quantity`<`item.stock`
        '''
        for i in self.items:
            data = {"item":str(i.id), "quantity":1}
            response = self.client.post('/order/', data)
            self.assertEqual(response.status_code, HTTP_200_OK, 'order.quantity>item.stock')

    def test_create_order_with_equal_stock(self):
        '''
        test OrdersViewSet create method when `order.quantity`==`item.stock`
        '''
        for i in self.items:
            stock = i.stock
            data = {"item":str(i.id), "quantity":f'{stock}'}
            response = self.client.post('/order/', data)
            self.assertEqual(response.status_code, HTTP_200_OK, 'order.quantity>item.stock')

    def test_create_order_with_item_that_doesnt_exist(self):
        '''
        test OrdersViewsSet create method with item that doesnt exist
        '''
        i = Item.objects.last()
        data = {"item":str(uuid4()), "quantity":1} # uses uuid so hopefuly an id +1 doesnt exist. can change to more strange stuff later
        response = self.client.post('/order/', data)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND, "Item exists")

    def test_get_all_orders(self):
        '''
        test OrdersViewSet list method
        '''
        self.assertEqual(Order.objects.count(), len(self.orders), 'Orders are tallying')
        response = self.client.get('/order/')
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_get_one_order(self):
        '''
        test OrdersViewSet to get/retrieve method for an order
        '''
        orders = Order.objects.filter(user = self.user)
        for o in orders:
            response = self.client.get(f'/order/{o.id}/')
            self.assertEqual(response.status_code, HTTP_200_OK)
