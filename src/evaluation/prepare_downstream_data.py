import os
import json
import sys
from typing import Set, Tuple, List, Dict

BASE = r"d:\SKRIPSI DILL KERJAIN\Proyek 2"
sys.path.append(BASE)

from src.utils.text_utils import clean_footnotes, normalize_text

def build_prefix_key(conll_block: str) -> str:
    """Extracts first 5 words as normalized prefix key for deduplication & alignment."""
    lines = conll_block.strip().split("\n")
    tokens = [l.split("\t")[0].strip(".,;:!?\"'()«»“”[]") for l in lines if l.strip()]
    tokens = [t for t in tokens if t]
    return " ".join(tokens[:5]).lower()

def prepare_downstream_dataset():
    print("\n" + "=" * 80)
    print("MEMPERSIAPKAN PARTISI DATASET EVALUASI EKSTRINSIK (DOWNSTREAM NER TASK)")
    print("=" * 80)

    out_dir = os.path.join(BASE, "data", "downstream")
    os.makedirs(out_dir, exist_ok=True)

    indqner_dir = os.path.join(BASE, "indqner_1.0")
    test_src = os.path.join(indqner_dir, "test.txt")
    dev_src = os.path.join(indqner_dir, "dev.txt")
    train_src = os.path.join(indqner_dir, "train.txt")
    extended_src = os.path.join(BASE, "data", "output", "extended_indqner.txt")

    # 1. Baca dan petakan test set & dev set untuk strict isolation (Zero Leakage)
    with open(test_src, "r", encoding="utf-8") as f:
        test_blocks = [b.strip() for b in f.read().split("\n\n") if b.strip()]
    with open(dev_src, "r", encoding="utf-8") as f:
        dev_blocks = [b.strip() for b in f.read().split("\n\n") if b.strip()]
    with open(train_src, "r", encoding="utf-8") as f:
        baseline_train_blocks = [b.strip() for b in f.read().split("\n\n") if b.strip()]

    print(f"• Baseline Train Set  : {len(baseline_train_blocks)} ayat")
    print(f"• Validation (Dev) Set: {len(dev_blocks)} ayat (ISOLATED)")
    print(f"• Unseen Test Set     : {len(test_blocks)} ayat (ISOLATED)")

    # Kumpulkan kunci prefix test & dev agar tidak ada 1 ayat pun yang bocor ke data latih
    forbidden_prefixes: Set[str] = set()
    for b in test_blocks:
        forbidden_prefixes.add(build_prefix_key(b))
    for b in dev_blocks:
        forbidden_prefixes.add(build_prefix_key(b))

    print(f"🔒 Terkunci {len(forbidden_prefixes)} prefix ayat terlarang (Test + Dev) untuk mencegah Data Leakage.")

    # 2. Baca Extended IndQNER (114 Surah)
    with open(extended_src, "r", encoding="utf-8") as f:
        extended_all_blocks = [b.strip() for b in f.read().split("\n\n") if b.strip()]

    print(f"• Korpus Penuh 114 Surah: {len(extended_all_blocks)} ayat")

    # Kumpulkan kunci prefix dari baseline train
    baseline_train_prefixes = {build_prefix_key(b) for b in baseline_train_blocks}

    # 3. Bentuk Extended Training Set:
    # Gabungan dari baseline train asli + ayat-ayat dari surah baru yang BUKAN test/dev dan BUKAN duplikat
    extended_train_blocks = list(baseline_train_blocks)
    new_added_count = 0

    for b in extended_all_blocks:
        p_key = build_prefix_key(b)
        if not p_key:
            continue
        # Jangan masukkan jika merupakan test/dev set
        if p_key in forbidden_prefixes:
            continue
        # Jangan masukkan jika sudah ada di baseline train
        if p_key in baseline_train_prefixes:
            continue

        extended_train_blocks.append(b)
        baseline_train_prefixes.add(p_key)
        new_added_count += 1

    print(f"✅ Berhasil menambahkan {new_added_count} ayat baru dari 106 surah tambahan ke Extended Train Set!")
    print(f"📊 Total Ayat Extended Train: {len(extended_train_blocks)} ayat (vs {len(baseline_train_blocks)} ayat Baseline)")

    # 4. Tulis berkas partisi
    p_baseline_train = os.path.join(out_dir, "baseline_train.txt")
    p_extended_train = os.path.join(out_dir, "extended_train.txt")
    p_dev = os.path.join(out_dir, "dev.txt")
    p_test = os.path.join(out_dir, "test.txt")

    with open(p_baseline_train, "w", encoding="utf-8") as f:
        f.write("\n\n".join(baseline_train_blocks) + "\n")
    with open(p_extended_train, "w", encoding="utf-8") as f:
        f.write("\n\n".join(extended_train_blocks) + "\n")
    with open(p_dev, "w", encoding="utf-8") as f:
        f.write("\n\n".join(dev_blocks) + "\n")
    with open(p_test, "w", encoding="utf-8") as f:
        f.write("\n\n".join(test_blocks) + "\n")

    # 5. Hitung metrik token dan entitas tiap berkas
    def count_conll_stats(blocks: List[str]) -> Dict[str, int]:
        n_tokens = 0
        n_entities = 0
        for b in blocks:
            for line in b.split("\n"):
                parts = line.strip().split("\t")
                if len(parts) >= 2:
                    n_tokens += 1
                    if parts[1].startswith("B-"):
                        n_entities += 1
        return {"verses": len(blocks), "tokens": n_tokens, "entities": n_entities}

    stats = {
        "baseline_train": count_conll_stats(baseline_train_blocks),
        "extended_train": count_conll_stats(extended_train_blocks),
        "dev": count_conll_stats(dev_blocks),
        "test": count_conll_stats(test_blocks)
    }

    summary_file = os.path.join(out_dir, "downstream_dataset_summary.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 80)
    print("RINGKASAN PARTISI DATASET EVALUASI EKSTRINSIK:")
    print("=" * 80)
    for name, s in stats.items():
        print(f"• {name:<16}: {s['verses']:>5d} ayat | {s['tokens']:>7d} token | {s['entities']:>5d} entitas")
    print(f"\n💾 Direktori downstream tersimpan: {out_dir}")
    return stats

if __name__ == "__main__":
    prepare_downstream_dataset()
