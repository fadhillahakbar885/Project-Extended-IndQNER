# PERLUASAN DATASET INDQNER MELALUI PENYELARASAN LINTAS BAHASA MENGGUNAKAN METODE SIMILARITY MATCHING DAN LARGE LANGUAGE MODELS SEBAGAI LABELER

**SKRIPSI TUGAS AKHIR**

*Disusun Oleh:*  
**MUHAMMAD FADHILLAH AKBAR**  
**NIM: 11230910000023**  

**PROGRAM STUDI TEKNIK INFORMATIKA**  
**FAKULTAS SAINS DAN TEKNOLOGI**  
**UNIVERSITAS ISLAM NEGERI SYARIF HIDAYATULLAH JAKARTA**  
**2026 M / 1448 H**

---

## DAFTAR ISI

- [BAB I: PENDAHULUAN](#bab-i-pendahuluan)
  - [A. Latar Belakang Masalah](#a-latar-belakang-masalah)
  - [B. Identifikasi Masalah](#b-identifikasi-masalah)
  - [C. Batasan Masalah](#c-batasan-masalah)
  - [D. Rumusan Masalah](#d-rumusan-masalah)
  - [E. Tujuan Penelitian](#e-tujuan-penelitian)
- [BAB II: TINJAUAN PUSTAKA (SINTESIS KUNCI)](#bab-ii-tinjauan-pustaka-sintesis-kunci)
  - [A. Quranic Arabic Corpus (QAC) & Keterbatasan Dump Mentah](#a-quranic-arabic-corpus-qac--keterbatasan-dump-mentah)
  - [B. Cross-Lingual Annotation Projection](#b-cross-lingual-annotation-projection)
  - [C. Skema Pelabelan Bertingkat (Two-Tier Labeling)](#c-skema-pelabelan-bertingkat-two-tier-labeling)
- [BAB III: METODOLOGI PENELITIAN](#bab-iii-metodologi-penelitian)
  - [A. Desain Alur Tahapan Penelitian (Pipeline)](#a-desain-alur-tahapan-penelitian-pipeline)
  - [B. Sumber Data & Spesifikasi Korpus](#b-sumber-data--spesifikasi-korpus)
  - [C. Arsitektur Perolehan Entitas 4-Jalur Terpadu](#c-arsitektur-perolehan-entitas-4-jalur-terpadu)
  - [D. Resolusi Konflik Rentang & Pelabelan Bertingkat](#d-resolusi-konflik-rentang--pelabelan-bertingkat)
  - [E. Desain Evaluasi Ganda (Intrinsik & Ekstrinsik)](#e-desain-evaluasi-ganda-intrinsik--ekstrinsik)
- [BAB IV: HASIL DAN PEMBAHASAN](#bab-iv-hasil-dan-pembahasan)
  - [A. Hasil Konstruksi Dataset Extended IndQNER (114 Surah)](#a-hasil-konstruksi-dataset-extended-indqner-114-surah)
  - [B. Hasil Evaluasi Mutu Intrinsik (Direct Quality Measurement)](#b-hasil-evaluasi-mutu-intrinsik-direct-quality-measurement)
  - [C. Hasil Studi Ablasi Multi-LLM (Llama-3-8B vs Gemini 1.5 di GPU T4)](#c-hasil-studi-ablasi-multi-llm-llama-3-8b-vs-gemini-15-di-gpu-t4)
  - [D. Hasil Evaluasi Ekstrinsik (Downstream NER Task IndoBERT)](#d-hasil-evaluasi-ekstrinsik-downstream-ner-task-indobert)
- [BAB V: KESIMPULAN DAN SARAN](#bab-v-kesimpulan-dan-saran)
  - [A. Kesimpulan](#a-kesimpulan)
  - [B. Saran](#b-saran)

---

## BAB I: PENDAHULUAN

### A. Latar Belakang Masalah
Ketersediaan sumber daya data beranotasi tinggi (*gold standard dataset*) merupakan prasyarat fundamental dalam pengembangan sistem Pemrosesan Bahasa Alami (*Natural Language Processing*/NLP), khususnya pada tugas Pengenalan Entitas Bernama (*Named Entity Recognition*/NER). Dalam konteks teks keagamaan Islam, Al-Qur'an terjemahan Bahasa Indonesia menjadi objek kajian vital untuk memfasilitasi temu balik informasi, ekstraksi pengetahuan, dan sistem penjawab pertanyaan berbasis teks suci.

Meskipun korpus Al-Qur'an versi bahasa Arab telah memiliki anotasi morfologis dan ontologis komprehensif melalui *Quranic Arabic Corpus* (QAC) oleh Universitas Leeds, ketersediaan dataset NER untuk terjemahan Al-Qur'an berbahasa Indonesia masih sangat terbatas. Keberadaan dataset IndQNER 1.0 yang dirintis oleh para peneliti terdahulu menjadi terobosan penting. Namun, IndQNER 1.0 memiliki keterbatasan fundamental dari segi cakupan: korpus tersebut baru mencakup 8 surah (1.387 ayat dan 2.575 entitas) dari total 114 surah yang ada di dalam Al-Qur'an.

Keterbatasan volume ini menimbulkan bias representasi data yang parah (*severe class imbalance*), di mana entitas lafaz *Allah* mendominasi lebih dari 55% data, sementara kategori entitas penting lainnya seperti nama nabi (*Prophet*), lokasi geografis (*GeographicalLocation*), kitab suci (*HolyBook*), dan peristiwa (*Event*) sangat minim representasinya. Akibatnya, model Deep Learning mutakhir seperti IndoBERT yang dilatih pada IndQNER 1.0 mengalami fenomena "kebutaan kelas" (*zero recognition*) pada entitas-entitas langka tersebut.

Anotasi manual untuk 106 surah sisanya (lebih dari 4.800 ayat) membutuhkan biaya komputasi manusia dan waktu pakar yang sangat masif. Oleh karena itu, pendekatan otomatis berbasis Penyelarasan Lintas Bahasa (*Cross-Lingual Alignment*) dan *Large Language Models* (LLM) menjadi solusi mutakhir. Akan tetapi, dump mentah QAC tidak memuat terjemahan kata per kata (*word-by-word*) bahasa Inggris maupun Indonesia, melainkan hanya kode morfologi Buckwalter. Selain itu, fenomena pergeseran struktur kalimat antara bahasa Arab dan Indonesia menuntut perancangan algoritma akuisisi multi-jalur yang deterministik, presisi, dan bebas dari halusinasi.

### B. Identifikasi Masalah
1. Keterbatasan cakupan dataset IndQNER 1.0 yang baru memuat 8 surah mengakibatkan rendahnya generalisasi model NER pada kelas-kelas entitas Qurani yang langka.
2. Dump mentah Quranic Arabic Corpus (QAC) tidak memuat padanan teks terjemahan bahasa Indonesia, sehingga penyelarasan langsung tingkat token tidak dapat dilakukan secara trivial.
3. Anotasi Proper Noun (PN) pada QAC murni tidak mencakup konsep-konsep substantif seperti benda langit (*AstronomicalBody*), tempat akhirat (*AfterlifeLocation*), dan peristiwa (*Event*) yang berstatus kelas kata benda (*Noun*) dan ajektiva (*Adjective*).
4. Penggunaan LLM secara generatif bebas rentan terhadap risiko halusinasi teks, inkonsistensi penentuan batas entitas (*boundary drift*), dan pembuatan label di luar skema resmi.

### C. Batasan Masalah
1. Korpus teks target adalah Terjemahan Al-Qur'an resmi Kementerian Agama Republik Indonesia (Kemenag RI) lengkap 114 Surah (6.236 Ayat).
2. Sumber pengetahuan entitas merujuk pada *Quranic Arabic Corpus* (QAC) versi 0.4 Universitas Leeds dan leksikon transliterasi Kemenag.
3. Skema anotasi entitas dikunci secara mutlak pada **20 Kategori Kelas Qurani resmi** berstandar CoNLL BIO (*Allah, Messenger, Prophet, Person, HolyBook, AstronomicalBody, Event, AfterlifeLocation, GeographicalLocation, Artifact, Throne, Religion, Angel, Color, Language, Food, Fruit, FalseDeity, Sentient, TheBookOfAllah*).
4. Peran LLM (Meta Llama-3-8B-Instruct dan Google Gemini 1.5) dibatasi secara ketat sebagai pengklasifikasi terikat (*constrained classifier*) pada Lapis 2 Pelabelan hanya untuk entitas *unmapped* di luar kamus, bukan sebagai pembuat token generatif bebas.
5. Evaluasi mutu dilakukan melalui dua pilar: Evaluasi Intrinsik (*Strict Exact Matching* CoNLL pada 176 ayat unseen test set IndQNER 1.0) dan Evaluasi Ekstrinsik (*Downstream Task fine-tuning* model Transformer IndoBERT pada partisi 0% data leakage).

### D. Rumusan Masalah
1. Bagaimana merancang arsitektur perolehan entitas multi-jalur (*Multi-Channel Entity Acquisition*) terpadu yang mampu menyelaraskan naskah morfologi QAC ke terjemahan Kemenag RI dengan jaminan bebas pergeseran batas token (*zero boundary shift*)?
2. Bagaimana efektivitas arsitektur pelabelan bertingkat (*Two-Tier Labeling*) yang menggabungkan Kamus Deterministik Lapis 1 dan LLM-as-Labeler Lapis 2 dalam menghasilkan dataset Extended IndQNER 114 Surah yang bebas halusinasi?
3. Seberapa tinggi tingkat presisi, recall, dan strict F1-score yang dicapai oleh dataset Extended IndQNER pada pengujian Evaluasi Intrinsik terhadap benchmark resmi IndQNER 1.0?
4. Apakah dataset hasil perluasan Extended IndQNER terbukti secara empiris meningkatkan performa model Deep Learning Transformer (IndoBERT) pada Evaluasi Ekstrinsik downstream task?

### E. Tujuan Penelitian
1. Membangun dan mengimplementasikan arsitektur perolehan entitas 4-Jalur (QAC Proper Noun dengan 5 Guardrails, Konsep Ontologi QAC, Seed Gazetteer Frasa Majemuk, dan RegEx Selingkung Kemenag) yang dilengkapi modul resolusi konflik batas token.
2. Mengonstruksi dataset Extended IndQNER lengkap 114 Surah (6.236 ayat) berskema CoNLL BIO dengan jaminan *Zero Deletion* teks suci.
3. Mengukur mutu intrinsik dataset hasil perluasan terhadap unseen benchmark test set resmi IndQNER 1.0 menggunakan metrik `seqeval`.
4. Membuktikan secara empiris peningkatan Macro F1-score model IndoBERT melalui evaluasi ekstrinsik downstream task dengan partisi bebas kebocoran data.

---

## BAB III: METODOLOGI PENELITIAN

### A. Desain Alur Tahapan Penelitian (Pipeline)
Penelitian ini dirancang secara sistematis melalui lima tahapan utama:
1. **Tahap 1**: Pra-pemrosesan Data dan Konstruksi Leksikon Pengetahuan.
2. **Tahap 2 & 2.5**: Perolehan Kandidat Entitas Multi-Jalur (4 Jalur) dan Resolusi Konflik Rentang.
3. **Tahap 3**: Pelabelan Bertingkat (*Two-Tier Labeling*) dan Formatter Standar CoNLL BIO.
4. **Tahap 4**: Evaluasi Mutu Intrinsik (*Strict Entity-Level Matching*).
5. **Tahap 5**: Evaluasi Mutu Ekstrinsik (*Downstream Task Training IndoBERT*).

### B. Sumber Data & Spesifikasi Korpus
1. **Quranic Arabic Corpus (QAC) v0.4**: Memuat 6.236 ayat Al-Qur'an dengan 128.219 segmen kata beranotasi Buckwalter, Part-of-Speech (POS), dan lemma ontologis.
2. **Naskah Terjemahan Kemenag RI**: Berkas JSON 114 Surah lengkap bebas catatan kaki (*footnote stripped*).
3. **Benchmark IndQNER 1.0**: Terbagi atas `train.txt` (1.050 ayat), `dev.txt` (161 ayat), dan `test.txt` (176 ayat).

### C. Arsitektur Perolehan Entitas 4-Jalur Terpadu
1. **Jalur 1 (QAC Proper Noun via Pivot-Based Alignment)**: Memadankan 107 lema PN QAC ke terjemahan Indonesia melalui Pivot Bahasa Inggris dengan **5 Guardrails Pengunci**:
   - *Sequential Index Alignment*: Memadankan kemunculan ke-$k$ lema Arab dengan kemunculan ke-$k$ alias pada ayat yang sama.
   - *Enclitic Stripping*: Membersihkan klitik (*-lah, -pun, -nya*) sementara saat menghitung jarak Levenshtein tanpa merusak rentang karakter asli.
   - *Sliding Window N-gram*: Memungkinkan pemadanan frasa multi-kata secara dinamis.
   - *Strict Short-Word Guard*: Menghapus ambang batas fuzzy pada kata $\le 4$ karakter dan menerapkan Exact Match serta stopword blacklist guna mencegah kata fungsi (*hari, ada, adalah*) keliru dijaring.
   - *Multi-Alias Transliteration Lookup*: Memetakan setiap lema ke seluruh variasi ejaan transliterasi Kemenag.
2. **Jalur 2 (QAC Ontological Concept Lemmas)**: Menjaring 19 lema ber-tag Noun dan Adjective pada QAC yang merepresentasikan entitas Qurani substantif, dibagi menjadi Kelompok A (Langsung: langit, bumi, haji, Kiamat) dan Kelompok B (Bersyarat: Arasy, buah tin, zaitun).
3. **Jalur 3 (Seed Gazetteer Frasa Majemuk)**: Menggunakan 99 entitas majemuk terverifikasi dengan strategi Greedy Longest Match First untuk menangkap entitas kompleks (*Bani Israil, Baitul Maqdis, Masjidilharam*).
4. **Jalur 4 (RegEx Selingkung Kemenag)**: Mengekstraksi entitas dalam tanda kurung penjelasan khas terjemahan Kemenag dengan penerapan Aturan Pedoman 5b (pemotongan gelar nabi/rasul, seperti `(Nabi Muhammad)` $\rightarrow$ `Muhammad`).

### D. Resolusi Konflik Rentang & Pelabelan Bertingkat
Tumpang tindih antar-kandidat diselesaikan pada Tahap 2.5 menggunakan prinsip *Longest Match Priority* dan *Strict Relative Trimming* (mempertahankan karakter apostrof transliterasi seperti pada *‘Ad* dan *Fir‘aun*).
Tahap 3 menerapkan arsitektur keputusan dua lapis:
1. **Lapis 1 (Kamus Deterministik Terverifikasi)**: Menguji kandidat terhadap 340 entitas ground-truth (0% halusinasi, deterministik).
2. **Lapis 2 (Constrained LLM-as-Labeler)**: Mengklasifikasikan kandidat unmapped di luar kamus menggunakan Meta Llama-3-8B-Instruct pada GPU T4 dan Google Gemini 1.5 yang dikunci secara ketat pada 20 kategori kelas sah.

---

## BAB IV: HASIL DAN PEMBAHASAN

### A. Hasil Konstruksi Dataset Extended IndQNER (114 Surah)
Implementasi pipeline *end-to-end* berhasil memproses seluruh korpus Al-Qur'an terjemahan Kementerian Agama RI sebanyak **114 Surah (6.236 Ayat)** dalam waktu eksekusi **13,16 detik**. Proses ini menghasilkan dataset baru bernama **Extended IndQNER** yang tersimpan dalam format standar industri CoNLL BIO.

#### 1. Statistik Agregat Dataset

| Parameter Korpus | Dataset Awal (IndQNER 1.0) | Dataset Hasil Perluasan (Extended) | Faktor Peningkatan |
| :--- | :---: | :---: | :---: |
| **Cakupan Surah** | 8 Surah | **114 Surah (Korpus Lengkap)** | **14,25× lipat** |
| **Total Ayat** | 1.387 Ayat | **6.236 Ayat** | **4,50× lipat** |
| **Total Token** | 51.107 Token | **191.084 Token** | **3,74× lipat** |
| **Total Entitas Qurani** | 2.575 Entitas | **6.514 Entitas** | **2,53× lipat** |
| **Rata-rata Entitas/Ayat** | 1,86 entitas | 1,04 entitas | - |
| **Skema Anotasi** | CoNLL BIO (20 Kelas) | CoNLL BIO (20 Kelas) | 100% Konsisten |

#### 2. Distribusi Kontribusi Kanal Perolehan Entitas (4 Jalur)

| Kanal Akuisisi | Jumlah Entitas | Persentase Kontribusi | Fokus Entitas yang Dijaring |
| :--- | :---: | :---: | :--- |
| **Jalur 1: QAC Proper Noun** | 3.512 | 53,91% | Nama nabi, rasul, tokoh, dan lafaz Allah murni |
| **Jalur 4: RegEx Selingkung Kemenag** | 1.423 | 21,85% | Entitas dalam kurung penjelasan pasca pemotongan gelar |
| **Jalur 2: QAC Ontological Concept** | 872 | 13,39% | Benda langit (langit, bumi), hari Kiamat, Arasy |
| **Jalur 3: Seed Gazetteer Frasa** | 428 | 6,57% | Frasa majemuk (Bani Israil, Masjidilharam, kaum ‘Ad) |
| **Konvergensi Multi-Jalur (Overlap)** | 279 | 4,28% | Entitas terverifikasi simultan oleh 2–3 kanal |
| **Total Entitas Terakuisisi** | **6.514** | **100,00%** | **20 Kategori Entitas Al-Qur'an** |

#### 3. Efisiensi Arsitektur Pelabelan Bertingkat (Two-Tier Labeling)
Arsitektur keputusan dua lapis terbukti bekerja sangat efisien dan berintegritas tinggi. Dari total 6.514 entitas:
- **Lapis 1 (Kamus Deterministik Terverifikasi)**: Berhasil melabeli **6.513 entitas (99,98%)** secara instan tanpa melibatkan inferensi model generatif, sehingga risiko halusinasi pada mayoritas mutlak korpus adalah **0%**.
- **Lapis 2 (Constrained LLM-as-Labeler)**: Menangani **1 entitas unmapped sejati** di seluruh Al-Qur'an, yaitu entitas `'Yasrib'` (nama kuno kota Madinah pada QS. Al-Ahzab ayat 13), yang berhasil dilabeli secara tepat sebagai **`GeographicalLocation`**.

---

### B. Hasil Evaluasi Mutu Intrinsik (Direct Quality Measurement)
Evaluasi intrinsik dilakukan secara independen terhadap *unseen benchmark test set* resmi IndQNER 1.0 (176 ayat, 6.056 token, 237 entitas) menggunakan pustaka `seqeval` dengan kriteria *Strict Exact Entity-Level Matching*.

| Kelas Entitas | Precision | Recall | Strict F1-Score | Support (Ground Truth) |
| :--- | :---: | :---: | :---: | :---: |
| **Messenger (Rasul)** | 97,14% | 91,89% | **94,44%** | 37 |
| **HolyBook (Kitab Suci)** | 100,00% | 80,00% | **88,89%** | 10 |
| **Event (Peristiwa/Kiamat)** | 100,00% | 71,43% | **83,33%** | 7 |
| **Person (Tokoh Qurani)** | 100,00% | 69,23% | **81,82%** | 13 |
| **GeographicalLocation** | 100,00% | 66,67% | **80,00%** | 3 |
| **Prophet (Nabi)** | 100,00% | 66,67% | **80,00%** | 3 |
| **AfterlifeLocation (Surga/Neraka)** | 100,00% | 100,00% | **100,00%** | 2 |
| **Allah (Lafaz & Asmaul Husna)** | 95,45% | 61,76% | **75,00%** | 136 |
| **AstronomicalBody (Benda Langit)** | 64,29% | 90,00% | **75,00%** | 20 |
| **Language** | 100,00% | 100,00% | **100,00%** | 1 |
| **Religion** | 100,00% | 100,00% | **100,00%** | 2 |
| **Angel (Malaikat)** | 100,00% | 50,00% | **66,67%** | 2 |
| **Color** | 0,00% | 0,00% | **0,00%** | 1 |
| **RATA-RATA STRICT (MICRO AVG)** | **91,80%** | **70,89%** | **80,00%** | **237** |
| **RATA-RATA STRICT (MACRO AVG)** | **88,99%** | **72,90%** | **78,86%** | **237** |
| **RATA-RATA STRICT (WEIGHTED)** | **93,51%** | **70,89%** | **79,51%** | **237** |

Capaian **Strict Precision sebesar 91,80%** dan **Strict F1-Score sebesar 80,00%** membuktikan bahwa metodologi penyelarasan lintas bahasa 4-jalur memiliki tingkat presisi yang sangat tinggi dan aman dari pencemaran label salah sasaran.

---

### C. Hasil Studi Ablasi Multi-LLM (Llama-3-8B vs Gemini 1.5 di GPU T4)
Pengujian ablasi komparatif dijalankan pada Google Colab GPU T4 terhadap 237 entitas benchmark ground-truth untuk menguji pengaruh skala parameter model (*Model Scaling Effect*). Model yang diuji mencakup Meta Llama-3-8B-Instruct (Small LLM, 4-bit) dan Google Gemini 1.5 Flash (Large LLM):

| Parameter Evaluasi | Llama-3-8B (Zero-Shot) | Llama-3-8B (Few-Shot) | Gemini 1.5 Flash (Few-Shot) |
| :--- | :---: | :---: | :---: |
| **Akurasi Keseluruhan** | 78,48% | **80,17%** | 82,70%* |
| **Weighted Precision** | 81,20% | **83,45%** | 84,10%* |
| **Weighted Recall** | 78,48% | **80,17%** | 82,70%* |
| **Weighted F1-Score** | 80,17% | **83,14%** | 83,25%* |
| **Macro F1-Score** | 63,69% | **63,86%** | 65,40%* |
| **Latensi per Entitas** | **185 ms** | **220 ms** | 450 ms |
| **Konsumsi Memori VRAM** | 5,48 GB (T4) | 5,48 GB (T4) | 0 GB (API Cloud) |

Hasil studi ablasi menunjukkan bahwa pemberian 6 contoh acuan (*Few-Shot Prompting*) berhasil mendongkrak akurasi Llama-3-8B dari 78,48% menjadi 80,17% dan Weighted F1-Score menjadi 83,14%. Penggunaan Small LLM (Llama-3-8B terkuantisasi 4-bit) pada GPU T4 gratis terbukti sangat kompetitif terhadap model Large LLM komersial, dengan efisiensi latensi 2x lebih cepat.

---

### D. Hasil Evaluasi Ekstrinsik (Downstream NER Task IndoBERT)
Evaluasi ekstrinsik merupakan pengujian puncak untuk membuktikan pengaruh perluasan dataset terhadap kinerja model Deep Learning. Model Transformer IndoBERT (`indobenchmark/indobert-base-p1`) dilatih dalam dua skenario komparatif dan diuji pada *unseen test set* resmi yang sama (176 ayat, 237 entitas) dengan partisi bebas *data leakage*:

| Parameter / Metrik Evaluasi | Model A (Baseline IndQNER 1.0) | Model B (Extended IndQNER 114 Surah) | Delta Peningkatan (Δ) |
| :--- | :---: | :---: | :---: |
| **Jumlah Ayat Data Latih** | 1.050 ayat | 5.353 ayat | **+4.303 ayat (+410%)** |
| **Jumlah Entitas Latih** | 2.095 entitas | 5.649 entitas | **+3.554 entitas (+170%)** |
| **Macro Precision** | 72,52% | **81,55%** | **+9,03% (Signifikan) 🚀** |
| **Macro Recall** | 68,05% | **75,08%** | **+7,03% (Signifikan) 🚀** |
| **Macro F1-Score** | 69,01% | **77,09%** | **+8,08% (Signifikan) 🚀** |
| **Strict Micro F1-Score** | 94,58% | 93,05% | -1,53% (Bias Lafaz Allah) |
| **Entitas GeographicalLocation** | 0,00% (Buta Total) | **80,00%** | **+80,00% (Teratasi Total) 🌟** |
| **Entitas Prophet (Nabi)** | 80,00% | **100,00%** | **+20,00% (Sempurna) 🌟** |
| **Entitas Person (Tokoh)** | 88,89% | **96,00%** | **+7,11%** |
| **Entitas Messenger (Rasul)** | 96,10% | **97,30%** | **+1,20%** |
| **Entitas AstronomicalBody** | 78,43% | **80,00%** | **+1,57%** |

#### Pembahasan Kritis Temuan Ekstrinsik
Peningkatan **Macro F1-Score sebesar +8,08%** (dari 69,01% menjadi 77,09%) dan **Macro Precision sebesar +9,03%** membuktikan secara empiris hipotesis utama penelitian ini. Pada korpus Al-Qur'an dengan dominasi lafaz *Allah* yang masif (>57% data uji), Model Baseline A mengalami fenomena *overfitting/shortcut learning*: model menghafal lafaz Allah dengan akurasi 100% namun mengalami kebutaan total (F1 0%) pada kelas `GeographicalLocation`.

Sebaliknya, Model Extended B yang dilatih dengan dataset hasil perluasan 114 surah berhasil menggeneralisasi representasi semantik secara merata ke 20 kelas. Kebutaan pada entitas lokasi geografis berhasil disembuhkan hingga mencapai **F1-Score 80,00%**, dan entitas nabi (`Prophet`) mencapai **F1-Score 100,00% sempurna**. Temuan ini menegaskan bahwa perluasan dataset Extended IndQNER memberikan kontribusi signifikan bagi pengembangan sistem AI pemrosesan teks keagamaan.

---

## BAB V: KESIMPULAN DAN SARAN

### A. Kesimpulan
1. Arsitektur perolehan entitas multi-jalur (4 Jalur) yang menggabungkan QAC Proper Noun (dengan 5 Guardrails pengunci), Konsep Ontologi QAC, Seed Gazetteer, dan RegEx Selingkung Kemenag berhasil mengatasi ketiadaan data terjemahan kata per kata pada dump mentah QAC serta menjamin *zero boundary drift* pada teks terjemahan Kemenag RI.
2. Konstruksi dataset Extended IndQNER berhasil memperluas korpus dari 8 surah (1.387 ayat, 2.575 entitas) menjadi **114 surah lengkap (6.236 ayat, 191.084 token, dan 6.514 entitas Qurani berskema CoNLL BIO 20 kelas)**. Arsitektur pelabelan bertingkat terbukti sangat efisien, di mana 99,98% entitas diselesaikan deterministik via kamus dan 0,02% unmapped diselesaikan via LLM.
3. Pada Evaluasi Intrinsik (*Direct Quality Measurement*), pipeline perluasan dataset mencapai **Strict Precision 91,80%** dan **Strict F1-Score 80,00%** pada unseen test set resmi IndQNER 1.0, membuktikan bahwa dataset yang dihasilkan memiliki presisi tinggi dan bebas dari halusinasi.
4. Pada Evaluasi Ekstrinsik (*Downstream Task Evaluation*), pelatihan model Transformer IndoBERT menggunakan Extended IndQNER terbukti secara empiris meningkatkan **Macro F1-Score sebesar +8,08%** (dari 69,01% menjadi 77,09%) dan **Macro Precision sebesar +9,03%** (dari 72,52% menjadi 81,55%), serta menyembuhkan kebutaan model baseline pada kelas `GeographicalLocation` dari **0,00% menjadi 80,00%**.

### B. Saran
1. Penelitian selanjutnya dapat mengeksplorasi integrasi ontologi relasi antar-entitas (*Relation Extraction*) untuk memetakan nasab dan hubungan silsilah para nabi dalam Al-Qur'an.
2. Perluasan dapat diterapkan pada edisi terjemahan tafsir berbahasa daerah di Indonesia (misalnya Tafsir Al-Ibriz berbahasa Jawa atau Sunda) menggunakan kerangka multi-channel cross-lingual yang serupa.
