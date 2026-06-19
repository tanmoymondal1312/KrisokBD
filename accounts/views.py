import uuid
from datetime import timedelta

from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from sslcommerz_lib import SSLCOMMERZ

from .forms import RegisterForm, LoginForm, ProfileForm
from .models import SubscriptionPlan, Payment


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


# ============ SSLCommerz Payment ============

@login_required
def initiate_payment(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, pk=plan_id, is_active=True)
    user = request.user

    tran_id = f"KRISOK-{user.pk}-{uuid.uuid4().hex[:8].upper()}"

    payment = Payment.objects.create(
        user=user,
        plan=plan,
        amount=plan.price,
        transaction_id=tran_id,
        payment_method='sslcommerz',
        status='pending',
    )

    site_url = django_settings.SITE_URL

    sslcz = SSLCOMMERZ({
        'store_id': django_settings.SSLCOMMERZ_STORE_ID,
        'store_pass': django_settings.SSLCOMMERZ_STORE_PASS,
        'issandbox': django_settings.SSLCOMMERZ_SANDBOX,
    })

    post_body = {
        'total_amount': float(plan.price),
        'currency': 'BDT',
        'tran_id': tran_id,
        'success_url': f'{site_url}/accounts/payment/success/',
        'fail_url': f'{site_url}/accounts/payment/fail/',
        'cancel_url': f'{site_url}/accounts/payment/cancel/',
        'ipn_url': f'{site_url}/accounts/payment/ipn/',
        'emi_option': 0,
        'cus_name': user.first_name or user.username,
        'cus_email': user.email or 'customer@krisokbd.com',
        'cus_phone': user.phone or '01700000000',
        'cus_add1': user.address or 'Dhaka',
        'cus_city': user.district or 'Dhaka',
        'cus_country': 'Bangladesh',
        'shipping_method': 'NO',
        'multi_card_name': '',
        'num_of_item': 1,
        'product_name': plan.name,
        'product_category': 'Subscription',
        'product_profile': 'non-physical-goods',
        'value_a': str(payment.pk),
        'value_b': str(user.pk),
        'value_c': str(plan.pk),
    }

    response = sslcz.createSession(post_body)

    if response.get('status') == 'SUCCESS':
        return redirect(response['GatewayPageURL'])
    else:
        payment.status = 'failed'
        payment.save(update_fields=['status'])
        messages.error(request, 'পেমেন্ট সেশন তৈরি করা যায়নি। আবার চেষ্টা করুন।')
        return redirect('accounts:packages')


@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        data = request.POST
        tran_id = data.get('tran_id', '')
        val_id = data.get('val_id', '')
        payment_pk = data.get('value_a', '')

        try:
            payment = Payment.objects.get(pk=payment_pk, transaction_id=tran_id)
        except Payment.DoesNotExist:
            messages.error(request, 'পেমেন্ট তথ্য পাওয়া যায়নি।')
            return redirect('accounts:packages')

        if payment.status == 'completed':
            messages.info(request, 'এই পেমেন্ট ইতিমধ্যে সম্পন্ন হয়েছে।')
            return redirect('accounts:profile')

        # Validate with SSLCommerz
        sslcz = SSLCOMMERZ({
            'store_id': django_settings.SSLCOMMERZ_STORE_ID,
            'store_pass': django_settings.SSLCOMMERZ_STORE_PASS,
            'issandbox': django_settings.SSLCOMMERZ_SANDBOX,
        })

        validation = sslcz.validationTransactionOrder(val_id)

        if validation.get('status') == 'VALID' or validation.get('status') == 'VALIDATED':
            payment.status = 'completed'
            payment.save(update_fields=['status'])

            user = payment.user
            user.subscription_status = 'active'
            user.subscription_plan = payment.plan
            user.subscription_expires = timezone.now() + timedelta(days=payment.plan.duration_days)
            user.save(update_fields=['subscription_status', 'subscription_plan', 'subscription_expires'])

            messages.success(request, f'পেমেন্ট সফল! {payment.plan.name} সক্রিয় হয়েছে।')
            return redirect('accounts:profile')
        else:
            payment.status = 'failed'
            payment.save(update_fields=['status'])
            messages.error(request, 'পেমেন্ট যাচাই করা যায়নি।')
            return redirect('accounts:packages')

    return redirect('accounts:packages')


@csrf_exempt
def payment_fail(request):
    if request.method == 'POST':
        tran_id = request.POST.get('tran_id', '')
        payment_pk = request.POST.get('value_a', '')
        try:
            payment = Payment.objects.get(pk=payment_pk, transaction_id=tran_id)
            payment.status = 'failed'
            payment.save(update_fields=['status'])
        except Payment.DoesNotExist:
            pass
    messages.error(request, 'পেমেন্ট ব্যর্থ হয়েছে। আবার চেষ্টা করুন।')
    return redirect('accounts:packages')


@csrf_exempt
def payment_cancel(request):
    if request.method == 'POST':
        tran_id = request.POST.get('tran_id', '')
        payment_pk = request.POST.get('value_a', '')
        try:
            payment = Payment.objects.get(pk=payment_pk, transaction_id=tran_id)
            payment.status = 'failed'
            payment.save(update_fields=['status'])
        except Payment.DoesNotExist:
            pass
    messages.info(request, 'পেমেন্ট বাতিল করা হয়েছে।')
    return redirect('accounts:packages')


@csrf_exempt
def payment_ipn(request):
    if request.method == 'POST':
        data = request.POST
        tran_id = data.get('tran_id', '')
        status = data.get('status', '')
        val_id = data.get('val_id', '')
        payment_pk = data.get('value_a', '')

        try:
            payment = Payment.objects.get(pk=payment_pk, transaction_id=tran_id)
        except Payment.DoesNotExist:
            return HttpResponse('Payment not found', status=400)

        if status == 'VALID' and payment.status != 'completed':
            sslcz = SSLCOMMERZ({
                'store_id': django_settings.SSLCOMMERZ_STORE_ID,
                'store_pass': django_settings.SSLCOMMERZ_STORE_PASS,
                'issandbox': django_settings.SSLCOMMERZ_SANDBOX,
            })
            validation = sslcz.validationTransactionOrder(val_id)

            if validation.get('status') in ('VALID', 'VALIDATED'):
                payment.status = 'completed'
                payment.save(update_fields=['status'])

                user = payment.user
                user.subscription_status = 'active'
                user.subscription_plan = payment.plan
                user.subscription_expires = timezone.now() + timedelta(days=payment.plan.duration_days)
                user.save(update_fields=['subscription_status', 'subscription_plan', 'subscription_expires'])

    return HttpResponse('IPN Received', status=200)
