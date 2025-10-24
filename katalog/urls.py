from django.urls import path
from . import views

app_name = "katalog"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("grid/", views.product_grid, name="product_grid"),
    path("create/", views.product_create, name="product_create"),
    path("<int:pk>/", views.product_detail, name="product_detail"),
    path("<int:pk>/edit/", views.product_update, name="product_update"),
    path("<int:pk>/delete/", views.product_delete, name="product_delete"),

    # 🔹 Routes untuk user authentication
    path("user/", views.user_home, name="user_home"),
    path("user/login/", views.user_login, name="user_login"),
    path("user/register/", views.user_register, name="user_register"),
    path("user/logout/", views.user_logout, name="user_logout"),
]
