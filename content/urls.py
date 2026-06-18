from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    path('videos/', views.video_list, name='video_list'),
    path('govt-prices/', views.govt_prices, name='govt_prices'),
    path('analysis/', views.price_analysis, name='price_analysis'),
]
