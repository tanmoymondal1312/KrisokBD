import re
from django.db import models


class VideoCategory(models.Model):
    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(unique=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Video categories'

    def __str__(self):
        return self.name


class Video(models.Model):
    url = models.URLField(help_text="YouTube ভিডিওর লিংক পেস্ট করুন")
    youtube_id = models.CharField(max_length=20, blank=True, editable=False)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    category = models.ForeignKey(VideoCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='videos')
    is_featured = models.BooleanField(default=False, help_text="হোমপেজে দেখাবে")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def save(self, *args, **kwargs):
        if self.url and not self.youtube_id:
            self.youtube_id = self._extract_youtube_id(self.url)
        super().save(*args, **kwargs)

    @staticmethod
    def _extract_youtube_id(url):
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return ''

    @property
    def thumbnail_url(self):
        if self.youtube_id:
            return f'https://img.youtube.com/vi/{self.youtube_id}/hqdefault.jpg'
        return ''

    @property
    def embed_url(self):
        if self.youtube_id:
            return f'https://www.youtube.com/embed/{self.youtube_id}'
        return ''

    def __str__(self):
        return self.title


class PriceAlert(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='price_alerts')
    product = models.ForeignKey('market.Product', on_delete=models.CASCADE)
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(max_length=10, choices=[('below', 'নিচে গেলে'), ('above', 'উপরে গেলে')])
    is_active = models.BooleanField(default=True)
    is_triggered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} {self.get_condition_display()} ৳{self.target_price}"
