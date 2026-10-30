import os, json
from typing import List, Dict, Any
from src.acquisition.channel1_pn import Channel1PNExtractor
from src.acquisition.channel2_concept import Channel2ConceptExtractor
from src.acquisition.channel3_gazetteer import Channel3GazetteerExtractor
from src.acquisition.channel4_regex import Channel4RegexExtractor

class EntityAcquisitionManager:
    def __init__(self):
        print("Initializing 4-Channel Acquisition Manager...")
        self.ch1 = Channel1PNExtractor()
        self.ch2 = Channel2ConceptExtractor()
        self.ch3 = Channel3GazetteerExtractor()
        self.ch4 = Channel4RegexExtractor()
        print("✅ All 4 channels initialized successfully.")

    def resolve_conflicts(self, raw_candidates: List[dict], target_text: str) -> List[dict]:
        """
        Tahap 2.5: Resolusi Konflik Span & Deduplikasi
        1. Longest Match Priority (Greedy selection for overlapping spans).
        2. Boundary Trimming.
        3. Merge metadata on exact duplicates.
        """
        if not raw_candidates:
            return []

        # Sort by span length descending (longest first), then by start position
        sorted_cands = sorted(
            raw_candidates,
            key=lambda c: (-(c["end"] - c["start"]), c["start"])
        )

        resolved = []
        occupied_spans = []

        for cand in sorted_cands:
            c_start = cand["start"]
            c_end = cand["end"]

            # Trim trailing/leading punctuation if inadvertently included
            clean_text = target_text[c_start:c_end].strip(".,;:!?\"'()«»“”")
            if clean_text:
                c_start = target_text.find(clean_text, c_start)
                c_end = c_start + len(clean_text)
                cand["start"] = c_start
                cand["end"] = c_end
                cand["text"] = clean_text

            # Check overlap with already accepted spans
            overlap_idx = None
            for idx, (occ_start, occ_end) in enumerate(occupied_spans):
                # Overlap condition
                if not (c_end <= occ_start or c_start >= occ_end):
                    overlap_idx = idx
                    break

            if overlap_idx is None:
                # No overlap: accept candidate
                occupied_spans.append((c_start, c_end))
                resolved.append(cand)
            else:
                # Overlap detected: If it's an exact match, merge channel metadata
                existing = resolved[overlap_idx]
                if existing["start"] == c_start and existing["end"] == c_end:
                    if isinstance(existing.get("channel"), list):
                        existing["channel"].append(cand.get("channel"))
                    else:
                        existing["channel"] = [existing.get("channel"), cand.get("channel")]
                # Otherwise, shorter candidate is discarded by longest-match priority

        # Sort resolved candidates by appearance order in sentence
        resolved.sort(key=lambda c: c["start"])
        return resolved

    def acquire_entities(self, surah: int, ayah: int, qac_tokens: List[dict], translation_data: dict) -> List[dict]:
        """
        Executes all 4 channels on verse (surah, ayah) and resolves conflicts.
        """
        cleaned_text = translation_data.get("cleaned_translation", "")
        tokens = translation_data.get("tokens", [])

        # Run 4 channels
        c1 = self.ch1.extract(surah, ayah, qac_tokens, tokens)
        c2 = self.ch2.extract(surah, ayah, qac_tokens, tokens)
        c3 = self.ch3.extract(surah, ayah, cleaned_text, tokens)
        c4 = self.ch4.extract(surah, ayah, cleaned_text)

        all_raw = c1 + c2 + c3 + c4
        final_entities = self.resolve_conflicts(all_raw, cleaned_text)
        return final_entities

    def save_audit_logs(self):
        """Saves all channel audit logs."""
        self.ch1.save_audit_log()

