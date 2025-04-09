"""
URL configuration for signal_analyser project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls
from .views import HybridLoginView,UserProfileView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

admin.site.site_header = 'Signal Analyser Admin'
admin.site.index_title = 'Administrator'

urlpatterns = [
    path('', include('core.urls')),
    path("admin/", admin.site.urls),
    path('comtrade_reader/', include('comtrade_reader.urls')),
    # path('auth/', include('djoser.urls')),
    # path('auth/', include('djoser.urls.jwt')),
    path("auth/jwt/create", HybridLoginView.as_view(), name="token_obtain_pair"),
    path("auth/jwt/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path('auth/users/me/', UserProfileView.as_view(), name='user_profile'),
] + debug_toolbar_urls() 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
