from django.test import TestCase

from .models import Product


class ProductModelTests(TestCase):
    def test_create_product(self):
        p = Product.objects.create(
            name="Yonex Astrox 100ZZ",
            category=Product.Category.RACKET,
            price=2999000,
            stock=10,
            description="Raket premium untuk kontrol dan power.",
            image_url="https://example.com/racket.jpg",
        )
        self.assertEqual(str(p), f"{p.name} ({p.get_category_display()})")
        self.assertGreater(p.pk, 0)
