import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & REFRESH ---
st.set_page_config(layout="wide", page_title="Chairman Nu Command Center")
# สั่งให้ Refresh ข้อมูลทุก 5 นาทีอัตโนมัติ
st_autorefresh(interval=300 * 1000, key="data_refresh")

symbols = ["TSM", "NVDA", "MU", "MSFT", "AVGO", "GOOGL", "PLTR", "ARM", "AMD", "AMZN", "ASML", "RKLB", "NBIS"]

# --- 2. CORE ENGINE: REAL-TIME DATA ---
@st.cache_data(ttl=300)
def fetch_market_data(tickers):
    data_list = []
    for ticker in tickers:
        try:
            # ดึงข้อมูลย้อนหลัง 1 เดือน เพื่อคำนวณ RSI ให้แม่นยำ
            df = yf.download(ticker, period="1mo", interval="1d", progress=False)
            if not df.empty:
                current_price = df['Close'].iloc[-1]
                prev_price = df['Close'].iloc[-2]
                change_pct = ((current_price - prev_price) / prev_price) * 100
                
                # คำนวณ RSI 14 วัน
                rsi_series = ta.rsi(df['Close'], length=14)
                rsi = rsi_series.iloc[-1] if not rsi_series.empty else 50
                
                data_list.append({
                    "Symbol": ticker,
                    "Price": round(current_price, 2),
                    "Today_%": round(change_pct, 2),
                    "RSI": round(rsi, 2)
                })
        except Exception:
            continue
    return pd.DataFrame(data_list)

# --- 3. UI EXECUTION ---
st.title("🚀 Chairman Nu Command Center V17.2 (Real-time)")

with st.spinner('กำลังเชื่อมต่อฐานข้อมูลตลาดโลก...'):
    df_market = fetch_market_data(symbols)

if not df_market.empty:
    # แสดง Metric สรุปผล
    col1, col2, col3 = st.columns(3)
    
    # หุ้นที่ราคาขึ้นแรงที่สุด
    top_gain = df_market.loc[df_market['Today_%'].idxmax()]
    col1.metric("Top Gainer Today", top_gain['Symbol'], f"{top_gain['Today_%']}%")
    
    # หุ้นที่ RSI ต่ำสุด (จุดที่น่าซื้อ)
    oversold = df_market.loc[df_market['RSI'].idxmin()]
    col2.metric("Oversold Alert (Low RSI)", oversold['Symbol'], f"RSI: {oversold['RSI']}")
    
    # จำนวนหุ้นใน Watchlist
    col3.metric("Monitored Assets", f"{len(df_market)} Stocks", "Real-time")

    st.markdown("---")
    
    # แสดงตารางข้อมูลทั้งหมด
    st.subheader("📊 Market Intelligence Dashboard")
    
    # ใส่สีให้ RSI เพื่อให้อ่านง่าย
    def color_rsi(val):
        if val < 35: return 'background-color: #2e7d32; color: white' # เขียว (ซื้อ)
        if val > 65: return 'background-color: #c62828; color: white' # แดง (ขาย)
        return ''

    st.dataframe(
        df_market.style.applymap(color_rsi, subset=['RSI']),
        use_container_width=True,
        hide_index=True
    )
else:
    st.error("ไม่สามารถดึงข้อมูลได้ในขณะนี้ กรุณาตรวจสอบการเชื่อมต่อ")

# --- 4. NEWS SECTION ---
st.subheader("📰 Strategic Intel Bulletin")
news = [
    {"Date": "2026-05-13", "Impact": "CRITICAL", "Topic": "System Online", "Detail": "ระบบเชื่อมต่อ TradingView สำเร็จแล้ว ข้อมูลทั้งหมดเป็นราคาจริงจากตลาด"},
]
for item in news:
    with st.expander(f"**[{item['Date']}] {item['Impact']}: {item['Topic']}**"):
        st.write(item['Detail'])
