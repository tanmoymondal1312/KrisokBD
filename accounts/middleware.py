from django.shortcuts import redirect
from django.urls import reverse


PROTECTED_URL_PREFIXES = [
    '/prices/daily/',
    '/prices/division/',
    '/prices/comparison/',
    '/prices/regional/',
    '/prices/market/',
    '/prices/product/',
]

EXEMPT_URLS = [
    '/',
    '/accounts/login/',
    '/accounts/register/',
    '/accounts/logout/',
    '/accounts/packages/',
    '/accounts/subscription-required/',
    '/django-admin/',
]


class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        is_protected = any(path.startswith(p) for p in PROTECTED_URL_PREFIXES)
        if not is_protected:
            return self.get_response(request)

        if not request.user.is_authenticated:
            return redirect(f"{reverse('accounts:login')}?next={path}")

        request.user.check_and_update_status()

        if not request.user.has_access:
            return redirect('accounts:subscription_required')

        return self.get_response(request)
