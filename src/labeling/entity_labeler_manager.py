import os, json
from typing import List, Dict, Tuple
from src.labeling.kamus_indqner import KamusIndQNER
from src.labeling.llm_labeler import LLMAsLabeler
from src.labeling.conll_formatter import CoNLLFormatter

class EntityLabelerManager:
    """
    Manajer Pelabelan Bertingkat (Tahap 3):
    - Lapis 1: Kamus IndQNER (Deterministik)
    - Lapis 2: LLM-as-Labeler (Zero-Shot / Few-Shot)
    - CoNLL BIO Formatting
    """
    def __init__(self, llm_mode: str = "few_shot"):
        print("Menginisialisasi Manajer Pelabelan Bertingkat (Tahap 3)...")
        self.kamus = KamusIndQNER()
        self.llm = LLMAsLabeler(mode=llm_mode)
        self.formatter = CoNLLFormatter()
        print("✅ Manajer Pelabelan Bertingkat siap.")

    def label_entities(self, sentence: str, candidates: List[dict]) -> List[dict]:
        """
        Melabeli setiap entitas kandidat melalui arsitektur keputusan dua lapis.
        """
        labeled_entities = []
        
        for cand in candidates:
            text = cand["text"]
            default_cls = cand.get("class")
            
            # Lapis 1: Cek Kamus IndQNER (Deterministik)
            dict_class = self.kamus.lookup(text)
            
            if dict_class:
                cand_copy = dict(cand)
                cand_copy["class"] = dict_class
                cand_copy["labeled_by"] = "Lapis_1_Kamus_Deterministik"
                labeled_entities.append(cand_copy)
            else:
                # Lapis 2: Delegasikan ke LLM-as-Labeler
                llm_class = self.llm.classify(sentence, text, default_class=default_cls)
                cand_copy = dict(cand)
                cand_copy["class"] = llm_class
                cand_copy["labeled_by"] = "Lapis_2_LLM_as_Labeler"
                labeled_entities.append(cand_copy)
                
        return labeled_entities

    def process_verse_to_conll(self, translation_data: dict, candidates: List[dict]) -> List[Tuple[str, str]]:
        """
        Menjalankan pelabelan bertingkat dan mengonversi ayat ke format BIO (word, tag).
        """
        sentence = translation_data.get("cleaned_translation", "")
        tokens = translation_data.get("tokens", [])
        
        # 1. Label entities
        final_labeled_entities = self.label_entities(sentence, candidates)
        
        # 2. Format to CoNLL BIO
        tagged_tokens = self.formatter.format_verse(tokens, final_labeled_entities)
        return tagged_tokens

    def save_audit_logs(self):
        """Saves LLM audit logs."""
        self.llm.save_audit_log()

