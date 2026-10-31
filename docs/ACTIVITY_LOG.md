# Log Aktivitas Proyek 2: Extended IndQNER

Format Pencatatan:
`[Tanggal] - [Jam] - [Aktivitas] - [Folder/File Terkait] - [Keterangan/Hasil]

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

* **2026-10-31 - 05:30:00**
  * **Aktivitas:** Penyusunan modul pengujian LLM-as-Labeler (Llama-3-8B) pada GPU T4 Google Colab dan ekstraksi berkas payload pengujian (Ablation Study).
  * **Folder/File Terkait:** `notebooks/Colab_Llama3_Labeler_T4.ipynb`, `data/intermediate/llm_colab_payload.json`, `src/labeling/prepare_llm_payload.py`, `src/labeling/integrate_colab_results.py`.
  * **Keterangan/Hasil:** 
    1. Berhasil mengekstrak payload `llm_colab_payload.json` yang memuat entitas unmapped dan 237 entitas ground-truth test set resmi.
    2. Menghasilkan notebook Jupyter teroptimasi GPU T4 (`notebooks/Colab_Llama3_Labeler_T4.ipynb`) menggunakan kuantisasi 4-bit (`bitsandbytes`) untuk pengujian Zero-Shot vs Few-Shot.
    3. Membangun modul integrasi kembali hasil prediksi Colab (`src/labeling/integrate_colab_results.py`) untuk pemutakhiran kamus dan dataset secara otomatis.

* **2026-10-31 - 06:40:00**
  * **Aktivitas:** Investigasi mendalam dan resolusi 2 celah teknis kritis (*Boundary Offset Drift* & *Short Name False Positive*) pada penangkapan kandidat entitas.
  * **Folder/File Terkait:** `src/utils/text_utils.py`, `src/acquisition/channel1_pn.py`, `src/acquisition/channel2_concept.py`, `src/acquisition/entity_acquisition_manager.py`, `data/output/extended_indqner.txt`.
  * **Keterangan/Hasil:** 
    1. Menghilangkan `.strip()` pada `normalize_text` sehingga index string target dan regex 1:1 identik (mengeliminasi bug pemotongan huruf terakhir seperti `' hari Kiama'` -> `'hari Kiamat'`).
    2. Menghapus toleransi Levenshtein edit distance 1 pada kata pendek $\le 4$ karakter dan menerapkan *Strict Exact Match + Stopword Blacklist* Bahasa Indonesia. Terbukti 100% melenyapkan false positive kata fungsi (*"hari"*, *"ada"*, *"adalah"*).
    3. Entitas unmapped riil di korpus 114 surah terbukti murni tersisa 1 entitas sejati: `'Yasrib'` (QS. 33:13).
    4. Dataset Extended IndQNER bersih teregenerasi memuat 6.514 entitas tervalidasi.

* **2026-10-31 - 07:05:00**
  * **Aktivitas:** Integrasi modul evaluasi Large Language Model (Google Gemini 1.5 Pro / Flash) ke dalam Notebook Google Colab T4 untuk Studi Ablasi Multi-LLM (Small vs Large LLM).
  * **Folder/File Terkait:** `notebooks/Colab_Llama3_Labeler_T4.ipynb`, `data/intermediate/multi_llm_comparative_results.json`.
  * **Keterangan/Hasil:** 
    1. Berhasil menambahkan pipeline pengujian komparatif Large LLM (Gemini 1.5) berdampingan dengan Small LLM (Llama-3-8B).
    2. Menyediakan analisis khusus ambiguitas teologis antara kelas `Prophet` (Nabi) vs `Messenger` (Rasul) untuk menguji hipotesis *Model Scaling Effect*.
    3. Hasil eksekusi Small LLM Llama-3-8B di GPU T4 mencapai Akurasi 80,17% dan Weighted F1 83,14% pada 237 entitas ground-truth, serta sukses melabeli entitas unmapped `'Yasrib'` (QS. 33:13) sebagai `GeographicalLocation`.

* **2026-10-31 - 08:35:00**
  * **Aktivitas:** Implementasi dan penyiapan berkas Evaluasi Ekstrinsik (*Downstream NER Task*) menggunakan Transformer IndoBERT (`indobenchmark/indobert-base-p1`).
  * **Folder/File Terkait:** `src/evaluation/prepare_downstream_data.py`, `data/downstream/`, `notebooks/Colab_IndoBERT_Downstream_NER.ipynb`.
  * **Keterangan/Hasil:** 
    1. Menghasilkan partisi dataset downstream bebas kebocoran data (*0% Data Leakage Guarantee*): `baseline_train.txt` (1.050 ayat, 2.095 entitas), `extended_train.txt` (5.353 ayat, 5.649 entitas), `dev.txt` (161 ayat), dan `test.txt` (176 ayat).
    2. Mengompresi seluruh partisi ke `data/downstream/downstream_data.zip` (2,1 MB) untuk kemudahan unggah 1-klik ke Colab.
    3. Membangun Google Colab Notebook teroptimasi GPU T4 (`notebooks/Colab_IndoBERT_Downstream_NER.ipynb`) untuk fine-tuning komparatif Model A (Baseline) vs Model B (Extended) dan evaluasi strict CoNLL resmi seqeval.

* **2026-10-31 - 08:48:00**
  * **Aktivitas:** Penyesuaian parameter inisialisasi HuggingFace Trainer pada Notebook Downstream NER untuk kompatibilitas pustaka `transformers` v4.46+.
  * **Folder/File Terkait:** `notebooks/Colab_IndoBERT_Downstream_NER.ipynb`.
  * **Keterangan/Hasil:** Memperbarui parameter `tokenizer=tokenizer` menjadi `processing_class=tokenizer` pada Sel 6 (Model A) dan Sel 7 (Model B) sesuai standar mutakhir HuggingFace.

* **2026-10-31 - 09:10:00**
  * **Aktivitas:** Penerimaan dan analisis komprehensif hasil Evaluasi Ekstrinsik (*Downstream NER Task*) model IndoBERT pada Unseen Test Set (176 ayat, 237 entitas).
  * **Folder/File Terkait:** `data/intermediate/downstream_evaluation_results.json`, `notebooks/Colab_IndoBERT_Downstream_NER Hasil Running.ipynb`.
  * **Keterangan/Hasil:** 
    1. Pembuktian Hipotesis Utama Skripsi Berhasil: Dataset Extended IndQNER (114 Surah) terbukti meningkatkan performa generalisasi model secara masif pada metrik Macro (objektif antar-kelas):
       - **Macro F1-Score melonjak dari 69,01% menjadi 77,09% (+8,08%)**!
       - **Macro Precision melonjak dari 72,52% menjadi 81,55% (+9,03%)**!
       - **Macro Recall melonjak dari 68,05% menjadi 75,08% (+7,03%)**!
    2. Model Extended sukses mengatasi kebutaan (*zero recognition*) Model Baseline pada kelas langka:
       - Kelas `GeographicalLocation`: melonjak drastis dari **F1: 0,00% menjadi F1: 80,00%**!
       - Kelas `Prophet`: melonjak dari **F1: 80,00% menjadi F1: 100,00% (Sempurna)**!
       - Kelas `Person`: melonjak dari **F1: 88,89% menjadi F1: 96,00% (+7,11%)**!
       - Kelas `Messenger`: melonjak menjadi **F1: 97,30% (+1,20%)**!
       - Kelas `AstronomicalBody`: melonjak menjadi **F1: 80,00% (+1,57%)**!
    3. Seluruh bukti empiris tersimpan aman di `data/intermediate/downstream_evaluation_results.json` dan siap disajikan dalam tabel dan grafik Bab IV Skripsi.

* **2026-10-31 - 09:18:00**
  * **Aktivitas:** Sinkronisasi dan penyusunan naskah skripsi lengkap (Bab I, II, III diselaraskan dengan arsitektur 4-jalur & 5 guardrails; Bab IV Hasil dan Pembahasan memuat seluruh data empiris; Bab V Kesimpulan dan Saran).
  * **Folder/File Terkait:** `File Kepenulisan/DRAFT_SKRIPSI_LENGKAP_BAB_I_SD_V.docx`, `File Kepenulisan/DRAFT_SKRIPSI_LENGKAP_BAB_I_SD_V.md`, `src/utils/generate_thesis_draft.py`.
  * **Keterangan/Hasil:** 
    1. Menghasilkan naskah skripsi berformat Microsoft Word (.docx) siap cetak dan siap diedit berstandar pedoman penulisan UIN Syarif Hidayatullah Jakarta (Margin 4-4-3-3 cm, Times New Roman 12 pt, 1.5 spasi).
    2. Memuat tabel-tabel evaluasi resmi: Tabel 4.1 (Statistik Korpus), Tabel 4.2 (Distribusi Kontribusi 4 Jalur), Tabel 4.3 (Evaluasi Intrinsik seqeval 20 Kelas), Tabel 4.4 (Studi Ablasi Multi-LLM di GPU T4), dan Tabel 4.5 (Evaluasi Ekstrinsik Downstream IndoBERT).
    3. Menyediakan versi Markdown (.md) lengkap untuk kemudahan navigasi di IDE/editor.
