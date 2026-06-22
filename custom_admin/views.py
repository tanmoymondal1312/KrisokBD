from datetime import date, timedelta
from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model
from core.pagination import paginate
from django.db.models import Count, Avg, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from market.models import (
    Division, District, Market, ProductCategory, Product,
    MarketPrice, GovernmentPrice, PopularMarket,
)
from marketplace.models import BuySellPost, Rating
from content.models import Video, VideoCategory

User = get_user_model()


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/accounts/login/?next={request.path}')
        if not request.user.is_staff:
            messages.error(request, 'আপনার এডমিন প্যানেলে প্রবেশের অনুমতি নেই।')
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper


# ============ DASHBOARD ============

@admin_required
def dashboard(request):
    today = date.today()

    latest_date = MarketPrice.objects.order_by('-date').values_list('date', flat=True).first() or today
    prices_qs = MarketPrice.objects.filter(date=latest_date).select_related(
        'product', 'product__category', 'market', 'market__district'
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
                'min_market': p.market,
                'max_market': p.market,
                'min_updated_at': p.updated_at,
                'max_updated_at': p.updated_at,
                'govt_price': govt.price if govt else None,
            }
        else:
            if p.min_price < product_data[key]['min_price']:
                product_data[key]['min_price'] = p.min_price
                product_data[key]['min_market'] = p.market
                product_data[key]['min_updated_at'] = p.updated_at
            if p.max_price > product_data[key]['max_price']:
                product_data[key]['max_price'] = p.max_price
                product_data[key]['max_market'] = p.market
                product_data[key]['max_updated_at'] = p.updated_at
    recent_prices = sorted(product_data.values(), key=lambda x: x['product'].category.order)[:10]

    context = {
        'total_users': User.objects.filter(is_staff=False).count(),
        'total_products': Product.objects.count(),
        'total_markets': Market.objects.count(),
        'total_prices_today': MarketPrice.objects.filter(date=today).count(),
        'pending_posts': BuySellPost.objects.filter(status='pending').count(),
        'total_videos': Video.objects.count(),
        'verified_users': User.objects.filter(is_verified=True).count(),
        'recent_users': User.objects.filter(is_staff=False).order_by('-date_joined')[:5],
        'recent_posts': BuySellPost.objects.order_by('-created_at')[:5],
        'recent_prices': recent_prices,
        'price_date': latest_date,
    }
    return render(request, 'custom_admin/dashboard.html', context)


# ============ MARKET PRICES ============

@admin_required
def price_list(request):
    price_date = request.GET.get('date', str(date.today()))
    prices = MarketPrice.objects.filter(date=price_date).select_related(
        'product', 'market', 'market__district__division'
    ).order_by('product__name', 'market__name')
    page_obj = paginate(request, prices, per_page=30)
    markets = Market.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    context = {'prices': page_obj, 'page_obj': page_obj, 'markets': markets, 'products': products, 'price_date': price_date}
    return render(request, 'custom_admin/price_list.html', context)


@admin_required
def price_add(request):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=request.POST.get('product'))
        market = get_object_or_404(Market, pk=request.POST.get('market'))
        price_date = request.POST.get('date', str(date.today()))
        MarketPrice.objects.update_or_create(
            product=product, market=market, date=price_date,
            defaults={
                'min_price': request.POST.get('min_price'),
                'max_price': request.POST.get('max_price'),
                'product_type': request.POST.get('product_type', 'দেশি'),
            }
        )
        messages.success(request, f'{product.name} — {market.name} এর দর সংরক্ষিত হয়েছে।')
        return redirect('custom_admin:price_list')

    markets = Market.objects.filter(is_active=True).select_related('district__division')
    products = Product.objects.filter(is_active=True).select_related('category')
    return render(request, 'custom_admin/price_form.html', {
        'markets': markets, 'products': products, 'today': str(date.today())
    })


@admin_required
def price_edit(request, pk):
    price = get_object_or_404(MarketPrice, pk=pk)
    if request.method == 'POST':
        price.product = get_object_or_404(Product, pk=request.POST.get('product'))
        price.market = get_object_or_404(Market, pk=request.POST.get('market'))
        price.date = request.POST.get('date', str(date.today()))
        price.min_price = request.POST.get('min_price')
        price.max_price = request.POST.get('max_price')
        price.product_type = request.POST.get('product_type', 'দেশি')
        price.avg_price = None
        price.save()
        messages.success(request, f'{price.product.name} — {price.market.name} এর দর আপডেট হয়েছে।')
        return redirect('custom_admin:price_list')

    markets = Market.objects.filter(is_active=True).select_related('district__division')
    products = Product.objects.filter(is_active=True).select_related('category')
    return render(request, 'custom_admin/price_form.html', {
        'price': price, 'markets': markets, 'products': products, 'today': str(date.today())
    })


