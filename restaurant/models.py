from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)
    position = models.PositiveSmallIntegerField(default=0, help_text="Lower numbers show first.")

    class Meta:
        ordering = ["position", "name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Dish(models.Model):
    category = models.ForeignKey(Category, related_name="dishes", on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=250, blank=True)
    price = models.DecimalField("Price (RM)", max_digits=8, decimal_places=2)
    photo = models.ImageField(upload_to="dishes/", blank=True, null=True)
    emoji = models.CharField(max_length=8, blank=True, default="🍽️", help_text="Shown when there is no photo.")
    is_available = models.BooleanField("Shown on menu", default=True)

    class Meta:
        ordering = ["category__position", "name"]
        verbose_name_plural = "dishes"

    def __str__(self):
        return self.name


class Table(models.Model):
    number = models.PositiveSmallIntegerField(unique=True)

    class Meta:
        ordering = ["number"]

    def __str__(self):
        return f"Table {self.number}"


class Order(models.Model):
    STATUS = [
        ("new", "New"),
        ("preparing", "Preparing"),
        ("served", "Served"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    customer_name = models.CharField(max_length=100, blank=True)
    table = models.ForeignKey(Table, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=12, choices=STATUS, default="new")
    note = models.CharField(max_length=300, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"Order #{self.pk}"

    @property
    def where(self):
        return str(self.table) if self.table else "Takeaway"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100)  # copied so old orders keep their wording and price
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveSmallIntegerField(default=1)

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.name}"
