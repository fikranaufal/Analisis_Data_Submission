import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

st.set_page_config(page_title="E-commerce Dashboard", page_icon="🛒", layout="wide")

@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    orders_df = pd.read_csv(os.path.join(base_dir, '../data/orders_dataset.csv'))
    order_items_df = pd.read_csv(os.path.join(base_dir, '../data/order_items_dataset.csv'))
    products_df = pd.read_csv(os.path.join(base_dir, '../data/products_dataset.csv'))
    product_category_df = pd.read_csv(os.path.join(base_dir, '../data/product_category_name_translation.csv'))
    order_reviews_df = pd.read_csv(os.path.join(base_dir, '../data/order_reviews_dataset.csv'))
    
    orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])
    
    return orders_df, order_items_df, products_df, product_category_df, order_reviews_df

st.title("🛒 E-Commerce Analytics Dashboard")
st.markdown("Dashboard ini difokuskan untuk mengeksplorasi dan menjawab dua pertanyaan bisnis utama berdasarkan data transaksi E-Commerce.")

with st.spinner("Memuat data..."):
    orders_df, order_items_df, products_df, product_category_df, order_reviews_df = load_data()

# Data Preparation
main_df = orders_df.merge(order_items_df, on='order_id', how='inner')
main_df = main_df.merge(products_df, on='product_id', how='inner')
main_df = main_df.merge(product_category_df, on='product_category_name', how='inner')
main_df = main_df.merge(order_reviews_df, on='order_id', how='left')

# Menyiapkan filter interaktif di halaman utama (Fitur Interaktif)
min_date = main_df['order_purchase_timestamp'].min().date()
max_date = main_df['order_purchase_timestamp'].max().date()

try:
    default_start = pd.to_datetime('2018-01-01').date()
    default_end = pd.to_datetime('2018-12-31').date()
    if default_start < min_date: default_start = min_date
    if default_end > max_date: default_end = max_date
except:
    default_start = min_date
    default_end = max_date

