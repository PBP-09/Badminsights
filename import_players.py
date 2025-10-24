import pandas as pd
import django
import os

# setup environment Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'badminsights.settings')
django.setup()

from main.models import Player

# Path ke file Excel
file_path = r"D:\Badminsights\players_fixture_final_v5.json"

# Baca Excel
df = pd.read_excel(file_path)

# Loop tiap baris dan simpan ke database
for _, row in df.iterrows():
    Player.objects.create(
        name=row['Nama'],
        category=row['Kategori'],
        status=row['Status'],
        birth_info=row['Tempat & Tanggal Lahir'],
        partner=row.get('Pasangan Untuk Kategori Ganda', None)
    )

print("✅ Semua data berhasil diimport ke database!")
