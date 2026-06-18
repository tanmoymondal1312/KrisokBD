from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import RegisterForm, LoginForm, ProfileForm
from .models import SubscriptionPlan


def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'স্বাগতম {user.first_name}! আপনার ৬০ দিনের ফ্রি ট্রায়াল শুরু হয়েছে।')
            return redirect('core:home')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            user.check_and_update_status()
            login(request, user)
            messages.success(request, f'স্বাগতম {user.first_name or user.username}!')
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'আপনি সফলভাবে লগআউট করেছেন।')
    return redirect('core:home')


@login_required
def profile_view(request):
    request.user.check_and_update_status()

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'প্রোফাইল আপডেট হয়েছে।')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


def subscription_packages(request):
    plans = SubscriptionPlan.objects.filter(is_active=True)
    return render(request, 'accounts/subscription.html', {'plans': plans})


def subscription_required(request):
    plans = SubscriptionPlan.objects.filter(is_active=True)
    return render(request, 'accounts/subscription_required.html', {'plans': plans})
