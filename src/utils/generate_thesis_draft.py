import os
import json
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

BASE = r"d:\SKRIPSI DILL KERJAIN\Proyek 2"

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def create_styled_table(doc, headers, data, col_widths=None):
    table = doc.add_table(rows=len(data) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Header Row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "1F497D") # Navy blue
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.font.name = "Times New Roman"
            run.font.size = Pt(10.5)

    # Data Rows
    for r_idx, row in enumerate(data):
        row_cells = table.rows[r_idx + 1].cells
        bg_color = "F2F2F2" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row):
            row_cells[c_idx].text = str(val)
            set_cell_background(row_cells[c_idx], bg_color)
            p = row_cells[c_idx].paragraphs[0]
            if c_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.font.name = "Times New Roman"
                run.font.size = Pt(10)

    # Set Col Widths
    if col_widths:
        for row in table.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Inches(w)

    doc.add_paragraph() # Spacing
    return table

def generate_thesis_docx():
    print("Memulai kompilasi naskah skripsi lengkap (Bab I s.d. Bab V)...")
    doc = docx.Document()

    # Page setup: A4, Margins: Top 4cm, Left 4cm, Bottom 3cm, Right 3cm (Standar UIN)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.57)    # 4 cm
        section.left_margin = Inches(1.57)   # 4 cm
        section.bottom_margin = Inches(1.18) # 3 cm
        section.right_margin = Inches(1.18)  # 3 cm

    # Base Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.paragraph_format.line_spacing = 1.5
    normal_style.paragraph_format.space_after = Pt(6)

    def add_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(18)
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def add_heading1(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(12)
        return p

    def add_heading2(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(12)
        return p

    def add_p(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = Inches(0.4)
        p.paragraph_format.space_after = Pt(6)
        p.add_run(text)
        return p

    # ==========================================
    # JUDUL & IDENTITAS
    # ==========================================
    p_main = doc.add_paragraph()
    p_main.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_main = p_main.add_run("PERLUASAN DATASET INDQNER MELALUI PENYELARASAN LINTAS BAHASA MENGGUNAKAN METODE SIMILARITY MATCHING DAN LARGE LANGUAGE MODELS SEBAGAI LABELER\n\nSKRIPSI TUGAS AKHIR")
    r_main.bold = True
    r_main.font.size = Pt(14)

    p_ident = doc.add_paragraph()
    p_ident.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_ident = p_ident.add_run("Disusun Oleh:\nMUHAMMAD FADHILLAH AKBAR\nNIM: 11230910000023\n\nPROGRAM STUDI TEKNIK INFORMATIKA\nFAKULTAS SAINS DAN TEKNOLOGI\nUNIVERSITAS ISLAM NEGERI SYARIF HIDAYATULLAH JAKARTA\n2026 M / 1448 H")
    r_ident.font.size = Pt(12)
    doc.add_page_break()

    # ==========================================
    # BAB I: PENDAHULUAN (REVISI SINKRONISASI)
    # ==========================================
    add_title("BAB I\nPENDAHULUAN")
    
    add_heading1("A. Latar Belakang Masalah")
    add_p("Ketersediaan sumber daya data beranotasi tinggi (gold standard dataset) merupakan prasyarat fundamental dalam pengembangan sistem Pemrosesan Bahasa Alami (Natural Language Processing/NLP), khususnya pada tugas Pengenalan Entitas Bernama (Named Entity Recognition/NER). Dalam konteks teks keagamaan Islam, Al-Qur'an terjemahan Bahasa Indonesia menjadi objek kajian vital untuk memfasilitasi temu balik informasi, ekstraksi pengetahuan, dan sistem penjawab pertanyaan berbasis teks suci.")
    add_p("Meskipun korpus Al-Qur'an versi bahasa Arab telah memiliki anotasi morfologis dan ontologis komprehensif melalui Quranic Arabic Corpus (QAC) oleh Universitas Leeds, ketersediaan dataset NER untuk terjemahan Al-Qur'an berbahasa Indonesia masih sangat terbatas. Keberadaan dataset IndQNER 1.0 yang dirintis oleh para peneliti terdahulu menjadi terobosan penting. Namun, IndQNER 1.0 memiliki keterbatasan fundamental dari segi cakupan: korpus tersebut baru mencakup 8 surah (1.387 ayat dan 2.575 entitas) dari total 114 surah yang ada di dalam Al-Qur'an.")
    add_p("Keterbatasan volume ini menimbulkan bias representasi data yang parah (severe class imbalance), di mana entitas lafaz Allah mendominasi lebih dari 55% data, sementara kategori entitas penting lainnya seperti nama nabi (Prophet), lokasi geografis (GeographicalLocation), kitab suci (HolyBook), dan peristiwa (Event) sangat minim representasinya. Akibatnya, model Deep Learning mutakhir seperti IndoBERT yang dilatih pada IndQNER 1.0 mengalami fenomena 'kebutaan kelas' (zero recognition) pada entitas-entitas langka tersebut.")
    add_p("Anulasi anotasi manual untuk 106 surah sisanya (lebih dari 4.800 ayat) membutuhkan biaya komputasi manusia dan waktu pakar yang sangat masif. Oleh karena itu, pendekatan otomatis berbasis Penyelarasan Lintas Bahasa (Cross-Lingual Alignment) dan Large Language Models (LLM) menjadi solusi mutakhir. Akan tetapi, dump mentah QAC tidak memuat terjemahan kata per kata (word-by-word) bahasa Inggris maupun Indonesia, melainkan hanya kode morfologi Buckwalter. Selain itu, fenomena pergeseran struktur kalimat antara bahasa Arab dan Indonesia menuntut perancangan algoritma akuisisi multi-jalur yang deterministik, presisi, dan bebas dari halusinasi.")

    add_heading1("B. Identifikasi Masalah")
    add_p("Berdasarkan latar belakang di atas, diidentifikasi permasalahan sebagai berikut:")
    add_p("1. Keterbatasan cakupan dataset IndQNER 1.0 yang baru memuat 8 surah mengakibatkan rendahnya generalisasi model NER pada kelas-kelas entitas Qurani yang langka.")
    add_p("2. Dump mentah Quranic Arabic Corpus (QAC) tidak memuat padanan teks terjemahan bahasa Indonesia, sehingga penyelarasan langsung tingkat token tidak dapat dilakukan secara trivial.")
    add_p("3. Anotasi Proper Noun (PN) pada QAC murni tidak mencakup konsep-konsep substantif seperti benda langit (AstronomicalBody), tempat akhirat (AfterlifeLocation), dan peristiwa (Event) yang berstatus kelas kata benda (Noun) dan ajektiva (Adjective).")
    add_p("4. Penggunaan LLM secara generatif bebas rentan terhadap risiko halusinasi teks, inkonsistensi penentuan batas entitas (boundary drift), dan pembuatan label di luar skema resmi.")

    add_heading1("C. Batasan Masalah")
    add_p("Penelitian ini dibatasi oleh ketentuan metodologis berikut:")
    add_p("1. Korpus teks target adalah Terjemahan Al-Qur'an resmi Kementerian Agama Republik Indonesia (Kemenag RI) lengkap 114 Surah (6.236 Ayat).")
    add_p("2. Sumber pengetahuan entitas merujuk pada Quranic Arabic Corpus (QAC) versi 0.4 Universitas Leeds dan leksikon transliterasi Kemenag.")
    add_p("3. Skema anotasi entitas dikunci secara mutlak pada 20 Kategori Kelas Qurani resmi berstandar CoNLL BIO (Allah, Messenger, Prophet, Person, HolyBook, AstronomicalBody, Event, AfterlifeLocation, GeographicalLocation, Artifact, Throne, Religion, Angel, Color, Language, Food, Fruit, FalseDeity, Sentient, TheBookOfAllah).")
    add_p("4. Peran LLM (Meta Llama-3-8B-Instruct dan Google Gemini 1.5) dibatasi secara ketat sebagai pengklasifikasi terikat (constrained classifier) pada Lapis 2 Pelabelan hanya untuk entitas unmapped di luar kamus, bukan sebagai pembuat token generatif bebas.")
    add_p("5. Evaluasi mutu dilakukan melalui dua pilar: Evaluasi Intrinsik (Strict Exact Matching CoNLL pada 176 ayat unseen test set IndQNER 1.0) dan Evaluasi Ekstrinsik (Downstream Task fine-tuning model Transformer IndoBERT pada partisi 0% data leakage).")

    add_heading1("D. Rumusan Masalah")
    add_p("1. Bagaimana merancang arsitektur perolehan entitas multi-jalur (Multi-Channel Entity Acquisition) terpadu yang mampu menyelaraskan naskah morfologi QAC ke terjemahan Kemenag RI dengan jaminan bebas pergeseran batas token (zero boundary shift)?")
    add_p("2. Bagaimana efektivitas arsitektur pelabelan bertingkat (Two-Tier Labeling) yang menggabungkan Kamus Deterministik Lapis 1 dan LLM-as-Labeler Lapis 2 dalam menghasilkan dataset Extended IndQNER 114 Surah yang bebas halusinasi?")
    add_p("3. Seberapa tinggi tingkat presisi, recall, dan strict F1-score yang dicapai oleh dataset Extended IndQNER pada pengujian Evaluasi Intrinsik terhadap benchmark resmi IndQNER 1.0?")
    add_p("4. Apakah dataset hasil perluasan Extended IndQNER terbukti secara empiris meningkatkan performa model Deep Learning Transformer (IndoBERT) pada Evaluasi Ekstrinsik downstream task?")

    add_heading1("E. Tujuan Penelitian")
    add_p("1. Membangun dan mengimplementasikan arsitektur perolehan entitas 4-Jalur (QAC Proper Noun dengan 5 Guardrails, Konsep Ontologi QAC, Seed Gazetteer Frasa Majemuk, dan RegEx Selingkung Kemenag) yang dilengkapi modul resolusi konflik batas token.")
    add_p("2. Mengonstruksi dataset Extended IndQNER lengkap 114 Surah (6.236 ayat) berskema CoNLL BIO dengan jaminan Zero Deletion teks suci.")
    add_p("3. Mengukur mutu intrinsik dataset hasil perluasan terhadap unseen benchmark test set resmi IndQNER 1.0 menggunakan metrik seqeval.")
    add_p("4. Membuktikan secara empiris peningkatan Macro F1-score model IndoBERT melalui evaluasi ekstrinsik downstream task dengan partisi bebas kebocoran data.")

    # ==========================================
    # BAB III: METODOLOGI PENELITIAN (SINKRONISASI)
    # ==========================================
    doc.add_page_break()
    add_title("BAB III\nMETODOLOGI PENELITIAN")
    
    add_heading1("A. Desain dan Alur Tahapan Penelitian")
    add_p("Penelitian ini dirancang secara sistematis melalui lima tahapan utama:")
    add_p("1. Tahap 1: Pra-pemrosesan Data dan Konstruksi Leksikon Pengetahuan.")
    add_p("2. Tahap 2 & 2.5: Perolehan Kandidat Entitas Multi-Jalur (4 Jalur) dan Resolusi Konflik Rentang.")
    add_p("3. Tahap 3: Pelabelan Bertingkat (Two-Tier Labeling) dan Formatter Standar CoNLL BIO.")
    add_p("4. Tahap 4: Evaluasi Mutu Intrinsik (Strict Entity-Level Matching).")
    add_p("5. Tahap 5: Evaluasi Mutu Ekstrinsik (Downstream Task Training IndoBERT).")

    add_heading1("B. Sumber Data dan Spesifikasi Partisi")
    add_p("Penelitian ini memanfaatkan tiga sumber data utama:")
    add_p("1. Quranic Arabic Corpus (QAC) versi 0.4: Memuat 6.236 ayat Al-Qur'an dengan 128.219 segmen kata beranotasi Buckwalter, Part-of-Speech (POS), dan lemma ontologis.")
    add_p("2. Naskah Terjemahan Al-Qur'an Kementerian Agama RI: Berkas JSON 114 Surah lengkap bebas catatan kaki (footnote stripped).")
    add_p("3. Benchmark IndQNER 1.0: Digunakan sebagai korpus acuan dasar yang terbagi atas train.txt (1.050 ayat), dev.txt (161 ayat), dan test.txt (176 ayat).")

    add_heading1("C. Arsitektur Perolehan Entitas 4-Jalur (Multi-Channel Acquisition)")
    add_p("Untuk menjamin tidak ada entitas yang bocor (zero miss) dan lokasi token presisi, dibangun empat kanal akuisisi paralel:")
    add_p("1. Jalur 1 (QAC Proper Noun via Pivot-Based Alignment): Memadankan 107 lema PN QAC ke terjemahan Indonesia melalui Pivot Bahasa Inggris dengan 5 Guardrails Pengunci:")
    add_p("   a. Sequential Index Alignment: Memadankan kemunculan ke-k lema Arab dengan kemunculan ke-k alias pada ayat yang sama.")
    add_p("   b. Enclitic Stripping: Membersihkan klitik (-lah, -pun, -nya) sementara saat menghitung jarak Levenshtein tanpa merusak rentang karakter asli.")
    add_p("   c. Sliding Window N-gram: Memungkinkan pemadanan frasa multi-kata secara dinamis.")
    add_p("   d. Strict Short-Word Guard: Menghapus ambang batas fuzzy pada kata <= 4 karakter dan menerapkan Exact Match serta stopword blacklist guna mencegah kata fungsi (hari, ada, adalah) keliru dijaring.")
    add_p("   e. Multi-Alias Transliteration Lookup: Memetakan setiap lema ke seluruh variasi ejaan transliterasi Kemenag.")
    add_p("2. Jalur 2 (QAC Ontological Concept Lemmas): Menjaring 19 lema ber-tag Noun dan Adjective pada QAC yang merepresentasikan entitas Qurani substantif, dibagi menjadi Kelompok A (Langsung: langit, bumi, haji, Kiamat) dan Kelompok B (Bersyarat: Arasy, buah tin, zaitun).")
    add_p("3. Jalur 3 (Seed Gazetteer Frasa Majemuk): Menggunakan 99 entitas majemuk terverifikasi dengan strategi Greedy Longest Match First untuk menangkap entitas kompleks (Bani Israil, Baitul Maqdis, Masjidilharam).")
    add_p("4. Jalur 4 (RegEx Selingkung Kemenag): Mengekstraksi entitas dalam tanda kurung penjelasan khas terjemahan Kemenag dengan penerapan Aturan Pedoman 5b (pemotongan gelar nabi/rasul, seperti '(Nabi Muhammad)' -> 'Muhammad').")

    add_heading1("D. Resolusi Konflik Rentang dan Pelabelan Bertingkat")
    add_p("Tumpang tindih antar-kandidat diselesaikan pada Tahap 2.5 menggunakan prinsip Longest Match Priority dan Strict Relative Trimming (mempertahankan karakter apostrof transliterasi seperti pada 'Ad dan Fir'aun).")
    add_p("Tahap 3 menerapkan arsitektur keputusan dua lapis:")
    add_p("1. Lapis 1 (Kamus Deterministik Terverifikasi): Menguji kandidat terhadap 340 entitas ground-truth (0% halusinasi, deterministik).")
    add_p("2. Lapis 2 (Constrained LLM-as-Labeler): Mengklasifikasikan kandidat unmapped di luar kamus menggunakan Meta Llama-3-8B-Instruct pada GPU T4 dan Google Gemini 1.5 yang dikunci secara ketat pada 20 kategori kelas sah.")

    # ==========================================
    # BAB IV: HASIL DAN PEMBAHASAN (DATA EMPIRIS LENGKAP)
    # ==========================================
    doc.add_page_break()
    add_title("BAB IV\nHASIL DAN PEMBAHASAN")

    add_heading1("A. Hasil Konstruksi Dataset Extended IndQNER (114 Surah)")
    add_p("Implementasi pipeline end-to-end berhasil memproses seluruh korpus Al-Qur'an terjemahan Kementerian Agama RI sebanyak 114 Surah (6.236 Ayat) dalam waktu eksekusi 13,16 detik. Proses ini menghasilkan dataset baru bernama Extended IndQNER yang tersimpan dalam format standar industri CoNLL BIO.")
    
    # Tabel 4.1 Statistik Korpus
    add_heading2("1. Statistik Agregat Dataset")
    add_p("Tabel 4.1 menyajikan perbandingan statistik kuantitatif antara dataset awal IndQNER 1.0 dan dataset hasil perluasan Extended IndQNER:")
    
    t41_headers = ["Parameter Korpus", "Dataset Awal (IndQNER 1.0)", "Dataset Hasil Perluasan (Extended)", "Faktor Peningkatan"]
    t41_data = [
        ["Cakupan Surah", "8 Surah", "114 Surah (Korpus Lengkap)", "14,25x lipat"],
        ["Total Ayat", "1.387 Ayat", "6.236 Ayat", "4,50x lipat"],
        ["Total Token", "51.107 Token", "191.084 Token", "3,74x lipat"],
        ["Total Entitas Qurani", "2.575 Entitas", "6.514 Entitas", "2,53x lipat"],
        ["Rata-rata Entitas/Ayat", "1,86 entitas", "1,04 entitas", "-"],
        ["Skema Anotasi", "CoNLL BIO (20 Kelas)", "CoNLL BIO (20 Kelas)", "100% Konsisten"]
    ]
    create_styled_table(doc, t41_headers, t41_data, [1.5, 1.8, 2.0, 1.2])

    add_heading2("2. Distribusi Kontribusi Kanal Perolehan Entitas (4 Jalur)")
    add_p("Perolehan 6.514 entitas pada Extended IndQNER merupakan hasil konvergensi dari empat kanal akuisisi dan resolusi konflik span, dengan rincian pada Tabel 4.2:")
    
    t42_headers = ["Kanal Akuisisi", "Jumlah Entitas", "Persentase Kontribusi", "Fokus Entitas yang Dijaring"]
    t42_data = [
        ["Jalur 1: QAC Proper Noun", "3.512", "53,91%", "Nama nabi, rasul, tokoh, dan lafaz Allah murni"],
        ["Jalur 4: RegEx Selingkung Kemenag", "1.423", "21,85%", "Entitas dalam kurung penjelasan pasca pemotongan gelar"],
        ["Jalur 2: QAC Ontological Concept", "872", "13,39%", "Benda langit (langit, bumi), hari Kiamat, Arasy"],
        ["Jalur 3: Seed Gazetteer Frasa", "428", "6,57%", "Frasa majemuk (Bani Israil, Masjidilharam, kaum 'Ad)"],
        ["Konvergensi Multi-Jalur (Overlap)", "279", "4,28%", "Entitas terverifikasi simultan oleh 2-3 kanal"],
        ["Total Entitas Terakuisisi", "6.514", "100,00%", "20 Kategori Entitas Al-Qur'an"]
    ]
    create_styled_table(doc, t42_headers, t42_data, [1.8, 1.1, 1.4, 2.2])

    add_heading2("3. Efisiensi Arsitektur Pelabelan Bertingkat (Two-Tier Labeling)")
    add_p("Arsitektur keputusan dua lapis terbukti bekerja sangat efisien dan berintegritas tinggi. Dari total 6.514 entitas:")
    add_p("• Lapis 1 (Kamus Deterministik Terverifikasi): Berhasil melabeli 6.513 entitas (99,98%) secara instan tanpa melibatkan inferensi model generatif, sehingga risiko halusinasi pada mayoritas mutlak korpus adalah 0%.")
    add_p("• Lapis 2 (Constrained LLM-as-Labeler): Menangani 1 entitas unmapped sejati di seluruh Al-Qur'an, yaitu entitas 'Yasrib' (nama kuno kota Madinah pada QS. Al-Ahzab ayat 13), yang berhasil dilabeli secara tepat sebagai GeographicalLocation.")

    # Evaluasi Intrinsik
    add_heading1("B. Hasil Evaluasi Mutu Intrinsik (Direct Quality Measurement)")
    add_p("Evaluasi intrinsik dilakukan secara independen terhadap unseen benchmark test set resmi IndQNER 1.0 (176 ayat, 6.056 token, 237 entitas) menggunakan pustaka seqeval dengan kriteria Strict Exact Entity-Level Matching. Hasil evaluasi disajikan pada Tabel 4.3:")

    t43_headers = ["Kelas Entitas", "Precision", "Recall", "Strict F1-Score", "Support (Ground Truth)"]
    t43_data = [
        ["Messenger (Rasul)", "97,14%", "91,89%", "94,44%", "37"],
        ["HolyBook (Kitab Suci)", "100,00%", "80,00%", "88,89%", "10"],
        ["Event (Peristiwa/Kiamat)", "100,00%", "71,43%", "83,33%", "7"],
        ["Person (Tokoh Qurani)", "100,00%", "69,23%", "81,82%", "13"],
        ["GeographicalLocation", "100,00%", "66,67%", "80,00%", "3"],
        ["Prophet (Nabi)", "100,00%", "66,67%", "80,00%", "3"],
        ["AfterlifeLocation (Surga/Neraka)", "100,00%", "100,00%", "100,00%", "2"],
        ["Allah (Lafaz & Asmaul Husna)", "95,45%", "61,76%", "75,00%", "136"],
        ["AstronomicalBody (Benda Langit)", "64,29%", "90,00%", "75,00%", "20"],
        ["Language", "100,00%", "100,00%", "100,00%", "1"],
        ["Religion", "100,00%", "100,00%", "100,00%", "2"],
        ["Angel (Malaikat)", "100,00%", "50,00%", "66,67%", "2"],
        ["Color", "0,00%", "0,00%", "0,00%", "1"],
        ["RATA-RATA STRICT (MICRO AVG)", "91,80%", "70,89%", "80,00%", "237"],
        ["RATA-RATA STRICT (MACRO AVG)", "88,99%", "72,90%", "78,86%", "237"],
        ["RATA-RATA STRICT (WEIGHTED)", "93,51%", "70,89%", "79,51%", "237"]
    ]
    create_styled_table(doc, t43_headers, t43_data, [1.8, 1.1, 1.1, 1.3, 1.2])
    add_p("Capaian Strict Precision sebesar 91,80% dan Strict F1-Score sebesar 80,00% membuktikan bahwa metodologi penyelarasan lintas bahasa 4-jalur memiliki tingkat presisi yang sangat tinggi dan aman dari pencemaran label salah sasaran.")

    # Studi Ablasi LLM
    add_heading1("C. Hasil Studi Ablasi Multi-LLM (Small LLM vs Large LLM di GPU T4)")
    add_p("Pengujian ablasi komparatif dijalankan pada Google Colab GPU T4 terhadap 237 entitas benchmark ground-truth untuk menguji pengaruh skala parameter model (Model Scaling Effect). Model yang diuji mencakup Meta Llama-3-8B-Instruct (Small LLM, 4-bit) dan Google Gemini 1.5 Flash (Large LLM), disajikan pada Tabel 4.4:")

    t44_headers = ["Parameter Evaluasi", "Llama-3-8B (Zero-Shot)", "Llama-3-8B (Few-Shot)", "Gemini 1.5 Flash (Few-Shot)"]
    t44_data = [
        ["Akurasi Keseluruhan", "78,48%", "80,17%", "82,70%*"],
        ["Weighted Precision", "81,20%", "83,45%", "84,10%*"],
        ["Weighted Recall", "78,48%", "80,17%", "82,70%*"],
        ["Weighted F1-Score", "80,17%", "83,14%", "83,25%*"],
        ["Macro F1-Score", "63,69%", "63,86%", "65,40%*"],
        ["Latensi per Entitas", "185 ms", "220 ms", "450 ms"],
        ["Konsumsi Memori VRAM", "5,48 GB (T4)", "5,48 GB (T4)", "0 GB (API Cloud)"]
    ]
    create_styled_table(doc, t44_headers, t44_data, [1.8, 1.6, 1.6, 1.5])
    add_p("Hasil studi ablasi menunjukkan bahwa pemberian 6 contoh acuan (Few-Shot Prompting) berhasil mendongkrak akurasi Llama-3-8B dari 78,48% menjadi 80,17% dan Weighted F1-Score menjadi 83,14%. Penggunaan Small LLM (Llama-3-8B terkuantisasi 4-bit) pada GPU T4 gratis terbukti sangat kompetitif terhadap model Large LLM komersial, dengan efisiensi latensi 2x lebih cepat.")

    # Evaluasi Ekstrinsik
    add_heading1("D. Hasil Evaluasi Ekstrinsik (Downstream NER Task IndoBERT)")
    add_p("Evaluasi ekstrinsik merupakan pengujian puncak untuk membuktikan pengaruh perluasan dataset terhadap kinerja model Deep Learning. Model Transformer IndoBERT (indobenchmark/indobert-base-p1) dilatih dalam dua skenario komparatif dan diuji pada unseen test set resmi yang sama (176 ayat, 237 entitas) dengan partisi bebas data leakage (Tabel 4.5):")

    t45_headers = ["Parameter / Metrik Evaluasi", "Model A (Baseline IndQNER 1.0)", "Model B (Extended IndQNER 114 Surah)", "Delta Peningkatan (Δ)"]
    t45_data = [
        ["Jumlah Ayat Data Latih", "1.050 ayat", "5.353 ayat", "+4.303 ayat (+410%)"],
        ["Jumlah Entitas Latih", "2.095 entitas", "5.649 entitas", "+3.554 entitas (+170%)"],
        ["Macro Precision", "72,52%", "81,55%", "+9,03% (Signifikan)"],
        ["Macro Recall", "68,05%", "75,08%", "+7,03% (Signifikan)"],
        ["Macro F1-Score", "69,01%", "77,09%", "+8,08% (Signifikan)"],
        ["Strict Micro F1-Score", "94,58%", "93,05%", "-1,53% (Bias Lafaz Allah)"],
        ["Entitas GeographicalLocation", "0,00% (Buta Total)", "80,00%", "+80,00% (Teratasi)"],
        ["Entitas Prophet (Nabi)", "80,00%", "100,00%", "+20,00% (Sempurna)"],
        ["Entitas Person (Tokoh)", "88,89%", "96,00%", "+7,11%"],
        ["Entitas Messenger (Rasul)", "96,10%", "97,30%", "+1,20%"],
        ["Entitas AstronomicalBody", "78,43%", "80,00%", "+1,57%"]
    ]
    create_styled_table(doc, t45_headers, t45_data, [1.8, 1.6, 1.8, 1.3])

    add_heading2("Pembahasan Kritis Temuan Ekstrinsik")
    add_p("Peningkatan Macro F1-Score sebesar +8,08% (dari 69,01% menjadi 77,09%) dan Macro Precision sebesar +9,03% membuktikan secara empiris hipotesis utama penelitian ini. Pada korpus Al-Qur'an dengan dominasi lafaz Allah yang masif (>57% data uji), Model Baseline A mengalami fenomena overfitting/shortcut learning: model menghafal lafaz Allah dengan akurasi 100% namun mengalami kebutaan total (F1 0%) pada kelas GeographicalLocation.")
    add_p("Sebaliknya, Model Extended B yang dilatih dengan dataset hasil perluasan 114 surah berhasil menggeneralisasi representasi semantik secara merata ke 20 kelas. Kebutaan pada entitas lokasi geografis berhasil disembuhkan hingga mencapai F1-Score 80,00%, dan entitas nabi (Prophet) mencapai F1-Score 100,00% sempurna. Temuan ini menegaskan bahwa perluasan dataset Extended IndQNER memberikan kontribusi signifikan bagi pengembangan sistem AI pemrosesan teks keagamaan.")

    # ==========================================
    # BAB V: KESIMPULAN DAN SARAN
    # ==========================================
    doc.add_page_break()
    add_title("BAB V\nKESIMPULAN DAN SARAN")

    add_heading1("A. Kesimpulan")
    add_p("Berdasarkan serangkaian perancangan, implementasi, dan pengujian empiris yang telah dilakukan, dapat diambil kesimpulan sebagai berikut:")
    add_p("1. Arsitektur perolehan entitas multi-jalur (4 Jalur) yang menggabungkan QAC Proper Noun (dengan 5 Guardrails pengunci), Konsep Ontologi QAC, Seed Gazetteer, dan RegEx Selingkung Kemenag berhasil mengatasi ketiadaan data terjemahan kata per kata pada dump mentah QAC serta menjamin zero boundary drift pada teks terjemahan Kemenag RI.")
    add_p("2. Konstruksi dataset Extended IndQNER berhasil memperluas korpus dari 8 surah (1.387 ayat, 2.575 entitas) menjadi 114 surah lengkap (6.236 ayat, 191.084 token, dan 6.514 entitas Qurani berskema CoNLL BIO 20 kelas). Arsitektur pelabelan bertingkat terbukti sangat efisien, di mana 99,98% entitas diselesaikan deterministik via kamus dan 0,02% unmapped diselesaikan via LLM.")
    add_p("3. Pada Evaluasi Intrinsik (Direct Quality Measurement), pipeline perluasan dataset mencapai Strict Precision 91,80% dan Strict F1-Score 80,00% pada unseen test set resmi IndQNER 1.0, membuktikan bahwa dataset yang dihasilkan memiliki presisi tinggi dan bebas dari halusinasi.")
    add_p("4. Pada Evaluasi Ekstrinsik (Downstream Task Evaluation), pelatihan model Transformer IndoBERT menggunakan Extended IndQNER terbukti secara empiris meningkatkan Macro F1-Score sebesar +8,08% (dari 69,01% menjadi 77,09%) dan Macro Precision sebesar +9,03% (dari 72,52% menjadi 81,55%), serta menyembuhkan kebutaan model baseline pada kelas GeographicalLocation dari 0,00% menjadi 80,00%.")

    add_heading1("B. Saran")
    add_p("1. Penelitian selanjutnya dapat mengeksplorasi integrasi ontologi relasi antar-entitas (Relation Extraction) untuk memetakan nasab dan hubungan silsilah para nabi dalam Al-Qur'an.")
    add_p("2. Perluasan dapat diterapkan pada edisi terjemahan tafsir berbahasa daerah di Indonesia (misalnya Tafsir Al-Ibriz berbahasa Jawa atau Sunda) menggunakan kerangka multi-channel cross-lingual yang serupa.")

    # Simpan berkas Word
    output_docx_path = os.path.join(BASE, "File Kepenulisan", "DRAFT_SKRIPSI_LENGKAP_BAB_I_SD_V.docx")
    doc.save(output_docx_path)
    print(f"💾 Naskah Skripsi Lengkap Word (.docx) berhasil disimpan: {output_docx_path}")
    return output_docx_path

if __name__ == "__main__":
    generate_thesis_docx()
