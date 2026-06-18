from django.shortcuts import render


def home(request):
    context = {
        'stats': {
            'today_visitors': 200,
            'total_visitors': 10054,
            'total_registered': 173,
            'total_page_views': 10153,
            'active_farmers': 85,
            'active_traders': 42,
            'markets_updated': 12,
        },
        'popular_markets': [
            {'name': 'কারওয়ান বাজার', 'name_en': 'Karwan Bazar', 'location': 'ঢাকা'},
            {'name': 'শ্যামবাজার', 'name_en': 'Shyambazar', 'location': 'ঢাকা'},
            {'name': 'চট্টগ্রাম পণ্য বাজার', 'name_en': 'Chattogram Market', 'location': 'চট্টগ্রাম'},
            {'name': 'রাজশাহী বাজার', 'name_en': 'Rajshahi Market', 'location': 'রাজশাহী'},
            {'name': 'রংপুর বাজার', 'name_en': 'Rangpur Market', 'location': 'রংপুর'},
            {'name': 'দিনাজপুর বাজার', 'name_en': 'Dinajpur Market', 'location': 'দিনাজপুর'},
            {'name': 'যশোর বাজার', 'name_en': 'Jashore Market', 'location': 'যশোর'},
            {'name': 'বগুড়া বাজার', 'name_en': 'Bogura Market', 'location': 'বগুড়া'},
        ],
    }
    return render(request, 'core/home.html', context)
