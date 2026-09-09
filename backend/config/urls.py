from django.conf import settings

from django.conf.urls.static import static

from django.contrib import admin

from django.http import HttpResponse

from django.urls import include, path, re_path

from opportunities.documents import StaffDocumentServeView

from opportunities.frontend import FrontendView



SITE_URL = "https://globalopportunityconnect.com"



def robots_txt(request):
    
    body = f"User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /api/\nSitemap: {SITE_URL}/sitemap.xml\n"
    
    return HttpResponse(body, content_type="text/plain; charset=utf-8")
    


def sitemap_xml(request):
    
    paths = ["/", "/opportunities", "/how-it-works", "/why-us", "/policies"]
    
    urls = "".join(f"<url><loc>{SITE_URL}{path}</loc><changefreq>weekly</changefreq></url>" for path in paths)
    
    body = "<?xml version='1.0' encoding='UTF-8'?>" + f"<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>{urls}</urlset>"
    
    return HttpResponse(body, content_type="application/xml; charset=utf-8")
    


urlpatterns = [
    
    path("robots.txt", robots_txt, name="robots-txt"),
    
    path("sitemap.xml", sitemap_xml, name="sitemap-xml"),
    
    path("admin/", admin.site.urls),
    
    path("api/", include("opportunities.urls")),
    
    path("", FrontendView.as_view(), name="frontend-root"),
    
    re_path(r"^manus-storage/(?P<key>.*)$", StaffDocumentServeView.as_view(), name="staff-document-serve-public-path"),
    
    re_path(r"^(?!api/|admin/|static/|robots\.txt$|sitemap\.xml$).*$", FrontendView.as_view(), name="frontend-route"),
    
]



urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

















