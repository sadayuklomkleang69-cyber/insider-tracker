import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="Chairman Nu Command Center V5.5", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #121212; color: white; }
    h1, h2, h3 { color: #4FA3FF !important; }
    .buy-card { background-color: #1E1E1E; padding: 15px; border-radius: 10px; border-left: 5px solid #2ECC71; margin-bottom: 10px; }
    .sell-card { background-color: #1E1E1E; padding: 15px; border-radius: 10px; border-left: 5px solid #E74C3C; margin-bottom: 10px; }
    .metric-box { background-color: #262730; padding: 15px; border-radius: 10px; border: 1px solid #4FA3FF; }
    </style>
    """, unsafe_allow_html=True)

LINE_ACCESS_TOKEN = "Tt4FXXuT6v9qP2m9p9p9p9p9p9p9p9p9" 
USER_ID = "U60411800f135b37699709f1938507c31"

# --- 2. WATCHLIST จาก TRADINGVIEW ---
watchlist = [
    'NVDA', 'TSM', 'ASML', 'PLTR', 'GOOGL', 'AVGO', 'MSFT', 'AMZN', 'ARM', 
    'AMD', 'MU', 'NBIS', 'RKLB', 'JEPQ', 'SPYI', 'SOFI', 'UPST'
]

@st.cache_data(ttl=600)
def fetch_all_data():
    all_buys, all_sells = [], []
    prices = {}
    for ticker in watchlist:
        try:
            t = yf.Ticker(ticker)
            live_p = t.info.get('regularMarketPrice') or t.info.get('currentPrice') or 0
            prices[ticker] = live_p
            df = t.insider_transactions
            if df is not None and not df.empty:
                df['Date'] = pd.to_datetime(df['Start Date'] if 'Start Date' in df.columns else df.index)
                df['Symbol'] = ticker
                df['DisplayPrice'] = df['Price'].apply(lambda x: live_p if x == 0 or pd.isna(x) else x)
                buys = df[df['Text'].str.contains('Purchase', case=False, na=False)]
                sells = df[df['Text'].str.contains('Sale', case=False, na=False)]
                if not buys.empty: all_buys.append(buys)
                if not sells.empty: all_sells.append(sells)
        except: continue
    return (pd.concat(all_buys) if all_buys else pd.DataFrame()), (pd.concat(all_sells) if all_sells else pd.DataFrame()), prices

# --- 3. UI ---
with st.sidebar:
    st.title("👨‍✈️ Command Center")
    menu = st.radio("เลือกโหมด:", ["🐳 ระบบจับตาปลาวาฬ", "🧮 ตารางคำนวณอัจฉริยะ", "📡 ระบบ LINE"])
    st.info(f"อัปเดต: {datetime.now().strftime('%H:%M:%S')}")

try:
    buys_df, sells_df, current_prices = fetch_all_data()

    if menu == "🐳 ระบบจับตาปลาวาฬ":
        st.header("🐳 รายงานความเคลื่อนไหวคนใน")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🟢 รายการซื้อ")
            if not buys_df.empty:
                for _, row in buys_df.sort_values('Date', ascending=False).head(20).iterrows():
                    st.markdown(f'<div class="buy-card"><b>{row["Symbol"]}</b> | {row["Date"].strftime("%d/%m/%y")}<br>ผู้ซื้อ: {row["Insider"]}<br>จำนวน: {int(row["Shares"]):,} หุ้น @ ${row["DisplayPrice"]:.2f}</div>', unsafe_allow_html=True)
            else: st.warning("ไม่มีรายการซื้อใหม่")
        with c2:
            st.subheader("🔴 รายการขาย")
            if not sells_df.empty:
                for _, row in sells_df.sort_values('Date', ascending=False).head(20).iterrows():
                    st.markdown(f'<div class="sell-card"><b>{row["Symbol"]}</b> | {row["Date"].strftime("%d/%m/%y")}<br>ผู้ขาย: {row["Insider"]}<br>จำนวน: {int(row["Shares"]):,} หุ้น @ ${row["DisplayPrice"]:.2f}</div>', unsafe_allow_html=True)
            else: st.warning("ไม่มีรายการขายใหม่")

    elif menu == "🧮 ตารางคำนวณอัจฉริยะ":
        st.header("🧮 ตารางคำนวณอัจฉริยะ (Sync Dime)")
        selected = st.selectbox("เลือกหุ้น:", watchlist)
        auto_p = current_prices.get(selected, 0)
        
        col1, col2 = st.columns([1, 1.2])
        with
