import os, json, re
from typing import Dict, List, Tuple
from src.utils.text_utils import clean_footnotes, tokenize_with_offsets

BASE = r"d:\SKRIPSI DILL KERJAIN\Proyek 2"
QAC_FILE = os.path.join(BASE, "QAC", "quranic-corpus-morphology-0.4", "quranic-corpus-morphology-0.4.txt")
TRANS_DIR = os.path.join(BASE, "Teks Terjemahan", "surah")

class QuranDataLoader:
    def __init__(self):
        self.qac_data: Dict[Tuple[int, int], List[dict]] = {}
        self._load_qac()

    def _load_qac(self):
        """Loads and indexes QAC morphology treebank per (surah, ayah)."""
        print("Loading QAC morphology database...")
        with open(QAC_FILE, encoding="utf-8") as f:
            for line in f:
                if not line.startswith("("):
                    continue
                loc, form, tag, feat = line.rstrip("\n").split("\t")
                s, a, w, seg = map(int, loc.strip("()").split(":"))
                
                # Extract lemma and root
                lem_m = re.search(r"LEM:([^|]+)", feat)
                root_m = re.search(r"ROOT:([^|]+)", feat)
                lemma = lem_m.group(1) if lem_m else form
                root = root_m.group(1) if root_m else ""

                entry = {
                    "location": f"{s}:{a}:{w}:{seg}",
                    "surah": s,
                    "ayah": a,
                    "word_pos": w,
                    "segment": seg,
                    "form": form,
                    "tag": tag,
                    "lemma": lemma,
                    "root": root,
                    "features": feat
                }
                key = (s, a)
                if key not in self.qac_data:
                    self.qac_data[key] = []
                self.qac_data[key].append(entry)
        print(f"✅ Loaded QAC: {len(self.qac_data)} verses indexed.")

    def get_qac_tokens(self, surah: int, ayah: int) -> List[dict]:
        """Returns all QAC segments for a given verse."""
        return self.qac_data.get((surah, ayah), [])

    def get_indonesian_translation(self, surah: int, ayah: int) -> dict:
        """
        Loads Indonesian translation for a given verse from JSON file,
        cleans footnotes, and performs tokenization with offsets.
        """
        surah_file = os.path.join(TRANS_DIR, f"{surah}.json")
        if not os.path.exists(surah_file):
            return None
        
        with open(surah_file, encoding="utf-8") as f:
            data = json.load(f)
            
        for a_obj in data:
            if a_obj.get("ayah") == ayah:
                raw_trans = a_obj.get("translation", "")
                cleaned_trans = clean_footnotes(raw_trans)
                tokens = tokenize_with_offsets(cleaned_trans)
                return {
                    "surah": surah,
                    "ayah": ayah,
                    "raw_translation": raw_trans,
                    "cleaned_translation": cleaned_trans,
                    "tokens": tokens
                }
        return None

