from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Product
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Product

@csrf_exempt
def save_product_flutter(request):
    if request.method != "POST":
        return JsonResponse({'success': False, 'error': 'POST only'}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Auth required'}, status=401)

    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Admin only'}, status=403)

    data = request.POST

    def to_int(v, default=0):
        try:
            return int(v)
        except (TypeError, ValueError):
            return default

    def to_float(v, default=0.0):
        try:
            return float(v)
        except (TypeError, ValueError):
            return default

    product_id = data.get('product_id')
    name = (data.get('name') or '').strip()
    category = (data.get('category') or '').strip()
    price = to_int(data.get('price'))
    stock = to_int(data.get('stock'))
    description = (data.get('description') or '').strip()
    image_url = (data.get('image_url') or '').strip()
    rating = to_float(data.get('rating'))

    if not name or not category:
        return JsonResponse({'success': False, 'error': 'Name & category required'}, status=400)

    if category not in dict(Product.Category.choices):
        return JsonResponse({'success': False, 'error': 'Invalid category'}, status=400)

    if price < 0 or stock < 0:
        return JsonResponse({'success': False, 'error': 'Invalid price/stock'}, status=400)

    if rating < 0 or rating > 5:
        return JsonResponse({'success': False, 'error': 'Rating must be 0–5'}, status=400)

    if product_id:
        product = get_object_or_404(Product, id=product_id)
        product.name = name
        product.category = category
        product.price = price
        product.stock = stock
        product.description = description
        product.image_url = image_url
        product.rating = rating
        product.save()
        msg = "updated"
    else:
        product = Product.objects.create(
            name=name,
            category=category,
            price=price,
            stock=stock,
            description=description,
            image_url=image_url,
            rating=rating
        )
        msg = "created"

    return JsonResponse({'success': True, 'message': msg, 'id': product.id})


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

@csrf_exempt
def delete_product_flutter(request, pk):
    if request.method != "POST":
        return JsonResponse(
            {'success': False, 'error': 'POST only'},
            status=405
        )

    if not request.user.is_authenticated:
        return JsonResponse(
            {'success': False, 'error': 'Auth required'},
            status=401
        )

    if not request.user.is_staff:
        return JsonResponse(
            {'success': False, 'error': 'Admin only'},
            status=403
        )

    product = get_object_or_404(Product, pk=pk)
    product.delete()

    return JsonResponse({
        'success': True,
        'message': 'Product deleted',
        'id': pk
    })
