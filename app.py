import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from streamlit_autorefresh import st_autorefresh

# --- 1. SETTINGS & REFRESH ---
st.set_page_config(layout="wide", page_title="Chairman Nu Command Center")
st_autorefresh(interval=300 * 1000, key="data_refresh")

# รายชื่อหุ้นที่ท่านประธานติดตาม
symbols = ["TSM", "NVDA", "MU", "MSFT", "AVGO", "GOOGL", "PLTR", "ARM", "AMD", "AMZN", "ASML", "RKLB", "NBIS"]

# --- 2. DATA ENGINE ---
@st.cache_data(ttl=300)
def get_live_data(tickers):
    results = []
    for t in tickers:
        try:
            # ดึงข้อมูลจาก Yahoo Finance
            ticker_obj = yf.Ticker(t)
            df = ticker_obj.history(period="1mo")
            if not df.empty:
                current_price = df['Close'].iloc[-1]
                prev_price = df['Close'].iloc[-2]
                change = ((current_price - prev_price) / prev_price) * 100
                
                # คำนวณ RSI 14 วัน ของจริง
                rsi_series = ta.rsi(df['Close'], length=14)
                current_rsi = rsi_series.iloc[-1] if not rsi_series.empty else 50
                
                results.append({
                    "Symbol": t,
                    "Price": round(current_price, 2),
                    "Change_%": round(change, 2),
                    "RSI": round(current_rsi, 2)
                })
        except:
            continue
    return pd.DataFrame(results)

# --- 3. UI DISPLAY ---
st.title("🚀 Chairman Nu Command Center V17.3 (Stable)")

with st.spinner('กำลังดึงข้อมูล Real-time...'):
    data = get_live_data(symbols)

if not data.empty:
    # สรุปภาพรวม
    m1, m2, m3 = st.columns(3)
    top_stock = data.loc[data['Change_%'].idxmax()]
    low_rsi = data.loc[data['RSI'].idxmin()]
    
    m1.metric("Top Gainer", top_stock['Symbol'], f"{top_stock['Change_%']}%")
    m2.metric("Oversold Alert", low_rsi['Symbol'], f"RSI: {low_rsi['RSI']}")
    m3.metric("Market Status", "LIVE", delta_color="normal")

    st.markdown("---")

    # ตารางข้อมูล
    st.subheader("📊 Strategic Monitor")
    
    def highlight_rsi(val):
        if val < 30: return 'background-color: #006400; color: white' # เขียวเข้ม (น่าซื้อ)
        if val > 70: return 'background-color: #8b0000; color: white' # แดงเข้ม (ระวัง)
        return ''

    st.dataframe(
        data.style.applymap(highlight_rsi, subset=['RSI']),
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("รอสักครู่ ระบบกำลัง Re-connect กับตลาดหุ้น...")

# --- 4. TERMINAL LOG ---
st.markdown("---")
st.caption("ระบบเชื่อมต่อตรงกับ Yahoo Finance API | อัปเดตทุก 5 นาที")
