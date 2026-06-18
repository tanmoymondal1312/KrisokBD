from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from market.models import Market, Product


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'daily'

    def items(self):
        return [
            'core:home',
            'market:daily_prices',
            'market:division_prices',
            'market:comparison_chart',
            'market:regional_graph',
            'content:video_list',
            'content:govt_prices',
            'content:price_analysis',
            'marketplace:post_list',
            'marketplace:profile_list',
        ]

    def location(self, item):
        return reverse(item)


class MarketSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.7

    def items(self):
        return Market.objects.filter(is_active=True)

    def location(self, obj):
        return reverse('market:market_detail', kwargs={'slug': obj.slug})


class ProductSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.7

    def items(self):
        return Product.objects.filter(is_active=True)

    def location(self, obj):
        return reverse('market:product_detail', kwargs={'slug': obj.slug})
