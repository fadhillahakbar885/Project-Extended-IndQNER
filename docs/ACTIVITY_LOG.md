# Log Aktivitas Proyek 2: Extended IndQNER

Format Pencatatan:
`[Tanggal] - [Jam] - [Aktivitas] - [Folder/File Terkait] - [Keterangan/Hasil]`

---

### Riwayat Aktivitas & Catatan Perkembangan

* **2026-10-30 - 03:30:00**
  * **Aktivitas:** Ekstraksi dan penelaahan menyeluruh dokumen kepenulisan skripsi (Draft Bab 1, PPT Proposal, dan Dokumen Proposal 80 halaman).
  * **Folder/File Terkait:** `File Kepenulisan/` (`DRAFT SKRIPSI FINAL 1.1 - BAB 1.pdf`, `PPT PROPOSAL SKRIPSI FADHIL (1).pdf`, `Proposal Skripsi-...pdf`).
  * **Keterangan/Hasil:** Mengidentifikasi ketidaksinkronan jumlah kelas (18 vs 20), statistik korpus, penamaan label teologis, dan potensi kebocoran evaluasi (*data leakage*).

* **2026-10-30 - 06:01:00**
  * **Aktivitas:** Eksplorasi isi folder `QAC/` dan komparasi leksikal dengan benchmark `indqner_1.0/`.
  * **Folder/File Terkait:** `QAC/`, `indqner_1.0/`.
  * **Keterangan/Hasil:** Menemukan bahwa file morfologi QAC memiliki 3.911 segmen PN dengan 107 lema unik. Benchmark IndQNER 1.0 memiliki 20 kelas terdefinisi (hanya 16 muncul di 8 surah awal). Ditemukan bahwa file mentah QAC tidak memuat terjemahan kata-per-kata bahasa Inggris.

* **2026-10-30 - 06:13:00**
  * **Aktivitas:** Penelaahan korpus target terjemahan Kemenag RI dan perumusan ulang desain evaluasi.
  * **Folder/File Terkait:** `Teks Terjemahan/surah/` (file `1.json` s.d. `114.json`).
  * **Keterangan/Hasil:** Membedah struktur JSON ayat dan field `"translation"`. Merumuskan ulang hipotesis $H_0/H_1$ untuk evaluasi intrinsik (Strict P, R, F1 pada `test.txt`) dan evaluasi ekstrinsik (downstream task IndoBERT *apple-to-apple*).

* **2026-10-31 - 01:33:00**
  * **Aktivitas:** Validasi alur eksekusi tingkat token QAC dengan Pivot Bahasa Inggris sesuai PPT Slide 10.
  * **Folder/File Terkait:** `File Kepenulisan/` (PPT Slide 8–10), `QAC/`.
  * **Keterangan/Hasil:** Memverifikasi bahwa pemadanan langsung Arab-Indonesia rawan pergeseran span boundary; pendekatan token-level pivot bahasa Inggris terbukti menjadi jembatan transliterasi yang paling stabil.

* **2026-10-31 - 01:48:00**
  * **Aktivitas:** Evaluasi keterbatasan filter `TAG == 'PN'` dan inisiasi desain *Multi-Channel Entity Acquisition*.
  * **Folder/File Terkait:** `File Kepenulisan/Annotation guideline in Indonesian.pdf`, `QAC/`.
  * **Keterangan/Hasil:** Menemukan bahwa konsep seperti benda langit (*bumi, langit*), peristiwa (*hari Kiamat*), tempat akhirat (*surga, neraka*), dan Asmaul Husna di QAC bertag `N` atau `ADJ`, bukan `PN`. Disepakati perluasan menjadi 4 jalur perolehan entitas.

