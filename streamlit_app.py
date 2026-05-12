import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Chairman Nu Command Center V5.6", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #121212; color: white; }
    h1, h2, h3 { color: #4FA3FF !important; }
    .buy-card { background-color: #1E1E1E; padding: 15px; border-radius: 10px; border-left: 5px solid #2ECC71; margin-bottom: 10px; }
    .sell-card { background-color: #1E1E1E; padding: 15px; border-radius: 10px; border-left: 5px solid #E74C3C; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. WATCHLIST ---
watchlist = ['NVDA', 'TSM', 'ASML', 'PLTR', 'GOOGL', 'AVGO', 'MSFT', 'AMZN', 'ARM', 'AMD', 'MU', 'NBIS', 'RKLB', 'JEPQ', 'SPYI', 'SOFI', 'UPST']

@st.cache_data(ttl=3600) # เก็บ Cache นานขึ้นเพื่อความเสถียร
def fetch_all_data():
    all_buys, all_sells = [], []
    prices = {}
    for ticker in watchlist:
        try:
            t = yf.Ticker(ticker)
            prices[ticker] = t.info.get('regularMarketPrice') or t.info.get('currentPrice') or 0
            df = t.insider_transactions
            if df is not None and not df.empty:
                df['Date'] = pd.to_datetime(df['Start Date'] if 'Start Date' in df.columns else df.index)
                df['Symbol'] = ticker
                # ดึงมา 100 รายการเพื่อให้ไม่พลาด CEO
                buys = df[df['Text'].str.contains('Purchase', case=False, na=False)].head(50)
                sells = df[df['Text'].str.contains('Sale', case=False, na=False)].head(50)
                if not buys.empty: all_buys.append(buys)
                if not sells.empty: all_sells.append(sells)
        except: continue
    return (pd.concat(all_buys) if all_buys else pd.DataFrame()), (pd.concat(all_sells) if all_sells else pd.DataFrame()), prices

try:
    buys_df, sells_df, current_prices = fetch_all_data()

    # หน้าแรก: จับตาปลาวาฬ
    st.title("🐳 จับตาปลาวาฬ (Deep Scan Mode)")
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("🟢 รายการซื้อ (เน้น CEO/Director)")
        if not buys_df.empty:
            # เรียงตามวันที่ล่าสุด
            for _, row in buys_df.sort_values('Date', ascending=False).head(30).iterrows():
                st.markdown(f'<div class="buy-card"><b>{row["Symbol"]}</b> | {row["Date"].strftime("%d/%m/%y")}<br><b>{row["Insider"]}</b> ({row.get("Position", "N/A")})<br>ซื้อ: {int(row["Shares"]):,} หุ้น</div>', unsafe_allow_html=True)
        else: st.info("ยังไม่มีรายงานการซื้อใหม่ในระบบ SEC")

    with c2:
        st.subheader("🔴 รายการขาย")
        if not sells_df.empty:
            for _, row in sells_df.sort_values('Date', ascending=False).head(30).iterrows():
                st.markdown(f'<div class="sell-card"><b>{row["Symbol"]}</b> | {row["Date"].strftime("%d/%m/%y")}<br><b>{row["Insider"]}</b><br>ขาย: {int(row["Shares"]):,} หุ้น</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {e}")
