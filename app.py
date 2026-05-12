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

# 3. ฟังก์ชันคำนวณ RSI แบบ Manual (เพื่อความเสถียรสูงสุด)
def calculate_rsi_manual(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 4. ดึงข้อมูล (เพิ่มระบบป้องกันการโดนบล็อก)
@st.cache_data(ttl=600)
def get_data(ticker_list):
    stock_data = []
    for symbol in ticker_list:
        try:
            df = yf.download(symbol, period="1mo", progress=False)
            if df.empty or len(df) < 15: continue
            
            # โหลด 5 โหมดหลัก
            df['RSI'] = calculate_rsi_manual(df['Close'])
            current_p = float(df['Close'].iloc[-1])
            prev_p = float(df['Close'].iloc[-2])
            current_rsi = float(df['RSI'].iloc[-1])
            
            # คำนวณส่วนต่างราคา (Change & Gap)
            change = ((current_p - prev_p) / prev_p) * 100
            target = target_prices.get(symbol, 0)
            gap = ((current_p - target) / target) * 100
            
            # โหมด Market Mood (อารมณ์ตลาด)
            if current_rsi < 35: mood = "🔥 น่าช้อน (คนกลัวมาก)"
            elif current_rsi < 45: mood = "📉 เริ่มถูก"
            elif current_rsi > 70: mood = "⚠️ ระวัง (คนโลภ)"
            else: mood = "⚖️ ปกติ"

            stock_data.append({
                "Ticker": symbol,
                "Price": round(current_p, 2),
                "Change %": f"{change:.2f}%",
                "RSI": round(current_rsi, 2),
                "Market Mood": mood,
                "Gap %": f"{gap:.2f}%"
            })
        except: continue
    return pd.DataFrame(stock_data)

# 5. แสดงผล
st.title("🎯 Chairman Nu Command Center V8.0")
st.sidebar.metric("Cash Available", "4,000 THB")

data = get_data(tickers)
if not data.empty:
    # โชว์ตาราง 5 โหมดครบถ้วน
    st.dataframe(data, use_container_width=True)
    
    # ไฮไลท์ตัวที่ RSI ต่ำสุด (จุดช้อนที่ดีที่สุด)
    best_deal = data.sort_values("RSI").iloc[0]
    if best_deal['RSI'] < 45:
        st.info(f"💡 **จาร์วิสสแกน:** {best_deal['Ticker']} ต่ำสุดในลิสต์! (RSI: {best_deal['RSI']})")
else:
    st.warning("⚠️ Yahoo Finance บล็อกการดึงข้อมูลชั่วคราว (Too Many Requests) กรุณารอ 1-2 นาทีแล้วกด Refresh หน้าเว็บครับ")
