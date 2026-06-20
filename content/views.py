from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Min, Max, Q
from core.pagination import paginate
from django.shortcuts import render

from .models import Video, VideoCategory, PriceAlert
from market.models import (
    MarketPrice, GovernmentPrice, Product, Division, ProductCategory as MktCategory,
)


def video_list(request):
    category_slug = request.GET.get('category', '')

    videos = Video.objects.filter(is_active=True).select_related('category')
    if category_slug:
        videos = videos.filter(category__slug=category_slug)

    categories = VideoCategory.objects.all()
    page_obj = paginate(request, videos, per_page=9)

    context = {
        'videos': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_slug,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'content/partials/video_grid.html', context)

    return render(request, 'content/video_list.html', context)


def govt_prices(request):
    prices = GovernmentPrice.objects.select_related('product', 'product__category').order_by(
        'product__category__order', 'product__name'
    )

    context = {'prices': prices}
    return render(request, 'content/govt_prices.html', context)


def price_analysis(request):
    today = date.today()
    latest = MarketPrice.objects.order_by('-date').values_list('date', flat=True).first()
    if not latest:
        latest = today

    prev_date = latest - timedelta(days=1)

    products = Product.objects.filter(is_active=True).select_related('category')

    analysis = []
    for product in products:
        curr = MarketPrice.objects.filter(product=product, date=latest).aggregate(
            avg=Avg('avg_price'), mn=Min('min_price'), mx=Max('max_price')
        )
        prev = MarketPrice.objects.filter(product=product, date=prev_date).aggregate(
            avg=Avg('avg_price')
        )

        if curr['avg'] and prev['avg'] and prev['avg'] > 0:
            change = ((curr['avg'] - prev['avg']) / prev['avg']) * 100
        else:
            change = 0

        analysis.append({
            'product': product,
            'avg_price': curr['avg'],
            'min_price': curr['mn'],
            'max_price': curr['mx'],
            'prev_avg': prev['avg'],
            'change_pct': round(float(change), 1),
        })

    analysis.sort(key=lambda x: abs(x['change_pct']), reverse=True)

    gainers = [a for a in analysis if a['change_pct'] > 0][:5]
    losers = [a for a in analysis if a['change_pct'] < 0][:5]

    context = {
        'analysis': analysis,
        'gainers': gainers,
        'losers': losers,
        'price_date': latest,
        'prev_date': prev_date,
    }
    return render(request, 'content/price_analysis.html', context)
