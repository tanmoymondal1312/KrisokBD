from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, SubscriptionPlan, Payment


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'user_type', 'subscription_status', 'is_verified', 'trial_end']
    list_filter = ['user_type', 'subscription_status', 'is_verified']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {'fields': ('phone', 'user_type', 'district', 'address', 'avatar', 'is_verified')}),
        ('Subscription', {'fields': ('trial_start', 'trial_end', 'subscription_status', 'subscription_plan', 'subscription_expires')}),
    )


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price', 'duration_days', 'is_active']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'amount', 'status', 'created_at']
    list_filter = ['status', 'plan']
