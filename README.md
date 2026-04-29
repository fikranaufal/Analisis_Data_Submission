# E-Commerce Analytics Dashboard ✨

Proyek ini merupakan submission analisis data untuk kelas Analisis Data. Proyek ini berfokus pada analisis dataset E-Commerce dari tahun 2018 dan mencakup Jupyter Notebook untuk *Exploratory Data Analysis* (EDA) serta dashboard Streamlit untuk visualisasi interaktif.

## 📌 Gambaran Umum Proyek
Tujuan utama dari proyek ini adalah untuk menjawab dua pertanyaan bisnis utama berdasarkan data E-Commerce tahun 2018:
1. **Perbandingan Pendapatan & Volume Pemesanan:** Bagaimana perbandingan kategori "Electronics & IT" dan "Fashion" dalam hal pendapatan bulanan dan volume pemesanan?
2. **Distribusi Kategori dengan Penilaian Terendah:** Bagaimana distribusi skor ulasan untuk 5 kategori produk dengan rata-rata penilaian terendah, dan apa yang menyebabkan skor rendah tersebut?

## 📁 Struktur Proyek
```text
Analisis_Data_Submission/
│
├── dashboard/
│   └── dashboard.py          # Aplikasi dashboard Streamlit
│
├── data/                     # Direktori yang berisi dataset (file CSV)
│
├── Proyek_Analisis_Data.ipynb# Jupyter Notebook utama berisi EDA dan analisis lengkap
├── README.md                 # Dokumentasi proyek
├── requirements.txt          # Dependensi Python
└── url.txt                   # Referensi URL (jika ada)
```

## 🛠️ Persiapan dan Instalasi

1. **Navigasi ke direktori proyek:**
   Pastikan Anda berada di dalam direktori `Analisis_Data_Submission`.

2. **Buat virtual environment (Opsional namun disarankan):**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Untuk Windows
   # source .venv/bin/activate  # Untuk macOS/Linux
   ```

3. **Instal dependensi yang diperlukan:**
   Pastikan Anda telah menginstal pustaka *data science* utama dan Streamlit:
   ```bash
   pip install -r requirements.txt
   pip install streamlit seaborn
   ```

## 🚀 Cara Menjalankan Dashboard

Untuk meluncurkan dashboard interaktif, jalankan perintah berikut di terminal Anda dari root direktori proyek:

```bash
streamlit run dashboard/dashboard.py
```

Dashboard akan otomatis terbuka di *web browser* default Anda, memungkinkan Anda untuk menjelajahi EDA dan wawasan bisnis spesifik untuk tahun 2018.

## 📊 Fitur
- **Exploratory Data Analysis (EDA):** Wawasan mengenai distribusi harga produk, distribusi skor ulasan secara keseluruhan, dan tren pemesanan bulanan di tahun 2018.
- **Pelacakan Pendapatan & Volume:** Grafik garis dan batang untuk melacak kinerja antar grup kategori spesifik.
- **Distribusi Ulasan:** Grafik batang bertumpuk (*stacked bar chart*) yang memvisualisasikan rincian ulasan dari kategori produk dengan performa terendah.

## 👤 Penulis
- **Muhammad Fikran Naufal**