@admin_required
def price_delete(request, pk):
    price = get_object_or_404(MarketPrice, pk=pk)
    price.delete()
    messages.success(request, 'দর মুছে ফেলা হয়েছে।')
    return redirect('custom_admin:price_list')


# ============ PRODUCTS ============

@admin_required
def product_list(request):
    products = Product.objects.select_related('category').all()
    page_obj = paginate(request, products, per_page=25)
    categories = ProductCategory.objects.all()
    return render(request, 'custom_admin/product_list.html', {'products': page_obj, 'page_obj': page_obj, 'categories': categories})


@admin_required
def product_add(request):
    if request.method == 'POST':
        cat = get_object_or_404(ProductCategory, pk=request.POST.get('category'))
        Product.objects.create(
            name=request.POST['name'], name_en=request.POST['name_en'],
            slug=request.POST['slug'], category=cat,
            unit=request.POST.get('unit', 'কেজি'),
        )
        messages.success(request, 'পণ্য যোগ করা হয়েছে।')
        return redirect('custom_admin:product_list')
    categories = ProductCategory.objects.all()
    return render(request, 'custom_admin/product_form.html', {'categories': categories})


@admin_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.name = request.POST['name']
        product.name_en = request.POST['name_en']
        product.slug = request.POST['slug']
        product.category = get_object_or_404(ProductCategory, pk=request.POST['category'])
        product.unit = request.POST.get('unit', 'কেজি')
        product.is_active = 'is_active' in request.POST
        product.save()
        messages.success(request, 'পণ্য আপডেট হয়েছে।')
        return redirect('custom_admin:product_list')
    categories = ProductCategory.objects.all()
    return render(request, 'custom_admin/product_form.html', {'product': product, 'categories': categories})


@admin_required
def product_delete(request, pk):
    get_object_or_404(Product, pk=pk).delete()
    messages.success(request, 'পণ্য মুছে ফেলা হয়েছে।')
    return redirect('custom_admin:product_list')


# ============ MARKETS ============

@admin_required
def market_list(request):
    markets = Market.objects.select_related('district__division').all()
    page_obj = paginate(request, markets, per_page=25)
    return render(request, 'custom_admin/market_list.html', {'markets': page_obj, 'page_obj': page_obj})


@admin_required
def market_add(request):
    if request.method == 'POST':
        district = get_object_or_404(District, pk=request.POST['district'])
        Market.objects.create(
            name=request.POST['name'], name_en=request.POST['name_en'],
            slug=request.POST['slug'], district=district,
        )
        messages.success(request, 'বাজার যোগ করা হয়েছে।')
        return redirect('custom_admin:market_list')
    districts = District.objects.select_related('division').all()
    return render(request, 'custom_admin/market_form.html', {'districts': districts})


@admin_required
def market_edit(request, pk):
    market = get_object_or_404(Market, pk=pk)
    if request.method == 'POST':
        market.name = request.POST['name']
        market.name_en = request.POST['name_en']
        market.slug = request.POST['slug']
        market.district = get_object_or_404(District, pk=request.POST['district'])
        market.is_active = 'is_active' in request.POST
        market.save()
        messages.success(request, 'বাজার আপডেট হয়েছে।')
        return redirect('custom_admin:market_list')
    districts = District.objects.select_related('division').all()
    return render(request, 'custom_admin/market_form.html', {'market': market, 'districts': districts})


# ============ DIVISIONS ============

@admin_required
def division_list(request):
    divisions = Division.objects.prefetch_related('districts').all()
    return render(request, 'custom_admin/division_list.html', {'divisions': divisions})


# ============ USERS ============

@admin_required
def user_list(request):
    q = request.GET.get('q', '')
    users = User.objects.filter(is_staff=False).annotate(
        rating_avg=Avg('received_ratings__score'),
        post_count=Count('posts'),
    ).order_by('-date_joined')
    if q:
        users = users.filter(Q(first_name__icontains=q) | Q(username__icontains=q) | Q(phone__icontains=q))
    page_obj = paginate(request, users, per_page=25)
    return render(request, 'custom_admin/user_list.html', {'users': page_obj, 'page_obj': page_obj, 'search_query': q})


