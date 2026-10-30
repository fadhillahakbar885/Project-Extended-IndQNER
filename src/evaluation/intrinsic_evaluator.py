import os, json, sys
from typing import List, Dict, Tuple
from seqeval.metrics import classification_report, f1_score, precision_score, recall_score
from seqeval.scheme import IOB2

BASE = r"d:\SKRIPSI DILL KERJAIN\Proyek 2"
sys.path.append(BASE)

from src.preprocessing.quran_loader import QuranDataLoader
from src.acquisition.entity_acquisition_manager import EntityAcquisitionManager
from src.labeling.entity_labeler_manager import EntityLabelerManager
from src.utils.text_utils import clean_footnotes, normalize_text

SURAH_LIST = [2, 3, 4, 5, 6, 7, 10, 16]

class IntrinsicEvaluator:
    """
    Evaluator Kualitas Dataset Tingkat Entitas (Evaluasi Intrinsik):
    Menguji performa pipeline secara objektif pada Unseen Test Set
    (indqner_1.0/test.txt: 176 ayat, 6.056 token, 237 entitas)
    menggunakan metrik Strict Matching resmi CoNLL (seqeval).
    """
    def __init__(self, llm_mode: str = "few_shot"):
        print("Menginisialisasi Evaluator Intrinsik...")
        self.loader = QuranDataLoader()
        self.acq_manager = EntityAcquisitionManager()
        self.label_manager = EntityLabelerManager(llm_mode=llm_mode)
        self.test_file = os.path.join(BASE, "indqner_1.0", "test.txt")
        self.ayah_map = self._build_ayah_alignment_map()

    def _build_ayah_alignment_map(self) -> Dict[str, Tuple[int, int]]:
        """Maps verse prefixes to (surah, ayah) coordinates."""
        index = {}
        for s in SURAH_LIST:
            fpath = os.path.join(BASE, "Teks Terjemahan", "surah", f"{s}.json")
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                a = item["ayah"]
                clean_t = clean_footnotes(item["translation"])
                words = [w.strip(".,;:!?\"'()«»“”") for w in clean_t.split() if w.strip(".,;:!?\"'()«»“”")]
                prefix_key = " ".join(words[:6]).lower()
                prefix_4 = " ".join(words[:4]).lower()
                index[prefix_key] = (s, a)
                if prefix_4 not in index:
                    index[prefix_4] = (s, a)
        return index

    def _find_coordinate(self, tokens: List[str]) -> Tuple[int, int]:
        clean_words = [w.strip(".,;:!?\"'()«»“”") for w in tokens if w.strip(".,;:!?\"'()«»“”")]
        prefix_6 = " ".join(clean_words[:6]).lower()
        if prefix_6 in self.ayah_map:
            return self.ayah_map[prefix_6]
        prefix_4 = " ".join(clean_words[:4]).lower()
        if prefix_4 in self.ayah_map:
            return self.ayah_map[prefix_4]
        return (None, None)

    def run_evaluation(self, output_report_path: str = None) -> dict:
        print(f"\n{'='*75}")
        print("MEMULAI EVALUASI INTRINSIK PADA TEST SET INDQNER 1.0 (UNSEEN 176 AYAT)")
        print(f"{'='*75}")

        with open(self.test_file, encoding="utf-8") as f:
            raw_test_blocks = [v.strip() for v in f.read().split("\n\n") if v.strip()]

        gold_sequences = []
        pred_sequences = []
        detailed_records = []

        total_verses = len(raw_test_blocks)
        print(f"Memproses {total_verses} ayat uji...")

        for v_idx, block in enumerate(raw_test_blocks):
            lines = block.split("\n")
            gold_toks = [l.split("\t")[0] for l in lines]
            gold_tags = [l.split("\t")[1] if len(l.split("\t")) > 1 else "O" for l in lines]

            # Find coordinate
            s, a = self._find_coordinate(gold_toks)
            
            # Predict
            pred_tags = ["O"] * len(gold_toks)
            cands = []
            if s and a:
                qac = self.loader.get_qac_tokens(s, a)
                trans = self.loader.get_indonesian_translation(s, a)
                if trans:
                    cands = self.acq_manager.acquire_entities(s, a, qac, trans)
                    labeled_cands = self.label_manager.label_entities(trans["cleaned_translation"], cands)
                    
                    # Align predicted candidate spans directly to gold tokens
                    for ent in labeled_cands:
                        e_text = ent["text"].strip(".,;:!?\"'()«»“”")
                        e_cls = ent["class"]
                        e_words = [w.strip(".,;:!?\"'()«»“”") for w in e_text.split() if w.strip(".,;:!?\"'()«»“”")]
                        
                        # Find matching window in gold_toks
                        N = len(e_words)
                        if N == 0:
                            continue
                        for t_i in range(len(gold_toks) - N + 1):
                            window = [w.strip(".,;:!?\"'()«»“”") for w in gold_toks[t_i : t_i + N]]
                            norm_w = [x.replace("‘","'").replace("’","'").lower() for x in window]
                            norm_e = [x.replace("‘","'").replace("’","'").lower() for x in e_words]
                            if norm_w == norm_e:
                                pred_tags[t_i] = f"B-{e_cls}"
                                for k in range(1, N):
                                    pred_tags[t_i + k] = f"I-{e_cls}"
                                break

            gold_sequences.append(gold_tags)
            pred_sequences.append(pred_tags)
            
            detailed_records.append({
                "verse_index": v_idx + 1,
                "surah": s,
                "ayah": a,
                "tokens_count": len(gold_toks),
                "gold_entities_count": sum(1 for t in gold_tags if t.startswith("B-")),
                "pred_entities_count": sum(1 for t in pred_tags if t.startswith("B-")),
                "cands_found": len(cands)
            })

        # Calculate official CoNLL metrics using seqeval
        strict_f1 = f1_score(gold_sequences, pred_sequences, mode='strict', scheme=IOB2)
        strict_prec = precision_score(gold_sequences, pred_sequences, mode='strict', scheme=IOB2)
        strict_rec = recall_score(gold_sequences, pred_sequences, mode='strict', scheme=IOB2)

        report = classification_report(gold_sequences, pred_sequences, mode='strict', scheme=IOB2, digits=4)

        print("\n" + "="*75)
        print("HASIL AKHIR EVALUASI INTRINSIK (STRICT ENTITY-LEVEL MATCHING)")
        print("="*75)
        print(f"• Strict Precision : {strict_prec*100:.2f}%")
        print(f"• Strict Recall    : {strict_rec*100:.2f}%")
        print(f"• Strict F1-Score  : {strict_f1*100:.2f}%")
        print("\nDetail Per-Kelas (Classification Report):")
        print(report)

        # Save audit report
        results_payload = {
            "overall": {
                "strict_precision": strict_prec,
                "strict_recall": strict_rec,
                "strict_f1": strict_f1
            },
            "classification_report": report,
            "detailed_verses": detailed_records
        }

        if output_report_path is None:
            output_report_path = os.path.join(BASE, "logs", "audit", "intrinsic_test_results.json")
        os.makedirs(os.path.dirname(output_report_path), exist_ok=True)
        with open(output_report_path, "w", encoding="utf-8") as f:
            json.dump(results_payload, f, ensure_ascii=False, indent=2)
        print(f"💾 Laporan hasil evaluasi intrinsik tersimpan: {output_report_path}")

        return results_payload

if __name__ == "__main__":
    evaluator = IntrinsicEvaluator(llm_mode="few_shot")
    evaluator.run_evaluation()

