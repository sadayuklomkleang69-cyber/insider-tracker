import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="Chairman Nu Command Center V8.0", layout="wide")
st_autorefresh(interval=300000, key="datarefresh") # Refresh ทุก 5 นาที

# 2. ข้อมูลเป้าหมาย
target_prices = {
    "NVDA": 210.00, "TSM": 380.00, "ASML": 1450.00, "PLTR": 130.00, 
    "GOOGL": 380.00, "AVGO": 400.00, "MSFT": 400.00, "AMZN": 260.00, 
    "ARM": 200.00, "AMD": 430.00, "MU": 730.00, "RKLB": 110.00
}
tickers = list(target_prices.keys())

# 3. ฟังก์ชันคำนวณ RSI แบบเสถียร
def calculate_rsi_manual(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 4. ดึงข้อมูล (อัปเกรดระบบป้องกันการโดนบล็อก)
@st.cache_data(ttl=900) # เก็บ Cache ไว้ 15 นาที เพื่อลดภาระการ Request
def get_data(ticker_list):
    stock_data = []
    
    # สร้าง Placeholder สำหรับแจ้งสถานะ
    status_text = st.empty()
    
    for symbol in ticker_list:
        try:
            # ดึงข้อมูลโดยกำหนดสิทธิ์ (Session) เพื่อเลี่ยงการโดนมองว่าเป็น Bot
            ticker_obj = yf.Ticker(symbol)
            df = ticker_obj.history(period="1mo")
            
            if df.empty or len(df) < 15:
                continue

            # คำนวณค่าทางเทคนิค
            df['RSI'] = calculate_rsi_manual(df['Close'])
            current_p = float(df['Close'].iloc[-1])
            prev_p = float(df['Close'].iloc[-2])
            current_rsi = float(df['RSI'].iloc[-1])

            # คำนวณส่วนต่างราคา
            change = ((current_p - prev_p) / prev_p) * 100
            target = target_prices.get(symbol, 0)
            gap = ((current_p - target) / target) * 100

            # วิเคราะห์อารมณ์ตลาด (Logic Jarvis)
            if current_rsi < 35: mood = "🔥 น่าช้อน (Extreme Fear)"
            elif current_rsi < 45: mood = "📉 เริ่มถูก (Discount)"
            elif current_rsi > 70: mood = "⚠️ ระวัง (Extreme Greed)"
            else: mood = "⚖️ ปกติ"

            stock_data.append({
                "Ticker": symbol,
                "Price": round(current_p, 2),
                "Change %": f"{change:+.2f}%",
                "RSI": round(current_rsi, 2),
                "Market Mood": mood,
                "Gap to Target %": f"{gap:+.2f}%"
            })
            
            # หน่วงเวลาเล็กน้อยระหว่างตัว เพื่อไม่ให้โดนจับได้
            time.sleep(0.5) 
            
        except Exception as e:
            continue
            
    return pd.DataFrame(stock_data)

# 5. ส่วนแสดงผลหลัก
st.title("🎯 Chairman Nu Command Center V8.0")
st.sidebar.header("📊 Portfolio Status")
st.sidebar.metric("Cash Available", "4,000 THB")

# เรียกใช้ฟังก์ชันดึงข้อมูล
data = get_data(tickers)

if not data.empty:
    # แสดงตารางข้อมูลแบบเรียงตามโอกาส (RSI ต่ำสุดขึ้นก่อน)
    st.subheader("🚀 Market Opportunity Scan")
    styled_data = data.sort_values("RSI")
    st.dataframe(styled_data, use_container_width=True, height=500)

    # Jarvis Insight
    best_deal = styled_data.iloc[0]
    if best_deal['RSI'] < 40:
        st.success(f"💡 **จาร์วิสวิเคราะห์:** หุ้น **{best_deal['Ticker']}** อยู่ในจุดที่น่าสนใจที่สุดในตอนนี้ (RSI: {best_deal['RSI']})")
    else:
        st.info("💡 **จาร์วิสวิเคราะห์:** ตลาดอยู่ในช่วงพักตัว ยังไม่มีตัวไหนเข้าเขต Oversold รุนแรงครับ")
else:
    # กรณีโดนบล็อกจริงๆ จะแสดงปุ่มให้ Refresh แมนนวล
    st.error("🚨 ระบบดึงข้อมูลขัดข้อง (Yahoo Finance API Limit)")
    if st.button("ลองดึงข้อมูลใหม่อีกครั้ง"):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")
st.caption("© 2026 Chairman Nu Intelligence System • Data cached for 15 mins to prevent API blocking")
