import json, os, re

BASE = r"d:\SKRIPSI DILL KERJAIN\Proyek 2"
OUT_DIR = os.path.join(BASE, "data", "dictionaries")
os.makedirs(OUT_DIR, exist_ok=True)

# 1. Jalur 2 Concept Whitelist
CONCEPT_WHITELIST = {
  # Kelompok A: Langsung (High precision >= 80% di data latih)
  ">aroD": {
    "arabic": "أَرْض",
    "pos": "N",
    "class": "AstronomicalBody",
    "aliases": ["bumi"],
    "group": "A",
    "description": "Bumi sebagai benda langit / ciptaan"
  },
  "$amos": {
    "arabic": "شَمْس",
    "pos": "N",
    "class": "AstronomicalBody",
    "aliases": ["matahari"],
    "group": "A",
    "description": "Matahari sebagai benda langit"
  },
  "samaA^'": {
    "arabic": "سَمَاء",
    "pos": "N",
    "class": "AstronomicalBody",
    "aliases": ["langit"],
    "group": "A",
    "description": "Langit sebagai benda kosmik"
  },
  "jaHiym": {
    "arabic": "جَحِيم",
    "pos": "N",
    "class": "AfterlifeLocation",
    "aliases": ["Jahim", "neraka Jahim"],
    "group": "A",
    "description": "Tempat di akhirat: Neraka Jahim"
  },
  "Haj~": {
    "arabic": "حَجّ",
    "pos": "N",
    "class": "Event",
    "aliases": ["haji", "ibadah haji"],
    "group": "A",
    "description": "Peristiwa / ritual ibadah haji"
  },
  "qiya`map": {
    "arabic": "قِيَٰمَة",
    "pos": "N",
    "class": "Event",
    "aliases": ["hari Kiamat", "Kiamat"],
    "group": "A",
    "expand_prefix": ["hari"],
    "description": "Peristiwa hari Kiamat"
  },

  # Kelompok B: Bersyarat (Konteks spesifik)
  "qamar": {
    "arabic": "قَمَر",
    "pos": "N",
    "class": "AstronomicalBody",
    "aliases": ["bulan"],
    "group": "B",
    "description": "Bulan sebagai benda langit (bukan satuan waktu syahr)"
  },
  "A^xir": {
    "arabic": "ءَاخِر",
    "pos": "ADJ",
    "class": "Event",
    "aliases": ["hari Akhir"],
    "group": "B",
    "require_prefix": ["hari"],
    "description": "Hari Akhir (hanya jika bersanding dengan kata hari / lema yawm)"
  },
  "Earo$": {
    "arabic": "عَرْش",
    "pos": "N",
    "class": "Throne",
    "aliases": ["ʻArasy", "‘Arasy", "Arasy", "‘Arasy-Nya"],
    "group": "B",
    "description": "Singgasana / Arasy Allah"
  },
  "man~": {
    "arabic": "مَنّ",
    "pos": "N",
    "class": "Food",
    "aliases": ["manna"],
    "group": "B",
    "description": "Makanan surgawi manna"
  },
  "salowaY`": {
    "arabic": "سَلْوَىٰ",
    "pos": "N",
    "class": "Food",
    "aliases": ["salwa"],
    "group": "B",
    "description": "Makanan burung salwa"
  },
  "tiyn": {
    "arabic": "تِين",
    "pos": "N",
    "class": "Fruit",
    "aliases": ["tin", "buah tin"],
    "group": "B",
    "description": "Buah tin"
  },
  "zayotuwn": {
    "arabic": "زَيْتُون",
    "pos": "N",
    "class": "Fruit",
    "aliases": ["zaitun", "buah zaitun", "pohon zaitun"],
    "group": "B",
    "description": "Buah zaitun"
  },
  "rum~aAn": {
    "arabic": "رُمَّان",
    "pos": "N",
    "class": "Fruit",
    "aliases": ["delima", "buah delima"],
    "group": "B",
    "description": "Buah delima"
  },
  "SuHuf": {
    "arabic": "صُحُف",
    "pos": "N",
    "class": "TheBookOfAllah",
    "aliases": ["Suhuf", "lembaran-lembaran suci", "kitab-kitab"],
    "group": "B",
    "description": "Lembaran wahyu Allah"
  },
  ">aboyaD": {
    "arabic": "أَبْيَض",
    "pos": "ADJ",
    "class": "Color",
    "aliases": ["putih"],
    "group": "B",
    "description": "Warna putih"
  },
  ">asowad": {
    "arabic": "أَسْوَد",
    "pos": "ADJ",
    "class": "Color",
    "aliases": ["hitam"],
    "group": "B",
    "description": "Warna hitam"
  },
  "Sufor": {
    "arabic": "صُفْر",
    "pos": "ADJ",
    "class": "Color",
    "aliases": ["kuning", "kuning tua"],
    "group": "B",
    "description": "Warna kuning"
  },
  "xuDor": {
    "arabic": "خُضْر",
    "pos": "ADJ",
    "class": "Color",
    "aliases": ["hijau"],
    "group": "B",
    "description": "Warna hijau"
  }
}

concept_out = os.path.join(OUT_DIR, "qac_concept_whitelist.json")
with open(concept_out, "w", encoding="utf-8") as f:
    json.dump(CONCEPT_WHITELIST, f, ensure_ascii=False, indent=2)
