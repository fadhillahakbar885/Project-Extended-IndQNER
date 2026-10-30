import os, json, re
from src.utils.text_utils import clean_footnotes, normalize_text

BASE = r"d:\SKRIPSI DILL KERJAIN\Proyek 2"
SURAH_LIST = [2, 3, 4, 5, 6, 7, 10, 16]

# Build index of all ayahs in the 8 surahs
ayah_index = {}
for s in SURAH_LIST:
    fpath = os.path.join(BASE, "Teks Terjemahan", "surah", f"{s}.json")
    with open(fpath, encoding="utf-8") as f:
        data = json.load(f)
    for item in data:
        a = item["ayah"]
        clean_t = clean_footnotes(item["translation"])
        words = [w.strip(".,;:!?\"'()«»“”") for w in clean_t.split() if w.strip(".,;:!?\"'()«»“”")]
        prefix_key = " ".join(words[:6]).lower()
        full_norm = normalize_text(clean_t).lower()
        ayah_index[(s, a)] = {
            "surah": s,
            "ayah": a,
            "prefix": prefix_key,
            "full_text": full_norm,
            "clean_translation": clean_t
        }

print(f"Indexed {len(ayah_index)} ayahs across 8 surahs.")

# Load test.txt
test_file = os.path.join(BASE, "indqner_1.0", "test.txt")
with open(test_file, encoding="utf-8") as f:
    test_verses = [v.strip() for v in f.read().split("\n\n") if v.strip()]

print(f"Loaded {len(test_verses)} verses in test.txt")

# Match each test verse
matched_test = []
unmatched = []

for idx, v in enumerate(test_verses):
    lines = v.split("\n")
    tokens = [l.split("\t")[0] for l in lines]
    clean_v_words = [w.strip(".,;:!?\"'()«»“”") for w in tokens if w.strip(".,;:!?\"'()«»“”")]
    v_prefix = " ".join(clean_v_words[:6]).lower()
    v_full = " ".join(clean_v_words).lower()

    best_match = None
    best_overlap = 0

    # 1. Try prefix exact
    for (s, a), info in ayah_index.items():
        if v_prefix and v_prefix == info["prefix"]:
            best_match = (s, a)
            break

    # 2. Try prefix 4 words
    if not best_match:
        v_sub = " ".join(clean_v_words[:4]).lower()
        for (s, a), info in ayah_index.items():
            if v_sub and v_sub in info["prefix"]:
                best_match = (s, a)
                break

    # 3. Try token containment
    if not best_match:
        for (s, a), info in ayah_index.items():
            if len(clean_v_words) >= 4 and " ".join(clean_v_words[:4]).lower() in info["full_text"]:
                best_match = (s, a)
                break

    if best_match:
        matched_test.append((idx + 1, best_match[0], best_match[1]))
    else:
        unmatched.append((idx + 1, v_prefix))

print(f"✅ Successfully aligned {len(matched_test)} of {len(test_verses)} test verses.")
if unmatched:
    print(f"Unmatched count: {len(unmatched)}")
    for u in unmatched[:5]:
        print(f"   Test verse {u[0]}: {u[1]}")

