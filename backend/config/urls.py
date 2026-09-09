from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path, re_path
from opportunities.documents import StaffDocumentServeView
from opportunities.frontend import FrontendView
SITE_URL = 'https://globalopportunityconnect.com'
robots_txt = lambda request: HttpResponse('User-agent: *' + chr(10) + 'Allow: /' + chr(10) + 'Disallow: /admin/' + chr(10) + 'Disallow: /api/' + chr(10) + 'Sitemap: ' + SITE_URL + '/sitemap.xml' + chr(10), content_type='text/plain; charset=utf-8')
sitemap_xml = lambda request: HttpResponse("<?xml version='1.0' encoding='UTF-8'?>" + "<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>" + ''.join('<url><loc>' + SITE_URL + item + '</loc><changefreq>weekly</changefreq></url>' for item in ['/', '/opportunities', '/how-it-works', '/why-us', '/policies']) + '</urlset>', content_type='application/xml; charset=utf-8')
urlpatterns = [path('robots.txt', robots_txt, name='robots-txt'), path('sitemap.xml', sitemap_xml, name='sitemap-xml'), path('admin/', admin.site.urls), path('api/', include('opportunities.urls')), path('', FrontendView.as_view(), name='frontend-root'), re_path(r'^manus-storage/(?P<key>.*)$', StaffDocumentServeView.as_view(), name='staff-document-serve-public-path'), re_path(r'^(?!api/|admin/|static/|robots.txt$|sitemap.xml$).*$', FrontendView.as_view(), name='frontend-route')]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
