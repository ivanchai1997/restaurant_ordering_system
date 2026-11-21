from django.contrib.auth import views as auth_views
from django.urls import path

from . import owner_views as owner
from .forms import AdminAuthForm, CustomerAuthForm
from . import views

urlpatterns = [
    path("", views.menu, name="menu"),
    path("dish/<int:pk>/photo/", views.dish_photo, name="dish_photo"),
    path("t/<int:number>/", views.table_entry, name="table_entry"),
    path("table/set/", views.set_table, name="set_table"),
    path("cart/", views.cart_detail, name="cart"),
    path("cart/add/<int:dish_id>/", views.cart_add, name="cart_add"),
    path("cart/change/<int:dish_id>/<str:action>/", views.cart_change, name="cart_change"),
    path("cart/clear/", views.cart_clear, name="cart_clear"),
    path("checkout/", views.checkout, name="checkout"),
    path("welcome/", views.welcome, name="welcome"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(authentication_form=CustomerAuthForm), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("orders/", views.my_orders, name="my_orders"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
    # admin (restaurant staff) area, with its own sign-in
    path("owner/login/", auth_views.LoginView.as_view(template_name="restaurant/owner/login.html", authentication_form=AdminAuthForm, next_page="owner_dashboard"), name="owner_login"),
    path("owner/logout/", auth_views.LogoutView.as_view(next_page="owner_login"), name="owner_logout"),
    path("owner/sales/", owner.sales, name="owner_sales"),
    path("owner/sales/export/", owner.sales_export, name="owner_sales_export"),
    path("owner/", owner.dashboard, name="owner_dashboard"),
    path("owner/orders/<int:pk>/status/", owner.order_status, name="owner_order_status"),
    path("owner/dishes/", owner.dish_list, name="owner_dishes"),
    path("owner/dishes/new/", owner.dish_edit, name="owner_dish_new"),
    path("owner/dishes/<int:pk>/edit/", owner.dish_edit, name="owner_dish_edit"),
    path("owner/dishes/<int:pk>/delete/", owner.dish_delete, name="owner_dish_delete"),
    path("owner/dishes/<int:pk>/toggle/", owner.dish_toggle, name="owner_dish_toggle"),
    path("owner/categories/add/", owner.category_add, name="owner_category_add"),
    path("owner/tables/", owner.tables, name="owner_tables"),
    path("owner/tables/<int:number>/qr.svg", owner.table_qr, name="table_qr"),
]
