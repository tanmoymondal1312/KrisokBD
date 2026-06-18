from datetime import date, timedelta
from collections import defaultdict

from django.db.models import Avg, Min, Max
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from .models import (
    Division, Market, ProductCategory, Product,
    MarketPrice, GovernmentPrice, PopularMarket,
)


def _get_latest_date_with_data():
    latest = MarketPrice.objects.order_by('-date').values_list('date', flat=True).first()
    return latest or date.today()


def daily_prices(request):
    selected_date = request.GET.get('date')
    category_slug = request.GET.get('category', '')
    division_slug = request.GET.get('division', '')

    if selected_date:
        try:
            price_date = date.fromisoformat(selected_date)
        except ValueError:
            price_date = _get_latest_date_with_data()
    else:
        price_date = _get_latest_date_with_data()

    is_today = price_date == date.today()

    prices = MarketPrice.objects.filter(date=price_date).select_related(
        'product', 'product__category', 'market', 'market__district__division'
    )

    if category_slug:
        prices = prices.filter(product__category__slug=category_slug)
    if division_slug:
        prices = prices.filter(market__district__division__slug=division_slug)

    product_data = {}
    for p in prices:
        key = p.product_id
        if key not in product_data:
            govt = GovernmentPrice.objects.filter(product=p.product).first()
            product_data[key] = {
                'product': p.product,
                'product_type': p.product_type or 'দেশি',
                'min_price': p.min_price,
                'max_price': p.max_price,
                'govt_price': govt.price if govt else None,
                'count': 1,
            }
        else:
            entry = product_data[key]
            entry['min_price'] = min(entry['min_price'], p.min_price)
            entry['max_price'] = max(entry['max_price'], p.max_price)
            entry['count'] += 1

    product_list = sorted(product_data.values(), key=lambda x: x['product'].category.order)

    context = {
        'prices': product_list,
        'price_date': price_date,
        'is_today': is_today,
        'categories': ProductCategory.objects.all(),
        'divisions': Division.objects.filter(is_active=True),
        'selected_category': category_slug,
        'selected_division': division_slug,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'market/partials/price_table.html', context)

    return render(request, 'market/daily_prices.html', context)


def division_prices(request):
    product_slug = request.GET.get('product', '')
    divisions = Division.objects.filter(is_active=True)
    price_date = _get_latest_date_with_data()

    products = Product.objects.filter(is_active=True).select_related('category')

    division_data = []
    selected_product = None

    if product_slug:
        selected_product = get_object_or_404(Product, slug=product_slug)
        for division in divisions:
            agg = MarketPrice.objects.filter(
                date=price_date,
                product=selected_product,
                market__district__division=division,
            ).aggregate(
                avg_min=Avg('min_price'),
                avg_max=Avg('max_price'),
                lowest=Min('min_price'),
                highest=Max('max_price'),
            )
            if agg['avg_min']:
                division_data.append({
                    'division': division,
                    'avg_min': round(agg['avg_min'], 2),
                    'avg_max': round(agg['avg_max'], 2),
                    'lowest': agg['lowest'],
                    'highest': agg['highest'],
                })
    else:
        for division in divisions:
            prices_qs = MarketPrice.objects.filter(
                date=price_date,
                market__district__division=division,
            ).select_related('product')

            product_prices = {}
            for p in prices_qs:
                key = p.product_id
                if key not in product_prices:
                    product_prices[key] = {
                        'product': p.product,
                        'min_price': p.min_price,
                        'max_price': p.max_price,
                    }
                else:
                    product_prices[key]['min_price'] = min(product_prices[key]['min_price'], p.min_price)
                    product_prices[key]['max_price'] = max(product_prices[key]['max_price'], p.max_price)

            division_data.append({
                'division': division,
                'products': sorted(product_prices.values(), key=lambda x: x['product'].name),
            })

    context = {
        'divisions': divisions,
        'products': products,
        'division_data': division_data,
        'selected_product': selected_product,
        'price_date': price_date,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'market/partials/division_table.html', context)

    return render(request, 'market/division_prices.html', context)


def comparison_chart(request):
    price_date = _get_latest_date_with_data()
    divisions = Division.objects.filter(is_active=True)
    categories = ProductCategory.objects.all()

    category_slug = request.GET.get('category', 'spices')
    category = ProductCategory.objects.filter(slug=category_slug).first() or categories.first()

    products = Product.objects.filter(category=category, is_active=True)

    chart_data = {'labels': [], 'datasets': []}

    chart_data['labels'] = [p.name for p in products]

    for division in divisions:
        prices_for_div = []
        for product in products:
            agg = MarketPrice.objects.filter(
                date=price_date, product=product,
                market__district__division=division,
            ).aggregate(avg_price=Avg('avg_price'))
            prices_for_div.append(float(agg['avg_price'] or 0))

        chart_data['datasets'].append({
            'label': division.name,
            'data': prices_for_div,
        })

    context = {
        'chart_data': chart_data,
        'categories': categories,
        'selected_category': category_slug,
        'price_date': price_date,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'market/partials/chart_data.html', context)

    return render(request, 'market/comparison_chart.html', context)


def regional_graph(request):
    price_date = _get_latest_date_with_data()
    product_slug = request.GET.get('product', 'onion')
    product = Product.objects.filter(slug=product_slug).first()
    if not product:
        product = Product.objects.first()

    products = Product.objects.filter(is_active=True).select_related('category')
    divisions = Division.objects.filter(is_active=True)

    graph_data = {'labels': [], 'min_prices': [], 'max_prices': []}

    for division in divisions:
        agg = MarketPrice.objects.filter(
            date=price_date, product=product,
            market__district__division=division,
        ).aggregate(
            avg_min=Avg('min_price'),
            avg_max=Avg('max_price'),
        )
        if agg['avg_min']:
            graph_data['labels'].append(division.name)
            graph_data['min_prices'].append(float(agg['avg_min']))
            graph_data['max_prices'].append(float(agg['avg_max']))

    context = {
        'graph_data': graph_data,
        'product': product,
        'products': products,
        'selected_product': product_slug,
        'price_date': price_date,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'market/partials/graph_data.html', context)

    return render(request, 'market/regional_graph.html', context)


def market_detail(request, slug):
    market = get_object_or_404(Market, slug=slug)
    price_date = _get_latest_date_with_data()

    prices = MarketPrice.objects.filter(
        market=market, date=price_date
    ).select_related('product', 'product__category').order_by('product__category__order', 'product__name')

    price_list = []
    for p in prices:
        govt = GovernmentPrice.objects.filter(product=p.product).first()
        price_list.append({
            'product': p.product,
            'min_price': p.min_price,
            'max_price': p.max_price,
            'avg_price': p.avg_price,
            'govt_price': govt.price if govt else None,
        })

    context = {
        'market': market,
        'prices': price_list,
        'price_date': price_date,
    }
    return render(request, 'market/market_detail.html', context)
