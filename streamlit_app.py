import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime

# --- 1. CONFIGURATION & REAL-TIME UI ---
st.set_page_config(page_title="Chairman Nu Real-time Tracker", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0A0A0A; color: #E0E0E0; }
    h1, h2, h3 { color: #00AAFF !important; }
    .whale-card { 
        background: linear-gradient(145deg, #1a1a1a, #252525);
        padding: 20px; border-radius: 15px; 
        border-left: 8px solid #00FF88; margin-bottom: 15px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.5);
    }
    .sell-card { border-left: 8px solid #FF4444; }
    .status-live { color: #00FF88; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LIST หุ้นจาก TRADINGVIEW (ครบทุกตัว) ---
watchlist = [
    'NVDA', 'TSM', 'ASML', 'PLTR', 'GOOGL', 'AVGO', 'MSFT', 'AMZN', 'ARM', 
    'AMD', 'MU', 'NBIS', 'RKLB', 'JEPQ', 'SPYI', 'SOFI', 'UPST'
]

@st.cache_data(ttl=60) # ตั้งให้ Refresh ทุก 1 นาที (Real-time สุดๆ)
def fetch_whale_data():
    all_data = []
    prices = {}
    for ticker in watchlist:
        try:
            t = yf.Ticker(ticker)
            # ดึงราคาสดจากกระดาน
            prices[ticker] = t.info.get('regularMarketPrice') or t.info.get('currentPrice') or 0
            df = t.insider_transactions
            if df is not None and not df.empty:
                df['Symbol'] = ticker
                df['Date'] = pd.to_datetime(df['Start Date'] if 'Start Date' in df.columns else df.index)
                all_data.append(df)
        except: continue
    return pd.concat(all_data) if all_data else pd.DataFrame(), prices

# --- 3. EXECUTION ---
st.title("🐳 Chairman Nu Intelligence: Whale Tracker")
st.markdown(f"สถานะระบบ: <span class='status-live'>● LIVE</span> | เชื่อมต่อตลาด NASDAQ ล่าสุด", unsafe_allow_html=True)

try:
    full_df, current_prices = fetch_whale_data()
    
    if not full_df.empty:
        # กรองเอาเฉพาะรายการล่าสุดจริงๆ 50 รายการแรกของตลาด
        latest_moves = full_df.sort_values('Date', ascending=False).head(50)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🟢 รายการช้อนซื้อ (ล่าสุด)")
            buys = latest_moves[latest_moves['Text'].str.contains('Purchase', case=False, na=False)]
            for _, row in buys.iterrows():
                st.markdown(f"""
                <div class="whale-card">
                    <h3 style='margin:0;'>{row['Symbol']} | ${current_prices.get(row['Symbol'], 0):.2f}</h3>
                    <p style='margin:5px 0;'><b>ใครซื้อ:</b> {row['Insider']} ({row['Position']})</p>
                    <p style='margin:0;'><b>จำนวน:</b> {int(row['Shares']):,} หุ้น | <b>วันที่:</b> {row['Date'].strftime('%d/%m/%Y')}</p>
                </div>
                """, unsafe_allow_html=True)
                
        with col2:
            st.subheader("🔴 รายการขาย (ล่าสุด)")
            sells = latest_moves[latest_moves['Text'].str.contains('Sale', case=False, na=False)]
            for _, row in sells.iterrows():
                st.markdown(f"""
                <div class="whale-card sell-card">
                    <h3 style='margin:0;'>{row['Symbol']} | ${current_prices.get(row['Symbol'], 0):.2f}</h3>
                    <p style='margin:5px 0;'><b>ใครขาย:</b> {row['Insider']}</p>
                    <p style='margin:0;'><b>จำนวน:</b> {int(row['Shares']):,} หุ้น | <b>วันที่:</b> {row['Date'].strftime('%d/%m/%Y')}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("กำลังกวาดข้อมูลปลาวาฬจาก SEC... กรุณารอ 10 วินาทีครับ")

except Exception as e:
    st.error(f"การเชื่อมต่อขัดข้อง: {e}")
