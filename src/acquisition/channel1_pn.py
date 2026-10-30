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
PN_LEXICON_FILE = os.path.join(BASE, "data", "dictionaries", "qac_pn_pivot_lexicon.json")

class Channel1PNExtractor:
    def __init__(self):
        with open(PN_LEXICON_FILE, encoding="utf-8") as f:
            self.lexicon: Dict[str, dict] = json.load(f)
        self.unmatched_audit: List[dict] = []

    def is_match(self, alias: str, candidate_text: str) -> Tuple[bool, float]:
        """
        Guardrail 4: Adaptive Length Threshold & Strict Short Name Guard
        - Filter out general Indonesian function words (COMMON_WORDS_BLACKLIST)
        - If |alias| <= 4: STRICT EXACT MATCH or apostrophe variant only (e.g., 'Isa vs Isa)
        - If |alias| > 4:  Similarity >= 0.85
        """
        clean_cand = clean_token_for_matching(candidate_text).lower()
        alias_clean = normalize_text(alias).lower()
        
        # Stopword blacklist guard: never allow generic Indonesian words as proper nouns
        if clean_cand in COMMON_WORDS_BLACKLIST and clean_cand != alias_clean:
            return False, 0.0

        if len(alias_clean) <= 4:
            if clean_cand == alias_clean:
                return True, 1.0
            # Allow pure apostrophe variations (e.g., 'Isa vs Isa)
            if clean_cand.replace("'", "") == alias_clean.replace("'", ""):
                return True, 0.95
            return False, 0.0
        else:
            sim = string_similarity(alias_clean, clean_cand)
            valid = (sim >= 0.85)
            return valid, sim

    def extract(self, surah: int, ayah: int, qac_tokens: List[dict], target_tokens: List[dict]) -> List[dict]:
        """
        Extracts candidate entities using Jalur 1 (QAC Proper Noun + 5 Guardrails).
        """
        candidates = []
        
        # 1. Filter QAC tokens with TAG == 'PN' and active in lexicon
        pn_qac = []
        for q in qac_tokens:
            if q.get("tag") == "PN":
                lem = q.get("lemma")
                lex_entry = self.lexicon.get(lem)
                if lex_entry and lex_entry.get("class") != "EXCLUDED_O":
                    pn_qac.append((q, lex_entry))

        if not pn_qac or not target_tokens:
            return candidates

        # Group by lemma to implement Guardrail 1: Sequential Index Alignment
        lemma_occurrences: Dict[str, List[Tuple[dict, dict]]] = {}
        for q, lex in pn_qac:
            lem = q.get("lemma")
            if lem not in lemma_occurrences:
                lemma_occurrences[lem] = []
            lemma_occurrences[lem].append((q, lex))

        # 2. For each unique lemma, search target tokens
        for lem, qac_list in lemma_occurrences.items():
            first_q, lex = qac_list[0]
            aliases = lex.get("aliases", [])
            target_cls = lex.get("class")
            english_pivot = lex.get("english_pivot")

            # Check max word length in aliases for Guardrail 3: Sliding Window N-gram
            max_alias_words = max(len(a.split()) for a in aliases) if aliases else 1
            
            # Find all matched spans in the Indonesian target text
            matched_spans = []
            
            for N in range(max_alias_words, 0, -1):
                i = 0
                while i <= len(target_tokens) - N:
                    window_toks = target_tokens[i : i + N]
                    window_text = " ".join(t["text"] for t in window_toks)
                    
                    best_match = False
                    best_sim = 0.0
                    best_alias = ""
                    
                    for alias in aliases:
                        if len(alias.split()) == N:
                            valid, sim = self.is_match(alias, window_text)
                            if valid and sim > best_sim:
                                best_sim = sim
                                best_match = True
                                best_alias = alias
                                
                    if best_match:
                        span_start = window_toks[0]["start"]
                        span_end = window_toks[-1]["end"]
                        # Check overlap with already matched spans
                        overlap = any(
                            not (span_end <= s["start"] or span_start >= s["end"])
                            for s in matched_spans
                        )
                        if not overlap:
                            matched_spans.append({
                                "text": window_text,
                                "start": span_start,
                                "end": span_end,
                                "sim": best_sim,
                                "matched_alias": best_alias,
                                "token_indices": list(range(i, i + N))
                            })
                            i += N  # Advance window past match
                            continue
                    i += 1

            # Sort matched spans by sentence appearance order
            matched_spans.sort(key=lambda x: x["start"])

            # Guardrail 1: Sequential Index Alignment
            # Match k-th QAC token to k-th Indonesian span
            num_qac = len(qac_list)
            num_matched = len(matched_spans)

            for k in range(min(num_qac, num_matched)):
                q_token, _ = qac_list[k]
                span = matched_spans[k]
                candidates.append({
                    "text": span["text"],
                    "start": span["start"],
                    "end": span["end"],
                    "class": target_cls,
                    "channel": "Jalur_1_QAC_PN",
                    "source_qac_loc": q_token.get("location"),
                    "lemma": lem,
                    "english_pivot": english_pivot,
                    "matched_alias": span["matched_alias"],
                    "sim": span["sim"]
                })

            # Audit logging: Record unmatched occurrences if QAC count > matched count
            if num_qac > num_matched:
                for k in range(num_matched, num_qac):
                    unmatched_q, _ = qac_list[k]
                    self.unmatched_audit.append({
                        "surah": surah,
                        "ayah": ayah,
                        "location": unmatched_q.get("location"),
                        "lemma": lem,
                        "english_pivot": english_pivot,
                        "aliases": aliases,
                        "reason": f"Occurrence {k+1} of {num_qac} not found in Indonesian text."
                    })

        # Sort candidates by character start offset
        candidates.sort(key=lambda x: x["start"])
        return candidates

    def save_audit_log(self, filepath: str = None):
        """Saves unmatched PN audit log to logs/audit/."""
        if filepath is None:
            filepath = os.path.join(BASE, "logs", "audit", "unmatched_qac_pn.json")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.unmatched_audit, f, ensure_ascii=False, indent=2)
        print(f"📝 Saved Jalur 1 audit log: {filepath} ({len(self.unmatched_audit)} records)")
