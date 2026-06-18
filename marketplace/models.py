from django.conf import settings
from django.db import models
from django.utils import timezone


class BuySellPost(models.Model):
    POST_TYPE_CHOICES = [
        ('sell', 'বিক্রয়'),
        ('buy', 'ক্রয়'),
    ]
    STATUS_CHOICES = [
        ('pending', 'অপেক্ষমান'),
        ('approved', 'অনুমোদিত'),
        ('sold', 'বিক্রিত'),
        ('closed', 'বন্ধ'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    post_type = models.CharField(max_length=10, choices=POST_TYPE_CHOICES)
    title = models.CharField(max_length=300)
    product_name = models.CharField(max_length=200)
    category = models.ForeignKey('market.ProductCategory', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default='কেজি')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='posts/%Y/%m/', blank=True)
    location = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_post_type_display()}: {self.title}"


class Rating(models.Model):
    rated_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_ratings'
    )
    rated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_ratings'
    )
    score = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['rated_user', 'rated_by']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rated_by} → {self.rated_user}: {self.score}★"
