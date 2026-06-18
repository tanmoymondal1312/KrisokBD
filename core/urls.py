from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.generic import TemplateView

from . import views
from .sitemaps import StaticViewSitemap, MarketSitemap, ProductSitemap

app_name = 'core'

sitemaps = {
    'static': StaticViewSitemap,
    'markets': MarketSitemap,
    'products': ProductSitemap,
}

urlpatterns = [
    path('', views.home, name='home'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name='robots'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]
