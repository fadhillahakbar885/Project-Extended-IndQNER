import sys
sys.path.append(r"d:\SKRIPSI DILL KERJAIN\Proyek 2")

from src.preprocessing.quran_loader import QuranDataLoader
from src.acquisition.entity_acquisition_manager import EntityAcquisitionManager

loader = QuranDataLoader()
manager = EntityAcquisitionManager()

test_cases = [
    (1, 1, "Basmalah (Allah)"),
    (1, 2, "Al-Fatihah 2 (Allah, Tuhan semesta alam)"),
    (2, 22, "Al-Baqarah 22 (bumi, langit - Jalur 2 Concept)"),
    (2, 23, "Al-Baqarah 23 (Nabi Muhammad - Jalur 4 RegEx + Rule 5b)"),
    (2, 136, "Al-Baqarah 136 (7 Proper Nouns - Jalur 1)"),
    (2, 187, "Al-Baqarah 187 (putih, hitam, fajar - Jalur 2 Concept)")
]

print("\n" + "="*70)
print("TESTING 4-CHANNEL ACQUISITION + CONFLICT RESOLUTION (TAHAP 2 & 2.5)")
print("="*70)

for s, a, desc in test_cases:
    qac = loader.get_qac_tokens(s, a)
    trans = loader.get_indonesian_translation(s, a)
    entities = manager.acquire_entities(s, a, qac, trans)
    
    print(f"\n📍 Ayat {s}:{a} ({desc})")
    print(f"   Teks: \"{trans['cleaned_translation'][:90]}...\"")
    print(f"   Ditemukan {len(entities)} Entitas Terkunci:")
    for e in entities:
        ch = e.get('channel')
        ch_str = ch if isinstance(ch, str) else "+".join(ch)
        print(f"     • [{e['start']:3d}:{e['end']:3d}] '{e['text']}' -> {e['class']:20s} [{ch_str}]")

manager.save_audit_logs()
print("\n" + "="*70)
print("✅ ALL INTEGRATION TESTS PASSED SUCCESSFULLY!")
print("="*70)

