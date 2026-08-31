# Proyek Analisis Data: Bike Sharing Dataset

Proyek ini merupakan analisis data peminjaman sepeda (Bike Sharing Dataset,
Capital Bikeshare 2011-2012) yang mencakup proses data wrangling, exploratory
data analysis (EDA), visualisasi, hingga dashboard interaktif menggunakan
Streamlit.

## Struktur Direktori

```
submission
├───dashboard
│   ├───main_data.csv      # data bersih (hasil export dari notebook.ipynb)
│   └───dashboard.py       # source code dashboard Streamlit
├───data
│   ├───data_1.csv         # data mentah harian (day.csv)
│   └───data_2.csv         # data mentah per jam (hour.csv)
├───notebook.ipynb         # notebook proses analisis data end-to-end
├───README.md
├───requirements.txt
└───url.txt                # tautan dashboard yang sudah di-deploy
```

## Setup Environment

1. Buat virtual environment (opsional tapi disarankan):
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
   ```
2. Install seluruh library yang dibutuhkan:
   ```
   pip install -r requirements.txt
   ```

## Menjalankan Notebook (notebook.ipynb)

1. Pastikan `data_1.csv` (day.csv) dan `data_2.csv` (hour.csv) sudah berada
   di dalam folder `data/`.
2. Buka `notebook.ipynb` dengan Jupyter Notebook/JupyterLab/VS Code, lalu
   jalankan seluruh cell secara berurutan (`Run All`).
3. Pada bagian **Cleaning Data**, notebook akan otomatis meng-export data
   bersih (`hour_clean`) menjadi `dashboard/main_data.csv`. File inilah yang
   digunakan oleh dashboard Streamlit, sehingga notebook wajib dijalankan
   minimal sekali sebelum menjalankan dashboard.

## Menjalankan Dashboard (Local)

1. Pastikan `dashboard/main_data.csv` sudah tersedia (lihat langkah di atas).
2. Masuk ke folder `dashboard`:
   ```
   cd dashboard
   ```
3. Jalankan dashboard dengan Streamlit:
   ```
   streamlit run dashboard.py
   ```
4. Dashboard akan otomatis terbuka di browser pada alamat
   `http://localhost:8501`.

## Fitur Dashboard

- **Filter interaktif** di sidebar: rentang tanggal, musim (season), dan tipe
  hari (hari kerja / libur-akhir pekan).
- **Ringkasan metrik**: total peminjaman, rata-rata harian, total pengguna
  casual dan registered.
- **Pertanyaan 1**: tren peminjaman bulanan (2011-2012) dan rata-rata
  peminjaman berdasarkan musim.
- **Pertanyaan 2**: pola peminjaman per jam (hari kerja vs libur/akhir pekan)
  serta perbandingan pengguna casual vs registered.
- **Analisis Lanjutan**: korelasi faktor cuaca terhadap jumlah peminjaman dan
  pengelompokan (manual grouping) berdasarkan kategori suhu.

## Deploy Dashboard

Setelah dashboard berhasil di-deploy (misalnya melalui
[Streamlit Community Cloud](https://streamlit.io/cloud)), tautannya
dituliskan pada berkas `url.txt`.
