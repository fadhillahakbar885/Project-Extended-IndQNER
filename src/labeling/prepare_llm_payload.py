import os
import json
import sys
from typing import List, Dict

BASE = r"d:\SKRIPSI DILL KERJAIN\Proyek 2"
sys.path.append(BASE)

from src.preprocessing.quran_loader import QuranDataLoader
from src.acquisition.entity_acquisition_manager import EntityAcquisitionManager
from src.labeling.kamus_indqner import KamusIndQNER

def extract_unmapped_and_benchmark_payload():
    print("Mengompilasi data payload untuk pengujian Llama-3-8B di Google Colab T4...")
    loader = QuranDataLoader()
    acq_manager = EntityAcquisitionManager()
    kamus = KamusIndQNER()

    unmapped_items = []
    
    # 1. Kumpulkan seluruh unmapped entities dari 114 Surah
    print("Memindai 114 surah untuk mendeteksi entitas unmapped...")
    for s in range(1, 115):
        surah_file = os.path.join(BASE, "Teks Terjemahan", "surah", f"{s}.json")
        if not os.path.exists(surah_file):
            continue
        with open(surah_file, encoding="utf-8") as f:
            ayah_list = json.load(f)
            
        for item in ayah_list:
            a = item["ayah"]
            qac = loader.get_qac_tokens(s, a)
            trans = loader.get_indonesian_translation(s, a)
            if not trans:
                continue
                
            cands = acq_manager.acquire_entities(s, a, qac, trans)
            for cand in cands:
                text = cand["text"]
                dict_class = kamus.lookup(text)
                if not dict_class:
                    unmapped_items.append({
                        "id": f"unmapped_{s}_{a}_{cand['start']}",
                        "type": "unmapped_corpus",
                        "surah": s,
                        "ayah": a,
                        "sentence": trans["cleaned_translation"],
                        "entity": text,
                        "start": cand["start"],
                        "end": cand["end"],
                        "channel": cand.get("channel", "Unknown"),
                        "ground_truth_class": None
                    })

    print(f"✅ Ditemukan {len(unmapped_items)} entitas unmapped di seluruh 114 surah.")

    # 2. Kumpulkan benchmark ground-truth sample dari indqner_1.0/test.txt untuk evaluasi akurasi LLM
    print("Mengumpulkan sampel benchmark ground-truth untuk menguji akurasi LLM (Zero-Shot vs Few-Shot)...")
    test_path = os.path.join(BASE, "indqner_1.0", "test.txt")
    with open(test_path, encoding="utf-8") as f:
        blocks = [b.strip() for b in f.read().split("\n\n") if b.strip()]

    benchmark_items = []
    item_counter = 0

    for b in blocks:
        lines = b.split("\n")
        tokens = [l.split("\t")[0] for l in lines]
        tags = [l.split("\t")[1] if len(l.split("\t")) > 1 else "O" for l in lines]
        sentence_text = " ".join(tokens)

        # Extract entities from BIO tags
        curr_ent = []
        curr_cls = None
        for tok, tag in zip(tokens, tags):
            if tag.startswith("B-"):
                if curr_ent:
                    ent_str = " ".join(curr_ent)
                    item_counter += 1
                    benchmark_items.append({
                        "id": f"benchmark_{item_counter}",
                        "type": "benchmark_test_set",
                        "sentence": sentence_text,
                        "entity": ent_str,
                        "ground_truth_class": curr_cls
                    })
                curr_ent = [tok]
                curr_cls = tag[2:]
            elif tag.startswith("I-") and curr_ent:
                curr_ent.append(tok)
            else:
                if curr_ent:
                    ent_str = " ".join(curr_ent)
                    item_counter += 1
                    benchmark_items.append({
                        "id": f"benchmark_{item_counter}",
                        "type": "benchmark_test_set",
                        "sentence": sentence_text,
                        "entity": ent_str,
                        "ground_truth_class": curr_cls
                    })
                    curr_ent = []
                    curr_cls = None
        if curr_ent:
            ent_str = " ".join(curr_ent)
            item_counter += 1
            benchmark_items.append({
                "id": f"benchmark_{item_counter}",
                "type": "benchmark_test_set",
                "sentence": sentence_text,
                "entity": ent_str,
                "ground_truth_class": curr_cls
            })

    print(f"✅ Terkumpul {len(benchmark_items)} entitas ground truth dari test set.")

    # Gabungkan payload
    payload = {
        "metadata": {
            "description": "Payload Pengujian LLM Llama-3-8B di Google Colab T4 untuk Skripsi Extended IndQNER",
            "total_unmapped": len(unmapped_items),
            "total_benchmark": len(benchmark_items),
            "valid_classes_count": 20
        },
        "unmapped_entities": unmapped_items,
        "benchmark_entities": benchmark_items
    }

    output_file = os.path.join(BASE, "data", "intermediate", "llm_colab_payload.json")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"💾 Payload tersimpan di: {output_file}")
    return payload

if __name__ == "__main__":
    extract_unmapped_and_benchmark_payload()