print(f"✅ Saved Concept Whitelist: {concept_out} ({len(CONCEPT_WHITELIST)} lemmas)")

# 2. Jalur 3: Seed Gazetteer (Kamus Frasa Majemuk dari train.txt, Guideline, & Asmaul Husna)
# Extract multi-word entities from train.txt
train_file = os.path.join(BASE, "indqner_1.0", "train.txt")
gaz_map = {}

def add_entry(text, cls):
    norm = text.strip()
    if norm and norm not in gaz_map:
        gaz_map[norm] = cls

# Add from train.txt (all multi-word entities)
cur_toks, cur_cls = [], None
with open(train_file, encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if not line.strip():
            if cur_toks and " " in " ".join(cur_toks):
                add_entry(" ".join(cur_toks), cur_cls)
            cur_toks, cur_cls = [], None
            continue
        p = line.split("\t")
        tok, tag = p[0], (p[1] if len(p) > 1 else "O")
        if tag.startswith("B-"):
            if cur_toks and " " in " ".join(cur_toks):
                add_entry(" ".join(cur_toks), cur_cls)
            cur_toks = [tok]
            cur_cls = tag[2:]
        elif tag.startswith("I-") and cur_toks and tag[2:] == cur_cls:
            cur_toks.append(tok)
        else:
            if cur_toks and " " in " ".join(cur_toks):
                add_entry(" ".join(cur_toks), cur_cls)
            cur_toks, cur_cls = [], None
    if cur_toks and " " in " ".join(cur_toks):
        add_entry(" ".join(cur_toks), cur_cls)

# Add standard expressions from Table 1 Guideline
guideline_entries = [
    # Allah
    ("Tuhan semesta alam", "Allah"),
    ("Tuhan Yang Maha Esa", "Allah"),
    ("Tuhan Yang Mahaperkasa lagi Maha Terpuji", "Allah"),
    ("Yang Maha Pengasih lagi Maha Penyayang", "Allah"),
    ("Yang Mahaperkasa lagi Mahabijaksana", "Allah"),
    ("Yang Maha Mengetahui lagi Mahabijaksana", "Allah"),
    ("Yang Maha Pengampun lagi Maha Penyayang", "Allah"),
    ("Yang Maha Mendengar lagi Maha Melihat", "Allah"),
    ("Yang Maha Penerima Tobat lagi Maha Penyayang", "Allah"),
    ("Yang Maha Mengetahui dan Maha Bijaksana", "Allah"),
    ("Yang Maha Teliti", "Allah"),
    # Artifact
    ("Baitulmaqdis", "GeographicalLocation"),
    ("Masjidilharam", "Artifact"),
    ("Masjidil Haram", "Artifact"),
    ("Masjidilaqsa", "Artifact"),
    ("Masjidil Aqsa", "Artifact"),
    ("Baitullah", "Artifact"),
    ("Baitul Makmur", "Artifact"),
    ("Maqam Ibrahim", "Artifact"),
    ("Tabut", "Artifact"),
    # Person / Kaum
    ("Bani Israil", "Person"),
    ("Ahlulkitab", "Person"),
    ("Anak cucu Adam", "Person"),
    ("anak cucu Adam", "Person"),
    ("kaum ‘Ad", "Person"),
    ("kaum 'Ad", "Person"),
    ("kaum Samud", "Person"),
    ("kaum Nuh", "Person"),
    ("kaum Lut", "Person"),
    ("orang-orang Yahudi", "Person"),
    ("orang Yahudi", "Person"),
    ("orang-orang Nasrani", "Person"),
    ("orang Nasrani", "Person"),
    ("penghuni gua", "Person"),
    ("pasukan bergajah", "Person"),
    ("penduduk Aikah", "Person"),
    ("penduduk Rass", "Person"),
    # Event
    ("hari Kiamat", "Event"),
    ("hari Akhir", "Event"),
    ("hari Kemudian", "Event"),
    ("hari Pembalasan", "Event"),
    ("hari Sabat", "Event"),
    ("padang Mahsyar", "Event"),
    ("hari kebangkitan", "Event"),
    # HolyBook / TheBookOfAllah
    ("Lauh Mahfuz", "TheBookOfAllah"),
    ("Lauh Mahfūẓ", "TheBookOfAllah"),
    # Throne
    ("‘Arasy Allah", "Throne"),
    ("ʻArasy Allah", "Throne"),
    # Religion
    ("agama Ibrahim", "Religion"),
    ("agama Islam", "Religion"),
    ("agama yang lurus", "Religion"),
    # Language
    ("bahasa Arab", "Language"),
    ("bahasa 'Ajam", "Language")
]

for text, cls in guideline_entries:
    add_entry(text, cls)

# Sort entries by character length descending for Greedy Longest Match!
sorted_gaz = dict(sorted(gaz_map.items(), key=lambda x: len(x[0]), reverse=True))

gaz_out = os.path.join(OUT_DIR, "seed_gazetteer.json")
with open(gaz_out, "w", encoding="utf-8") as f:
    json.dump(sorted_gaz, f, ensure_ascii=False, indent=2)

print(f"✅ Saved Seed Gazetteer: {gaz_out} ({len(sorted_gaz)} multi-word expressions, longest first)")

