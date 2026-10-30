import json, os, re
from typing import List, Dict, Any
from src.utils.text_utils import clean_token_for_matching, normalize_text

BASE = r"d:\SKRIPSI DILL KERJAIN\Proyek 2"
PN_LEX_FILE = os.path.join(BASE, "data", "dictionaries", "qac_pn_pivot_lexicon.json")
GAZ_FILE = os.path.join(BASE, "data", "dictionaries", "seed_gazetteer.json")

TITLE_PREFIXES = ["Nabi", "Rasul", "Raja", "Malaikat", "kitab", "Kitab", "kaum", "Kaum", "negeri", "Negeri", "bukit", "Bukit"]

class Channel4RegexExtractor:
    def __init__(self):
        # Load known entity references for verification
        self.known_entities: Dict[str, str] = {}
        
        # Load gazetteer
        with open(GAZ_FILE, encoding="utf-8") as f:
            gaz = json.load(f)
            for k, v in gaz.items():
                self.known_entities[normalize_text(k).lower()] = v

        # Load PN lexicon aliases
        with open(PN_LEX_FILE, encoding="utf-8") as f:
            pn_lex = json.load(f)
            for lem, spec in pn_lex.items():
                cls = spec.get("class")
                if cls and cls != "EXCLUDED_O":
                    for a in spec.get("aliases", []):
                        self.known_entities[normalize_text(a).lower()] = cls

    def extract(self, surah: int, ayah: int, target_text: str) -> List[dict]:
        """
        Extracts entities appearing inside parentheses, applying Rule 5b (Title Stripping).
        """
        candidates = []
        if not target_text:
            return candidates

        # Find all parentheses in target text
        paren_pattern = re.compile(r'\(([^()]+)\)')
        for match in paren_pattern.finditer(target_text):
            inside_raw = match.group(1).strip()
            inside_start = match.start(1)
            inside_end = match.end(1)

            # Apply Rule 5b: Strip titles if present
            # e.g., "Nabi Muhammad" -> title="Nabi", entity="Muhammad"
            detected_entity = inside_raw
            entity_start = inside_start
            entity_end = inside_end

            words = inside_raw.split()
            if len(words) >= 2 and words[0] in TITLE_PREFIXES:
                title_len = len(words[0])
                # Skip title and following whitespace
                sub_match = re.search(r'\S', inside_raw[title_len:])
                if sub_match:
                    offset = title_len + sub_match.start()
                    detected_entity = inside_raw[offset:].strip()
                    entity_start = inside_start + offset
                    entity_end = entity_start + len(detected_entity)

            # Verification: Check if detected_entity matches a known entity
            norm_cand = normalize_text(detected_entity).lower()
            matched_cls = self.known_entities.get(norm_cand)

            if matched_cls:
                candidates.append({
                    "text": detected_entity,
                    "start": entity_start,
                    "end": entity_end,
                    "class": matched_cls,
                    "channel": "Jalur_4_RegEx_Selingkung",
                    "raw_parentheses": match.group(0),
                    "rule_5b_applied": (detected_entity != inside_raw)
                })

        candidates.sort(key=lambda x: x["start"])
        return candidates

