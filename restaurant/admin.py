from django.contrib import admin

from .models import Category, Dish, Order, OrderItem, Table


class ItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "position")


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_available")
    list_filter = ("category", "is_available")
    search_fields = ("name",)


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("number",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "where", "customer_name", "status", "created")
    list_filter = ("status",)
    inlines = [ItemInline]
