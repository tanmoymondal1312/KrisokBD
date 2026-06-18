# KrisokBD

Agricultural market intelligence platform for Bangladesh. Daily wholesale market prices, farmer-trader network, and market analytics.

## Tech Stack

- **Backend:** Django 5.x
- **Frontend:** Django Templates, Tailwind CSS, HTMX, Alpine.js
- **Database:** SQLite (dev) / MySQL (production)
- **Hosting:** cPanel with Passenger WSGI

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install django
python manage.py migrate
python manage.py runserver
```

## Project Structure

```
├── core/           # Homepage, common views
├── accounts/       # User auth, registration, subscription
├── market/         # Market prices, divisions, products
├── custom_admin/   # Custom admin panel
├── templates/      # HTML templates
├── static/         # CSS, JS, images, fonts
└── krisokbd/       # Project settings
```