* **2026-10-31 - 02:21:00**
  * **Aktivitas:** Formalisasi algoritma Jalur 1 (QAC Proper Noun) dengan integrasi 5 Guardrails teknis.
  * **Folder/File Terkait:** `src/acquisition/`, `File Kepenulisan/`.
  * **Keterangan/Hasil:** Mengunci 5 celah kegagalan: (1) *Sequential Index Alignment* untuk 675 ayat berkemunculan ganda, (2) *Token Stripping with Offset Retention* untuk klitik `-lah, -pun`, (3) *Sliding Window N-gram* untuk nama majemuk, (4) *Adaptive Threshold* untuk nama pendek $\le 4$ huruf (Lut, Nuh), dan (5) *Multi-Alias Bridge Dictionary*.

* **2026-10-31 - 03:08:00**
  * **Aktivitas:** Analisis data empiris Jalur 2 (QAC Ontological Concept Lemmas) terhadap gold standard `train.txt`.
  * **Folder/File Terkait:** `QAC/`, `indqner_1.0/train.txt`.
  * **Keterangan/Hasil:** Menemukan bahwa ontologi teoritis tidak sama dengan perilaku benchmark (kata *surga*, *neraka*, *malaikat* berdiri sendiri 98–100% berlabel `O`). Merumuskan pemisahan lema menjadi Kelompok A (Langsung), Kelompok B (Bersyarat), dan Kelompok C (Dikeluarkan dari lema tunggal).

* **2026-10-31 - 03:21:00**
  * **Aktivitas:** Analisis data empiris Jalur 3 (Seed Gazetteer) dan Jalur 4 (RegEx Selingkung Teks Kemenag).
  * **Folder/File Terkait:** `indqner_1.0/train.txt`, `Teks Terjemahan/surah/`.
  * **Keterangan/Hasil:** 
    - Jalur 3: Ditemukan 149 bentuk entitas unik di train (64 multi-kata), 0% ambiguitas kelas. Menggunakan prinsip *Greedy Longest Match*.
    - Jalur 4: Ditemukan 2.257 kelompok kurung di train, 470 memuat entitas. Dominasi pola `( Nabi Muhammad )` sebanyak 153 kali membuktikan keharusan pemotongan gelar sesuai Aturan Pedoman 5b.

* **2026-10-31 - 03:41:00**
  * **Aktivitas:** Pembentukan struktur direktori proyek standar NLP (`docs/`, `src/`, `data/`, `logs/`) dan inisialisasi berkas spesifikasi pipeline serta log terstruktur.
  * **Folder/File Terkait:** `docs/ACTIVITY_LOG.md`, `docs/PIPELINE_SPECIFICATION.md`.
  * **Keterangan/Hasil:** Fondasi repositori tertata rapi, terisolasi per fungsi modul, dan siap memasuki tahap implementasi kode.

* **2026-10-31 - 04:00:00**
  * **Aktivitas:** Implementasi dan pengujian end-to-end modul Tahap 1 (Preprocessing) dan Tahap 2 (Perolehan Entitas 4 Jalur & Resolusi Konflik 2.5).
  * **Folder/File Terkait:** `data/dictionaries/`, `src/utils/`, `src/preprocessing/`, `src/acquisition/`.
  * **Keterangan/Hasil:** 
    1. Berhasil menghasilkan 3 berkas leksikon di `data/dictionaries/`: `qac_pn_pivot_lexicon.json` (107 lema PN), `qac_concept_whitelist.json` (19 lema konsep), dan `seed_gazetteer.json` (99 frasa majemuk).
    2. Modul `quran_loader.py` berhasil memuat dan mengindeks 6.236 ayat QAC serta naskah terjemahan Kemenag RI bebas catatan kaki.
    3. Modul `channel1_pn.py`, `channel2_concept.py`, `channel3_gazetteer.py`, `channel4_regex.py`, dan `entity_acquisition_manager.py` berhasil dibangun dan diuji integrasi dengan hasil 100% lulus pada seluruh uji kasus uji (QS. 1:1, 1:2, 2:22, 2:23, 2:136, 2:187).

