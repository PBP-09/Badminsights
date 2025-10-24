import pandas as pd
import uuid
import json
import re
from datetime import datetime

# === CONFIG ===
file_path = r"D:\datashet (4).xlsx"
output_path = r"D:\Badminsights\players_fixture_final_v5.json"

# === LOAD FILE ===
df = pd.read_excel(file_path)
df.columns = [col.strip().lower() for col in df.columns]
df['nama'] = df['nama'].astype(str).str.strip()

# === PARSE DATE FROM 'Tempat & Tanggal Lahir' ===
bulan_map = {
    # Bahasa Indonesia
    "januari": "01", "februari": "02", "maret": "03", "april": "04",
    "mei": "05", "juni": "06", "juli": "07", "agustus": "08",
    "september": "09", "oktober": "10", "november": "11", "desember": "12",
    # Bahasa Inggris
    "january": "01", "february": "02", "march": "03", "april": "04",
    "may": "05", "june": "06", "july": "07", "august": "08",
    "september": "09", "october": "10", "november": "11", "december": "12",
    # Singkatan
    "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05",
    "jun": "06", "jul": "07", "aug": "08", "sep": "09", "sept": "09",
    "oct": "10", "nov": "11", "dec": "12",
    # Lain-lain
    "mai": "05",  # varian dari "mei"
}


def extract_date(text):
    if not isinstance(text, str):
        return None

    # Bersihkan karakter aneh
    original_text = text
    text = text.replace(",", " ").strip()

    match = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', text)
    if match:
        day, month_str, year = match.groups()
        month_str = month_str.lower()
        month = bulan_map.get(month_str)
        if month:
            try:
                return f"{int(year):04d}-{month}-{int(day):02d}"
            except Exception as e:
                print(f"⚠️ Gagal konversi angka: '{original_text}' → {e}")
                return None
        else:
            print(f"⚠️ Bulan tidak dikenali: '{original_text}'")
    else:
        print(f"⚠️ Format tanggal tidak cocok: '{original_text}'")

    return None

df['date_of_birth'] = df['tempat & tanggal lahir'].apply(extract_date)

# === NORMALIZE CATEGORY & STATUS ===
def normalize_category(cat):
    if not isinstance(cat, str):
        return "unknown"
    cat = cat.lower().replace("’", "'").strip()

    # Bersihkan spasi dan simbol
    cat = cat.replace(".", "").replace("-", " ").replace("_", " ")

    # Aturan umum
    if any(x in cat for x in ["men", "putra", "ms", "male"]):
        if "double" in cat or "ganda" in cat or "md" in cat:
            return "men's double"
        return "men's single"

    if any(x in cat for x in ["women", "putri", "ws", "female"]):
        if "double" in cat or "ganda" in cat or "wd" in cat:
            return "women's double"
        return "women's single"

    if any(x in cat for x in ["mixed", "campuran", "xd"]):
        return "mixed double"

    return "unknown"


def normalize_status(status):
    s = str(status).lower().strip()

    # Bahasa Inggris & Indonesia
    if any(x in s for x in ["active", "aktif", "playing", "current"]):
        return "active"
    if any(x in s for x in ["injur", "cedera"]):
        return "injured"
    if any(x in s for x in ["retir", "pensiun", "retired"]):
        return "retired"

    return "inactive"


df['category'] = df.apply(lambda row: normalize_category(row['kategori'], row['nama']), axis=1)
df['status'] = df['status'].apply(normalize_status)

# === BUILD PARTNER RELATION MAP ===
name_to_uuid = {row["nama"]: str(uuid.uuid4()) for _, row in df.iterrows()}
partner_map = {}
for _, row in df.iterrows():
    if pd.notna(row.get("pasangan untuk kategori ganda")):
        partner_name = row["pasangan untuk kategori ganda"].strip()
        partner_map[row["nama"]] = partner_name

# === BUILD PLAYER OBJECTS ===
players = []
for _, row in df.iterrows():
    player_id = name_to_uuid[row["nama"]]
    partner_name = partner_map.get(row["nama"])
    partner_id = name_to_uuid.get(partner_name) if partner_name else None

    player_data = {
        "model": "main.Player",
        "pk": player_id,
        "fields": {
            "name": row["nama"],
            "date_of_birth": row["date_of_birth"],
            "country": "ID",
            "bio": "",
            "category": row["category"],
            "status": row["status"],
            "thumbnail": "",
            "world_rank": None,
            "partner": partner_id,
            "is_featured": False
        }
    }
    players.append(player_data)

# === AUTO LINK PARTNERS TWO-WAY ===
for p in players:
    partner_id = p["fields"]["partner"]
    if partner_id:
        # cari partner-nya dan set balik ke player_id kalau belum diisi
        partner_obj = next((x for x in players if x["pk"] == partner_id), None)
        if partner_obj and not partner_obj["fields"]["partner"]:
            partner_obj["fields"]["partner"] = p["pk"]

# === SAVE JSON ===
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(players, f, ensure_ascii=False, indent=4)

# === REMOVE DUPLICATE PKs ===
unique_players = {}
for p in players:
    pk = p["pk"]
    if pk not in unique_players:
        unique_players[pk] = p
players = list(unique_players.values())

print(f"✅ Fixture berhasil dibuat: {output_path}")
print(f"Total pemain: {len(players)}")
print(f"Pemain dengan partner: {sum(1 for p in players if p['fields']['partner'])}")
print(f"Pemain dengan tanggal lahir valid: {sum(1 for p in players if p['fields']['date_of_birth'])}")
print(f"✅ Dihapus duplikat: {100 - len(players)} pemain duplikat dihapus")
