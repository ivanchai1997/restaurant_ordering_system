from django.contrib import messages
from django.contrib.auth import login
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import RegisterForm
from .models import Category, Dish, Order, OrderItem, Table


def _safe_next(request, default="menu"):
    target = request.POST.get("next") or request.GET.get("next")
    if target and url_has_allowed_host_and_scheme(
        target, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return target
    return default


def menu(request):
    dishes = Dish.objects.filter(is_available=True).select_related("category")
    selected = request.GET.get("c")
    selected = int(selected) if selected and selected.isdigit() else None
    if selected:
        dishes = dishes.filter(category_id=selected)
    return render(request, "restaurant/menu.html", {
        "categories": Category.objects.all(),
        "dishes": dishes,
        "selected": selected,
    })


def table_entry(request, number):
    """Opened by scanning a table's QR code."""
    table = get_object_or_404(Table, number=number)
    request.session["table"] = table.number
    messages.success(request, f"You’re ordering from Table {table.number}.")
    return redirect("menu")


@require_POST
def set_table(request):
    number = request.POST.get("table", "")
    table = Table.objects.filter(number=int(number)).first() if number.isdigit() else None
    if table:
        request.session["table"] = table.number
    else:
        request.session.pop("table", None)
    return redirect(_safe_next(request, "cart"))


@require_POST
def cart_add(request, dish_id):
    dish = get_object_or_404(Dish, pk=dish_id, is_available=True)
    Cart(request).add(dish.pk)
    messages.success(request, f"Added {dish.name} to your order.")
    return redirect(_safe_next(request))


@require_POST
def cart_change(request, dish_id, action):
    cart = Cart(request)
    if action == "inc":
        cart.add(dish_id, 1)
    elif action == "dec":
        cart.add(dish_id, -1)
    elif action == "remove":
        cart.remove(dish_id)
    else:
        raise Http404
    return redirect("cart")


@require_POST
def cart_clear(request):
    Cart(request).clear()
    return redirect("cart")


def cart_detail(request):
    cart = Cart(request)
    return render(request, "restaurant/cart.html", {
        "lines": cart.lines(),
        "total": cart.total(),
        "tables": Table.objects.all(),
        "can_order": request.user.is_authenticated or request.session.get("guest", False),
    })


def welcome(request):
    """Sign in, create an account, or continue as a guest."""
    if request.method == "POST":
        request.session["guest"] = True
        request.session["guest_name"] = request.POST.get("name", "").strip()[:100]
        return redirect(_safe_next(request, "menu"))
    return render(request, "restaurant/welcome.html", {"next": request.GET.get("next", "")})


def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.save())
        messages.success(request, "Your account is ready. Welcome to William’s!")
        return redirect(_safe_next(request))
    return render(request, "restaurant/register.html", {"form": form, "next": request.GET.get("next", "")})


@require_POST
def checkout(request):
    cart = Cart(request)
    lines = cart.lines()
    if not lines:
        messages.error(request, "Your order is empty. Add a dish first.")
        return redirect("menu")
    if not (request.user.is_authenticated or request.session.get("guest")):
        messages.info(request, "Sign in or continue as a guest to place your order.")
        return redirect(f"{reverse('welcome')}?next={reverse('cart')}")

    number = request.POST.get("table", "")
    table = Table.objects.filter(number=int(number)).first() if number.isdigit() else None
    if table:
        request.session["table"] = table.number
    else:
        request.session.pop("table", None)

    if request.user.is_authenticated:
        name = request.user.get_username()
    else:
        name = request.session.get("guest_name") or "Guest"

    with transaction.atomic():
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_name=name,
            table=table,
            note=request.POST.get("note", "").strip()[:300],
        )
        OrderItem.objects.bulk_create([
            OrderItem(order=order, dish=l["dish"], name=l["dish"].name, price=l["dish"].price, quantity=l["quantity"])
            for l in lines
        ])
    cart.clear()
    mine = request.session.get("my_orders", [])
    request.session["my_orders"] = (mine + [order.pk])[-20:]
    messages.success(request, "Order placed. Thank you!")
    return redirect("order_detail", pk=order.pk)


def _can_see(request, order):
    return (
        request.user.is_staff
        or (request.user.is_authenticated and order.user_id == request.user.pk)
        or order.pk in request.session.get("my_orders", [])
    )


def order_detail(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items"), pk=pk)
    if not _can_see(request, order):
        raise Http404
    return render(request, "restaurant/order_detail.html", {"order": order})


def my_orders(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user)
    else:
        orders = Order.objects.filter(pk__in=request.session.get("my_orders", []))
    return render(request, "restaurant/my_orders.html", {"orders": orders.prefetch_related("items")})
