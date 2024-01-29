"""drf_course URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from core import views as core_views
from ecommerce import views as ecommerce_views

# adding routers from DRF
router = routers.DefaultRouter()
# registering routes instead of using urlpatterns mainly for viewsets
router.register(r'item', ecommerce_views.ItemViewSet, basename='item')
router.register(r'order', ecommerce_views.OrderViewSet, basename='order')

#urlpatterns += router.urls #to add a good prefix to the url i decided to add with include to urlpattern

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/v1/', include('core.urls')),
    path("api/v1/", include(router.urls)),
    path('api/docs/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='swagger-redoc-ui'),
    #path('api-auth/', include('rest_framework.urls', namespace="rest_framework"))
    path("api-token-auth/", obtain_auth_token), # gives us access to token auth
] + static(settings.STATIC_URL,document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
