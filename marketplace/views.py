from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from core.pagination import paginate

from .models import BuySellPost, Rating
from .forms import PostForm, RatingForm

User = get_user_model()


def post_list(request):
    post_type = request.GET.get('type', '')
    category = request.GET.get('category', '')
    q = request.GET.get('q', '')

    posts = BuySellPost.objects.filter(status='approved').select_related('user', 'category')

    if post_type:
        posts = posts.filter(post_type=post_type)
    if category:
        posts = posts.filter(category__slug=category)
    if q:
        posts = posts.filter(Q(title__icontains=q) | Q(product_name__icontains=q))

    from market.models import ProductCategory
    categories = ProductCategory.objects.all()

    page_obj = paginate(request, posts, per_page=12)

    context = {
        'posts': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'selected_type': post_type,
        'selected_category': category,
        'search_query': q,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'marketplace/partials/post_grid.html', context)

    return render(request, 'marketplace/post_list.html', context)


def post_detail(request, pk):
    post = get_object_or_404(BuySellPost, pk=pk, status='approved')
    post.views_count += 1
    post.save(update_fields=['views_count'])

    context = {'post': post}
    return render(request, 'marketplace/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            if not post.phone:
                post.phone = request.user.phone
            post.save()
            messages.success(request, 'আপনার পোস্ট সফলভাবে তৈরি হয়েছে। অনুমোদনের পর প্রকাশিত হবে।')
            return redirect('marketplace:post_list')
    else:
        form = PostForm(initial={'phone': request.user.phone})

    return render(request, 'marketplace/post_create.html', {'form': form})


@login_required
def my_posts(request):
    posts = BuySellPost.objects.filter(user=request.user)
    return render(request, 'marketplace/my_posts.html', {'posts': posts})


def profile_list(request):
    user_type = request.GET.get('type', '')
    q = request.GET.get('q', '')

    users = User.objects.filter(is_active=True, is_staff=False).annotate(
        avg_rating=Avg('received_ratings__score'),
        rating_count=Count('received_ratings'),
        post_count=Count('posts', filter=Q(posts__status='approved')),
    )

    if user_type:
        users = users.filter(user_type=user_type)
    if q:
        users = users.filter(Q(first_name__icontains=q) | Q(username__icontains=q) | Q(district__icontains=q))

    users = users.order_by('-is_verified', '-avg_rating')
    page_obj = paginate(request, users, per_page=12)

    context = {
        'users': page_obj,
        'page_obj': page_obj,
        'selected_type': user_type,
        'search_query': q,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'marketplace/partials/profile_grid.html', context)

    return render(request, 'marketplace/profile_list.html', context)


def profile_detail(request, username):
    profile_user = get_object_or_404(User, username=username, is_active=True)

    stats = Rating.objects.filter(rated_user=profile_user).aggregate(
        avg_rating=Avg('score'), rating_count=Count('id')
    )

    posts = BuySellPost.objects.filter(user=profile_user, status='approved')[:6]
    ratings = Rating.objects.filter(rated_user=profile_user).select_related('rated_by')[:5]

    already_rated = False
    if request.user.is_authenticated and request.user != profile_user:
        already_rated = Rating.objects.filter(rated_user=profile_user, rated_by=request.user).exists()

    rating_form = None
    if request.user.is_authenticated and request.user != profile_user and not already_rated:
        rating_form = RatingForm()

    context = {
        'profile_user': profile_user,
        'stats': stats,
        'posts': posts,
        'ratings': ratings,
        'rating_form': rating_form,
        'already_rated': already_rated,
    }
    return render(request, 'marketplace/profile_detail.html', context)


@login_required
def rate_user(request, username):
    profile_user = get_object_or_404(User, username=username)

    if request.user == profile_user:
        messages.error(request, 'আপনি নিজেকে রেটিং দিতে পারবেন না।')
        return redirect('marketplace:profile_detail', username=username)

    if Rating.objects.filter(rated_user=profile_user, rated_by=request.user).exists():
        messages.warning(request, 'আপনি ইতিমধ্যে এই ব্যবহারকারীকে রেটিং দিয়েছেন।')
        return redirect('marketplace:profile_detail', username=username)

    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.rated_user = profile_user
            rating.rated_by = request.user
            rating.save()
            messages.success(request, 'রেটিং সফলভাবে দেওয়া হয়েছে।')

    return redirect('marketplace:profile_detail', username=username)
