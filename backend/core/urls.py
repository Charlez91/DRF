from django.urls import path
from rest_framework.routers import DefaultRouter

from core import views as core_views


router = DefaultRouter()
# registering routes mainly for viewsets
router.register(r'comment', core_views.CommentViewset, basename='comment')

urlpatterns = [

    path("contact/", core_views.ContactAPIView.as_view(), name="contact"),
    path("register/", core_views.CustomerRegisterAPIView.as_view(), name="user-register"),
    path("profile/", core_views.CustomerUpdateAPIView.as_view(), name="profile-update"),
    path("staff/register/", core_views.EmployeerRegisterAPIView.as_view(), name="staff-register"),

]
