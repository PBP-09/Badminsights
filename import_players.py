import pandas as pd
import django
import os, json
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'badminsights.settings')
django.setup()

from main.models import Player

file_path = os.path.join(settings.BASE_DIR, "data", "players_fixture_final_v6.json")

# Pastikan file ada
if not os.path.exists(file_path):
    raise FileNotFoundError(f"❌ File tidak ditemukan di: {file_path}")

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Loop dan masukkan data pemain, cek apakah pemain sudah ada
for entry in data:
    fields = entry["fields"]
    
    # Cek apakah pemain sudah ada berdasarkan nama
    if Player.objects.filter(name=fields["name"]).exists():
        print(f"⚠️ Pemain {fields['name']} sudah ada, melewati...")
        continue  # Skip pemain yang sudah ada

    Player.objects.create(
        name=fields["name"],
        category=fields["category"],
        status=fields["status"],
        date_of_birth=fields["date_of_birth"],
        bio=fields.get("bio", ""),
        thumbnail=fields.get("thumbnail", ""),
        world_rank=fields.get("world_rank", None),
        is_featured=fields.get("is_featured", False)
    )

print("✅ Semua data pemain berhasil diimport ke database!")