st.markdown("### 🗓️ Filter Rentang Waktu")
date_range = st.date_input(
    label="Pilih rentang waktu untuk mengubah data pada visualisasi di bawah:",
    value=[default_start, default_end],
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
elif isinstance(date_range, tuple) and len(date_range) == 1:
    start_date = date_range[0]
    end_date = date_range[0]
else:
    start_date = default_start
    end_date = default_end

# Filter berdasarkan tanggal yang dipilih pada sidebar interaktif
filtered_df = main_df[
    (main_df['order_purchase_timestamp'].dt.date >= start_date) & 
    (main_df['order_purchase_timestamp'].dt.date <= end_date)
].copy()

st.divider()

# --- Exploratory Data Analysis (EDA) ---
st.header("📊 Exploratory Data Analysis (EDA)")

with st.expander("Klik di sini untuk melihat visualisasi EDA dan penjelasan mendalam"):
    st.markdown("Bagian ini memberikan gambaran umum mengenai distribusi data pada rentang waktu yang dipilih sebelum kita masuk ke pertanyaan bisnis spesifik.")
    
    eda_col1, eda_col2 = st.columns(2)
    
    # 1. Distribusi Harga Produk
    with eda_col1:
        st.subheader("Distribusi Harga Produk")
        fig_price, ax_price = plt.subplots(figsize=(8, 5))
        sns.histplot(filtered_df['price'], bins=50, kde=True, color='skyblue', ax=ax_price)
        ax_price.set_xlim(0, 1000)
        ax_price.set_xlabel("Harga (R$)")
        ax_price.set_ylabel("Frekuensi")
        st.pyplot(fig_price)
        st.markdown('''
        **Penjelasan:**
        - **Right-Skewed Distribution:** Distribusi sangat condong ke kanan (right-skewed). Sebagian besar produk yang terjual berada di kisaran harga rendah (di bawah R$ 200).
        - **Long Tail:** Keberadaan produk dengan harga tinggi tetap ada namun jarang dibeli (terlihat dari garis tipis memanjang ke kanan).
        - **Dampak Bisnis:** Volume transaksi bertumpu pada barang murah. Sangat penting bagi platform untuk menjaga biaya kirim (freight) tetap terjangkau untuk produk-produk di rentang harga ini.
        ''')
    
    # 2. Distribusi Skor Penilaian (Semua Kategori)
    with eda_col2:
        st.subheader("Distribusi Skor Penilaian")
        fig_score, ax_score = plt.subplots(figsize=(8, 5))
        sns.countplot(data=filtered_df, x='review_score', palette='viridis', ax=ax_score)
        ax_score.set_xlabel("Skor Penilaian (Bintang)")
        ax_score.set_ylabel("Jumlah Ulasan")
        st.pyplot(fig_score)
        st.markdown('''
        **Penjelasan:**
        - **Dominasi Bintang 5:** Kepuasan pelanggan sangat tinggi secara umum. Sebagian besar pembeli memberikan nilai 5 bintang.
        - **Polarisasi Bintang 1:** Skor bintang 1 merupakan skor terbanyak ketiga setelah bintang 5 dan 4. Hal ini menunjukkan bahwa pelanggan yang memiliki pengalaman buruk cenderung bereaksi ekstrem dibandingkan memberikan nilai 2 atau 3.
        - **Dampak Bisnis:** Meskipun dominan memuaskan, tingginya lonjakan pada bintang 1 perlu dimitigasi. Tim Customer Support harus fokus pada keluhan yang memicu bintang 1 ini.
        ''')
        
    # 3. Tren Pemesanan per Bulan (Keseluruhan)
    st.subheader("Tren Volume Pemesanan per Bulan (Keseluruhan)")
    
    # Menggunakan filter yang sama untuk trend pemesanan
    orders_filtered = orders_df[
        (orders_df['order_purchase_timestamp'].dt.date >= start_date) & 
        (orders_df['order_purchase_timestamp'].dt.date <= end_date)
    ].copy()
    orders_filtered['purchase_month'] = orders_filtered['order_purchase_timestamp'].dt.month
    
    fig_trend, ax_trend = plt.subplots(figsize=(10, 4))
    sns.countplot(data=orders_filtered, x='purchase_month', palette='mako', ax=ax_trend)
    
    unique_months = sorted(orders_filtered['purchase_month'].unique())
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    labels = [month_names[m-1] for m in unique_months]
    
    ax_trend.set_xticks(range(len(unique_months)))
    ax_trend.set_xticklabels(labels)
    ax_trend.set_xlabel("Bulan")
    ax_trend.set_ylabel("Jumlah Pesanan")
    st.pyplot(fig_trend)
    st.markdown('''
    **Penjelasan:**
    - **Stabilitas Awal Tahun:** Jumlah pesanan cukup tinggi dan stabil di Kuartal 1 hingga pertengahan tahun 2018.
    - **Penurunan Signifikan:** Mulai bulan September, grafik menunjukkan tidak ada/sangat minim pesanan. Ini biasanya karena batas pencatatan dataset yang berhenti di akhir Agustus atau September awal tahun 2018.
    - **Dampak Bisnis:** Analisis historis menunjukkan platform berada dalam kondisi kesehatan transaksi yang stabil di paruh pertama 2018.
    ''')

st.divider()

# --- Pertanyaan 1 ---
st.header("1. Pendapatan & Volume Pemesanan (Electronics/IT vs Fashion)")

electronics_it_categories = ['computers_accessories', 'telephony', 'electronics', 'computers', 'tablets_printing_image']
fashion_categories = ['fashion_bags_accessories', 'fashion_shoes', 'fashion_male_clothing', 'fashion_female_clothing', 'fashion_childrens_clothes', 'fashion_underwear_beach', 'fashion_sport']

def categorize(category):
    if category in electronics_it_categories:
        return 'Electronics & IT'
    elif category in fashion_categories:
        return 'Fashion'
    else:
        return 'Other'

filtered_df['category_group'] = filtered_df['product_category_name_english'].apply(categorize)
q1_df_grouped = filtered_df[filtered_df['category_group'] != 'Other'].copy()

if not q1_df_grouped.empty:
    q1_df_grouped['month'] = q1_df_grouped['order_purchase_timestamp'].dt.to_period('M').astype(str)
    monthly_stats = q1_df_grouped.groupby(['month', 'category_group']).agg({
        'price': 'sum',
        'order_id': 'nunique'
    }).reset_index()
    monthly_stats.rename(columns={'price': 'revenue', 'order_id': 'order_volume'}, inplace=True)

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Total Pendapatan per Bulan")
        fig_rev, ax_rev = plt.subplots(figsize=(8, 5))
        sns.lineplot(data=monthly_stats, x='month', y='revenue', hue='category_group', marker='o', ax=ax_rev)
        plt.xticks(rotation=45)
        plt.ylabel("Pendapatan (R$)")
        plt.xlabel("Bulan")
        st.pyplot(fig_rev)
        
    with col2:
        st.subheader("Total Volume Pemesanan per Bulan")
        fig_vol, ax_vol = plt.subplots(figsize=(8, 5))
        sns.barplot(data=monthly_stats, x='month', y='order_volume', hue='category_group', ax=ax_vol)
        plt.xticks(rotation=45)
        plt.ylabel("Volume Pemesanan")
        plt.xlabel("Bulan")
        st.pyplot(fig_vol)

st.divider()

# --- Pertanyaan 2 ---
st.header("2. Distribusi Penilaian 5 Kategori Produk dengan Rata-rata Terendah")

avg_rating = filtered_df.groupby('product_category_name_english')['review_score'].mean().reset_index()
worst_5_categories = avg_rating.sort_values(by='review_score', ascending=True).head(5)['product_category_name_english'].tolist()

q2_worst_5_df = filtered_df[filtered_df['product_category_name_english'].isin(worst_5_categories)]
score_distribution = q2_worst_5_df.groupby(['product_category_name_english', 'review_score']).size().unstack(fill_value=0)
score_distribution_pct = score_distribution.div(score_distribution.sum(axis=1), axis=0) * 100

fig_rating, ax_rating = plt.subplots(figsize=(10, 5))
score_distribution_pct.plot(kind='bar', stacked=True, ax=ax_rating, colormap='viridis')
plt.xticks(rotation=45, ha='right')
plt.ylabel("Persentase Penilaian (%)")
plt.xlabel("Kategori Produk")
plt.legend(title="Skor Penilaian (Bintang)", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
st.pyplot(fig_rating)

st.markdown('''
**Penjelasan Singkat:**
- **Mengapa masih banyak bintang 5?** Distribusi rating di platform E-Commerce ini secara keseluruhan sangat didominasi oleh bintang 5 (bisa dilihat di bagian EDA). Bahkan untuk kategori terburuk pun, sebagian besar pembeli yang merasa "biasa saja" akan tetap memberikan bintang 5.
- **Mengapa mereka menjadi yang terburuk?** Jika dilihat dari **proporsi/persentase** (grafik di atas), kategori-kategori ini memiliki persentase rating 1, 2, dan 3 yang *jauh lebih besar* dibandingkan kategori lain yang sehat, sehingga menarik rata-rata rating mereka jatuh ke kisaran 2.2 hingga 3.5.
- **Volume vs Rata-rata:** Kategori seperti *home_comfort_2* sangat rentan karena penjualannya sangat kecil (rata-ratanya jatuh hanya karena beberapa ulasan buruk). Sementara *office_furniture* memiliki volume sangat besar, sehingga meskipun bintang 5 terlihat tinggi secara absolut, mereka menimbun ratusan ulasan bintang 1 yang harus diwaspadai.
''')

st.sidebar.markdown("**Proyek Analisis Data - Dicoding**<br>by Muhammad Fikran Naufal", unsafe_allow_html=True)
