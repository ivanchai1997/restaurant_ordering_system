def shop(request):
    cart = request.session.get("cart", {}) if hasattr(request, "session") else {}
    return {
        "cart_count": sum(cart.values()),
        "current_table": request.session.get("table") if hasattr(request, "session") else None,
        "is_guest": request.session.get("guest", False) if hasattr(request, "session") else False,
    }
