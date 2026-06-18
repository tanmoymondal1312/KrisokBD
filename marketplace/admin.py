from django.contrib import admin
from .models import BuySellPost, Rating


@admin.register(BuySellPost)
class BuySellPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'post_type', 'product_name', 'price', 'status', 'created_at']
    list_filter = ['post_type', 'status', 'category']
    list_editable = ['status']
    search_fields = ['title', 'product_name', 'user__username']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['rated_user', 'rated_by', 'score', 'created_at']
    list_filter = ['score']
