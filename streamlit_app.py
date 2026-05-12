import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import ta as ta

# 1. ตั้งค่าหน้ากระดาษ
st.set_page_config(page_title="Chairman Nu Command Center V7.2", layout="wide")
st_autorefresh(interval=300000, key="datarefresh")

# 2. ระบบจัดการเงินสด
if 'base_cash' not in st.session_state:
    st.session_state.base_cash = 4000

# 3. เป้าหมายราคา
target_prices = {
    "NVDA": 210.00, "TSM": 380.00, "ASML": 1450.00, "PLTR": 130.00,
    "GOOGL": 380.00, "AVGO": 400.00, "MSFT": 400.00, "AMZN": 260.00,
    "ARM": 200.00, "AMD": 430.00, "MU": 730.00, "RKLB": 110.00
}
tickers = list(target_prices.keys())

# 4. ฟังก์ชันดึงราคา + คำนวณอารมณ์ตลาด
@st.cache_data(ttl=300)
def get_live_data_with_sentiment(ticker_list):
    stock_data = []
    for symbol in ticker_list:
        try:
            t = yf.Ticker(symbol)
            df = t.history(period="1mo")
            if df.empty or len(df) < 14:
                continue

            # คำนวณ RSI
            rsi_series = ta.rsi(df['Close'], length=14)
            current_rsi = rsi_series.iloc[-1] if not rsi_series.empty else 50
            
            current_p = df['Close'].iloc[-1]
            prev_p = df['Close'].iloc[-2]
            change = ((current_p - prev_p) / prev_p) * 100
            target = target_prices.get(symbol, 0)
            dist_to_target = ((current_p - target) / target) * 100
            
            # กำหนด Market Mood
            if current_rsi < 30: sentiment = "🔥 น่าช้อน (คนกลัวสุดขีด)"
            elif current_rsi < 45: sentiment = "📉 เริ่มถูก (รอจังหวะ)"
            elif current_rsi > 70: sentiment = "⚠️ ระวัง (คนโลภเกินไป)"
            else: sentiment = "⚖️ ปกติ"

            stock_data.append({
                "Ticker": symbol, 
                "Price": round(current_p, 2), 
                "Change %": f"{change:.2f}%", 
                "RSI (Sentiment)": round(current_rsi, 2), 
                "Market Mood": sentiment, 
                "Gap": f"{dist_to_target:.2f}%"
            })
        except:
            continue
    return pd.DataFrame(stock_data)

# 5. แสดงผลหน้าจอหลัก
st.sidebar.metric("Cash Available", f"{st.session_state.base_cash:,} THB")

st.title("🎯 กลยุทธ์: ตัวไหนน่าช้อน? (รวมอารมณ์ตลาด)")

df_live = get_live_data_with_sentiment(tickers)

if not df_live.empty:
    # แสดงตารางสรุป
    st.dataframe(df_live[["Ticker", "Price", "Change %", "RSI (Sentiment)", "Market Mood", "Gap"]], use_container_width=True)
    
    # ระบบแจ้งเตือนตัวที่น่าช้อนที่สุด
    best_buy = df_live.sort_values(by="RSI (Sentiment)").iloc[0]
    if best_buy['RSI (Sentiment)'] < 45:
        st.success(f"🚀 **จาร์วิสแนะนำ:** {best_buy['Ticker']} น่าสนใจที่สุดในตอนนี้ (RSI: {best_buy['RSI (Sentiment)']})")
else:
    st.warning("กำลังดึงข้อมูลจากตลาด... โปรดรอสักครู่")
