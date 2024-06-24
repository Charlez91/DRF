from django.contrib import admin

from .models import (
    Contact, EmployeeProfile, 
    CustomerProfile, CustomUser, Comment)
from ecommerce.admin import OrderInline, ItemInline


#headers and titles
admin.site.site_header = "Ecommerce App"
admin.site.site_title = "...one stop shop on the web."

#inlines
class CustomerInline(admin.TabularInline):
    model = CustomerProfile
    field = ["user_type",]

class EmployeeInline(admin.TabularInline):
    model = EmployeeProfile
    field = ["department", "skills"]


class CommentInline(admin.StackedInline):
    model = Comment
    field = ["email", "comment", "rating", "approved"]


# Register your models here.
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ( 'title', 'description', 'email',)
    search_fields = ("title",)
    list_filter = ("email",)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    field = ["email", "name", "comment", "rating", "approved"]
    search_fields = ("email", "comment",)
    ordering = ("date_created",)

@admin.register(CustomerProfile)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ( 'id', "user", "user_type")
    list_filter = ('user__email',)
    search_fields = ('user_type',)
    ordering = ['user', ]
    

@admin.register(EmployeeProfile)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ( "id", "user", "department",)
    list_filter = ('user',)
    search_fields = ('user',)
    ordering = ['user', ]


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "is_staff", "username", "is_active", )
    search_fields = ("email", "username", "id",)
    inlines = [OrderInline, ItemInline, CustomerInline, EmployeeInline, CommentInline]

admin.site.register(CustomUser,CustomUserAdmin)