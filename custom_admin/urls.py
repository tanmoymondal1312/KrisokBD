from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('prices/', views.price_list, name='price_list'),
    path('prices/add/', views.price_add, name='price_add'),
    path('prices/<int:pk>/edit/', views.price_edit, name='price_edit'),
    path('prices/<int:pk>/delete/', views.price_delete, name='price_delete'),

    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    path('markets/', views.market_list, name='market_list'),
    path('markets/add/', views.market_add, name='market_add'),
    path('markets/<int:pk>/edit/', views.market_edit, name='market_edit'),

    path('divisions/', views.division_list, name='division_list'),

    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/toggle-verify/', views.user_toggle_verify, name='user_toggle_verify'),

    path('posts/', views.post_list, name='post_list'),
    path('posts/<int:pk>/approve/', views.post_approve, name='post_approve'),
    path('posts/<int:pk>/reject/', views.post_reject, name='post_reject'),

    path('videos/', views.video_list, name='video_list'),
    path('videos/add/', views.video_add, name='video_add'),
    path('videos/<int:pk>/delete/', views.video_delete, name='video_delete'),

    path('govt-prices/', views.govt_price_list, name='govt_price_list'),
    path('govt-prices/add/', views.govt_price_add, name='govt_price_add'),

    path('popular-markets/', views.popular_market_list, name='popular_market_list'),
    path('popular-markets/add/', views.popular_market_add, name='popular_market_add'),
    path('popular-markets/<int:pk>/remove/', views.popular_market_remove, name='popular_market_remove'),
]
