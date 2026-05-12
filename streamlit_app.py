import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="Chairman Nu Command Center V8.0", layout="wide")
st_autorefresh(interval=300000, key="datarefresh")

# รายชื่อหุ้นเป้าหมาย
target_prices = {
    "NVDA": 210.00, "TSM": 380.00, "ASML": 1450.00, "PLTR": 130.00,
    "GOOGL": 380.00, "AVGO": 400.00, "MSFT": 400.00, "AMZN": 260.00,
    "ARM": 200.00, "AMD": 430.00, "MU": 730.00, "RKLB": 110.00
}
tickers = list(target_prices.keys())

# ฟังก์ชันคำนวณ RSI แบบ Manual (ไม่ใช้ Library เสริมเพื่อตัดปัญหา Error)
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# ดึงข้อมูล
@st.cache_data(ttl=300)
def get_data(ticker_list):
    stock_data = []
    for symbol in ticker_list:
        try:
            df = yf.download(symbol, period="1mo", progress=False)
            if df.empty: continue
            
            # คำนวณค่าต่างๆ
            df['RSI'] = calculate_rsi(df['Close'])
            current_p = float(df['Close'].iloc[-1])
            current_rsi = float(df['RSI'].iloc[-1])
            target = target_prices.get(symbol, 0)
            gap = ((current_p - target) / target) * 100
            
            # กำหนด Mood
            if current_rsi < 35: mood = "🔥 น่าช้อน (คนกลัวมาก)"
            elif current_rsi < 45: mood = "📉 เริ่มถูก"
            else: mood = "⚖️ ปกติ"

            stock_data.append({
                "Ticker": symbol,
                "Price": round(current_p, 2),
                "RSI": round(current_rsi, 2),
                "Market Mood": mood,
                "Gap %": f"{gap:.2f}%"
            })
        except: continue
    return pd.DataFrame(stock_data)

# แสดงผล
st.title("🎯 Chairman Nu Command Center V8.0")
st.sidebar.metric("Cash Available", "4,000 THB")

data = get_data(tickers)
if not data.empty:
    st.dataframe(data, use_container_width=True)
else:
    st.warning("กำลังดึงข้อมูล... หากนานเกินไปให้กด Reboot App")
