from django.urls import path, include
from rest_framework.routers import DefaultRouter

from core import views as core_views

#specifies appname for name spacing
app_name = "core"

router = DefaultRouter()
# registering routes mainly for viewsets
router.register(r'comment', core_views.CommentViewset, basename='comment')

urlpatterns = [

    path("", include(router.urls)),
    path("contact/", core_views.ContactAPIView.as_view(), name="contact"),
    path("register/", core_views.CustomerRegisterAPIView.as_view(), name="user-register"),
    path("user_profile/", core_views.CustomerUpdateAPIView.as_view(), name="profile-update"),
    path("profile/<str:username>/", core_views.CustomerRetrieveView.as_view(), name="profile-get"),
    path("profile/", core_views.CustomerListView.as_view(), name="profile-get"),
    path("staff/", core_views.EmployeerAPIView.as_view(), name="staff"),
    path(route='activate/<uidb64>/<token>/', view= core_views.ActivateView.as_view(),name='activate'),
    path("email-verify/", core_views.EmailVerificationView.as_view(), name="email-verify")

]
