"""
URL configuration for strampolati project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from allauth.account.views import password_reset_from_key
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from strampolati.views import HomeView

urlpatterns = [
    path('', HomeView.as_view()),
    path('manager/', include("api.urls")),
    path('manager/', admin.site.urls),
    path("__debug__/", include("debug_toolbar.urls")),
    path('log_viewer/', include('log_viewer.urls', namespace='logs')),
    path('api/schema', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    re_path(
        r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
        password_reset_from_key,
        name='password_reset_confirm'
    ),
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('accounts/', include('allauth.urls')),
]

handler404 = 'frontend.views.view404'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
