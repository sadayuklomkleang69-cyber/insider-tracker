import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="Chairman Nu Insider", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #121212; color: white; }
    h1, h2, h3 { color: #4FA3FF !important; font-family: 'Kanit', sans-serif; }
    .buy-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #2ECC71;
        margin-bottom: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    .ticker-name { color: #F1C40F; font-size: 22px; font-weight: bold; }
    .price-text { color: #4FA3FF; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HEADER ---
st.title('🎯 ระบบจับตา "คนใน" (ฉบับเสถียรที่สุด)')
st.write(f"อัปเดตล่าสุด: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# --- 3. WATCHLIST (หุ้นเป้าหมายของท่านประธาน) ---
watchlist = ['NVDA', 'TSM', 'MSFT', 'PLTR', 'UPST', 'SOFI', 'GOOGL', 'AMD', 'TSLA']

@st.cache_data(ttl=600)
def get_yfinance_insider():
    all_data = []
    for ticker in watchlist:
        try:
            t = yf.Ticker(ticker)
            df = t.insider_transactions
            if df is not None and not df.empty:
                # กรองเฉพาะรายการซื้อ (Purchase)
                buys = df[df['Text'].str.contains('Purchase', case=False, na=False)].copy()
                if not buys.empty:
                    buys['Symbol'] = ticker
                    # บังคับให้ Index กลายเป็นคอลัมน์ เพื่อดึงวันที่ออกมาให้ได้
                    buys = buys.reset_index()
                    all_data.append(buys)
        except:
            continue
    return pd.concat(all_data) if all_data else pd.DataFrame()

# --- 4. EXECUTION ---
try:
    with st.spinner('จาร์วิสกำลังสแกนหาปลาวาฬ...'):
        final_df = get_yfinance_insider()

    if not final_df.empty:
        col_left, col_right = st.columns([1, 2])
        
        with col_left:
            st.subheader("📊 สัดส่วนการเก็บหุ้น")
            fig = px.pie(final_df, values='Shares', names='Symbol', hole=0.7,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_traces(textfont=dict(color='black', size=14), textinfo='percent+label')
            fig.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

        with col_right:
            st.subheader("💎 รายการซื้อล่าสุด (10 อันดับ)")
            # เรียงจากใหม่ไปเก่า
            final_df = final_df.sort_values(by=final_df.columns[0], ascending=False).head(10)
            
            for _, row in final_df.iterrows():
                # ด
