from django.contrib import admin
from .models import VideoCategory, Video, PriceAlert


@admin.register(VideoCategory)
class VideoCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    prepopulated_fields = {'slug': ('name_en',)}


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'youtube_id', 'is_featured', 'is_active', 'created_at']
    list_filter = ['category', 'is_featured', 'is_active']
    list_editable = ['is_featured', 'is_active']
    search_fields = ['title']
    readonly_fields = ['youtube_id', 'created_at']
    fieldsets = (
        (None, {
            'fields': ('url', 'title', 'description', 'category'),
            'description': 'শুধু YouTube URL পেস্ট করুন — বাকি সব স্বয়ংক্রিয়ভাবে হবে।'
        }),
        ('অপশন', {
            'fields': ('is_featured', 'is_active', 'order'),
        }),
        ('অটো জেনারেটেড', {
            'fields': ('youtube_id', 'created_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'target_price', 'condition', 'is_active', 'is_triggered']
    list_filter = ['condition', 'is_active', 'is_triggered']
