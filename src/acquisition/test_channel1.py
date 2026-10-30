import sys
sys.path.append(r"d:\SKRIPSI DILL KERJAIN\Proyek 2")

from src.preprocessing.quran_loader import QuranDataLoader
from src.acquisition.channel1_pn import Channel1PNExtractor

loader = QuranDataLoader()
extractor = Channel1PNExtractor()

print("\n--- Test Ayat 2:136 ---")
qac_136 = loader.get_qac_tokens(2, 136)
trans_136 = loader.get_indonesian_translation(2, 136)
cands_136 = extractor.extract(2, 136, qac_136, trans_136["tokens"])
print(f"Jalur 1 found {len(cands_136)} entities:")
for c in cands_136:
    print(f"   [{c['start']}:{c['end']}] '{c['text']}' -> {c['class']} (QAC: {c['source_qac_loc']} {c['lemma']} -> '{c['english_pivot']}')")

print("\n--- Test Ayat 2:20 (Multiple Allah occurrences) ---")
qac_20 = loader.get_qac_tokens(2, 20)
trans_20 = loader.get_indonesian_translation(2, 20)
cands_20 = extractor.extract(2, 20, qac_20, trans_20["tokens"])
print(f"Jalur 1 found {len(cands_20)} entities in 2:20:")
for c in cands_20:
    print(f"   [{c['start']}:{c['end']}] '{c['text']}' -> {c['class']} (QAC: {c['source_qac_loc']})")

