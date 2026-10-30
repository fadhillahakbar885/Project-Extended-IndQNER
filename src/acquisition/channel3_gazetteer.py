import json, os, re
from typing import List, Dict, Any
from src.utils.text_utils import clean_token_for_matching, normalize_text

BASE = r"d:\SKRIPSI DILL KERJAIN\Proyek 2"
GAZ_FILE = os.path.join(BASE, "data", "dictionaries", "seed_gazetteer.json")

class Channel3GazetteerExtractor:
    def __init__(self):
        with open(GAZ_FILE, encoding="utf-8") as f:
            # Sorted longest first
            self.gazetteer: Dict[str, str] = json.load(f)

    def extract(self, surah: int, ayah: int, target_text: str, target_tokens: List[dict]) -> List[dict]:
        """
        Extracts multi-word expressions using Greedy Longest Match First.
        """
        candidates = []
        if not target_text or not target_tokens:
            return candidates

        norm_text = normalize_text(target_text)
        occupied_spans = []

        # Iterate through gazetteer entries (ordered by length descending)
        for phrase, cls in self.gazetteer.items():
            norm_phrase = normalize_text(phrase)
            
            # Construct case-insensitive boundary-aware regex pattern
            # Escape regex special characters in phrase
            escaped_p = re.escape(norm_phrase)
            pattern = re.compile(rf"\b{escaped_p}\b", re.IGNORECASE)

            for match in pattern.finditer(norm_text):
                start = match.start()
                end = match.end()
                matched_str = target_text[start:end]

                # Check if this span overlaps with an already locked longer span
                overlap = any(
                    not (end <= occ[0] or start >= occ[1])
                    for occ in occupied_spans
                )
                if not overlap:
                    occupied_spans.append((start, end))
                    candidates.append({
                        "text": matched_str,
                        "start": start,
                        "end": end,
                        "class": cls,
                        "channel": "Jalur_3_Seed_Gazetteer",
                        "matched_phrase": phrase
                    })

        candidates.sort(key=lambda x: x["start"])
        return candidates

