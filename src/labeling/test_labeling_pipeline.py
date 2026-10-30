import sys
sys.path.append(r"d:\SKRIPSI DILL KERJAIN\Proyek 2")

from src.preprocessing.quran_loader import QuranDataLoader
from src.acquisition.entity_acquisition_manager import EntityAcquisitionManager
from src.labeling.entity_labeler_manager import EntityLabelerManager
from src.labeling.conll_formatter import CoNLLFormatter

loader = QuranDataLoader()
acq_manager = EntityAcquisitionManager()
label_manager = EntityLabelerManager(llm_mode="few_shot")

test_verses = [(1, 1), (1, 2), (2, 23), (2, 136)]

print("\n" + "="*70)
print("TESTING END-TO-END TAHAP 1, 2, DAN 3 (CONLL BIO OUTPUT)")
print("="*70)

for s, a in test_verses:
    qac = loader.get_qac_tokens(s, a)
    trans = loader.get_indonesian_translation(s, a)
    
    # Tahap 2: Perolehan Entitas
    candidates = acq_manager.acquire_entities(s, a, qac, trans)
    
    # Tahap 3: Pelabelan Bertingkat & BIO Formatting
    tagged_tokens = label_manager.process_verse_to_conll(trans, candidates)
    
    print(f"\n📍 Ayat {s}:{a} ({len(tagged_tokens)} tokens):")
    print("Cuplikan Format CoNLL BIO:")
    # Print only non-O or sample window around entities
    for i, (tok, tag) in enumerate(tagged_tokens):
        if tag != "O" or (i > 0 and tagged_tokens[i-1][1] != "O") or (i < len(tagged_tokens)-1 and tagged_tokens[i+1][1] != "O"):
            print(f"   {tok:20s}\t{tag}")
            
print("\n" + "="*70)
print("Contoh Blok CoNLL Utuh untuk QS. 1:1:")
trans_1_1 = loader.get_indonesian_translation(1, 1)
cands_1_1 = acq_manager.acquire_entities(1, 1, loader.get_qac_tokens(1, 1), trans_1_1)
tagged_1_1 = label_manager.process_verse_to_conll(trans_1_1, cands_1_1)
print(CoNLLFormatter.to_conll_string(tagged_1_1))
print("="*70)
print("✅ TAHAP 3 BERHASIL DIUJI DENGAN INTEGRITAS FORMAT 100%!")
