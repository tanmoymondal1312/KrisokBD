from django.urls import path
from . import views

app_name = 'market'

urlpatterns = [
    path('daily/', views.daily_prices, name='daily_prices'),
    path('division/', views.division_prices, name='division_prices'),
    path('comparison/', views.comparison_chart, name='comparison_chart'),
    path('regional/', views.regional_graph, name='regional_graph'),
    path('market/<slug:slug>/', views.market_detail, name='market_detail'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
]
