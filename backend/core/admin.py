from django.contrib import admin
from django.contrib.auth.models import User

from .models import Contact, EmployeeProfile, CustomerProfile, CustomUser
from ecommerce.admin import OrderInline, ItemInline

#inlines
class CustomerInline(admin.TabularInline):
    model = CustomerProfile
    field = ["user_type",]

class EmployeeInline(admin.TabularInline):
    model = EmployeeProfile
    field = ["department", "skills"]


# Register your models here.
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ( 'title', 'description', 'email',)
    search_fields = ("title",)
    list_filter = ("created",)

@admin.register(CustomerProfile)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ( 'id', "user", "user_type")
    

@admin.register(EmployeeProfile)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ( "id", "user", "department",)


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "is_staff", "username", "is_active", )
    search_fields = ("email", "username", "id",)
    inlines = [OrderInline, ItemInline, CustomerInline, EmployeeInline]

admin.site.register(CustomUser,CustomUserAdmin)