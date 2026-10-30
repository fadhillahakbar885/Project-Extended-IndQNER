# Spesifikasi Teknis Pipeline Extended IndQNER (114 Surah)

Dokumen ini memuat spesifikasi formal, matematis, dan prosedural dari pipeline konstruksi dataset **Extended IndQNER**.

---

## 1. Arsitektur Umum Sistem

Pipeline terdiri dari 4 tahapan sekuensial terintegrasi:
1. **Tahap 1: Pra-Pemrosesan & Normalisasi Teks Target**
2. **Tahap 2: Perolehan Kandidat Entitas (4 Jalur Paralel)**
   * Jalur 1: QAC Proper Noun (`TAG == PN`) via Pivot-Based Alignment + 5 Guardrails
   * Jalur 2: QAC Ontological Concept Lemmas (`TAG == N` & `TAG == ADJ`)
   * Jalur 3: Seed Gazetteer & Multi-Word Expressions (Greedy Longest Match)
   * Jalur 4: RegEx Selingkung Teks Kemenag (Tanda Kurung & Aturan 5b Pemotongan Gelar)
3. **Tahap 2.5: Resolusi Konflik Span & Deduplikasi**
4. **Tahap 3: Pelabelan Entitas Bertingkat (Kamus IndQNER & LLM-as-Labeler Llama-3-8B)**
5. **Tahap 4: Konversi ke Format CoNLL BIO & Evaluasi Mutu**

---

## 2. Rincian Teknis Perolehan Entitas (Tahap 2)

### A. Jalur 1: QAC Proper Noun (`PN`) via Pivot Language
* **Masukan:** Token QAC dengan `TAG == 'PN'`.
* **Leksikon Pivot:** 107 Lema unik dipetakan ke *English Pivot* dan daftar varian transliterasi Indonesia (*Multi-Alias Dictionary*).
* **5 Guardrails Teknis:**
  1. **Sequential Index Alignment:** Mengunci kemunculan ke-$k$ token QAC pada ayat bersangkutan ke kemunculan kecocokan ke-$k$ pada teks terjemahan (menangani 675 ayat berkemunculan ganda).
  2. **Token Stripping with Offset Retention:** Klitik enklitis (`-lah`, `-pun`, `-kah`, `-nya`, `-ku`, `-mu`) dibersihkan sementara saat menghitung skor kemiripan, namun rentang offset karakter `(start_char, end_char)` tetap mempertahankan kata asli di kalimat.
  3. **Sliding Window N-gram:** Untuk nama majemuk (*Bani Israil*, *Dzul Qarnain*), pemadanan dilakukan pada jendela geser $N$-token.
  4. **Adaptive Length Threshold:**
     $$\text{ValidMatch}(v, t) = \begin{cases} 
     \text{True}, & \text{jika } |v| \le 4 \ \land \ \text{Levenshtein}(v, \text{Clean}(t)) \le 1 \\
     \text{True}, & \text{jika } |v| > 4 \ \land \ \left(1 - \frac{\text{Levenshtein}(v, \text{Clean}(t))}{\max(|v|, |\text{Clean}(t)|)}\right) \ge 0.85 \\
     \text{False}, & \text{lainnya}
     \end{cases}$$
  5. **Multi-Alias Lookup:** Menjaring variasi transliterasi (*Fir'aun / Firaun / Fir‘aun*, *Ya'qub / Yakub*).