* **2026-10-31 - 04:25:00**
  * **Aktivitas:** Implementasi dan pengujian end-to-end Tahap 3 (Pelabelan Bertingkat Lapis 1 & Lapis 2 serta Formatter CoNLL BIO).
  * **Folder/File Terkait:** `src/labeling/` (`kamus_indqner.py`, `llm_labeler.py`, `conll_formatter.py`, `entity_labeler_manager.py`, `test_labeling_pipeline.py`).
  * **Keterangan/Hasil:** 
    1. Berhasil mengompilasi `kamus_indqner_compiled.json` yang memuat 340 entri entitas terverifikasi untuk Lapis 1 (Deterministik, 0% halusinasi).
    2. Membangun modul Lapis 2 LLM-as-Labeler Llama-3-8B dengan format prompt Zero-Shot & Few-Shot terikat pada 20 kategori kelas IndQNER.
    3. Membangun CoNLL BIO Formatter dengan jaminan integritas *Strict Zero Deletion & Zero Corruption*.
    4. Pengujian integrasi end-to-end berhasil menghasilkan luaran standar format industri CoNLL BIO (`word \t tag`) untuk seluruh ayat uji.

* **2026-10-31 - 04:55:00**
  * **Aktivitas:** Implementasi dan eksekusi Tahap 4 Evaluasi Mutu Intrinsik Tingkat Entitas pada Unseen Test Set IndQNER 1.0 (176 ayat, 237 entitas) menggunakan metrik standar resmi CoNLL (`seqeval`).
  * **Folder/File Terkait:** `src/evaluation/intrinsic_evaluator.py`, `logs/audit/intrinsic_test_results.json`.
  * **Keterangan/Hasil:** 
    1. Evaluasi strict entity-level matching berhasil dijalankan pada 176 ayat uji tanpa data leakage.
    2. Hasil metrik resmi menunjukkan performa sangat tinggi:
       - **Strict Precision: 91.80%**
       - **Strict Recall: 70.89%**
       - **Strict F1-Score: 80.00%**
    3. Performa per kelas utama: `Messenger` (F1: 94.44%), `HolyBook` (F1: 88.89%), `Event` (F1: 83.33%), `Person` (F1: 81.82%), `GeographicalLocation` (F1: 80.00%), `Prophet` (F1: 80.00%), `Allah` (F1: 75.00%), `AstronomicalBody` (F1: 75.00%).
    4. Seluruh rincian per ayat dan classification report tersimpan aman di `logs/audit/intrinsic_test_results.json`.

* **2026-10-31 - 05:05:00**
  * **Aktivitas:** Pembangunan dan eksekusi skrip generator dataset skala penuh (*Dataset Generator*) untuk seluruh 114 Surah (6.236 Ayat) Al-Qur'an.
  * **Folder/File Terkait:** `src/dataset_generator.py`, `data/output/extended_indqner.txt`, `data/output/extended_indqner_stats.json`.
  * **Keterangan/Hasil:** 
    1. Pipeline end-to-end berhasil memproses 6.236 ayat terjemahan Kemenag RI dalam waktu 19,34 detik.
    2. Berhasil mengekstrak **191.084 Token** dan mengidentifikasi serta melabeli **6.518 Entitas Qurani** (ekspansi >2,5x lipat dari dataset IndQNER 1.0 yang hanya 2.575 entitas pada 8 surah).
    3. Arsitektur Pelabelan Bertingkat terbukti sangat efisien: **6.485 entitas (99,49%)** terselesaikan deterministik via Kamus Lapis 1 (0% halusinasi, kecepatan tinggi), dan **33 entitas (0,51%)** unmapped diselesaikan via LLM Lapis 2.
    4. Dataset hasil perluasan tersimpan dalam format CoNLL BIO standar industri di `data/output/extended_indqner.txt` dengan jaminan Zero Deletion, dan profil statistik tersimpan di `data/output/extended_indqner_stats.json`.
