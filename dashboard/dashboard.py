import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px

# Set Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Beijing Air Quality Dashboard",
    page_icon="🎈",
    layout="wide"
)

# Set Style Visualisasi
sns.set_theme(style="whitegrid")

# Load Data dengan Caching agar Performa Cepat
@st.cache_data
def load_data():
    df = pd.read_csv('dashboard/main_data.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])
    return df

main_df = load_data()

# -----------------------------------------------------------------------------
# SIDEBAR (FILTER DATA)
# -----------------------------------------------------------------------------

# Membuat 3 kolom di sidebar untuk posisi tengah (center alignment)
col1, col2, col3 = st.sidebar.columns([1, 2, 1])

with col2:
    st.image("https://cdn-icons-png.flaticon.com/512/495/495694.png", width=140)

st.sidebar.title("Filter Dashboard")

# Filter Rentang Tanggal
min_date = main_df['datetime'].dt.date.min()
max_date = main_df['datetime'].dt.date.max()

start_date, end_date = st.sidebar.date_input(
    label='Rentang Waktu',
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

# Filter Stasiun Pemantau
station_list = ['Semua Stasiun'] + list(main_df['station'].unique())
selected_station = st.sidebar.selectbox('Pilih Stasiun Pemantau', station_list)

# Penerapan Filter ke DataFrame
filtered_df = main_df[(main_df['datetime'].dt.date >= start_date) & 
                      (main_df['datetime'].dt.date <= end_date)]

if selected_station != 'Semua Stasiun':
    filtered_df = filtered_df[filtered_df['station'] == selected_station]

# -----------------------------------------------------------------------------
# HEADER DASHBOARD
# -----------------------------------------------------------------------------
st.title("Beijing Air Quality Analysis Dashboard")
st.markdown("Dashboard interaktif untuk memantau tren polusi udara (PM2.5) dan pengaruh faktor cuaca di Beijing.")

# Metric Cards
st.subheader(" Ringkasan Indikator Utama")
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_pm25 = filtered_df['PM2.5'].mean()
    st.metric("Rata-rata PM2.5", f"{avg_pm25:.2f} µg/m³")

with col2:
    avg_temp = filtered_df['TEMP'].mean()
    st.metric("Rata-rata Suhu", f"{avg_temp:.2f} °C")

with col3:
    avg_wspm = filtered_df['WSPM'].mean()
    st.metric("Kecepatan Angin", f"{avg_wspm:.2f} m/s")

with col4:
    total_records = len(filtered_df)
    st.metric("Total Observasi (Jam)", f"{total_records:,}")

st.divider()

# -----------------------------------------------------------------------------
# VISUALISASI 1: TREN BULANAN PM2.5 
# -----------------------------------------------------------------------------
st.subheader("1. Tren Rata-Rata Konsentrasi PM2.5 Bulanan")

monthly_df = filtered_df.groupby(['year', 'month'])['PM2.5'].mean().reset_index()
monthly_df['year_month'] = monthly_df['year'].astype(str) + '-' + monthly_df['month'].astype(str).str.zfill(2)

# Membuat Line Chart Interaktif dengan Plotly
fig_trend = px.line(
    monthly_df, 
    x='year_month', 
    y='PM2.5', 
    markers=True,
    labels={'year_month': 'Tahun-Bulan', 'PM2.5': 'Rata-Rata PM2.5 (µg/m³)'},
    title='Tren PM2.5 Bulanan di Beijing'
)

# Custom tampilan garis dan warna
fig_trend.update_traces(line_color='firebrick', line_width=2.5)
fig_trend.update_layout(xaxis_tickangle=-45, template='plotly_white')

# Menampilkan grafik plotly di Streamlit
st.plotly_chart(fig_trend, use_container_width=True)

st.caption(" Insight: Polusi PM2.5 menunjukkan fluktuasi musiman yang tajam, di mana konsentrasi melonjak tinggi pada bulan-bulan musim dingin (Desember–Februari).")

# -----------------------------------------------------------------------------
# VISUALISASI 2 & 3: KORELASI CUACA & BINNING (Menjawab Q2 & Analisis Lanjutan)
# -----------------------------------------------------------------------------
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("2. Korelasi Parameter Cuaca & PM2.5")
    
    corr_cols = ['PM2.5', 'TEMP', 'WSPM', 'PRES', 'DEWP']
    corr_matrix = filtered_df[corr_cols].corr()
    
    # Mengatur ukuran figure heatmap agar seimbang
    fig_corr, ax_corr = plt.subplots(figsize=(6, 5))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5, vmin=-1, vmax=1, ax=ax_corr, cbar_kws={'shrink': 0.8})
    
    plt.tight_layout()
    st.pyplot(fig_corr)
    st.caption(" Insight: Kecepatan angin (WSPM) dan Suhu (TEMP) memiliki korelasi negatif terhadap PM2.5. Angin kencang mempercepat dispersi polutan.")

with col_right:
    st.subheader("3. Distribusi Kategori Kualitas Udara")
    
    bins = [0, 35, 75, 150, 1000]
    labels = ['Baik', 'Sedang', 'Tidak Sehat', 'Sangat Tidak Sehat']
    
    filtered_df['pm25_category'] = pd.cut(filtered_df['PM2.5'], bins=bins, labels=labels)
    cat_counts = filtered_df['pm25_category'].value_counts().reindex(labels)
    
    # Mengatur ukuran figure barplot dan merapikan margin
    fig_cat, ax_cat = plt.subplots(figsize=(6, 5))
    colors = ['#2ecc71', '#f1c40f', '#e67e22', '#e74c3c']
    
    bars = ax_cat.bar(cat_counts.index, cat_counts.values, color=colors)
    ax_cat.set_ylabel('Jumlah Jam Observasi', fontsize=10)
    
    # Memberikan batas atas sumbu Y agar nilai angka di atas batang tidak terpotong
    ax_cat.set_ylim(0, max(cat_counts.values) * 1.15)
    
    # Memutar label sumbu X agar tidak bertabrakan
    ax_cat.set_xticklabels(cat_counts.index, rotation=15, ha='right', fontsize=9)
    
    # Menambahkan angka di atas bar
    for bar in bars:
        height = bar.get_height()
        if not pd.isna(height) and height > 0:
            ax_cat.annotate(f'{int(height):,}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # offset 3 points ke atas
                            textcoords="offset points",
                            ha='center', va='bottom', fontweight='bold', fontsize=9)
            
    plt.tight_layout()
    st.pyplot(fig_cat)
    st.caption(" Insight: Frekuensi akumulasi jam observasi pada kategori Tidak Sehat hingga Sangat Tidak Sehat menunjukkan tingginya paparan polusi di Beijing.")

# Atribusi

st.divider()
st.caption(
    "Data diperoleh dari repositori GitHub [HTI (marceloreis/HTI)](https://github.com/marceloreis/HTI) "
    "berlisensi GPL 3.0 | Copyright © 2026 - [HA/The Query Trailblazer](https://github.com/thequerytrailblazer/beijing-air-quality-analysis)"
)