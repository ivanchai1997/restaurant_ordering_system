import io

import qrcode
import qrcode.image.svg
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import DishForm
from .models import Category, Dish, Order, Table
from .sales import build_report, workbook_bytes

owner_required = staff_member_required(login_url="owner_login")


@owner_required
def dashboard(request):
    show = request.GET.get("show", "open")
    orders = Order.objects.select_related("table").prefetch_related("items")
    if show == "open":
        orders = orders.filter(status__in=["new", "preparing", "served"])
    return render(request, "restaurant/owner/dashboard.html", {
        "orders": orders[:100], "show": show, "statuses": Order.STATUS,
    })


@owner_required
@require_POST
def order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    status = request.POST.get("status")
    if status in dict(Order.STATUS):
        order.status = status
        order.save(update_fields=["status"])
    return redirect(request.POST.get("back") or "owner_dashboard")


@owner_required
def dish_list(request):
    return render(request, "restaurant/owner/dish_list.html", {
        "dishes": Dish.objects.select_related("category"),
        "categories": Category.objects.all(),
    })


@owner_required
def dish_edit(request, pk=None):
    dish = get_object_or_404(Dish, pk=pk) if pk else None
    form = DishForm(request.POST or None, request.FILES or None, instance=dish)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Dish saved.")
        return redirect("owner_dishes")
    return render(request, "restaurant/owner/dish_form.html", {"form": form, "dish": dish})


@owner_required
@require_POST
def dish_delete(request, pk):
    get_object_or_404(Dish, pk=pk).delete()
    messages.success(request, "Dish deleted.")
    return redirect("owner_dishes")


@owner_required
@require_POST
def dish_toggle(request, pk):
    dish = get_object_or_404(Dish, pk=pk)
    dish.is_available = not dish.is_available
    dish.save(update_fields=["is_available"])
    return redirect("owner_dishes")


@owner_required
@require_POST
def category_add(request):
    name = request.POST.get("name", "").strip()
    if name:
        Category.objects.get_or_create(name=name, defaults={"position": Category.objects.count() + 1})
        messages.success(request, f"Category “{name}” added.")
    return redirect("owner_dishes")


@owner_required
def tables(request):
    if request.method == "POST":
        try:
            count = min(60, max(1, int(request.POST.get("count", ""))))
        except ValueError:
            messages.error(request, "Enter a number of tables from 1 to 60.")
            return redirect("owner_tables")
        for n in range(1, count + 1):
            Table.objects.get_or_create(number=n)
        Table.objects.filter(number__gt=count).delete()
        messages.success(request, f"The restaurant now has {count} tables.")
        return redirect("owner_tables")
    items = Table.objects.all()
    return render(request, "restaurant/owner/tables.html", {"tables": items, "count": items.count()})


@owner_required
def table_qr(request, number):
    """SVG QR code that opens the menu for this table."""
    get_object_or_404(Table, number=number)
    path = reverse("table_entry", args=[number])
    base = settings.PUBLIC_BASE_URL.rstrip("/")
    url = f"{base}{path}" if base else request.build_absolute_uri(path)
    image = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, box_size=10)
    buffer = io.BytesIO()
    image.save(buffer)
    return HttpResponse(buffer.getvalue(), content_type="image/svg+xml")


@owner_required
def sales(request):
    return render(request, "restaurant/owner/sales.html", build_report(request.GET.get("view", "daily"), request.GET))


@owner_required
def sales_export(request):
    report = build_report(request.GET.get("view", "daily"), request.GET)
    response = HttpResponse(
        workbook_bytes(report),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{report["filename"]}"'
    return response
