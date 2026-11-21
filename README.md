# William’s Restaurant · Ordering System (Django)

A Django version of the William’s Restaurant ordering site (Melaka). Unlike the single-file HTML demo, the menu,
accounts and orders live in one shared database, so an order placed on a customer’s phone shows up on the owner’s page.

## Features
- **Customers:** create an account, sign in, or continue as a guest. Add, change and remove dishes in the order, then place it.
- **Table QR codes:** scanning a table’s code opens the menu with that table chosen. Orders are tagged with the table, or “Takeaway”.
- **Owner (staff user) at `/owner/`:** see and update customer orders (New, Preparing, Served, Paid, Cancelled), add / edit / hide / delete dishes with photos and prices, add categories, set the number of tables, and print every table’s QR code.
- **Django admin** at `/admin/` for full database access.

## Run it
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations restaurant
python manage.py migrate
python manage.py seed_menu        # sample menu, 12 tables, demo owner (owner / william123)
python manage.py runserver
```
Open http://127.0.0.1:8000/ . The owner signs in at `/login/` and then opens **Owner** in the menu bar.

## Before going live
- Change the owner password (or run `python manage.py createsuperuser` and delete the demo `owner` user).
- Set environment variables: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS=yourdomain.com`,
  `DJANGO_CSRF_ORIGINS=https://yourdomain.com` and `PUBLIC_BASE_URL=https://yourdomain.com` (used inside the QR codes).
- Serve static and uploaded files with your web server (`python manage.py collectstatic`), and use a production server such as gunicorn.
- Use HTTPS so customers’ passwords are protected.

## Project layout
- `williams/` project settings and URLs
- `restaurant/models.py` Category, Dish, Table, Order, OrderItem
- `restaurant/views.py` customer pages; `restaurant/owner_views.py` owner pages and QR codes
- `restaurant/cart.py` session-based cart used by guests and customers
- `restaurant/templates/` and `restaurant/static/` pages and styling
