from django.db import models


class Product(models.Model):
    class Category(models.TextChoices):
        RACKET = "racket", "Raket"
        SHUTTLECOCK = "shuttlecock", "Shuttlecock"
        JERSEY = "jersey", "Jersey"
        SHOES = "shoes", "Sepatu"
        ACCESSORIES = "accessories", "Aksesoris"

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=Category.choices)
    price = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    rating = models.FloatField(default=0, help_text="Rating produk (0-5)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_category_display()})"





