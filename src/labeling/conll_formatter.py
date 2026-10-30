from typing import List, Dict, Tuple

class CoNLLFormatter:
    """
    Format standard industri CoNLL BIO (word \\t tag).
    Menjamin 'Strict Zero Deletion & Zero Corruption Guarantee'
    sesuai standar IndQNER 1.0.
    """

    @staticmethod
    def format_verse(tokens: List[dict], entities: List[dict]) -> List[Tuple[str, str]]:
        """
        Memetakan rentang entitas (start, end) ke tag BIO per-token.
        Args:
            tokens: List of dict {'text': str, 'start': int, 'end': int}
            entities: List of dict {'text': str, 'start': int, 'end': int, 'class': str}
        Returns:
            List of tuple (token_text, bio_tag)
        """
        tagged_tokens = []
        
        # Sort entities by start offset
        sorted_ents = sorted(entities, key=lambda x: x["start"])
        
        for tok in tokens:
            t_start = tok["start"]
            t_end = tok["end"]
            t_text = tok["text"]
            
            # Check if token falls inside any entity span
            assigned_tag = "O"
            for ent in sorted_ents:
                e_start = ent["start"]
                e_end = ent["end"]
                e_cls = ent["class"]
                
                # Overlap condition: token intersects entity span
                if not (t_end <= e_start or t_start >= e_end):
                    # If this token is the first token of the entity span -> B-Class
                    # Otherwise -> I-Class
                    if t_start == e_start or (t_start > e_start and (not tagged_tokens or not tagged_tokens[-1][1].endswith(e_cls))):
                        assigned_tag = f"B-{e_cls}"
                    else:
                        assigned_tag = f"I-{e_cls}"
                    break
                    
            tagged_tokens.append((t_text, assigned_tag))
            
        return tagged_tokens

    @staticmethod
    def to_conll_string(tagged_tokens: List[Tuple[str, str]]) -> str:
        """Converts list of (token, tag) to CoNLL formatted text block."""
        lines = [f"{tok}\t{tag}" for tok, tag in tagged_tokens]
        return "\n".join(lines)

    @staticmethod
    def write_conll_file(verses_data: List[List[Tuple[str, str]]], filepath: str):
        """
        Writes full dataset to CoNLL file where each verse is separated
        by exactly one blank line (\n).
        """
        with open(filepath, "w", encoding="utf-8") as f:
            for i, v in enumerate(verses_data):
                f.write(CoNLLFormatter.to_conll_string(v))
                if i < len(verses_data) - 1:
                    f.write("\n\n")
                else:
                    f.write("\n")
        print(f"💾 File CoNLL berhasil disimpan: {filepath} ({len(verses_data)} ayat)")
