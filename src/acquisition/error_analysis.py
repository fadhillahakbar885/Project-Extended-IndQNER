import sys, os
sys.path.append(r"d:\SKRIPSI DILL KERJAIN\Proyek 2")

from src.preprocessing.quran_loader import QuranDataLoader
from src.acquisition.entity_acquisition_manager import EntityAcquisitionManager

loader = QuranDataLoader()
manager = EntityAcquisitionManager()

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

print("\n--- ANALISIS PERBEDAAN (ERROR ANALYSIS): SURAH 2:1 - 2:50 ---")
for idx, g_verse in enumerate(gold_verses):
    ayah = idx + 1
    g_ents = []
    cur_e = []
    cur_c = None
    for tok, tag in g_verse:
        if tag.startswith("B-"):
            if cur_e: g_ents.append((" ".join(cur_e), cur_c))
            cur_e = [tok]; cur_c = tag[2:]
        elif tag.startswith("I-") and cur_e and tag[2:] == cur_c:
            cur_e.append(tok)
        else:
            if cur_e: g_ents.append((" ".join(cur_e), cur_c))
            cur_e = []; cur_c = None
    if cur_e: g_ents.append((" ".join(cur_e), cur_c))

    qac = loader.get_qac_tokens(2, ayah)
    trans = loader.get_indonesian_translation(2, ayah)
    pred_cands = manager.acquire_entities(2, ayah, qac, trans) if trans else []

    pred_clean = [p["text"].strip(".,;:!?\"'()«»“”").replace("‘","'").replace("’","'") for p in pred_cands]
    gold_clean = [g[0].strip(".,;:!?\"'()«»“”").replace("‘","'").replace("’","'") for g in g_ents]

    # Unmatched in pred (Potential False Positives)
    fp = [p for p in pred_cands if p["text"].strip(".,;:!?\"'()«»“”").replace("‘","'").replace("’","'") not in gold_clean]
    # Unmatched in gold (Potential False Negatives)
    fn = [g for g in g_ents if g[0].strip(".,;:!?\"'()«»“”").replace("‘","'").replace("’","'") not in pred_clean]

    if fp or fn:
        print(f"\n[Ayat 2:{ayah}]")
        if fp:
            for p in fp:
                print(f"   ⚠️ FP (Sistem mendeteksi, tapi Gold = O): '{p['text']}' -> {p['class']} ({p['channel']})")
        if fn:
            for g in fn:
                print(f"   ❓ FN (Ada di Gold, tapi belum terjaring) : '{g[0]}' -> {g[1]}")

