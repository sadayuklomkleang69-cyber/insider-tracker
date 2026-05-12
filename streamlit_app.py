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
        background-color: #1E1E1E; padding: 20px; border-radius: 12px;
        border-left: 6px solid #2ECC71; margin-bottom: 10px;
    }
    .sell-card {
        background-color: #1E1E1E; padding: 20px; border-radius: 12px;
        border-left: 6px solid #E74C3C; margin-bottom: 10px;
    }
    .ticker-name { color: #F1C40F; font-size: 22px; font-weight: bold; }
    .price-text { color: #4FA3FF; font-size: 18px; }
    .sell-text { color: #E74C3C; font-weight: bold; }
    .buy-text { color: #2ECC71; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HEADER ---
st.title('🎯 ระบบจับตาปลาวาฬ: ซื้อ & ขาย')
st.write(f"ข้อมูลสดจาก Yahoo Finance | อัปเดต: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# --- 3. WATCHLIST ---
watchlist = ['NVDA', 'TSM', 'MSFT', 'PLTR', 'UPST', 'SOFI', 'GOOGL', 'AMD', 'TSLA', 'ARM', 'MU']

@st.cache_data(ttl=600)
def get_insider_combined():
    all_buys = []
    all_sells = []
    for ticker in watchlist:
        try:
            t = yf.Ticker(ticker)
            df = t.insider_transactions
            if df is not None and not df.empty:
                df['Symbol'] = ticker
                # แยกซื้อและขาย
                buys = df[df['Text'].str.contains('Purchase', case=False, na=False)].copy()
                sells = df[df['Text'].str.contains('Sale', case=False, na=False)].copy()
                if not buys.empty: all_buys.append(buys)
                if not sells.empty: all_sells.append(sells)
        except: continue
    return (pd.concat(all_buys) if all_buys else pd.DataFrame(), 
            pd.concat(all_sells) if all_sells else pd.DataFrame())

# --- 4. EXECUTION ---
try:
    with st.spinner('จาร์วิสกำลังสแกนหาการเคลื่อนไหว...'):
        buys_df, sells_df = get_insider_combined()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("🟢 รายการซื้อ (สะสมของ)")
        if not buys_df.empty:
            buys_df = buys_df.sort_index(ascending=False).head(10)
            for _, row in buys_df.iterrows():
                st.markdown(f"""
                <div class="buy-card">
                    <span class="ticker-name">{row['Symbol']}</span> | <span class="buy-text">BUY</span><br>
                    {int(row['Shares']):,} หุ้น @ ${row['Price']:.2f}<br>
                    <b>{row['Insider']}</b> ({row['Position']})
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("ยังไม่มีรายการซื้อใหม่")

    with col_right:
        st.subheader("🔴 รายการขาย (ระวังตัว)")
        if not sells_df.empty:
            sells_df = sells_df.sort_index(ascending=False).head(10)
            for _, row in sells_df.iterrows():
                st.markdown(f"""
                <div class="sell-card">
                    <span class="ticker-name">{row['Symbol']}</span> | <span class="sell-text">SELL</span><br>
                    {int(row['Shares']):,} หุ้น @ ${row['Price']:.2f}<br>
                    <b>{row['Insider']}</b> ({row['Position']})
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("ปลอดภัย! ยังไม่มีปลาวาฬเทขายในกลุ่มนี้ครับ")

except Exception as e:
    st.error(f"ระบบกำลังปรับปรุง: {e}")

if st.button('🔄 อัปเดตข้อมูล'):
    st.rerun()
