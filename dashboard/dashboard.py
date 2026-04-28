import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="E-commerce Dashboard", page_icon="🛒", layout="wide")

# Function to load data
import os

@st.cache_data
def load_data():
    # Base directory of the script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load datasets
    orders_df = pd.read_csv(os.path.join(base_dir, '../data/orders_dataset.csv'))
    order_items_df = pd.read_csv(os.path.join(base_dir, '../data/order_items_dataset.csv'))
    products_df = pd.read_csv(os.path.join(base_dir, '../data/products_dataset.csv'))
    product_category_df = pd.read_csv(os.path.join(base_dir, '../data/product_category_name_translation.csv'))
    order_reviews_df = pd.read_csv(os.path.join(base_dir, '../data/order_reviews_dataset.csv'))
    
    # Data Cleaning & Datetime conversion
    datetime_columns = ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"]
    for col in datetime_columns:
        orders_df[col] = pd.to_datetime(orders_df[col])
        
    orders_df.dropna(subset=['order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date'], inplace=True)
    products_df.dropna(subset=['product_category_name'], inplace=True)
    order_reviews_df.dropna(subset=['review_score'], inplace=True)
    
    return orders_df, order_items_df, products_df, product_category_df, order_reviews_df

# --- MAIN DASHBOARD LAYOUT ---
st.title("🛒 E-Commerce Analytics Dashboard")
st.markdown("Dashboard interaktif untuk menganalisis performa toko E-Commerce.")

with st.spinner("Memuat data..."):
    orders_df, order_items_df, products_df, product_category_df, order_reviews_df = load_data()

# --- DATA PREPARATION (MERGING) ---
# Merge datasets to get a comprehensive view
main_df = orders_df.merge(order_items_df, on='order_id', how='inner')
main_df = main_df.merge(products_df, on='product_id', how='inner')
main_df = main_df.merge(product_category_df, on='product_category_name', how='inner')
main_df = main_df.merge(order_reviews_df, on='order_id', how='left')

# --- SIDEBAR: FILTERS ---
st.sidebar.header("🔍 Filter Data")

# Date range filter
min_date = main_df['order_purchase_timestamp'].min().date()
max_date = main_df['order_purchase_timestamp'].max().date()

