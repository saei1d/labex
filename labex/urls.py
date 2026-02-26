from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("accounts.urls")),
    path("api/", include("courses.urls")),
    path("api/", include("labs.urls")),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

schema_view = get_schema_view(
    openapi.Info(title="LabEx API", default_version="v1", description="LabEx platform API"),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0)),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0)),
]
