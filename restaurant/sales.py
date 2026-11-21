import calendar
import io
from datetime import date
from decimal import Decimal

from django.db.models import Count, DecimalField, ExpressionWrapper, F, Sum
from django.db.models.functions import TruncDate, TruncMonth, TruncYear
from django.utils import timezone

from .models import Order, OrderItem

ZERO = Decimal("0")
LINE = ExpressionWrapper(F("price") * F("quantity"), output_field=DecimalField(max_digits=12, decimal_places=2))


def _totals(orders):
    r = OrderItem.objects.filter(order__in=orders).aggregate(
        revenue=Sum(LINE), orders=Count("order", distinct=True), qty=Sum("quantity")
    )
    return {"revenue": r["revenue"] or ZERO, "orders": r["orders"] or 0, "qty": r["qty"] or 0}


def build_report(view, params):
    """Daily (one month), monthly (one year) or yearly sales. Cancelled orders are never counted."""
    today = timezone.localdate()
    basis = "paid" if params.get("basis") == "paid" else "all"
    base = Order.objects.exclude(status="cancelled")
    if basis == "paid":
        base = base.filter(status__in=["paid", "cleared"])

    cards = {
        "today": _totals(base.filter(created__date=today)),
        "month": _totals(base.filter(created__year=today.year, created__month=today.month)),
        "year": _totals(base.filter(created__year=today.year)),
    }

    try:
        year = int(params.get("year", ""))
        date(year, 1, 1)
    except (ValueError, TypeError):
        year = today.year
    try:
        y, m = (int(p) for p in params.get("month", "").split("-"))
        date(y, m, 1)
    except (ValueError, TypeError):
        y, m = today.year, today.month

    keys = None
    if view == "daily":
        orders = base.filter(created__year=y, created__month=m)
        trunc = TruncDate
        title = f"Daily sales, {calendar.month_name[m]} {y}"
        query = {"view": "daily", "month": f"{y:04d}-{m:02d}"}
        keys = [date(y, m, d) for d in range(1, calendar.monthrange(y, m)[1] + 1)]
        label = lambda k: k.strftime("%a %d %b")  # noqa: E731
        period_name = "Day"
        slug = f"{y:04d}-{m:02d}"
    elif view == "monthly":
        orders = base.filter(created__year=year)
        trunc = TruncMonth
        title = f"Monthly sales, {year}"
        query = {"view": "monthly", "year": year}
        keys = [date(year, i, 1) for i in range(1, 13)]
        label = lambda k: calendar.month_name[k.month]  # noqa: E731
        period_name = "Month"
        slug = str(year)
    else:
        view = "yearly"
        orders = base
        trunc = TruncYear
        title = "Yearly sales"
        query = {"view": "yearly"}
        label = lambda k: str(k.year)  # noqa: E731
        period_name = "Year"
        slug = "all-years"
    query["basis"] = basis

    items = OrderItem.objects.filter(order__in=orders)
    found = {}
    grouped = (
        items.annotate(period=trunc("order__created"))
        .values("period")
        .annotate(revenue=Sum(LINE), qty=Sum("quantity"), orders=Count("order", distinct=True))
    )
    for r in grouped:
        p = r["period"]
        found[p.date() if hasattr(p, "date") else p] = r
    if keys is None:
        keys = sorted(found)

    rows = []
    for k in keys:
        r = found.get(k)
        rows.append({
            "label": label(k),
            "orders": r["orders"] if r else 0,
            "qty": r["qty"] if r else 0,
            "revenue": r["revenue"] if r else ZERO,
        })
    peak = max((r["revenue"] for r in rows), default=ZERO)
    for r in rows:
        r["pct"] = int(r["revenue"] / peak * 100) if peak else 0

    return {
        "view": view, "basis": basis, "title": title, "period_name": period_name,
        "rows": rows, "totals": _totals(orders), "cards": cards,
        "top_dishes": list(items.values("name").annotate(qty=Sum("quantity"), revenue=Sum(LINE)).order_by("-qty", "name")[:10]),
        "orders": orders, "year": year, "month_value": f"{y:04d}-{m:02d}",
        "query": "&".join(f"{k}={v}" for k, v in query.items()),
        "filename": f"williams-sales-{view}-{slug}.xlsx",
    }


def workbook_bytes(rep):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill

    money = "#,##0.00"
    head_font = Font(bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="5A1224")

    def style_header(ws, row):
        for cell in ws[row]:
            cell.font, cell.fill = head_font, head_fill

    def widths(ws, sizes):
        for col, size in zip("ABCDEFG", sizes):
            ws.column_dimensions[col].width = size

    wb = Workbook()
    ws = wb.active
    ws.title = "Sales"
    ws["A1"] = rep["title"]
    ws["A1"].font = Font(bold=True, size=14)
    ws["A2"] = "Paid orders only" if rep["basis"] == "paid" else "All orders except cancelled"
    ws.append([])
    ws.append([rep["period_name"], "Orders", "Items sold", "Revenue (RM)"])
    style_header(ws, 4)
    for r in rep["rows"]:
        ws.append([r["label"], r["orders"], r["qty"], float(r["revenue"])])
    t = rep["totals"]
    ws.append(["Total", t["orders"], t["qty"], float(t["revenue"])])
    for cell in ws[ws.max_row]:
        cell.font = Font(bold=True)
    for row in ws.iter_rows(min_row=5, min_col=4, max_col=4):
        for cell in row:
            cell.number_format = money
    widths(ws, [22, 10, 12, 16])

    ws2 = wb.create_sheet("Top dishes")
    ws2.append(["Dish", "Quantity", "Revenue (RM)"])
    style_header(ws2, 1)
    for d in rep["top_dishes"]:
        ws2.append([d["name"], d["qty"], float(d["revenue"])])
    for row in ws2.iter_rows(min_row=2, min_col=3, max_col=3):
        for cell in row:
            cell.number_format = money
    widths(ws2, [30, 10, 16])

    ws3 = wb.create_sheet("Orders")
    ws3.append(["Order #", "Date and time", "Table", "Customer", "Status", "Items", "Total (RM)"])
    style_header(ws3, 1)
    qs = rep["orders"].select_related("table").prefetch_related("items").order_by("created")
    for o in qs:
        ws3.append([
            o.pk,
            timezone.localtime(o.created).replace(tzinfo=None),
            o.where,
            o.customer_name or "Guest",
            o.get_status_display(),
            ", ".join(f"{i.quantity}x {i.name}" for i in o.items.all()),
            float(o.total),
        ])
    for row in ws3.iter_rows(min_row=2, min_col=2, max_col=2):
        for cell in row:
            cell.number_format = "yyyy-mm-dd hh:mm"
    for row in ws3.iter_rows(min_row=2, min_col=7, max_col=7):
        for cell in row:
            cell.number_format = money
    widths(ws3, [10, 18, 12, 18, 12, 60, 14])

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
