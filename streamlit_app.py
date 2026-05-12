import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="Chairman Nu Command Center", layout="wide")
st_autorefresh(interval=300000, key="datarefresh")

# หุ้นที่ท่านประธานตามอยู่
target_prices = {"MU": 730.00, "NVDA": 210.00, "TSM": 380.00, "ARM": 200.00}
tickers = list(target_prices.keys())

# ระบบคำนวณ RSI แบบแมนนวล (ป้องกัน Error)
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=300)
def get_data(ticker_list):
    results = []
    for s in ticker_list:
        try:
            df = yf.download(s, period="1mo", progress=False)
            if df.empty: continue
            current_p = float(df['Close'].iloc[-1])
            rsi = calculate_rsi(df['Close']).iloc[-1]
            target = target_prices.get(s, 0)
            gap = ((current_p - target) / target) * 100
            
            if rsi < 35: mood = "🔥 น่าช้อน (คนกลัวมาก)"
            elif rsi < 45: mood = "📉 เริ่มถูก"
            else: mood = "⚖️ ปกติ"
            
            results.append({"Ticker": s, "Price": round(current_p, 2), "RSI": round(rsi, 2), "Market Mood": mood, "Gap %": f"{gap:.2f}%"})
        except: continue
    return pd.DataFrame(results)

st.title("🎯 Chairman Nu Command Center V8.0")
st.sidebar.metric("Cash Available", "4,000 THB")

data = get_data(tickers)
if not data.empty:
    st.dataframe(data, use_container_width=True)
else:
    st.warning("กำลังดึงข้อมูล... กรุณารอสักครู่")
