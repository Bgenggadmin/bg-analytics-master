import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import pytz

# --- 1. CONFIG ---
st.set_page_config(page_title="B&G Analytics", layout="wide", page_icon="📊")
IST = pytz.timezone('Asia/Kolkata') # This line fixes the NameError in your footer

# --- 2. UPDATED RAW DATA LINKS ---
# Using the confirmed repository name from your tabs
PROD_RAW_URL = "https://raw.githubusercontent.com/Bgenggadmin/shopfloor-monitor/main/production_logs.csv"
LOGI_RAW_URL = "https://raw.githubusercontent.com/Bgenggadmin/bg-logistics-master/main/logistics_logs.csv"

st.title("📊 B&G Master Performance Analytics")

# --- 3. DATA FETCHING ---
@st.cache_data(ttl=60)
def fetch_data(url):
    try:
        # Fetching directly from the URL provided
        df = pd.read_csv(url)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        return df
    except Exception as e:
        # Returning an empty dataframe if the link fails
        return pd.DataFrame()

df_prod = fetch_data(PROD_RAW_URL)
df_logi = fetch_data(LOGI_RAW_URL)

# --- 4. FILTERS ---
st.sidebar.header("🗓️ Filter Period")
period = st.sidebar.radio("View Range", ["Weekly", "Monthly", "Yearly"], index=1)
now = datetime.now()
if period == "Weekly": 
    start_date = now - timedelta(days=7)
elif period == "Monthly": 
    start_date = now - timedelta(days=30)
else: 
    start_date = now - timedelta(days=365)

# --- 5. TOP SUMMARY CARDS ---
st.subheader(f"📈 {period} Summary")
sc1, sc2, sc3, sc4 = st.columns(4)

if not df_prod.empty:
    f_prod = df_prod[df_prod['Timestamp'] >= start_date]
    sc1.metric("Total Man-Hours", f"{f_prod['Hours'].sum():,.1f} Hrs")
    sc2.metric("Total Units Produced", f"{f_prod['Output'].sum():,.0f}")
else:
    sc1.metric("Total Man-Hours", "0.0 Hrs")
    sc2.metric("Total Units Produced", "0")

if not df_logi.empty:
    f_logi = df_logi[df_logi['Timestamp'] >= start_date]
    sc3.metric("Total KMs Driven", f"{f_logi['Distance'].sum():,.1f} KM")
    sc4.metric("Total Fuel Added", f"{f_logi['Fuel_Ltrs'].sum():,.1f} L")
else:
    sc3.metric("Total KMs Driven", "0.0 KM")
    sc4.metric("Total Fuel Added", "0.0 L")

st.divider()

# --- 6. PRODUCTION SECTION (Charts & Tables) ---
st.header("⚙️ Production Efficiency")
if not df_prod.empty:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🏗️ Jobwise Total Man-Hours")
        job_stats = f_prod.groupby("Job_Code")["Hours"].sum().reset_index()
        fig_job = px.bar(job_stats, x="Job_Code", y="Hours", text_auto=True, color_discrete_sequence=['#2E7D32'])
        st.plotly_chart(fig_job, use_container_width=True)

    with c2:
        st.subheader("👷 Worker Productivity (Output/Hr)")
        worker_stats = f_prod.groupby("Worker").agg({'Output': 'sum', 'Hours': 'sum'}).reset_index()
        worker_stats = worker_stats[worker_stats['Hours'] > 0]
        worker_stats['Efficiency'] = worker_stats['Output'] / worker_stats['Hours']
        fig_worker = px.bar(worker_stats, x="Worker", y="Efficiency", text_auto='.2f', color_discrete_sequence=['#1565C0'])
        st.plotly_chart(fig_worker, use_container_width=True)

    with st.expander("📋 View Detailed Production Table"):
        st.dataframe(f_prod.sort_values(by="Timestamp", ascending=False), use_container_width=True)
else:
    st.info("No production data found for this period. Check if the Production Log CSV is empty or the URL is incorrect.")

# --- 7. LOGISTICS SECTION (Charts & Tables) ---
st.divider()
st.header("🚛 Logistics Audit")
if not df_logi.empty:
    l1, l2 = st.columns(2)
    with l1:
        st.subheader("🛣️ KMs by Driver")
        driver_kms = f_logi.groupby("Driver")["Distance"].sum().reset_index()
        fig_kms = px.pie(driver_kms, values="Distance", names="Driver", hole=0.4)
        st.plotly_chart(fig_kms, use_container_width=True)

    with l2:
        st.subheader("⛽ Fuel Usage by Driver")
        driver_fuel = f_logi.groupby("Driver")["Fuel_Ltrs"].sum().reset_index()
        fig_fuel = px.bar(driver_fuel, x="Driver", y="Fuel_Ltrs", text_auto=True, color_discrete_sequence=['#EF6C00'])
        st.plotly_chart(fig_fuel, use_container_width=True)

    with st.expander("📋 View Detailed Logistics Table"):
        display_logi = f_logi.drop(columns=["Photo"]) if "Photo" in f_logi.columns else f_logi
        st.dataframe(display_logi.sort_values(by="Timestamp", ascending=False), use_container_width=True)

# FOOTER WITH CORRECTED TIMEZONE VARIABLE
st.caption(f"Last updated: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')} IST")