### B. Jalur 2: QAC Ontological Concept Lemmas (`N` & `ADJ`)
* **Masukan:** Token QAC dengan `TAG == 'N'` atau `TAG == 'ADJ'`.
* **Klasifikasi Lema:**
  * **Kelompok A (Langsung):** Lema dengan tingkat pelabelan $\ge 80\%$ di data latih:
    * `>aroD` (bumi) $\rightarrow$ `AstronomicalBody`
    * `$amos` (matahari) $\rightarrow$ `AstronomicalBody`
    * `samaA^'` (langit) $\rightarrow$ `AstronomicalBody`
    * `qiya`map` (hari Kiamat) $\rightarrow$ `Event`
    * `jaHiym` (Jahim) $\rightarrow$ `AfterlifeLocation`
    * `Haj~` (haji) $\rightarrow$ `Event`
  * **Kelompok B (Bersyarat):** Memerlukan validasi fitur morfologi/konteks (misal: `qamar` hanya jika merujuk benda langit; `A^xir` bertag `ADJ` $\rightarrow$ *hari Akhir*).
  * **Kelompok C (Dikeluarkan):** Kata umum yang terbukti berlabel `O` di data acuan (*surga, neraka, malaikat, jin, setan, akhirat*). Dilarang dilabeli jika berdiri sendiri.

### C. Jalur 3: Seed Gazetteer (Frasa Majemuk Longest-Match)
* **Masukan:** Leksikon frasa multi-kata dari `train.txt` (64 pola), Tabel 1 Pedoman Pelabelan, dan 99 Asmaul Husna.
* **Algoritma:** *Greedy Longest Match First*.
* **Cakupan Utama:**
  * Sifat Ilahiah: *"Tuhan semesta alam"*, *"Tuhan Yang Maha Esa"*, *"Yang Mahaperkasa lagi Mahabijaksana"*.
  * Tokoh/Kaum Majemuk: *"Bani Israil"*, *"anak cucu Adam"*, *"Ahlulkitab"*.
  * Peristiwa: *"hari Kiamat"*, *"hari Akhir"*, *"hari Sabat"*.
  * Artefak: *"Masjidilharam"*, *"Baitullah"*, *"Ka‘bah"*, *"Lauh Mahfuz"*.

### D. Jalur 4: RegEx Selingkung Teks Kemenag & Aturan 5b
* **Masukan:** Teks terjemahan resmi Kemenag RI.
* **Pembersihan Awal:** Menghapus angka catatan kaki `\d+\)` (contoh: `Tuhan1)` $\rightarrow$ `Tuhan`).
* **Ekstraksi Tanda Kurung:** Pola `r'\(([^()]+)\)'`.
* **Penerapan Aturan Pedoman 5b (Pembersihan Gelar):**
  * Memotong prefiks gelar: `Nabi`, `Rasul`, `Raja`, `Malaikat`.
  * Contoh: `(Nabi Muhammad)` $\rightarrow$ hanya kata `"Muhammad"` yang diekstrak sebagai entitas `Messenger`.
* **Verifikasi Kamus:** Teks hasil pemotongan dicocokkan ke kamus referensi IndQNER.

---

## 3. Resolusi Konflik Span & Deduplikasi

Jika terdapat irisan batas karakter antar-jalur pada ayat yang sama:
1. **Longest Match Priority:** Span yang lebih panjang dan utuh diprioritaskan (contoh: *"hari Kiamat"* mengalahkan *"Kiamat"*).
2. **Boundary Trimming:** Membuang spasi awal/akhir dan tanda baca luar agar selaras dengan batas token CoNLL BIO.
3. **Deduplikasi Identik:** Jika span sama persis, gabungkan metadata asal jalur.

---

## 4. Pelabelan Entitas Bertingkat (Tahap 3)

* **Lapis 1 (Deterministik - Tanpa LLM):**
  Cek entitas ke Kamus IndQNER (dibangun dari `train.txt` & Tabel 1 Pedoman). Jika ditemukan $\rightarrow$ langsung beri label kelasnya (100% konsisten & bebas halusinasi).
* **Lapis 2 (Modular LLM-as-Labeler):**
  Jika entitas belum pernah terdaftar di kamus $\rightarrow$ kirim ke **Llama-3-8B** secara lokal dengan instruksi klasifikasi tertutup (memilih 1 dari 20 kelas yang sah dengan panduan definisi & contoh few-shot).

---

## 5. Desain Evaluasi & Pembagian Dataset

* **Dataset Acuan Benchmark:** IndQNER 1.0 (8 surah, 1.387 ayat, 2.575 entitas).
* **Partisi Data Latih & Uji:**
  * `train.txt` (1.050 ayat): Sumber penyusunan Kamus IndQNER & Leksikon Jalur 3.
  * `dev.txt` (161 ayat): Kalibrasi ambang batas similarity dan penyiapan contoh few-shot.
  * `test.txt` (176 ayat): **Data uji murni (unseen test set)** untuk evaluasi intrinsik.
* **Evaluasi Intrinsik:** Mengukur Strict Precision, Strict Recall, dan Strict F1-score pada `test.txt` menggunakan pustaka `seqeval`.
* **Evaluasi Ekstrinsik:** Melatih model downstream NER (IndoBERT) dengan skenario *apple-to-apple*: Model Baseline (`train.txt` 8 surah) vs Model Proposed (`train.txt` + 106 surah Extended IndQNER), keduanya diuji pada `test.txt` yang sama.

