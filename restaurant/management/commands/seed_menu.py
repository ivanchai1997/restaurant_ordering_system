from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from restaurant.models import Category, Dish, Table

MENU = {
    "Steaks": [
        ("Ribeye Steak", 68, "🥩", "250g grilled ribeye with pepper sauce, fries and greens."),
        ("Sirloin Steak", 56, "🥩", "Tender sirloin, mushroom sauce, mashed potato."),
        ("Grilled Lamb Chops", 62, "🍖", "Rosemary lamb chops with mint jelly and roast veg."),
    ],
    "Pasta": [
        ("Spaghetti Carbonara", 28, "🍝", "Creamy egg sauce, smoked beef bacon, parmesan."),
        ("Spaghetti Bolognese", 26, "🍝", "Slow-cooked beef ragù over al dente spaghetti."),
        ("Aglio Olio Prawns", 32, "🍤", "Garlic, chilli, olive oil and tiger prawns."),
    ],
    "Breads": [
        ("Garlic Bread", 11, "🥖", "Baguette, roasted garlic butter, parsley."),
        ("Cheese Focaccia", 14, "🍞", "Rosemary focaccia baked with mozzarella."),
    ],
    "Soups": [
        ("Cream of Mushroom", 13, "🍲", "Velvety soup served with a bread roll."),
        ("Pumpkin Soup", 12, "🎃", "Roasted pumpkin, cream, toasted seeds."),
    ],
    "Sides & Desserts": [
        ("Caesar Salad", 19, "🥗", "Crisp romaine, croutons, parmesan, anchovy dressing."),
        ("Chocolate Lava Cake", 18, "🍰", "Warm molten centre with vanilla ice cream."),
    ],
}


class Command(BaseCommand):
    help = "Adds the sample menu, 12 tables and a demo owner account (owner / william123)."

    def handle(self, *args, **options):
        for position, (cat_name, dishes) in enumerate(MENU.items(), start=1):
            category, _ = Category.objects.get_or_create(name=cat_name, defaults={"position": position})
            for name, price, emoji, desc in dishes:
                Dish.objects.get_or_create(
                    name=name, defaults={"category": category, "price": price, "emoji": emoji, "description": desc}
                )
        for n in range(1, 13):
            Table.objects.get_or_create(number=n)
        if not User.objects.filter(username="owner").exists():
            User.objects.create_superuser("owner", "owner@example.com", "william123")
            self.stdout.write(self.style.WARNING("Created owner / william123. Change this password before going live."))
        self.stdout.write(self.style.SUCCESS("Sample menu and tables are ready."))
