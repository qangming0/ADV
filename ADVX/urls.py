"""ADVX URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path, include, re_path
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import TemplateView
from rest_framework import permissions
from .views import HelloView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,   # lấy access + refresh
    TokenRefreshView,      # làm mới access bằng refresh
    TokenVerifyView,       # (tuỳ chọn) xác thực chữ ký token
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from core.errorhandler import views as errorhandler_view


handler400 = errorhandler_view.bad_request
handler403 = errorhandler_view.permission_denied
handler404 = errorhandler_view.page_not_found
handler500 = errorhandler_view.server_error


from authen import urls as url_authen
from device import urls as url_device
from media import urls as url_media
from globalconfig import urls as url_global
from config.provider import urls as url_provider
from config.system import urls as url_system
from config.user import urls as url_config_user
from modules.adversiting import urls as url_adversiting
from positioncontrol import urls as url_position
from synch import urls as url_synch
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views


schema_view = get_schema_view(
    openapi.Info(
        title="ADV API",
        default_version="v1",
        description="Test API with Swagger",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
# i18n_patterns # for language
urlpatterns = [
    # path('',
    #     TemplateView.as_view(template_name='templates/frontend/index.html'),
    #     name='Home'
    # ),
    path('admin/', admin.site.urls),  # thêm / ở cuối cho chuẩn
    path('api/v1/auth/', include('dj_rest_auth.urls')),
    path('api/v1/auth/registration/', include('dj_rest_auth.registration.urls')),
    path("api/hello/", HelloView.as_view(), name="hello"),

    # SimpleJWT endpoints thay cho rest_framework_jwt
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('api/v1/', include(url_authen)),
    path('api/v1/', include(url_global)),
    path('api/v1/', include(url_device)),
    path('api/v1/', include(url_provider)),
    path('api/v1/', include(url_system)),
    path('api/v1/', include(url_synch)),
    path('api/v1/', include(url_config_user)),
    path('api/v1/', include(url_media)),
    path('api/v1/', include(url_adversiting)),
    path('api/v1/', include(url_position)),
    re_path(r"^swagger(?P<format>\.json|\.yaml)$",
            schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0),
         name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0),
         name="schema-redoc"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html'), name='Home'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)