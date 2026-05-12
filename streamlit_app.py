import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="Chairman Nu Command Center V8.0", layout="wide")
st_autorefresh(interval=300000, key="datarefresh")

# 2. ข้อมูลเป้าหมาย
target_prices = {
    "NVDA": 210.00, "TSM": 380.00, "ASML": 1450.00, "PLTR": 130.00,
    "GOOGL": 380.00, "AVGO": 400.00, "MSFT": 400.00, "AMZN": 260.00,
    "ARM": 200.00, "AMD": 430.00, "MU": 730.00, "RKLB": 110.00
}
tickers = list(target_prices.keys())

# 3. ฟังก์ชันคำนวณ RSI แบบไม่ง้อ Library
def calculate_rsi_manual(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 4. ดึงข้อมูล
@st.cache_data(ttl=300)
def get_data(ticker_list):
    stock_data = []
    for symbol in ticker_list:
        try:
            df = yf.download(symbol, period="1mo", progress=False)
            if df.empty or len(df) < 15: continue
            
            # คำนวณ RSI เอง
            df['RSI'] = calculate_rsi_manual(df['Close'])
            current_rsi = df['RSI'].iloc[-1]
            current_p = df['Close'].iloc[-1]
            target = target_prices.get(symbol, 0)
            dist_to_target = ((current_p - target) / target) * 100
            
            if current_rsi < 35: mood = "🔥 น่าช้อน (คนกลัวมาก)"
            elif current_rsi < 45: mood = "📉 เริ่มถูก"
            elif current_rsi > 70: mood = "⚠️ ระวัง (คนโลภ)"
            else: mood = "⚖️ ปกติ"

            stock_data.append({
                "Ticker": symbol,
                "Price": round(float(current_p), 2),
                "RSI": round(float(current_rsi), 2),
                "Market Mood": mood,
                "Gap %": f"{dist_to_target:.2f}%"
            })
        except:
            continue
    return pd.DataFrame(stock_data)

# 5. แสดงผล
st.title("🎯 Chairman Nu Command Center V8.0")
st.sidebar.metric("Cash Available", "4,000 THB")

data = get_data(tickers)
if not data.empty:
    st.dataframe(data, use_container_width=True)
    # ไฮไลท์ตัวที่ RSI ต่ำสุด
    best_deal = data.sort_values("RSI").iloc[0]
    st.info(f"💡 จาร์วิสสแกนแล้ว: {best_deal['Ticker']} มี RSI ต่ำสุดที่ {best_deal['RSI']} ({best_deal['Market Mood']})")
else:
    st.warning("กำลังเชื่อมต่อระบบตลาด... โปรดรอสักครู่")
