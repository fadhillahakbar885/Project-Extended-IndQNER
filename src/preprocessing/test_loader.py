import sys
sys.path.append(r"d:\SKRIPSI DILL KERJAIN\Proyek 2")
from src.preprocessing.quran_loader import QuranDataLoader

loader = QuranDataLoader()
qac_2_136 = loader.get_qac_tokens(2, 136)
print(f"Ayah 2:136 QAC segments: {len(qac_2_136)}")
pn_segs = [x for x in qac_2_136 if x['tag'] == 'PN']
print(f"Ayah 2:136 PN segments: {len(pn_segs)}")
for p in pn_segs:
    print(f"   {p['location']}: {p['form']} (LEM:{p['lemma']})")

trans_2_136 = loader.get_indonesian_translation(2, 136)
print(f"Ayah 2:136 Cleaned Trans: {trans_2_136['cleaned_translation'][:80]}...")
print(f"Tokens count: {len(trans_2_136['tokens'])}")
print("Sample first 5 tokens:", trans_2_136['tokens'][:5])

