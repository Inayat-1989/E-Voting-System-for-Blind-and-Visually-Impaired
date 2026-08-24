from django.urls import include, path

urlpatterns = [
    path("", include("accounts.urls")),
    # path("admin/", admin.site.urls),
    path("admin/", include("ecp_admin.urls")),
]
