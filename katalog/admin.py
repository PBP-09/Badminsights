from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "updated_at")
    list_filter = ("category", "updated_at")
    search_fields = ("name", "description")
    ordering = ("name",)
    list_editable = ()
    list_display_links = ("name",)

    fieldsets = (
        (None, {
            "fields": (
                "name",
                "category",
                "price",
                "stock",
                "description",
                "image_url",
            )
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    readonly_fields = ("created_at", "updated_at")  

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff
