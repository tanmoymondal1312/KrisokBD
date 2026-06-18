from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Avg, Max, Min

User = get_user_model()
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
                'updated_at': p.updated_at,
            }
        else:
            product_data[key]['min_price'] = min(product_data[key]['min_price'], p.min_price)
            product_data[key]['max_price'] = max(product_data[key]['max_price'], p.max_price)

    recent_prices = sorted(product_data.values(), key=lambda x: x['product'].category.order)[:10]

    # Calculate price change (today vs yesterday)
    prev_date = latest_date - timedelta(days=1)
    price_changes = []
    for prod_id, current in product_data.items():
        prev = MarketPrice.objects.filter(
            product_id=prod_id, date=prev_date
        ).aggregate(avg_prev=Avg('avg_price'))
        curr = MarketPrice.objects.filter(
            product_id=prod_id, date=latest_date
        ).aggregate(avg_curr=Avg('avg_price'))

        if prev['avg_prev'] and curr['avg_curr'] and prev['avg_prev'] > 0:
            change_pct = ((curr['avg_curr'] - prev['avg_prev']) / prev['avg_prev']) * 100
            price_changes.append({
                'product': current['product'],
                'change_pct': round(float(change_pct), 1),
                'direction': 'up' if change_pct > 0 else 'down' if change_pct < 0 else 'same',
            })

    price_changes.sort(key=lambda x: abs(x['change_pct']), reverse=True)
    top_change = price_changes[0] if price_changes else None

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
        'top_change': top_change,
    }
    return render(request, 'core/home.html', context)
