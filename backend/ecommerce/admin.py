from django.contrib import admin
from django.contrib.auth.models import User

from .models import Order, Item, Color, Category, OrderItem, Currency

#inlines here
class ItemInline(admin.StackedInline):
    model = Item
    extra = 1
    show_change_link = True

class OrderInline(admin.StackedInline):
    model = Order
    extra = 1

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    inlines = [OrderInline, ItemInline]
    extra = 1
    show_change_link = True


# Register your models here.
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'stock', 'price', 'created', 'category')
    list_filter = ("created",)
    search_fields = ("title", "status", "id")
    inlines = [ OrderItemInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'quantity', 'status', "created", 'total_price', "user")
    list_filter = ("created",)
    search_fields = ("title", "status", "id")
    inlines = [OrderItemInline]


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', )
    list_filter = ("name",)
    search_fields = ("name",)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', "symbol" )
    list_filter = ("name",)
    search_fields = ("name", "symbol",)
    inlines = [ItemInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    list_filter = ("name",)
    search_fields = ("name",)
    inlines = [ItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'item', 'quantity')
