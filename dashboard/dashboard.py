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

st.title("🛒 E-Commerce Dashboard")
st.markdown("Dashboard ini menampilkan analisis data E-Commerce untuk menjawab beberapa pertanyaan bisnis.")

with st.spinner("Memuat data..."):
    orders_df, order_items_df, products_df, product_category_df, order_reviews_df = load_data()

# Data Preparation for Q1
q1_df = orders_df.merge(order_items_df, on='order_id', how='inner')
q1_df = q1_df.merge(products_df, on='product_id', how='inner')
q1_df = q1_df.merge(product_category_df, on='product_category_name', how='inner')

q1_df_2017 = q1_df[q1_df['order_purchase_timestamp'].dt.year == 2017].copy()
q1_df_2017['month_num'] = q1_df_2017['order_purchase_timestamp'].dt.month
q1_df_2017['month'] = q1_df_2017['order_purchase_timestamp'].dt.month_name()

electronics_it_categories = ['computers_accessories', 'telephony', 'electronics', 'computers', 'tablets_printing_image']
fashion_categories = ['fashion_bags_accessories', 'fashion_shoes', 'fashion_male_clothing', 'fashion_female_clothing', 'fashion_childrens_clothes', 'fashion_underwear_beach', 'fashion_sport']

def categorize(category):
    if category in electronics_it_categories:
        return 'Electronics & IT'
    elif category in fashion_categories:
        return 'Fashion'
    else:
        return 'Other'

q1_df_2017['category_group'] = q1_df_2017['product_category_name_english'].apply(categorize)
q1_df_grouped = q1_df_2017[q1_df_2017['category_group'] != 'Other']

# Monthly revenue and volume
monthly_stats = q1_df_grouped.groupby(['month_num', 'month', 'category_group']).agg({
    'price': 'sum',
    'order_id': 'count'
}).reset_index()
monthly_stats.rename(columns={'price': 'revenue', 'order_id': 'order_volume'}, inplace=True)


# Data Preparation for Q2
q2_df = order_reviews_df.merge(order_items_df, on='order_id', how='inner')
q2_df = q2_df.merge(products_df, on='product_id', how='inner')
q2_df = q2_df.merge(product_category_df, on='product_category_name', how='inner')

avg_rating = q2_df.groupby('product_category_name_english')['review_score'].mean().reset_index()
worst_5_categories = avg_rating.sort_values(by='review_score', ascending=True).head(5)['product_category_name_english'].tolist()

q2_worst_5_df = q2_df[q2_df['product_category_name_english'].isin(worst_5_categories)]
score_distribution = q2_worst_5_df.groupby(['product_category_name_english', 'review_score']).size().unstack(fill_value=0)

# Sidebar
st.sidebar.header("Pilih Visualisasi")
option = st.sidebar.selectbox("Pertanyaan Bisnis", 
                              ["1. Pendapatan & Volume (Electronics/IT vs Fashion 2017)", 
                               "2. Distribusi Rating 5 Kategori Terbawah"])

if option == "1. Pendapatan & Volume (Electronics/IT vs Fashion 2017)":
    st.header("Pendapatan & Volume Pemesanan (Electronics/IT vs Fashion) di Tahun 2017")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Total Pendapatan per Bulan")
        fig_rev, ax_rev = plt.subplots(figsize=(10, 6))
        sns.lineplot(data=monthly_stats, x='month', y='revenue', hue='category_group', marker='o', ax=ax_rev)
        plt.xticks(rotation=45)
        plt.ylabel("Pendapatan")
        plt.xlabel("Bulan")
        plt.legend(title="Kategori")
        st.pyplot(fig_rev)
        
    with col2:
        st.subheader("Total Volume Pemesanan per Bulan")
        fig_vol, ax_vol = plt.subplots(figsize=(10, 6))
        sns.barplot(data=monthly_stats, x='month', y='order_volume', hue='category_group', ax=ax_vol)
        plt.xticks(rotation=45)
        plt.ylabel("Volume Pemesanan")
        plt.xlabel("Bulan")
        plt.legend(title="Kategori")
        st.pyplot(fig_vol)

elif option == "2. Distribusi Rating 5 Kategori Terbawah":
    st.header("Distribusi Penilaian 5 Kategori Produk dengan Rata-rata Terendah")
    
    fig_rating, ax_rating = plt.subplots(figsize=(12, 6))
    score_distribution.plot(kind='bar', stacked=True, ax=ax_rating, colormap='viridis')
    plt.xticks(rotation=45, ha='right')
    plt.ylabel("Jumlah Penilaian")
    plt.xlabel("Kategori Produk")
    plt.legend(title="Skor Penilaian (Bintang)")
    st.pyplot(fig_rating)

st.caption("Proyek Analisis Data - Dicoding - by Muhammad Fikran Naufal")
