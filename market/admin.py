from django.contrib import admin
from .models import (
    Division, District, Market, ProductCategory,
    Product, MarketPrice, GovernmentPrice, PopularMarket,
)


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en', 'order', 'is_active']
    prepopulated_fields = {'slug': ('name_en',)}


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en', 'division', 'is_active']
    list_filter = ['division']
    prepopulated_fields = {'slug': ('name_en',)}


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en', 'district', 'is_active']
    list_filter = ['district__division', 'is_active']
    prepopulated_fields = {'slug': ('name_en',)}


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en', 'order']
    prepopulated_fields = {'slug': ('name_en',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en', 'category', 'unit', 'is_active']
    list_filter = ['category', 'is_active']
    prepopulated_fields = {'slug': ('name_en',)}


@admin.register(MarketPrice)
class MarketPriceAdmin(admin.ModelAdmin):
    list_display = ['product', 'market', 'date', 'min_price', 'max_price']
    list_filter = ['date', 'market__district__division', 'product__category']
    date_hierarchy = 'date'


@admin.register(GovernmentPrice)
class GovernmentPriceAdmin(admin.ModelAdmin):
    list_display = ['product', 'price', 'effective_date']
    list_filter = ['effective_date']


@admin.register(PopularMarket)
class PopularMarketAdmin(admin.ModelAdmin):
    list_display = ['market', 'order', 'is_featured']
    list_editable = ['order', 'is_featured']
