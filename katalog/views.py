from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Product


def product_list(request: HttpRequest) -> HttpResponse:
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
        "katalog/product_list.html",
        {
            "page_obj": page_obj,
            "query": query,
            "category": category,
            "categories": Product.Category.choices,
        },
    )


def product_detail(request: HttpRequest, pk: int) -> HttpResponse:
    product = get_object_or_404(Product, pk=pk)
    return render(request, "katalog/product_detail.html", {"product": product})


@login_required
def product_create(request: HttpRequest) -> HttpResponse:
    if not request.user.is_staff:
        return redirect("katalog:product_list")

    if request.method == "POST":
        product = Product.objects.create(
            name=request.POST.get("name", "").strip(),
            category=request.POST.get("category", "").strip(),
            price=request.POST.get("price") or 0,
            stock=request.POST.get("stock") or 0,
            description=request.POST.get("description", "").strip(),
            image_url=request.POST.get("image_url", "").strip(),
            rating=request.POST.get("rating") or 0,
        )
        return redirect("katalog:product_detail", pk=product.pk)

    return render(
        request,
        "katalog/product_form.html",
        {"categories": Product.Category.choices},
    )


@login_required
def product_update(request: HttpRequest, pk: int) -> HttpResponse:
    if not request.user.is_staff:
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
        return redirect("katalog:product_detail", pk=product.pk)

    return render(
        request,
        "katalog/product_form.html",
        {"product": product, "categories": Product.Category.choices},
    )


@login_required
def product_delete(request: HttpRequest, pk: int) -> HttpResponse:
    if not request.user.is_staff:
        return redirect("katalog:product_list")

    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product.delete()
        return redirect("katalog:product_list")

    return render(
        request,
        "katalog/product_confirm_delete.html",
        {"product": product},
    )


def user_home(request: HttpRequest) -> HttpResponse:
    return render(request, "katalog/user_home.html")


def user_register(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("katalog:user_home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        if password1 == password2 and username:
            from django.contrib.auth.models import User
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password=password1)
                login(request, user)
                return redirect("katalog:user_home")

    return render(request, "katalog/user_register.html")


def user_login(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("katalog:user_home")

    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username", "").strip(),
            password=request.POST.get("password", ""),
        )
        if user:
            login(request, user)
            return redirect("katalog:user_home")

    return render(request, "login.html")


@login_required
def user_logout(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("katalog:user_login")


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
        {
            "page_obj": page_obj,
            "is_admin": request.user.is_staff,
        },
    )


def product_list_json(request: HttpRequest):
    products = Product.objects.all().values(
        "id",
        "name",
        "category",
        "price",
        "stock",
        "description",
        "image_url",
        "rating",
    )
    return JsonResponse(list(products), safe=False)
