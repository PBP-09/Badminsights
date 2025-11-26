from django.conf import settings
from django.db import models
import uuid
from django_countries.fields import CountryField
from django.contrib.auth.models import User

class Player(models.Model):
    CATEGORY_CHOICES = [
        ('women\'s single', 'Women\'s Single'),
        ('men\'s single', 'Men\'s Single'),
        ('women\'s double', 'Women\'s Double'),
        ('men\'s double', 'Men\'s Double'),
        ('mixed double', 'Mixed Double'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('injured', 'Injured'),
        ('retired', 'Retired'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255) # nama panjang
    date_of_birth = models.DateField(null=True, blank=True) # tanggal lahir
    country = CountryField(blank_label='(select country)') # asal negara pemain 
    bio = models.TextField(blank=True) # untuk biografi singkat atau deskripsi singkat mengenai pemain
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='women\'s single') # kategori pemain
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active') # status aktif pemain
    thumbnail = models.URLField(blank=True, null=True) # untuk foto pemain
    world_rank = models.PositiveIntegerField(null=True, blank=True, help_text="Peringkat dunia saat ini") # peringkat dunia (bwf) pemain
    partner = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, help_text="Pilih pemain lain sebagai partner (jika pemain ganda)") # pasangan untuk pemain ganda
    is_featured = models.BooleanField(default=False) # featured player

    def __str__(self):
        return self.name
    