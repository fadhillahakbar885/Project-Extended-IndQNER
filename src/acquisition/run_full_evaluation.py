import sys, os, collections
sys.path.append(r"d:\SKRIPSI DILL KERJAIN\Proyek 2")

from src.preprocessing.quran_loader import QuranDataLoader
from src.acquisition.entity_acquisition_manager import EntityAcquisitionManager

loader = QuranDataLoader()
manager = EntityAcquisitionManager()

def evaluate_surah(surah_num: int, max_ayah: int = None):
    print(f"\n{'='*75}")
    print(f"HASIL EKSTRAKSI PEROLEHAN ENTITAS (TAHAP 2 & 2.5) - SURAH {surah_num}")
    print(f"{'='*75}")
    
    total_entities = 0
    channel_counts = collections.Counter()
    class_counts = collections.Counter()
    
    # Check how many ayahs exist in this surah
    surah_data = loader.get_indonesian_translation(surah_num, 1)
    if not surah_data:
        print(f"Surah {surah_num} data not found.")
        return

    # Count total ayahs
    import json
    surah_file = os.path.join(loader.TRANS_DIR if hasattr(loader, 'TRANS_DIR') else r"d:\SKRIPSI DILL KERJAIN\Proyek 2\Teks Terjemahan\surah", f"{surah_num}.json")
    with open(surah_file, encoding="utf-8") as f:
        all_ayahs = json.load(f)
        
    num_ayahs = len(all_ayahs) if max_ayah is None else min(len(all_ayahs), max_ayah)
    print(f"Memproses {num_ayahs} ayat dari total {len(all_ayahs)} ayat...")

    sample_results = []

    for a_obj in all_ayahs[:num_ayahs]:
        a = a_obj["ayah"]
        qac_tokens = loader.get_qac_tokens(surah_num, a)
        trans_data = loader.get_indonesian_translation(surah_num, a)
        if not trans_data:
            continue
            
        cands = manager.acquire_entities(surah_num, a, qac_tokens, trans_data)
        total_entities += len(cands)
        
        for c in cands:
            ch = c.get("channel")
            if isinstance(ch, list):
                ch_key = "+".join(ch)
            else:
                ch_key = ch
            channel_counts[ch_key] += 1
            class_counts[c.get("class")] += 1
            
        if len(cands) > 0 and len(sample_results) < 12:
            sample_results.append((a, trans_data["cleaned_translation"], cands))

    print(f"\n📊 STATISTIK HASIL:")
    print(f"   • Total Ayat Diproses  : {num_ayahs}")
    print(f"   • Total Entitas Didapat: {total_entities}")
    print(f"   • Rata-rata Entitas/Ayat: {total_entities / num_ayahs:.2f}")

    print(f"\n📈 KONTRIBUSI PER JALUR:")
    for ch, count in channel_counts.most_common():
        pct = (count / total_entities) * 100 if total_entities else 0
        print(f"   • {ch:32s}: {count:4d} entitas ({pct:5.1f}%)")

    print(f"\n🏷️ DISTRIBUSI KELAS ENTITAS:")
    for cls, count in class_counts.most_common():
        pct = (count / total_entities) * 100 if total_entities else 0
        print(f"   • {cls:24s}: {count:4d} entitas ({pct:5.1f}%)")

    print(f"\n🔍 CONTOH CUPLIKAN DETEKSI NYATA (BEBERAPA AYAT):")
    for a, text, cands in sample_results[:8]:
        print(f"\n[QS. {surah_num}:{a}] \"{text[:80]}...\"")
        for c in cands:
            print(f"   --> [{c['start']:3d}:{c['end']:3d}] '{c['text']}' -> {c['class']:18s} ({c['channel']})")

# Run on Surah 1 (Full 7 ayat) and Surah 2 (first 50 ayat)
evaluate_surah(1)
evaluate_surah(2, max_ayah=50)

