from django.urls import path
from rest_framework.routers import DefaultRouter

from core import views as core_views

#specifies appname for name spacing
appname = "core"

router = DefaultRouter()
# registering routes mainly for viewsets
router.register(r'comment', core_views.CommentViewset, basename='comment')

urlpatterns = [

    path("contact/", core_views.ContactAPIView.as_view(), name="contact"),
    path("register/", core_views.CustomerRegisterAPIView.as_view(), name="user-register"),
    path("profile/", core_views.CustomerUpdateAPIView.as_view(), name="profile-update"),
    path("staff/", core_views.EmployeerAPIView.as_view(), name="staff"),
    path(route='activate/<uidb64>/<token>/', view= core_views.ActivateView.as_view(),name='activate'),

]
