from .models import Dish

KEY = "cart"


class Cart:
    """Shopping cart kept in the visitor's session, so guests and customers both have one."""

    def __init__(self, request):
        self.session = request.session
        self.data = dict(self.session.get(KEY, {}))

    def _save(self):
        self.session[KEY] = self.data

    def add(self, dish_id, qty=1):
        key = str(dish_id)
        self.data[key] = self.data.get(key, 0) + qty
        if self.data[key] <= 0:
            del self.data[key]
        self._save()

    def remove(self, dish_id):
        self.data.pop(str(dish_id), None)
        self._save()

    def clear(self):
        self.data = {}
        self._save()

    def count(self):
        return sum(self.data.values())

    def lines(self):
        dishes = Dish.objects.filter(pk__in=self.data.keys(), is_available=True).select_related("category")
        return [
            {"dish": d, "quantity": self.data[str(d.pk)], "subtotal": d.price * self.data[str(d.pk)]}
            for d in dishes
        ]

    def total(self):
        return sum(line["subtotal"] for line in self.lines())
