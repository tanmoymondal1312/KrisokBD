from decimal import Decimal

from django.db import models
from django.utils import timezone


class Division(models.Model):
    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='districts')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.division.name})"


class Market(models.Model):
    name = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='markets')
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.district.name}"


class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Product categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    unit = models.CharField(max_length=50, default='কেজি')
    image = models.ImageField(upload_to='products/', blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category__order', 'name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class MarketPrice(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='prices')
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='prices')
    date = models.DateField(default=timezone.now)
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    max_price = models.DecimalField(max_digits=10, decimal_places=2)
    avg_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    product_type = models.CharField(max_length=100, blank=True, default='দেশি')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'product__name']
        unique_together = ['product', 'market', 'date']

    def save(self, *args, **kwargs):
        if not self.avg_price:
            self.avg_price = (Decimal(str(self.min_price)) + Decimal(str(self.max_price))) / 2
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.market.name} ({self.date})"


class GovernmentPrice(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='govt_prices')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateField()
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-effective_date']

    def __str__(self):
        return f"{self.product.name} - ৳{self.price}"


class PopularMarket(models.Model):
    market = models.OneToOneField(Market, on_delete=models.CASCADE, related_name='popular')
    order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.market.name
