import sys, os
sys.path.append(r"d:\SKRIPSI DILL KERJAIN\Proyek 2")

from src.preprocessing.quran_loader import QuranDataLoader
from src.acquisition.entity_acquisition_manager import EntityAcquisitionManager

loader = QuranDataLoader()
manager = EntityAcquisitionManager()

# Load first 50 verses of Surah 2 from train.txt
# Surah 2 starts at line where 2:1 is.
# In train.txt, verses are separated by blank lines.
train_file = r"d:\SKRIPSI DILL KERJAIN\Proyek 2\indqner_1.0\train.txt"

gold_verses = []
cur_tokens = []
with open(train_file, encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if not line.strip():
            if cur_tokens:
                gold_verses.append(cur_tokens)
                cur_tokens = []
                if len(gold_verses) >= 50:
                    break
            continue
        p = line.split("\t")
        cur_tokens.append((p[0], p[1] if len(p) > 1 else "O"))
if cur_tokens and len(gold_verses) < 50:
    gold_verses.append(cur_tokens)

print(f"Loaded {len(gold_verses)} gold verses from train.txt (Surah 2:1 - 2:50)")

# Extract gold entities per verse: list of (word_span_text, class)
gold_entities_total = 0
pred_entities_total = 0
correct_strict = 0
correct_span_only = 0

for idx, g_verse in enumerate(gold_verses):
    ayah = idx + 1
    # extract gold entities
    g_ents = []
    cur_e_words = []
    cur_e_cls = None
    for tok, tag in g_verse:
        if tag.startswith("B-"):
            if cur_e_words:
                g_ents.append((" ".join(cur_e_words), cur_e_cls))
            cur_e_words = [tok]
            cur_e_cls = tag[2:]
        elif tag.startswith("I-") and cur_e_words and tag[2:] == cur_e_cls:
            cur_e_words.append(tok)
        else:
            if cur_e_words:
                g_ents.append((" ".join(cur_e_words), cur_e_cls))
            cur_e_words = []
            cur_e_cls = None
    if cur_e_words:
        g_ents.append((" ".join(cur_e_words), cur_e_cls))

    gold_entities_total += len(g_ents)

    # Now get predicted entities from our manager
    qac = loader.get_qac_tokens(2, ayah)
    trans = loader.get_indonesian_translation(2, ayah)
    pred_cands = manager.acquire_entities(2, ayah, qac, trans) if trans else []
    pred_entities_total += len(pred_cands)

    # Match gold and pred
    # Clean text comparison
    matched_gold = set()
    for p in pred_cands:
        p_text = p["text"].strip(".,;:!?\"'()«»“”")
        p_cls = p["class"]
        found = False
        for g_i, (g_text, g_cls) in enumerate(g_ents):
            if g_i not in matched_gold:
                g_clean = g_text.strip(".,;:!?\"'()«»“”")
                # Normalize ayn / apostrophe
                if p_text.replace("‘","'").replace("’","'") == g_clean.replace("‘","'").replace("’","'"):
                    correct_span_only += 1
                    if p_cls == g_cls:
                        correct_strict += 1
                    matched_gold.add(g_i)
                    found = True
                    break

print(f"\n=======================================================")
print(f"KOMPARASI EMPIRIS DENGAN INDQNER 1.0 (QS. 2:1 - 2:50)")
print(f"=======================================================")
print(f"Total Entitas Gold Standard (IndQNER 1.0): {gold_entities_total}")
print(f"Total Entitas Hasil Ekstraksi Pipeline  : {pred_entities_total}")
print(f"Kecocokan Span Boundary Sempurna        : {correct_span_only}")
print(f"Kecocokan Strict (Span + Kelas Cocok)   : {correct_strict}")

p_strict = correct_strict / pred_entities_total if pred_entities_total else 0
r_strict = correct_strict / gold_entities_total if gold_entities_total else 0
f1_strict = (2 * p_strict * r_strict) / (p_strict + r_strict) if (p_strict + r_strict) else 0

p_span = correct_span_only / pred_entities_total if pred_entities_total else 0
r_span = correct_span_only / gold_entities_total if gold_entities_total else 0
f1_span = (2 * p_span * r_span) / (p_span + r_span) if (p_span + r_span) else 0

print(f"\nStrict Entity-Level Metrics:")
print(f"   • Precision : {p_strict*100:.2f}%")
print(f"   • Recall    : {r_strict*100:.2f}%")
print(f"   • F1-Score  : {f1_strict*100:.2f}%")

print(f"\nSpan Boundary (Boundary Only) Metrics:")
print(f"   • Precision : {p_span*100:.2f}%")
print(f"   • Recall    : {r_span*100:.2f}%")
print(f"   • F1-Score  : {f1_span*100:.2f}%")

