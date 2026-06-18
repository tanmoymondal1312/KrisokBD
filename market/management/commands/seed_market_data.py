from datetime import date, timedelta
from decimal import Decimal
import random

from django.core.management.base import BaseCommand
from market.models import (
    Division, District, Market, ProductCategory,
    Product, MarketPrice, GovernmentPrice, PopularMarket,
)


class Command(BaseCommand):
    help = 'Seed market data for development'

    def handle(self, *args, **options):
        self.stdout.write('Seeding divisions...')
        divisions_data = [
            ('ঢাকা', 'Dhaka', 'dhaka', 1),
            ('চট্টগ্রাম', 'Chattogram', 'chattogram', 2),
            ('রাজশাহী', 'Rajshahi', 'rajshahi', 3),
            ('খুলনা', 'Khulna', 'khulna', 4),
            ('বরিশাল', 'Barishal', 'barishal', 5),
            ('সিলেট', 'Sylhet', 'sylhet', 6),
            ('রংপুর', 'Rangpur', 'rangpur', 7),
            ('ময়মনসিংহ', 'Mymensingh', 'mymensingh', 8),
        ]
        divisions = {}
        for name, name_en, slug, order in divisions_data:
            div, _ = Division.objects.get_or_create(
                slug=slug, defaults={'name': name, 'name_en': name_en, 'order': order}
            )
            divisions[slug] = div

        self.stdout.write('Seeding districts and markets...')
        markets_data = [
            ('dhaka', 'ঢাকা', 'Dhaka', 'dhaka-city', [
                ('কারওয়ান বাজার', 'Karwan Bazar', 'karwan-bazar'),
                ('শ্যামবাজার', 'Shyambazar', 'shyambazar'),
                ('মিরপুর বাজার', 'Mirpur Bazar', 'mirpur-bazar'),
            ]),
            ('chattogram', 'চট্টগ্রাম', 'Chattogram', 'chattogram-city', [
                ('চট্টগ্রাম পণ্য বাজার', 'Chattogram Commodity Market', 'chattogram-commodity'),
                ('রেয়াজুদ্দিন বাজার', 'Reazuddin Bazar', 'reazuddin-bazar'),
            ]),
            ('rajshahi', 'রাজশাহী', 'Rajshahi', 'rajshahi-city', [
                ('রাজশাহী বাজার', 'Rajshahi Market', 'rajshahi-market'),
            ]),
            ('rangpur', 'রংপুর', 'Rangpur', 'rangpur-city', [
                ('রংপুর বাজার', 'Rangpur Market', 'rangpur-market'),
            ]),
            ('khulna', 'যশোর', 'Jashore', 'jashore', [
                ('যশোর বাজার', 'Jashore Market', 'jashore-market'),
            ]),
            ('rajshahi', 'বগুড়া', 'Bogura', 'bogura', [
                ('বগুড়া বাজার', 'Bogura Market', 'bogura-market'),
            ]),
            ('rangpur', 'দিনাজপুর', 'Dinajpur', 'dinajpur', [
                ('দিনাজপুর বাজার', 'Dinajpur Market', 'dinajpur-market'),
            ]),
        ]

        all_markets = []
        for div_slug, dist_name, dist_name_en, dist_slug, market_list in markets_data:
            district, _ = District.objects.get_or_create(
                slug=dist_slug,
                defaults={'name': dist_name, 'name_en': dist_name_en, 'division': divisions[div_slug]}
            )
            for m_name, m_name_en, m_slug in market_list:
                market, _ = Market.objects.get_or_create(
                    slug=m_slug,
                    defaults={'name': m_name, 'name_en': m_name_en, 'district': district}
                )
                all_markets.append(market)

        self.stdout.write('Seeding product categories and products...')
        categories_data = [
            ('মসলা', 'Spices', 'spices', 'fa-pepper-hot', 1),
            ('সবজি', 'Vegetables', 'vegetables', 'fa-carrot', 2),
            ('ফল', 'Fruits', 'fruits', 'fa-apple-alt', 3),
            ('চাল ও ডাল', 'Rice & Lentils', 'rice-lentils', 'fa-seedling', 4),
            ('মাছ', 'Fish', 'fish', 'fa-fish', 5),
        ]
        categories = {}
        for name, name_en, slug, icon, order in categories_data:
            cat, _ = ProductCategory.objects.get_or_create(
                slug=slug, defaults={'name': name, 'name_en': name_en, 'icon': icon, 'order': order}
            )
            categories[slug] = cat

        products_data = [
            ('পেঁয়াজ', 'Onion', 'onion', 'spices', 'কেজি', 35, 55, 40),
            ('রসুন', 'Garlic', 'garlic', 'spices', 'কেজি', 180, 240, 200),
            ('আদা', 'Ginger', 'ginger', 'spices', 'কেজি', 240, 320, None),
            ('মরিচ (কাঁচা)', 'Green Chili', 'green-chili', 'spices', 'কেজি', 60, 100, None),
            ('হলুদ (গুঁড়া)', 'Turmeric Powder', 'turmeric', 'spices', 'কেজি', 200, 280, None),
            ('আলু', 'Potato', 'potato', 'vegetables', 'কেজি', 18, 30, 25),
            ('টমেটো', 'Tomato', 'tomato', 'vegetables', 'কেজি', 40, 70, None),
            ('বেগুন', 'Eggplant', 'eggplant', 'vegetables', 'কেজি', 30, 50, None),
            ('শসা', 'Cucumber', 'cucumber', 'vegetables', 'কেজি', 25, 40, None),
            ('ফুলকপি', 'Cauliflower', 'cauliflower', 'vegetables', 'কেজি', 35, 55, None),
            ('বাঁধাকপি', 'Cabbage', 'cabbage', 'vegetables', 'কেজি', 20, 35, None),
            ('লাউ', 'Bottle Gourd', 'bottle-gourd', 'vegetables', 'পিস', 30, 50, None),
            ('মুলা', 'Radish', 'radish', 'vegetables', 'কেজি', 20, 35, None),
            ('আম', 'Mango', 'mango', 'fruits', 'কেজি', 60, 150, None),
            ('কলা', 'Banana', 'banana', 'fruits', 'ডজন', 40, 70, None),
            ('চাল (মোটা)', 'Rice Coarse', 'rice-coarse', 'rice-lentils', 'কেজি', 45, 55, 50),
            ('চাল (চিকন)', 'Rice Fine', 'rice-fine', 'rice-lentils', 'কেজি', 60, 80, 65),
            ('মসুর ডাল', 'Red Lentil', 'red-lentil', 'rice-lentils', 'কেজি', 95, 120, 100),
            ('রুই মাছ', 'Rohu Fish', 'rohu-fish', 'fish', 'কেজি', 250, 350, None),
            ('ইলিশ মাছ', 'Hilsa Fish', 'hilsa-fish', 'fish', 'কেজি', 800, 1500, None),
        ]

        all_products = []
        for p_name, p_name_en, p_slug, cat_slug, unit, base_min, base_max, govt in products_data:
            product, _ = Product.objects.get_or_create(
                slug=p_slug,
                defaults={
                    'name': p_name, 'name_en': p_name_en,
                    'category': categories[cat_slug], 'unit': unit,
                }
            )
            all_products.append((product, base_min, base_max, govt))

        self.stdout.write('Seeding market prices for last 7 days...')
        today = date.today()
        MarketPrice.objects.all().delete()

        for day_offset in range(7):
            price_date = today - timedelta(days=day_offset)
            for product, base_min, base_max, _ in all_products:
                for market in all_markets:
                    variation = random.uniform(-0.15, 0.15)
                    min_p = round(base_min * (1 + variation), 2)
                    max_p = round(base_max * (1 + variation), 2)
                    if min_p > max_p:
                        min_p, max_p = max_p, min_p
                    MarketPrice.objects.create(
                        product=product, market=market, date=price_date,
                        min_price=Decimal(str(min_p)),
                        max_price=Decimal(str(max_p)),
                    )

        self.stdout.write('Seeding government prices...')
        GovernmentPrice.objects.all().delete()
        for product, _, _, govt in all_products:
            if govt:
                GovernmentPrice.objects.create(
                    product=product, price=Decimal(str(govt)),
                    effective_date=today,
                )

        self.stdout.write('Seeding popular markets...')
        PopularMarket.objects.all().delete()
        for i, market in enumerate(all_markets[:8]):
            PopularMarket.objects.create(market=market, order=i)

        total_prices = MarketPrice.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f'Done! {len(all_markets)} markets, {len(all_products)} products, {total_prices} price entries'
        ))
