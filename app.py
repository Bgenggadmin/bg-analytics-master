import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- 1. CONFIG ---
st.set_page_config(page_title="B&G Analytics", layout="wide", page_icon="📊")

# --- 2. RAW DATA LINKS (Update these to your actual GitHub URLs) ---
PROD_RAW_URL = "https://raw.githubusercontent.com/Bgenggadmin/bg-production-master/main/production_logs.csv"
LOGI_RAW_URL = "https://raw.githubusercontent.com/Bgenggadmin/bg-logistics-master/main/logistics_logs.csv"

st.title("📊 B&G Performance Analytics")

# --- 3. DATA LOADING ---
@st.cache_data(ttl=300) # Refreshes every 5 minutes
def fetch_data(url):
    try:
        df = pd.read_csv(url)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        return df
    except Exception as e:
        return pd.DataFrame()

df_prod = fetch_data(PROD_RAW_URL)
df_logi = fetch_data(LOGI_RAW_URL)

# --- 4. FILTERS ---
period = st.sidebar.radio("View Range", ["Weekly", "Monthly", "Yearly"])
now = datetime.now()
if period == "Weekly": start_date = now - timedelta(days=7)
elif period == "Monthly": start_date = now - timedelta(days=30)
else: start_date = now - timedelta(days=365)

# --- 5. PRODUCTION DASHBOARD ---
st.header("⚙️ Production Efficiency")
if not df_prod.empty:
    f_prod = df_prod[df_prod['Timestamp'] >= start_date]
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏗️ Jobwise Total Man-Hours")
        job_stats = f_prod.groupby("Job_Code")["Hours"].sum().reset_index()
        fig_job = px.bar(job_stats, x="Job_Code", y="Hours", text_auto=True, color_discrete_sequence=['#2E7D32'])
        st.plotly_chart(fig_job, use_container_width=True)

    with col2:
        st.subheader("👷 Worker Productivity (Output/Hr)")
        worker_stats = f_prod.groupby("Worker").agg({'Output': 'sum', 'Hours': 'sum'}).reset_index()
        worker_stats = worker_stats[worker_stats['Hours'] > 0]
        worker_stats['Efficiency'] = worker_stats['Output'] / worker_stats['Hours']
        fig_worker = px.bar(worker_stats, x="Worker", y="Efficiency", text_auto='.2f', color_discrete_sequence=['#1565C0'])
        st.plotly_chart(fig_worker, use_container_width=True)

# --- 6. LOGISTICS DASHBOARD ---
st.divider()
st.header("🚛 Logistics Audit")
if not df_logi.empty:
    f_logi = df_logi[df_logi['Timestamp'] >= start_date]
    lcol1, lcol2 = st.columns(2)

    with lcol1:
        st.subheader("🛣️ KMs Driven by Driver")
        driver_kms = f_logi.groupby("Driver")["Distance"].sum().reset_index()
        fig_kms = px.pie(driver_kms, values="Distance", names="Driver", hole=0.4)
        st.plotly_chart(fig_kms, use_container_width=True)

    with lcol2:
        st.subheader("⛽ Fuel Consumed (Litres)")
        driver_fuel = f_logi.groupby("Driver")["Fuel_Ltrs"].sum().reset_index()
        fig_fuel = px.bar(driver_fuel, x="Driver", y="Fuel_Ltrs", text_auto=True, color_discrete_sequence=['#EF6C00'])
        st.plotly_chart(fig_fuel, use_container_width=True)
