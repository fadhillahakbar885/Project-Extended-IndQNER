import os
import json
import sys

BASE = r"d:\SKRIPSI DILL KERJAIN\Proyek 2"
sys.path.append(BASE)

from src.dataset_generator import ExtendedIndQNERGenerator

def integrate_colab_results(colab_result_path: str = None):
    """
    Mengintegrasikan kembali hasil inferensi Llama-3-8B dari Google Colab T4
    ke dalam Kamus & Dataset Extended IndQNER.
    """
    if colab_result_path is None:
        colab_result_path = os.path.join(BASE, "data", "intermediate", "llama3_labeling_results.json")
        
    if not os.path.exists(colab_result_path):
        print(f"❌ Berkas hasil Colab '{colab_result_path}' belum ditemukan.")
        print("Pastikan Anda telah menjalankan notebook di Colab dan meletakkan berkas 'llama3_labeling_results.json' di folder 'data/intermediate/'.")
        return False

    with open(colab_result_path, "r", encoding="utf-8") as f:
        colab_data = json.load(f)

    unmapped_preds = colab_data.get("unmapped_results", [])
    print(f"\nMemproses {len(unmapped_preds)} entitas unmapped hasil pelabelan Llama-3-8B...")

    # Update kamus
    kamus_path = os.path.join(BASE, "data", "dictionaries", "kamus_indqner_compiled.json")
    with open(kamus_path, "r", encoding="utf-8") as f:
        kamus_dict = json.load(f)

    updated_count = 0
    for it in unmapped_preds:
        ent_text = it["entity"]
        pred_cls = it["predicted_class"]
        norm_key = ent_text.strip(".,;:!?\"'()«»“”").lower()
        if norm_key not in kamus_dict:
            kamus_dict[norm_key] = pred_cls
            updated_count += 1

    with open(kamus_path, "w", encoding="utf-8") as f:
        json.dump(kamus_dict, f, ensure_ascii=False, indent=2)

    print(f"✅ Kamus berhasil diperbarui dengan {updated_count} entitas baru dari Llama-3-8B!")

    # Jalankan ulang generator dataset skala penuh
    print("\nMenjalankan ulang generator dataset skala penuh dengan entitas terintegrasi...")
    generator = ExtendedIndQNERGenerator(llm_mode="few_shot")
    generator.generate_full_dataset()

    print("\n🎉 Integrasi hasil Llama-3-8B Google Colab T4 ke Extended IndQNER 100% SELESAI!")
    return True

if __name__ == "__main__":
    integrate_colab_results()

