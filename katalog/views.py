from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
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


def is_staff(user) -> bool:
    return user.is_authenticated and user.is_staff


@user_passes_test(is_staff)
def product_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        category = request.POST.get("category", "").strip()
        price = request.POST.get("price", "0").strip()
        stock = request.POST.get("stock", "0").strip()
        description = request.POST.get("description", "").strip()
        image_url = request.POST.get("image_url", "").strip()

        try:
            product = Product.objects.create(
                name=name,
                category=category,
                price=price or 0,
                stock=stock or 0,
                description=description,
                image_url=image_url,
            )
            messages.success(request, "Produk berhasil dibuat.")
            return redirect("katalog:product_detail", pk=product.pk)
        except Exception as e:  # pragma: no cover - sederhana
            messages.error(request, f"Gagal membuat produk: {e}")

    return render(request, "katalog/product_form.html", {"categories": Product.Category.choices})


@user_passes_test(is_staff)
def product_update(request: HttpRequest, pk: int) -> HttpResponse:
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product.name = request.POST.get("name", product.name).strip()
        product.category = request.POST.get("category", product.category).strip()
        product.price = request.POST.get("price", product.price)
        product.stock = request.POST.get("stock", product.stock)
        product.description = request.POST.get("description", product.description)
        product.image_url = request.POST.get("image_url", product.image_url)
        product.save()
        messages.success(request, "Produk berhasil diperbarui.")
        return redirect("katalog:product_detail", pk=product.pk)

    return render(
        request,
        "katalog/product_form.html",
        {"product": product, "categories": Product.Category.choices},
    )


@user_passes_test(is_staff)
def product_delete(request: HttpRequest, pk: int) -> HttpResponse:
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product.delete()
        messages.success(request, "Produk berhasil dihapus.")
        return redirect("katalog:product_list")

    return render(request, "katalog/product_confirm_delete.html", {"product": product})
