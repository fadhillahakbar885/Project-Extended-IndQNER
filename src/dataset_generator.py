import os
import json
import sys
import time
from collections import Counter
from typing import Dict, List, Any

BASE_DIR = r"d:\SKRIPSI DILL KERJAIN\Proyek 2"
sys.path.append(BASE_DIR)

from src.preprocessing.quran_loader import QuranDataLoader
from src.acquisition.entity_acquisition_manager import EntityAcquisitionManager
from src.labeling.entity_labeler_manager import EntityLabelerManager
from src.labeling.conll_formatter import CoNLLFormatter

class ExtendedIndQNERGenerator:
    """
    Generator Dataset Extended IndQNER Skala Penuh (114 Surah, 6.236 Ayat):
    Menjalankan pipeline end-to-end:
    1. Preprocessing & Ekstraksi Teks (QAC + Kemenag RI)
    2. Perolehan Entitas 4-Jalur Terintegrasi + Resolusi Konflik
    3. Pelabelan Bertingkat (Kamus Lapis 1 + LLM Lapis 2)
    4. Formatter CoNLL BIO (Zero Deletion Guarantee)
    5. Agregasi Statistik & Ekspor Data
    """

    def __init__(self, llm_mode: str = "few_shot"):
        print("\n" + "=" * 80)
        print("MEMULAI INISIALISASI GENERATOR DATASET EXTENDED INDQNER (114 SURAH)")
        print("=" * 80)
        start_t = time.time()
        self.loader = QuranDataLoader()
        self.acq_manager = EntityAcquisitionManager()
        self.label_manager = EntityLabelerManager(llm_mode=llm_mode)
        self.formatter = CoNLLFormatter()
        print(f"✅ Inisialisasi selesai dalam {time.time() - start_t:.2f} detik.")

    def generate_full_dataset(
        self,
        output_conll_path: str = None,
        output_stats_path: str = None,
        max_surah: int = 114
    ) -> Dict[str, Any]:
        """
        Menjalankan proses perluasan dataset untuk seluruh surah (1 s.d. max_surah).
        """
        if output_conll_path is None:
            output_conll_path = os.path.join(BASE_DIR, "data", "output", "extended_indqner.txt")
        if output_stats_path is None:
            output_stats_path = os.path.join(BASE_DIR, "data", "output", "extended_indqner_stats.json")

        os.makedirs(os.path.dirname(output_conll_path), exist_ok=True)
        os.makedirs(os.path.dirname(output_stats_path), exist_ok=True)

        print(f"\n🚀 Menjalankan pipeline perluasan dataset untuk Surah 1 s.d. {max_surah}...")
        
        start_time = time.time()
        total_verses_processed = 0
        total_tokens_count = 0
        total_entities_count = 0
        
        class_distribution = Counter()
        channel_distribution = Counter()
        label_source_distribution = Counter()
        surah_stats = {}

        conll_blocks = []

        for surah_num in range(1, max_surah + 1):
            surah_file = os.path.join(BASE_DIR, "Teks Terjemahan", "surah", f"{surah_num}.json")
            if not os.path.exists(surah_file):
                print(f"⚠️ Berkas terjemahan surah {surah_num} tidak ditemukan, dilewati.")
                continue

            with open(surah_file, "r", encoding="utf-8") as f:
                ayah_list = json.load(f)

            surah_entity_count = 0
            surah_tokens_count = 0

            for item in ayah_list:
                ayah_num = item["ayah"]
                total_verses_processed += 1

                # 1. Ambil data QAC & Kemenag
                qac_tokens = self.loader.get_qac_tokens(surah_num, ayah_num)
                trans_dict = self.loader.get_indonesian_translation(surah_num, ayah_num)

                if not trans_dict:
                    continue

                raw_trans = trans_dict["raw_translation"]
                cleaned_trans = trans_dict["cleaned_translation"]

                # 2. Perolehan Entitas 4-Jalur + Resolusi Konflik
                cands = self.acq_manager.acquire_entities(surah_num, ayah_num, qac_tokens, trans_dict)

                # 3. Pelabelan Bertingkat
                labeled_entities = self.label_manager.label_entities(cleaned_trans, cands)

                # Catat statistik kanal & label source
                for ent in labeled_entities:
                    cls_name = ent.get("class", "Unknown")
                    class_distribution[cls_name] += 1
                    total_entities_count += 1
                    surah_entity_count += 1
                    
                    source = ent.get("labeled_by", ent.get("source", "Unknown"))
                    label_source_distribution[source] += 1

                    channel = ent.get("channel", "Unknown")
                    if isinstance(channel, list):
                        channel_str = "+".join(sorted(list(set(channel))))
                    else:
                        channel_str = str(channel)
                    channel_distribution[channel_str] += 1

                # 4. Format CoNLL BIO
                tagged_tokens = self.formatter.format_verse(trans_dict["tokens"], labeled_entities)
                conll_block = self.formatter.to_conll_string(tagged_tokens)
                conll_blocks.append(conll_block)

                # Hitung token dari tagged_tokens
                surah_tokens_count += len(tagged_tokens)
                total_tokens_count += len(tagged_tokens)

            surah_stats[surah_num] = {
                "total_ayahs": len(ayah_list),
                "total_tokens": surah_tokens_count,
                "total_entities": surah_entity_count
            }

            if surah_num % 10 == 0 or surah_num == max_surah or surah_num <= 5:
                elapsed = time.time() - start_time
                print(f"  [Surah {surah_num:3d}/{max_surah}] Selesai | Akumulasi Ayat: {total_verses_processed:5d} | Token: {total_tokens_count:6d} | Entitas: {total_entities_count:5d} | Waktu: {elapsed:.1f}s")

        # Tulis berkas CoNLL BIO
        print(f"\nMenulis output dataset ke {output_conll_path}...")
        with open(output_conll_path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(conll_blocks) + "\n")

        total_duration = time.time() - start_time

        # Susun laporan statistik
        stats = {
            "dataset_name": "Extended IndQNER (114 Surah)",
            "base_corpus": "Terjemahan Al-Qur'an Kementerian Agama RI & Quranic Arabic Corpus (QAC)",
            "total_surahs": max_surah,
            "total_verses": total_verses_processed,
            "total_tokens": total_tokens_count,
            "total_entities": total_entities_count,
            "average_entities_per_verse": round(total_entities_count / total_verses_processed, 4) if total_verses_processed else 0,
            "average_tokens_per_verse": round(total_tokens_count / total_verses_processed, 4) if total_verses_processed else 0,
            "class_distribution": dict(class_distribution.most_common()),
            "channel_distribution": dict(channel_distribution.most_common()),
            "label_source_distribution": dict(label_source_distribution.most_common()),
            "surah_summary": surah_stats,
            "generation_duration_seconds": round(total_duration, 2)
        }

        print(f"Menulis ringkasan statistik ke {output_stats_path}...")
        with open(output_stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        print("\n" + "=" * 80)
        print("PENYUSUNAN EXTENDED INDQNER BERHASIL DILAKUKAN")
        print("=" * 80)
        print(f"• Total Surah Diproses  : {max_surah} Surah")
        print(f"• Total Ayat Diproses   : {total_verses_processed:,} Ayat")
        print(f"• Total Token Diekstrak : {total_tokens_count:,} Token")
        print(f"• Total Entitas Dihasilkan: {total_entities_count:,} Entitas")
        print(f"• Waktu Eksekusi Total  : {total_duration:.2f} detik")
        print("\nTop-10 Kelas Entitas Terbanyak:")
        for cls_name, count in class_distribution.most_common(10):
            print(f"  - {cls_name:<20}: {count:>5d} entitas ({count/total_entities_count*100:5.2f}%)")

        print(f"\nDistribusi Kanal Perolehan Entitas:")
        for ch, count in channel_distribution.most_common():
            print(f"  - {ch:<25}: {count:>5d} entitas ({count/total_entities_count*100:5.2f}%)")

        print(f"\nDistribusi Sumber Pelabelan:")
        for src, count in label_source_distribution.most_common():
            print(f"  - {src:<25}: {count:>5d} entitas ({count/total_entities_count*100:5.2f}%)")

        print(f"\n💾 Berkas CoNLL BIO : {output_conll_path}")
        print(f"💾 Berkas Statistik : {output_stats_path}")
        return stats

if __name__ == "__main__":
    generator = ExtendedIndQNERGenerator(llm_mode="few_shot")
    generator.generate_full_dataset()
