import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. Konfigurasi Halaman ---
st.set_page_config(page_title="Spotify Data Dashboard", layout="wide")

st.title("🎵 Dashboard Analisis Data Musik Spotify")
st.markdown("Analisis interaktif karakteristik lagu, popularitas, dan genre musik.")
st.markdown("---")

# --- 2. Memuat Data (Caching agar cepat) ---
@st.cache_data
def load_data():
    # Pastikan file csv ada di folder yang sama dengan app.py
    data = pd.read_csv("spotify_cleaned.csv")
    return data

# Load data
try:
    df = load_data()
    # Tampilkan cuplikan data jika user ingin melihat (Checkbox)
    if st.checkbox("Tampilkan Raw Data (5 Baris Teratas)"):
        st.write(df.head())
except FileNotFoundError:
    st.error("File 'spotify_cleaned.csv' tidak ditemukan. Pastikan file ada di folder yang sama.")
    st.stop()

# --- 3. Sidebar (Filter Interaktif) ---
st.sidebar.header("Filter Konfigurasi")
st.sidebar.write("Gunakan filter di bawah ini untuk mengubah tampilan grafik Scatter Plot.")

# Widget Filter Genre (Multiselect)
# Ambil daftar genre unik
unique_genres = df['track_genre'].unique()
selected_genres = st.sidebar.multiselect(
    "Pilih Genre untuk Dianalisis:",
    options=unique_genres,
    default=['pop', 'rock', 'k-pop', 'anime', 'chill'] # Default selection
)

# Filter data berdasarkan genre yang dipilih
filtered_df = df[df['track_genre'].isin(selected_genres)]

# --- 4. Visualisasi Data (Sesuai Bab 3 Metodologi) ---

# --- A. Analisis Univariat (Popularitas) ---
st.subheader("1. Sebaran Popularitas Lagu (Univariat)")
fig_hist = px.histogram(df, x='popularity', nbins=30, 
                        title="Distribusi Frekuensi Popularitas",
                        color_discrete_sequence=['#1DB954'])
st.plotly_chart(fig_hist, use_container_width=True)

# --- B. Analisis Bivariat (Korelasi) ---
st.subheader("2. Korelasi Antar Fitur Audio (Bivariat)")
col1, col2 = st.columns([2, 1])

with col1:
    # Heatmap
    corr_matrix = df.corr(numeric_only=True)
    fig_corr = px.imshow(corr_matrix, text_auto='.2f', aspect="auto",
                         color_continuous_scale='RdBu_r',
                         title="Matriks Korelasi (Heatmap)")
    st.plotly_chart(fig_corr, use_container_width=True)

with col2:
    st.info("""
    **Cara Membaca:**
    * **Merah Tua:** Korelasi Positif Kuat (Contoh: Energy & Loudness).
    * **Biru Tua:** Korelasi Negatif (Contoh: Acousticness & Energy).
    """)

# --- C. Visualisasi Interaktif & Filter (Multivariat) ---
st.subheader("3. Hubungan Energy vs Loudness (Multivariat)")
st.markdown(f"Menampilkan data untuk genre: **{', '.join(selected_genres)}**")

# Scatter Plot dengan data yang sudah difilter
if not filtered_df.empty:
    # Kita ambil sampel max 2000 agar tidak berat saat render di web
    if len(filtered_df) > 2000:
        plot_data = filtered_df.sample(2000, random_state=42)
    else:
        plot_data = filtered_df
        
    fig_scatter = px.scatter(plot_data, x='energy', y='loudness',
                             color='track_genre',
                             hover_data=['track_name', 'artists'],
                             title="Scatter Plot Interaktif: Energy vs Loudness",
                             template='plotly_dark')
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.warning("Silakan pilih minimal satu genre di Sidebar sebelah kiri.")

# --- D. Top Genre (Kategori) ---
st.subheader("4. Top 10 Genre Paling Populer")
genre_rank = df.groupby('track_genre')['popularity'].mean().sort_values(ascending=False).head(10).reset_index()

fig_bar = px.bar(genre_rank, x='popularity', y='track_genre', orientation='h',
                 title="Rata-rata Popularitas per Genre",
                 color='popularity', color_continuous_scale='Viridis')
fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_bar, use_container_width=True)