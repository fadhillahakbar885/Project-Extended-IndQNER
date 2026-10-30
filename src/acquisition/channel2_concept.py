import json, os, re
from typing import List, Dict, Any, Tuple
from src.utils.text_utils import (
    clean_token_for_matching,
    levenshtein_distance,
    string_similarity,
    normalize_text,
    COMMON_WORDS_BLACKLIST
)

BASE = r"d:\SKRIPSI DILL KERJAIN\Proyek 2"
CONCEPT_FILE = os.path.join(BASE, "data", "dictionaries", "qac_concept_whitelist.json")

class Channel2ConceptExtractor:
    def __init__(self):
        with open(CONCEPT_FILE, encoding="utf-8") as f:
            self.whitelist: Dict[str, dict] = json.load(f)

    def is_match(self, alias: str, candidate_text: str) -> Tuple[bool, float]:
        """
        Adaptive matching for concept lemmas:
        - Stopword blacklist guard: never allow generic words (e.g. 'hari' for 'haji')
        - If |alias| <= 4: STRICT EXACT MATCH or apostrophe variant only
        - If |alias| > 4:  Similarity >= 0.85
        """
        clean_cand = clean_token_for_matching(candidate_text).lower()
        alias_clean = normalize_text(alias).lower()
        
        # Stopword blacklist guard
        if clean_cand in COMMON_WORDS_BLACKLIST and clean_cand != alias_clean:
            return False, 0.0

        if len(alias_clean) <= 4:
            if clean_cand == alias_clean:
                return True, 1.0
            if clean_cand.replace("'", "") == alias_clean.replace("'", ""):
                return True, 0.95
            return False, 0.0
        else:
            sim = string_similarity(alias_clean, clean_cand)
            valid = (sim >= 0.85)
            return valid, sim

    def extract(self, surah: int, ayah: int, qac_tokens: List[dict], target_tokens: List[dict]) -> List[dict]:
        """
        Extracts candidate entities using Jalur 2 (QAC Ontological Concept Lemmas).
        """
        candidates = []
        if not qac_tokens or not target_tokens:
            return candidates

        # 1. Filter QAC segments matching concept whitelist
        active_concepts = []
        for q in qac_tokens:
            tag = q.get("tag")
            lem = q.get("lemma")
            if tag in ("N", "ADJ") and lem in self.whitelist:
                spec = self.whitelist[lem]
                # Check POS match if specified
                if spec.get("pos") and spec.get("pos") != tag:
                    continue
                active_concepts.append((q, spec))

        if not active_concepts:
            return candidates

        # 2. Search matches in Indonesian target tokens
        for q, spec in active_concepts:
            lem = q.get("lemma")
            target_cls = spec.get("class")
            aliases = spec.get("aliases", [])
            expand_prefix = spec.get("expand_prefix", [])

            max_alias_words = max(len(a.split()) for a in aliases) if aliases else 1
            
            for N in range(max_alias_words, 0, -1):
                i = 0
                while i <= len(target_tokens) - N:
                    window_toks = target_tokens[i : i + N]
                    window_text = " ".join(t["text"] for t in window_toks)
                    
                    for alias in aliases:
                        if len(alias.split()) == N:
                            valid, sim = self.is_match(alias, window_text)
                            if valid:
                                span_start = window_toks[0]["start"]
                                span_end = window_toks[-1]["end"]
                                matched_text = window_text

                                # Check prefix expansion (e.g. 'hari' + 'Kiamat')
                                if expand_prefix and i > 0:
                                    prev_tok = target_tokens[i - 1]
                                    if clean_token_for_matching(prev_tok["text"]).lower() in [p.lower() for p in expand_prefix]:
                                        span_start = prev_tok["start"]
                                        matched_text = prev_tok["text"] + " " + matched_text

                                # Check duplicate/overlap
                                overlap = any(
                                    not (span_end <= c["start"] or span_start >= c["end"])
                                    for c in candidates
                                )
                                if not overlap:
                                    candidates.append({
                                        "text": matched_text,
                                        "start": span_start,
                                        "end": span_end,
                                        "class": target_cls,
                                        "channel": "Jalur_2_QAC_Concept",
                                        "source_qac_loc": q.get("location"),
                                        "lemma": lem,
                                        "sim": sim
                                    })
                                break
                    i += 1

        candidates.sort(key=lambda x: x["start"])
        return candidates
