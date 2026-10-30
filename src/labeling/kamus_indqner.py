import json, os, re
from typing import Dict, Optional, Tuple
from src.utils.text_utils import normalize_text, clean_token_for_matching

BASE = r"d:\SKRIPSI DILL KERJAIN\Proyek 2"
PN_LEX_FILE = os.path.join(BASE, "data", "dictionaries", "qac_pn_pivot_lexicon.json")
CONCEPT_FILE = os.path.join(BASE, "data", "dictionaries", "qac_concept_whitelist.json")
GAZ_FILE = os.path.join(BASE, "data", "dictionaries", "seed_gazetteer.json")
TRAIN_FILE = os.path.join(BASE, "indqner_1.0", "train.txt")

class KamusIndQNER:
    """
    Lapis 1 Pelabelan Deterministik:
    Kamus rujukan lengkap yang dibangun dari data latih IndQNER 1.0 (train.txt),
    Pedoman Pelabelan Entitas (Tabel 1 Leeds), dan Kamus Pivot QAC.
    """
    def __init__(self):
        self.dictionary: Dict[str, str] = {}
        self._build_dictionary()

    def _add_entry(self, text: str, cls: str):
        if not text or not cls or cls == "EXCLUDED_O":
            return
        # Store normalized lower-case
        norm_key = normalize_text(text).lower()
        if norm_key and norm_key not in self.dictionary:
            self.dictionary[norm_key] = cls

    def _build_dictionary(self):
        print("Membangun Kamus IndQNER (Lapis 1 Deterministik)...")

        # 1. Load from train.txt (Gold Standard entities from training set)
        if os.path.exists(TRAIN_FILE):
            cur_tokens = []
            cur_class = None
            with open(TRAIN_FILE, encoding="utf-8") as f:
                for line in f:
                    line = line.rstrip("\n")
                    if not line.strip():
                        if cur_tokens:
                            self._add_entry(" ".join(cur_tokens), cur_class)
                        cur_tokens = []
                        cur_class = None
                        continue
                    parts = line.split("\t")
                    tok = parts[0]
                    tag = parts[1] if len(parts) > 1 else "O"
                    if tag.startswith("B-"):
                        if cur_tokens:
                            self._add_entry(" ".join(cur_tokens), cur_class)
                        cur_tokens = [tok]
                        cur_class = tag[2:]
                    elif tag.startswith("I-") and cur_tokens and tag[2:] == cur_class:
                        cur_tokens.append(tok)
                    else:
                        if cur_tokens:
                            self._add_entry(" ".join(cur_tokens), cur_class)
                        cur_tokens = []
                        cur_class = None
                if cur_tokens:
                    self._add_entry(" ".join(cur_tokens), cur_class)

        # 2. Load from Seed Gazetteer (multi-word expressions & Asmaul Husna)
        if os.path.exists(GAZ_FILE):
            with open(GAZ_FILE, encoding="utf-8") as f:
                gaz = json.load(f)
                for k, v in gaz.items():
                    self._add_entry(k, v)

        # 3. Load from QAC PN Lexicon aliases
        if os.path.exists(PN_LEX_FILE):
            with open(PN_LEX_FILE, encoding="utf-8") as f:
                pn_lex = json.load(f)
                for lem, spec in pn_lex.items():
                    cls = spec.get("class")
                    if cls and cls != "EXCLUDED_O":
                        for alias in spec.get("aliases", []):
                            self._add_entry(alias, cls)

        # 4. Load from QAC Concept Whitelist
        if os.path.exists(CONCEPT_FILE):
            with open(CONCEPT_FILE, encoding="utf-8") as f:
                concept_lex = json.load(f)
                for lem, spec in concept_lex.items():
                    cls = spec.get("class")
                    if cls:
                        for alias in spec.get("aliases", []):
                            self._add_entry(alias, cls)

        # Save compiled dictionary to data/dictionaries/kamus_indqner_compiled.json
        compiled_path = os.path.join(BASE, "data", "dictionaries", "kamus_indqner_compiled.json")
        with open(compiled_path, "w", encoding="utf-8") as f:
            json.dump(self.dictionary, f, ensure_ascii=False, indent=2)

        print(f"✅ Kamus IndQNER tersusun: {len(self.dictionary)} entri entitas terverifikasi.")

    def lookup(self, entity_text: str) -> Optional[str]:
        """
        Mencari label kelas suatu entitas secara deterministik.
        Returns:
            class_name jika ditemukan, None jika tidak ada di kamus.
        """
        if not entity_text:
            return None
        
        # Exact match (normalized)
        norm_key = normalize_text(entity_text).lower()
        if norm_key in self.dictionary:
            return self.dictionary[norm_key]
            
        # Cleaned match (without enclitics and outer punctuation)
        clean_key = clean_token_for_matching(entity_text).lower()
        if clean_key in self.dictionary:
            return self.dictionary[clean_key]

        return None
