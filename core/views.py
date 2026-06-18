from datetime import date

from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render

from market.models import (
    MarketPrice, PopularMarket, GovernmentPrice, Product, Market,
)


def home(request):
    today = date.today()

    latest_date = MarketPrice.objects.order_by('-date').values_list('date', flat=True).first()
    if not latest_date:
        latest_date = today

    markets_updated = Market.objects.filter(
        prices__date=latest_date
    ).distinct().count()

    prices_qs = MarketPrice.objects.filter(date=latest_date).select_related(
        'product', 'product__category'
    )

    product_data = {}
    for p in prices_qs:
        key = p.product_id
        if key not in product_data:
            govt = GovernmentPrice.objects.filter(product=p.product).first()
            product_data[key] = {
                'product': p.product,
                'product_type': p.product_type or 'দেশি',
                'min_price': p.min_price,
                'max_price': p.max_price,
                'govt_price': govt.price if govt else None,
            }
        else:
            product_data[key]['min_price'] = min(product_data[key]['min_price'], p.min_price)
            product_data[key]['max_price'] = max(product_data[key]['max_price'], p.max_price)

    recent_prices = sorted(product_data.values(), key=lambda x: x['product'].category.order)[:10]

    popular_markets = PopularMarket.objects.filter(
        is_featured=True
    ).select_related('market', 'market__district', 'market__district__division')

    context = {
        'stats': {
            'today_visitors': 200,
            'total_visitors': 10054,
            'total_registered': User.objects.count(),
            'total_page_views': 10153,
            'active_farmers': 85,
            'active_traders': 42,
            'markets_updated': markets_updated,
        },
        'recent_prices': recent_prices,
        'price_date': latest_date,
        'is_today': latest_date == today,
        'popular_markets': popular_markets,
    }
    return render(request, 'core/home.html', context)