@admin_required
def user_toggle_verify(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_verified = not user.is_verified
    user.save(update_fields=['is_verified'])
    status = 'ভেরিফাই' if user.is_verified else 'আনভেরিফাই'
    messages.success(request, f'{user.first_name or user.username} {status} করা হয়েছে।')
    return redirect('custom_admin:user_list')


# ============ BUY-SELL POSTS ============

@admin_required
def post_list(request):
    status_filter = request.GET.get('status', '')
    posts = BuySellPost.objects.select_related('user', 'category').all()
    if status_filter:
        posts = posts.filter(status=status_filter)
    page_obj = paginate(request, posts, per_page=20)
    return render(request, 'custom_admin/post_list.html', {'posts': page_obj, 'page_obj': page_obj, 'status_filter': status_filter})


@admin_required
def post_approve(request, pk):
    post = get_object_or_404(BuySellPost, pk=pk)
    post.status = 'approved'
    post.save(update_fields=['status'])
    messages.success(request, f'"{post.title}" অনুমোদিত হয়েছে।')
    return redirect('custom_admin:post_list')


@admin_required
def post_reject(request, pk):
    post = get_object_or_404(BuySellPost, pk=pk)
    post.status = 'closed'
    post.save(update_fields=['status'])
    messages.success(request, f'"{post.title}" বাতিল করা হয়েছে।')
    return redirect('custom_admin:post_list')


# ============ VIDEOS ============

@admin_required
def video_list(request):
    videos = Video.objects.select_related('category').all()
    page_obj = paginate(request, videos, per_page=12)
    return render(request, 'custom_admin/video_list.html', {'videos': page_obj, 'page_obj': page_obj})


@admin_required
def video_add(request):
    if request.method == 'POST':
        cat = None
        if request.POST.get('category'):
            cat = VideoCategory.objects.filter(pk=request.POST['category']).first()
        Video.objects.create(
            url=request.POST['url'], title=request.POST['title'],
            description=request.POST.get('description', ''),
            category=cat, is_featured='is_featured' in request.POST,
        )
        messages.success(request, 'ভিডিও যোগ করা হয়েছে।')
        return redirect('custom_admin:video_list')
    categories = VideoCategory.objects.all()
    return render(request, 'custom_admin/video_form.html', {'categories': categories})


@admin_required
def video_delete(request, pk):
    get_object_or_404(Video, pk=pk).delete()
    messages.success(request, 'ভিডিও মুছে ফেলা হয়েছে।')
    return redirect('custom_admin:video_list')


# ============ GOVT PRICES ============

@admin_required
def govt_price_list(request):
    prices = GovernmentPrice.objects.select_related('product').all()
    page_obj = paginate(request, prices, per_page=25)
    return render(request, 'custom_admin/govt_price_list.html', {'prices': page_obj, 'page_obj': page_obj})


@admin_required
def govt_price_add(request):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=request.POST['product'])
        GovernmentPrice.objects.update_or_create(
            product=product,
            defaults={'price': request.POST['price'], 'effective_date': request.POST['effective_date']}
        )
        messages.success(request, 'সরকারি মূল্য সংরক্ষিত হয়েছে।')
        return redirect('custom_admin:govt_price_list')
    products = Product.objects.filter(is_active=True)
    return render(request, 'custom_admin/govt_price_form.html', {'products': products, 'today': str(date.today())})


# ============ POPULAR MARKETS ============

@admin_required
def popular_market_list(request):
    popular = PopularMarket.objects.select_related('market__district__division').all()
    markets = Market.objects.filter(is_active=True).exclude(popular__isnull=False)
    return render(request, 'custom_admin/popular_market_list.html', {'popular': popular, 'available_markets': markets})


@admin_required
def popular_market_add(request):
    if request.method == 'POST':
        market = get_object_or_404(Market, pk=request.POST['market'])
        order = PopularMarket.objects.count()
        PopularMarket.objects.get_or_create(market=market, defaults={'order': order})
        messages.success(request, f'{market.name} জনপ্রিয় বাজারে যোগ হয়েছে।')
    return redirect('custom_admin:popular_market_list')


@admin_required
def popular_market_remove(request, pk):
    get_object_or_404(PopularMarket, pk=pk).delete()
    messages.success(request, 'জনপ্রিয় বাজার থেকে সরানো হয়েছে।')
    return redirect('custom_admin:popular_market_list')
