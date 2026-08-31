"""
Dashboard Interaktif - Analisis Bike Sharing Dataset
=====================================================
Struktur folder yang diharapkan:
    submission/
    ├── dashboard/
    │   ├── main_data.csv   <- data bersih hasil export dari notebook.ipynb
    │   └── dashboard.py    <- file ini
    ├── data/
    │   ├── data_1.csv
    │   └── data_2.csv
    ├── notebook.ipynb
    ├── README.md
    ├── requirements.txt
    └── url.txt

Cara menjalankan (local):
    1. pip install -r ../requirements.txt   (atau requirements.txt di root submission)
    2. cd dashboard
    3. streamlit run dashboard.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

sns.set_theme(style="whitegrid")

# =========================================================
# KONFIGURASI HALAMAN
# =========================================================
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "main_data.csv"

# =========================================================
# LOAD DATA (main_data.csv = hasil export hour_clean dari notebook)
# =========================================================
@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["dteday"] = pd.to_datetime(df["dteday"])
    return df


try:
    hour_clean = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(
        f"File `main_data.csv` tidak ditemukan di `{DATA_PATH}`.\n\n"
        "Jalankan notebook.ipynb hingga selesai (bagian Cleaning Data) agar "
        "file `main_data.csv` otomatis ter-export ke folder `dashboard/`."
    )
    st.stop()

# Menurunkan data harian (day-level) dari data per jam (hour-level)
day_clean = (
    hour_clean.groupby("dteday", as_index=False)
    .agg(
        season_label=("season_label", "first"),
        year_actual=("year_actual", "first"),
        mnth=("mnth", "first"),
        casual=("casual", "sum"),
        registered=("registered", "sum"),
        cnt=("cnt", "sum"),
        temp=("temp", "mean"),
        atemp=("atemp", "mean"),
        hum=("hum", "mean"),
        windspeed=("windspeed", "mean"),
    )
)

# Kategori suhu (manual grouping) untuk analisis lanjutan
bins = [0, 0.25, 0.5, 0.75, 1.0]
labels = ["Dingin", "Sejuk", "Hangat", "Panas"]
day_clean["temp_category"] = pd.cut(
    day_clean["temp"], bins=bins, labels=labels, include_lowest=True
)

# =========================================================
# SIDEBAR - FILTER
# =========================================================
st.sidebar.header("🔍 Filter Data")

min_date = day_clean["dteday"].min()
max_date = day_clean["dteday"].max()

date_range = st.sidebar.date_input(
    "Rentang Tanggal",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

season_options = ["Spring", "Summer", "Fall", "Winter"]
selected_seasons = st.sidebar.multiselect(
    "Musim (Season)", options=season_options, default=season_options
)

day_type_options = st.sidebar.radio(
    "Tipe Hari (untuk analisis per jam)",
    options=["Semua", "Hari Kerja (Workingday)", "Hari Libur / Akhir Pekan"],
    index=0,
)

# Terapkan filter ke day_clean
day_filtered = day_clean[
    (day_clean["dteday"] >= pd.to_datetime(start_date))
    & (day_clean["dteday"] <= pd.to_datetime(end_date))
    & (day_clean["season_label"].isin(selected_seasons))
]

# Terapkan filter tanggal & musim ke hour_clean
hour_filtered = hour_clean[
    (hour_clean["dteday"] >= pd.to_datetime(start_date))
    & (hour_clean["dteday"] <= pd.to_datetime(end_date))
    & (hour_clean["season_label"].isin(selected_seasons))
]

if day_type_options == "Hari Kerja (Workingday)":
    hour_filtered = hour_filtered[hour_filtered["workingday"] == 1]
elif day_type_options == "Hari Libur / Akhir Pekan":
    hour_filtered = hour_filtered[hour_filtered["workingday"] == 0]

if day_filtered.empty or hour_filtered.empty:
    st.warning("Tidak ada data pada kombinasi filter yang dipilih. Silakan ubah filter.")
    st.stop()

# =========================================================
# HEADER
# =========================================================
st.title("🚲 Bike Sharing Dashboard")
st.markdown(
    "Dashboard ini menyajikan hasil analisis data peminjaman sepeda "
    "(Bike Sharing Dataset) tahun 2011-2012 secara interaktif."
)

# =========================================================
# RINGKASAN METRIK
# =========================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Peminjaman", f"{day_filtered['cnt'].sum():,.0f}")
with col2:
    st.metric("Rata-rata Harian", f"{day_filtered['cnt'].mean():,.0f}")
with col3:
    st.metric("Total Pengguna Casual", f"{day_filtered['casual'].sum():,.0f}")
with col4:
    st.metric("Total Pengguna Registered", f"{day_filtered['registered'].sum():,.0f}")

st.markdown("---")

# =========================================================
# PERTANYAAN 1: TREN BULANAN & PERBANDINGAN MUSIM
# =========================================================
st.header("Pertanyaan 1: Tren Peminjaman Bulanan & Pengaruh Musim")
st.caption(
    "Bagaimana performa dan tren total peminjaman sepeda per bulan sepanjang "
    "tahun 2011-2012, serta pada musim apa permintaan mencapai titik tertinggi?"
)

monthly_summary = (
    day_filtered.groupby(["year_actual", "mnth"])["cnt"].sum().reset_index()
)
monthly_summary["period"] = (
    monthly_summary["year_actual"].astype(str)
    + "-"
    + monthly_summary["mnth"].astype(str).str.zfill(2)
)
monthly_summary = monthly_summary.sort_values("period")

col_a, col_b = st.columns(2)

with col_a:
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    sns.lineplot(
        data=monthly_summary,
        x="period",
        y="cnt",
        marker="o",
        linewidth=2.5,
        color="#1f77b4",
        ax=ax1,
    )
    ax1.set_title("Tren Total Peminjaman Sepeda per Bulan", fontweight="bold")
    ax1.set_xlabel("Periode (Tahun-Bulan)")
    ax1.set_ylabel("Total Peminjaman")
    ax1.tick_params(axis="x", rotation=60)
    st.pyplot(fig1)

with col_b:
    season_order = [s for s in season_options if s in selected_seasons]
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    sns.barplot(
        data=day_filtered,
        x="season_label",
        y="cnt",
        order=season_order,
        palette="Blues_r",
        errorbar=None,
        ax=ax2,
    )
    ax2.set_title("Rata-rata Peminjaman Berdasarkan Musim", fontweight="bold")
    ax2.set_xlabel("Musim (Season)")
    ax2.set_ylabel("Rata-rata Peminjaman Harian")
    st.pyplot(fig2)

with st.expander("💡 Insight Pertanyaan 1"):
    st.markdown(
        "- Total peminjaman sepeda meningkat signifikan dari tahun 2011 ke 2012 "
        "di hampir semua bulan.\n"
        "- Musim **Fall (Gugur)** mencatat rata-rata peminjaman harian tertinggi, "
        "diikuti **Summer (Panas)**, sedangkan **Spring (Semi)** mencatat "
        "permintaan terendah akibat suhu dingin di awal tahun."
    )

st.markdown("---")

# =========================================================
# PERTANYAAN 2: POLA PER JAM & PERBANDINGAN TIPE PENGGUNA
# =========================================================
st.header("Pertanyaan 2: Pola Peminjaman per Jam & Tipe Pengguna")
st.caption(
    "Bagaimana pola peminjaman sepeda pada setiap jam dalam sehari antara hari "
    "kerja dibandingkan akhir pekan/libur, serta perbedaan karakteristik "
    "pengguna casual dan registered?"
)

hourly_daytype = (
    hour_filtered.groupby(["hr", "workingday"])
    .agg({"casual": "mean", "registered": "mean", "cnt": "mean"})
    .reset_index()
)
hourly_daytype["day_type"] = hourly_daytype["workingday"].map(
    {1: "Hari Kerja (Workingday)", 0: "Hari Libur / Akhir Pekan"}
)

col_c, col_d = st.columns(2)

with col_c:
    fig3, ax3 = plt.subplots(figsize=(8, 5))
    sns.lineplot(
        data=hourly_daytype,
        x="hr",
        y="cnt",
        hue="day_type",
        style="day_type",
        markers=True,
        dashes=False,
        palette=["#2ca02c", "#d62728"],
        linewidth=2.5,
        ax=ax3,
    )
    ax3.set_title("Pola Peminjaman per Jam", fontweight="bold")
    ax3.set_xlabel("Jam (0-23)")
    ax3.set_ylabel("Rata-rata Peminjaman")
    ax3.set_xticks(range(0, 24, 2))
    ax3.legend(title="Tipe Hari", fontsize=8)
    st.pyplot(fig3)

with col_d:
    hourly_work = hourly_daytype[hourly_daytype["workingday"] == 1]
    fig4, ax4 = plt.subplots(figsize=(8, 5))
    if not hourly_work.empty:
        ax4.plot(
            hourly_work["hr"], hourly_work["registered"],
            marker="s", label="Registered (Terdaftar)", color="#1f77b4", linewidth=2,
        )
        ax4.plot(
            hourly_work["hr"], hourly_work["casual"],
            marker="o", label="Casual (Kasual)", color="#ff7f0e", linewidth=2,
        )
        ax4.legend()
    else:
        ax4.text(0.5, 0.5, "Tidak ada data hari kerja\npada filter saat ini",
                  ha="center", va="center")
    ax4.set_title("Casual vs Registered (Hari Kerja)", fontweight="bold")
    ax4.set_xlabel("Jam (0-23)")
    ax4.set_ylabel("Rata-rata Peminjaman")
    ax4.set_xticks(range(0, 24, 2))
    st.pyplot(fig4)

with st.expander("💡 Insight Pertanyaan 2"):
    st.markdown(
        "- Pada **hari kerja**, pola peminjaman berbentuk bimodal dengan dua "
        "puncak tajam pukul 08:00 dan 17:00-18:00, didominasi pengguna "
        "**registered** — mengindikasikan penggunaan sebagai transportasi komuter.\n"
        "- Pada **hari libur/akhir pekan**, peminjaman meningkat bertahap dan "
        "memuncak pukul 12:00-16:00, dengan kontribusi pengguna **casual** yang "
        "meningkat signifikan untuk aktivitas rekreasi."
    )

st.markdown("---")

# =========================================================
# ANALISIS LANJUTAN (OPSIONAL)
# =========================================================
st.header("Analisis Lanjutan: Pengaruh Faktor Cuaca")

col_e, col_f = st.columns(2)

with col_e:
    weather_corr = day_filtered[
        ["temp", "atemp", "hum", "windspeed", "casual", "registered", "cnt"]
    ].corr()
    fig5, ax5 = plt.subplots(figsize=(7, 5))
    sns.heatmap(weather_corr, annot=True, fmt=".2f", cmap="coolwarm",
                linewidths=0.5, ax=ax5)
    ax5.set_title("Korelasi Variabel Cuaca vs Peminjaman", fontweight="bold")
    st.pyplot(fig5)

with col_f:
    temp_group_summary = (
        day_filtered.groupby("temp_category", observed=True)
        .agg({"cnt": "mean", "casual": "mean", "registered": "mean"})
        .reset_index()
    )
    fig6, ax6 = plt.subplots(figsize=(7, 5))
    sns.barplot(
        data=temp_group_summary, x="temp_category", y="cnt",
        order=["Dingin", "Sejuk", "Hangat", "Panas"], palette="YlOrRd", ax=ax6,
    )
    ax6.set_title("Rata-rata Peminjaman Berdasarkan Kategori Suhu", fontweight="bold")
    ax6.set_xlabel("Kategori Suhu")
    ax6.set_ylabel("Rata-rata Peminjaman Harian")
    st.pyplot(fig6)

with st.expander("💡 Insight Analisis Lanjutan"):
    st.markdown(
        "- Suhu (`temp`/`atemp`) berkorelasi **positif** paling kuat terhadap "
        "jumlah peminjaman, terutama pada pengguna casual.\n"
        "- Kelembapan (`hum`) dan kecepatan angin (`windspeed`) berkorelasi "
        "**negatif** terhadap jumlah peminjaman.\n"
        "- Rata-rata peminjaman meningkat dari kategori suhu 'Dingin' menuju "
        "'Hangat', namun sedikit menurun pada kategori 'Panas', menandakan "
        "suhu ekstrem kurang ideal untuk bersepeda."
    )

st.markdown("---")

# =========================================================
# DATA MENTAH (OPSIONAL)
# =========================================================
with st.expander("📄 Lihat Data Harian (day_clean) Setelah Filter"):
    st.dataframe(
        day_filtered[
            ["dteday", "season_label", "temp_category",
             "casual", "registered", "cnt"]
        ].reset_index(drop=True)
    )

st.caption("Sumber data: Bike Sharing Dataset (Capital Bikeshare, 2011-2012)")
