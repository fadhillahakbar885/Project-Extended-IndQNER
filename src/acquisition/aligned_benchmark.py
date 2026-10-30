import sys, os, json
sys.path.append(r"d:\SKRIPSI DILL KERJAIN\Proyek 2")

from src.preprocessing.quran_loader import QuranDataLoader
from src.acquisition.entity_acquisition_manager import EntityAcquisitionManager
from src.utils.text_utils import clean_footnotes, normalize_text

loader = QuranDataLoader()
manager = EntityAcquisitionManager()

# Load all 50 verses from train.txt
train_file = r"d:\SKRIPSI DILL KERJAIN\Proyek 2\indqner_1.0\train.txt"
with open(train_file, encoding="utf-8") as f:
    raw_verses = [v.strip() for v in f.read().split("\n\n") if v.strip()]

with open(r"d:\SKRIPSI DILL KERJAIN\Proyek 2\Teks Terjemahan\surah\2.json", encoding="utf-8") as f:
    kemenag_surah2 = json.load(f)

# Build a mapping from normalized first 6 words to kemenag ayah number
kemenag_map = {}
for a_obj in kemenag_surah2:
    a_num = a_obj["ayah"]
    cleaned = clean_footnotes(a_obj["translation"])
    norm_w = " ".join([w.strip(".,;:!?\"'()«»“”") for w in cleaned.split()[:6]]).lower()
    kemenag_map[norm_w] = a_num

print(f"Loaded {len(raw_verses)} verses in train.txt and {len(kemenag_surah2)} ayahs in 2.json")

# Now let's benchmark the first 50 verses of train.txt WITH ACCURATE AYAH ALIGNMENT!
gold_total = 0
pred_total = 0
correct_strict = 0
correct_span = 0

for v_idx in range(50):
    lines = raw_verses[v_idx].split("\n")
    toks = [l.split("\t")[0] for l in lines]
    tags = [l.split("\t")[1] if len(l.split("\t")) > 1 else "O" for l in lines]
    
    # Identify which ayah this is in Kemenag
    v_norm = " ".join([w.strip(".,;:!?\"'()«»“”") for w in toks[:6]]).lower()
    matched_ayah = kemenag_map.get(v_norm)
    if not matched_ayah:
        # fuzzy match
        for k_norm, a_num in kemenag_map.items():
            if v_norm[:20] == k_norm[:20]:
                matched_ayah = a_num
                break
                
    if not matched_ayah:
        matched_ayah = v_idx + 1 # fallback

    # Extract gold entities
    g_ents = []
    cur_w, cur_c = [], None
    for t, g in zip(toks, tags):
        if g.startswith("B-"):
            if cur_w: g_ents.append((" ".join(cur_w), cur_c))
            cur_w, cur_c = [t], g[2:]
        elif g.startswith("I-") and cur_w and g[2:] == cur_c:
            cur_w.append(t)
        else:
            if cur_w: g_ents.append((" ".join(cur_w), cur_c))
            cur_w, cur_c = [], None
    if cur_w: g_ents.append((" ".join(cur_w), cur_c))
    gold_total += len(g_ents)

    # Predict using manager for that exact matched ayah
    qac = loader.get_qac_tokens(2, matched_ayah)
    trans = loader.get_indonesian_translation(2, matched_ayah)
    pred_cands = manager.acquire_entities(2, matched_ayah, qac, trans) if trans else []
    pred_total += len(pred_cands)

    matched_gold = set()
    for p in pred_cands:
        p_text = p["text"].strip(".,;:!?\"'()«»“”").replace("‘","'").replace("’","'")
        p_cls = p["class"]
        for g_i, (g_text, g_cls) in enumerate(g_ents):
            if g_i not in matched_gold:
                g_clean = g_text.strip(".,;:!?\"'()«»“”").replace("‘","'").replace("’","'")
                if p_text == g_clean:
                    correct_span += 1
                    if p_cls == g_cls:
                        correct_strict += 1
                    matched_gold.add(g_i)
                    break

print(f"\n=================================================================")
print(f"HASIL AKURASI REALISTIS (AYAT SELARAS 1-TO-1 DENGAN INDQNER 1.0)")
print(f"=================================================================")
print(f"Total Entitas Gold Standard : {gold_total}")
print(f"Total Entitas Hasil Sistem  : {pred_total}")
print(f"Kecocokan Span Boundary     : {correct_span}")
print(f"Kecocokan Strict (Span+Kelas): {correct_strict}")

p = correct_strict / pred_total if pred_total else 0
r = correct_strict / gold_total if gold_total else 0
f1 = (2 * p * r) / (p + r) if (p + r) else 0

print(f"\nStrict Metrics:")
print(f"   • Precision : {p*100:.2f}%")
print(f"   • Recall    : {r*100:.2f}%")
print(f"   • F1-Score  : {f1*100:.2f}%")