try:
    start_date, end_date = st.sidebar.date_input(
        label='Pilih Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
except ValueError:
    st.sidebar.error("Silakan pilih rentang tanggal yang valid.")
    start_date, end_date = min_date, max_date

# Apply filters
filtered_df = main_df[
    (main_df['order_purchase_timestamp'].dt.date >= start_date) &
    (main_df['order_purchase_timestamp'].dt.date <= end_date)
]

# --- KEY PERFORMANCE INDICATORS (KPIs) ---
st.subheader("💡 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

total_revenue = filtered_df['price'].sum()
total_orders = filtered_df['order_id'].nunique()
total_items = filtered_df['order_item_id'].count()
avg_review = filtered_df['review_score'].mean()

with col1:
    st.metric("Total Revenue", f"R$ {total_revenue:,.0f}")
with col2:
    st.metric("Total Orders", f"{total_orders:,}")
with col3:
    st.metric("Items Sold", f"{total_items:,}")
with col4:
    st.metric("Avg Review", f"{avg_review:.2f} ⭐")

st.divider()

# --- TABS FOR VISUALIZATION ---
tab1, tab2, tab3 = st.tabs(["📈 Tren Pendapatan & Volume", "⭐ Distribusi Rating (Terbawah)", "🏆 Top 10 Kategori Produk"])

# Tab 1: Q1 Logic
with tab1:
    st.header("Pendapatan & Volume Pemesanan (Electronics/IT vs Fashion)")
    
    # Logic from Q1
    q1_df = filtered_df.copy()

    electronics_it_categories = ['computers_accessories', 'telephony', 'electronics', 'computers', 'tablets_printing_image']
    fashion_categories = ['fashion_bags_accessories', 'fashion_shoes', 'fashion_male_clothing', 'fashion_female_clothing', 'fashion_childrens_clothes', 'fashion_underwear_beach', 'fashion_sport']

    def categorize(category):
        if category in electronics_it_categories:
            return 'Electronics & IT'
        elif category in fashion_categories:
            return 'Fashion'
        else:
            return 'Other'

    q1_df['category_group'] = q1_df['product_category_name_english'].apply(categorize)
    q1_df_grouped = q1_df[q1_df['category_group'] != 'Other']
    
    if not q1_df_grouped.empty:
        # Group by year-month to keep chronological order
        q1_df_grouped['year_month'] = q1_df_grouped['order_purchase_timestamp'].dt.to_period('M').astype(str)
        monthly_stats = q1_df_grouped.groupby(['year_month', 'category_group']).agg({
            'price': 'sum',
            'order_id': 'nunique' # distinct orders
        }).reset_index()
        monthly_stats.rename(columns={'price': 'revenue', 'order_id': 'order_volume'}, inplace=True)

        col1_1, col1_2 = st.columns(2)
        
        with col1_1:
            st.subheader("Total Pendapatan per Bulan")
            fig_rev, ax_rev = plt.subplots(figsize=(10, 6))
            sns.lineplot(data=monthly_stats, x='year_month', y='revenue', hue='category_group', marker='o', ax=ax_rev)
            plt.xticks(rotation=45)
            plt.ylabel("Pendapatan (R$)")
            plt.xlabel("Bulan")
            st.pyplot(fig_rev)
            
        with col1_2:
            st.subheader("Total Volume Pemesanan per Bulan")
            fig_vol, ax_vol = plt.subplots(figsize=(10, 6))
            sns.barplot(data=monthly_stats, x='year_month', y='order_volume', hue='category_group', ax=ax_vol)
            plt.xticks(rotation=45)
            plt.ylabel("Volume Pemesanan")
            plt.xlabel("Bulan")
            st.pyplot(fig_vol)
    else:
        st.info("Tidak ada data Electronics/IT atau Fashion pada rentang waktu ini.")

# Tab 2: Q2 Logic
with tab2:
    st.header("Distribusi Penilaian 5 Kategori Produk dengan Rata-rata Terendah")
    
    avg_rating = filtered_df.groupby('product_category_name_english')['review_score'].mean().reset_index()
    if not avg_rating.empty:
        worst_5_categories = avg_rating.sort_values(by='review_score', ascending=True).head(5)['product_category_name_english'].tolist()
        
        q2_worst_5_df = filtered_df[filtered_df['product_category_name_english'].isin(worst_5_categories)]
        score_distribution = q2_worst_5_df.groupby(['product_category_name_english', 'review_score']).size().unstack(fill_value=0)
        
        fig_rating, ax_rating = plt.subplots(figsize=(12, 6))
        score_distribution.plot(kind='bar', stacked=True, ax=ax_rating, colormap='viridis')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel("Jumlah Penilaian")
        plt.xlabel("Kategori Produk")
        plt.legend(title="Skor Penilaian (Bintang)")
        st.pyplot(fig_rating)
    else:
        st.info("Belum ada data review pada rentang waktu ini.")

# Tab 3: New Feature (Top Categories)
with tab3:
    st.header("Top 10 Kategori Produk dengan Penjualan Tertinggi")
    
    top_categories = filtered_df.groupby('product_category_name_english')['price'].sum().reset_index()
    top_categories = top_categories.sort_values(by='price', ascending=False).head(10)
    
    if not top_categories.empty:
        fig_top, ax_top = plt.subplots(figsize=(12, 6))
        sns.barplot(data=top_categories, y='product_category_name_english', x='price', ax=ax_top, palette='Blues_r')
        plt.xlabel("Total Pendapatan (R$)")
        plt.ylabel("Kategori Produk")
        st.pyplot(fig_top)
    else:
        st.info("Belum ada data pada rentang waktu ini.")

st.sidebar.markdown("---")
st.sidebar.caption("Proyek Analisis Data - Dicoding\nby Muhammad Fikran Naufal")
