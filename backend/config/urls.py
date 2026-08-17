from django.contrib import admin
from django.urls import include, path, re_path
from opportunities.frontend import FrontendView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("opportunities.urls")),
    path("", FrontendView.as_view(), name="frontend-root"),
    re_path(r"^(?!api/|admin/|static/).*$", FrontendView.as_view(), name="frontend-route"),
]
