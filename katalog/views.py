from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Product


# ------------------------
# 🔹 KATALOG PRODUK
# ------------------------
def product_list(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    products = Product.objects.all()

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category:
        products = products.filter(category=category)

    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
        "category": category,
        "categories": Product.Category.choices,
    }
    return render(request, "katalog/product_list.html", context)


def product_detail(request: HttpRequest, pk: int) -> HttpResponse:
    product = get_object_or_404(Product, pk=pk)
    return render(request, "katalog/product_detail.html", {"product": product})


@login_required
def product_create(request: HttpRequest) -> HttpResponse:
    if request.user.username not in ["Adminpbpb09", "adminpbpb09"]:
        messages.error(request, "Only admin users can create products.")
        return redirect("katalog:product_list")
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        category = request.POST.get("category", "").strip()
        price = request.POST.get("price", "0").strip()
        stock = request.POST.get("stock", "0").strip()
        description = request.POST.get("description", "").strip()
        image_url = request.POST.get("image_url", "").strip()
        rating = request.POST.get("rating", "0").strip() 
        try:
            product = Product.objects.create(
                name=name,
                category=category,
                price=price or 0,
                stock=stock or 0,
                description=description,
                image_url=image_url,
                rating=rating or 0,
            )
            messages.success(request, "Produk berhasil dibuat.")
            return redirect("katalog:product_detail", pk=product.pk)
        except Exception as e:
            messages.error(request, f"Gagal membuat produk: {e}")
    return render(request, "katalog/product_form.html", {"categories": Product.Category.choices})


@login_required
def product_update(request: HttpRequest, pk: int) -> HttpResponse:
    if request.user.username not in ["Admin", "admin"]:
        messages.error(request, "Only admin users can update products.")
        return redirect("katalog:product_list")
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.name = request.POST.get("name", product.name).strip()
        product.category = request.POST.get("category", product.category).strip()
        product.price = request.POST.get("price", product.price)
        product.stock = request.POST.get("stock", product.stock)
        product.description = request.POST.get("description", product.description)
        product.image_url = request.POST.get("image_url", product.image_url)
        product.rating = request.POST.get("rating", product.rating)
        product.save()
        messages.success(request, "Produk berhasil diperbarui.")
        return redirect("katalog:product_detail", pk=product.pk)
    return render(request, "katalog/product_form.html", {"product": product, "categories": Product.Category.choices})


@login_required
def product_delete(request: HttpRequest, pk: int) -> HttpResponse:
    if request.user.username not in ["Admin", "admin"]:
        messages.error(request, "Only admin users can delete products.")
        return redirect("katalog:product_list")
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Produk berhasil dihapus.")
        return redirect("katalog:product_list")
    return render(request, "katalog/product_confirm_delete.html", {"product": product})


# ------------------------
# 🔹 USER AUTHENTICATION
# ------------------------
def user_home(request: HttpRequest) -> HttpResponse:
    return render(request, "katalog/user_home.html")


def user_register(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("katalog:user_home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        if not username or not password1:
            messages.error(request, "Username dan password wajib diisi.")
        elif password1 != password2:
            messages.error(request, "Konfirmasi password tidak cocok.")
        else:
            from django.contrib.auth.models import User
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username sudah digunakan.")
            else:
                user = User.objects.create_user(username=username, password=password1)
                login(request, user)
                messages.success(request, "Registrasi berhasil.")
                return redirect("katalog:user_home")

    return render(request, "katalog/user_register.html")


def user_login(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("katalog:user_home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("katalog:user_home")

        messages.error(request, "Kredensial tidak valid.")
    return render(request, "login.html")


@login_required
def user_logout(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("main:login")


# ------------------------
# 🔹 AJAX PRODUCT GRID
# ------------------------
def product_grid(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    products = Product.objects.all()

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category:
        products = products.filter(category=category)

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "katalog/_product_grid.html",
        {"page_obj": page_obj, "query": query, "category": category},
    )
