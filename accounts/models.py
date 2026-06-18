from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('farmer', 'কৃষক'),
        ('trader', 'ব্যবসায়ী'),
        ('general', 'সাধারণ'),
    ]

    SUBSCRIPTION_STATUS = [
        ('trial', 'ট্রায়াল'),
        ('active', 'সক্রিয়'),
        ('expired', 'মেয়াদ শেষ'),
    ]

    phone = models.CharField(max_length=20, blank=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='general')
    district = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    is_verified = models.BooleanField(default=False)

    trial_start = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)
    subscription_status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS, default='trial')
    subscription_plan = models.ForeignKey(
        'SubscriptionPlan', on_delete=models.SET_NULL, null=True, blank=True, related_name='subscribers'
    )
    subscription_expires = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk and not self.trial_start:
            self.trial_start = timezone.now()
            self.trial_end = timezone.now() + timedelta(days=60)
            self.subscription_status = 'trial'
        super().save(*args, **kwargs)

    @property
    def has_access(self):
        now = timezone.now()
        if self.is_superuser or self.is_staff:
            return True
        if self.subscription_status == 'trial' and self.trial_end and now < self.trial_end:
            return True
        if self.subscription_status == 'active' and self.subscription_expires and now < self.subscription_expires:
            return True
        return False

    @property
    def trial_days_left(self):
        if self.subscription_status != 'trial' or not self.trial_end:
            return 0
        delta = self.trial_end - timezone.now()
        return max(0, delta.days)

    @property
    def subscription_days_left(self):
        if self.subscription_status != 'active' or not self.subscription_expires:
            return 0
        delta = self.subscription_expires - timezone.now()
        return max(0, delta.days)

    def check_and_update_status(self):
        now = timezone.now()
        if self.subscription_status == 'trial' and self.trial_end and now >= self.trial_end:
            self.subscription_status = 'expired'
            self.save(update_fields=['subscription_status'])
        elif self.subscription_status == 'active' and self.subscription_expires and now >= self.subscription_expires:
            self.subscription_status = 'expired'
            self.save(update_fields=['subscription_status'])

    class Meta:
        db_table = 'auth_user'


class SubscriptionPlan(models.Model):
    PLAN_TYPE = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
    ]

    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField(default=30)
    description = models.TextField(blank=True)
    features = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name} - ৳{self.price}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=200, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} - {self.status}"
