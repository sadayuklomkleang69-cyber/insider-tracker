import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import pandas_ta as ta  # ระบบคำนวณอารมณ์ตลาด

# 1. ตั้งค่าหน้ากระดาษ
st.set_page_config(page_title="Chairman Nu Command Center V7.2", layout="wide")
st_autorefresh(interval=300000, key="datarefresh")

# 2. ระบบจัดการเงินสด
if 'base_cash' not in st.session_state:
    st.session_state.base_cash = 4000
if 'history_logs' not in st.session_state:
    st.session_state.history_logs = []

# 3. เป้าหมายราคา
target_prices = {
    "NVDA": 210.00, "TSM": 380.00, "ASML": 1450.00, "PLTR": 130.00,
    "GOOGL": 380.00, "AVGO": 400.00, "MSFT": 400.00, "AMZN": 260.00,
    "ARM": 200.00, "AMD": 430.00, "MU": 730.00, "RKLB": 110.00
}
tickers = list(target_prices.keys())

# 4. ฟังก์ชันดึงราคา + คำนวณอารมณ์ตลาด (RSI)
@st.cache_data(ttl=300)
def get_live_data_with_sentiment(ticker_list):
    stock_data = []
    for symbol in ticker_list:
        try:
            t = yf.Ticker(symbol)
            df = t.history(period="1mo") # ดึงข้อมูล 1 เดือนเพื่อหา RSI
            
            # คำนวณ RSI (อารมณ์ตลาด)
            df['RSI'] = ta.rsi(df['Close'], length=14)
            current_rsi = df['RSI'].iloc[-1]
            
            current_p = df['Close'].iloc[-1]
            prev_p = df['Close'].iloc[-2]
            change = ((current_p - prev_p) / prev_p) * 100
            target = target_prices.get(symbol, 0)
            dist_to_target = ((current_p - target) / target) * 100
            
            # วิเคราะห์อารมณ์
            if current_rsi < 30: sentiment = "😱 กลัวสุดขีด (น่าซื้อ)"
            elif current_rsi > 70: sentiment = "🤑 โลภเกินไป (ระวัง)"
            else: sentiment = "😐 ปกติ"

            stock_data.append({
                "Ticker": symbol,
                "Price": round(current_p, 2),
                "Change %": f"{change:.2f}%",
                "RSI (Sentiment)": round(current_rsi, 2),
                "Market Mood": sentiment,
                "Gap": f"{dist_to_target:.2f}%",
                "Raw_Gap": dist_to_target,
                "Raw_RSI": current_rsi
            })
        except:
            continue
    return pd.DataFrame(stock_data)

df_live = get_live_data_with_sentiment(tickers)

# --- ส่วนแสดงผล ---
st.title("🎯 กลยุทธ์: ตัวไหนน่าช้อน? (รวมอารมณ์ตลาด)")
st.sidebar.metric("Cash Available", f"{st.session_state.base_cash:,} THB")

# ตารางหลัก
st.dataframe(df_live[["Ticker", "Price", "Change %", "RSI (Sentiment)", "Market Mood", "Gap"]], use_container_width=True)

# 💡 ระบบประเมินความเสี่ยงโดยจาร์วิส
st.markdown("---")
st.subheader("💡 Jarvis Analysis: จังหวะช้อนที่ดีที่สุด")

# เงื่อนไข: ราคาต้องต่ำกว่าเป้า (Gap < 0) และ RSI ต้องต่ำ (คนกลัว)
perfect_buy = df_live[(df_live['Raw_Gap'] <= 0) & (df_live['Raw_RSI'] < 40)]

if not perfect_buy.empty:
    for _, row in perfect_buy.iterrows():
        st.success(f"🔥 **{row['Ticker']}** จังหวะนี้แหละ! ราคาถูกกว่าเป้า และคนกำลังกลัว (RSI: {row['RSI (Sentiment)']})")
else:
    st.info("📢 ตอนนี้ 'ราคา' อาจจะถึงเป้า แต่ 'อารมณ์ตลาด' ยังไม่นิ่ง (คนยังไม่หยุดเทขาย) รอก่อนดีกว่าครับประธาน")

# สรุปภาพรวม
worst_stock = df_live.loc[df_live['Raw_RSI'].idxmin()]
st.warning(f"🚨 หุ้นที่คนกลัวที่สุดตอนนี้คือ **{worst_stock['Ticker']}** (RSI: {worst_stock['RSI (Sentiment)']})")
