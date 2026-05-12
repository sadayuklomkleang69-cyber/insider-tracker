import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# 1. Setup & Configuration
st.set_page_config(page_title="Chairman Nu Command Center V9.3", layout="wide")
st_autorefresh(interval=60000, key="datarefresh") # ปรับเป็น Refresh ทุก 1 นาทีเพื่อความเรียลไทม์

# 2. Initializing Systems
if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 4000.0
if 'battle_log' not in st.session_state:
    st.session_state.battle_log = []

# 3. Target Data
target_prices = {
    "NBIS": 170.0, "MU": 730.0, "NVDA": 210.0, "TSM": 380.0, "ASML": 1450.0, 
    "PLTR": 130.0, "GOOGL": 380.0, "AVGO": 400.0, "MSFT": 400.0, 
    "AMZN": 260.0, "ARM": 200.0, "AMD": 430.0, "RKLB": 110.0, "SPY": 530.0
}
tickers = list(target_prices.keys())

# 4. Functions
@st.cache_data(ttl=60) # ลด Cache เหลือ 1 นาทีเพื่อให้ราคาขยับตามจริง
def get_stock_data(ticker_list):
    stock_data = []
    for symbol in ticker_list:
        try:
            ticker_obj = yf.Ticker(symbol)
            df = ticker_obj.history(period="1d", interval="1m") # ดึงข้อมูลนาทีต่อนาที
            if df.empty: continue
            
            # ดึงราคาปัจจุบัน
            current_p = float(df['Close'].iloc[-1])
            prev_close = ticker_obj.fast_info['previousClose']
            change = ((current_p - prev_close) / prev_close) * 100
            
            # คำนวณ RSI (ใช้ข้อมูล 1 วันย้อนหลัง)
            hist_rsi = ticker_obj.history(period="5d")
            delta = hist_rsi['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            current_rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]

            mood = "🔥 น่าช้อน" if current_rsi < 35 else "📉 เริ่มถูก" if current_rsi < 45 else "⚖️ ปกติ"
            stock_data.append({
                "Ticker": symbol, "Price": round(current_p, 2),
                "Change %": f"{change:+.2f}%", "RSI": round(current_rsi, 2),
                "Market Mood": mood
            })
        except: continue
    return pd.DataFrame(stock_data)

def get_breaking_news(ticker_list):
    important_news = []
    # คำสำคัญที่บ่งบอกว่าเป็นข่าวใหญ่
    keywords = ['breaking', 'urgent', 'ipo', 'earnings', 'surge', 'plummet', 'crash', 'acquisition', 'deal', 'alert']
    
    for symbol in ticker_list[:8]:
        try:
            ticker_obj = yf.Ticker(symbol)
            news_items = ticker_obj.news
            for item in news_items[:3]:
                title = item.get('title', '').lower()
                # กรองเฉพาะข่าวที่มี Keyword สำคัญ
                if any(kw in title for kw in keywords):
                    important_news.append({
                        "Ticker": symbol, "Title": item.get('title'),
                        "Summary": item.get('summary', ''),
                        "Publisher": item.get('publisher'),
                        "Time": time.ctime(item.get('providerPublishTime'))
                    })
        except: continue
    return important_news

# --- TOP HUD ---
st.title("🎯 Chairman Nu Command Center V9.3")
col_status, col_ammo, col_fill, col_fire = st.columns([1, 2, 1, 1])

with col_status:
    st.write("📡 **LIVE SIGNAL**")
    st.caption(f"Last sync: {time.strftime('%H:%M:%S')}")

with col_ammo:
    st.metric("🔥 กระสุนคงเหลือ", f"{st.session_state.cash_balance:,.2f} THB")

with col_fill:
    with st.popover("📥 เติมเงิน"):
        amt = st.number_input("จำนวนเงิน", min_value=0.0, step=500.0)
        if st.button("ยืนยัน"):
            st.session_state.cash_balance += amt
            st.rerun()

with col_fire:
    with st.popover("🎯 ยิงกระสุน"):
        sel = st.selectbox("เป้าหมาย", tickers)
        p = st.number_input("ราคา ($)", min_value=0.0)
        s = st.number_input("ใช้กระสุน (THB)", min_value=0.0)
        if st.button("Execute"):
            if s <= st.session_state.cash_balance:
                st.session_state.cash_balance -= s
                st.session_state.battle_log.append({"Time": time.strftime("%H:%M"), "Ticker": sel, "Spent": s, "Price": p})
                st.balloons(); st.rerun()
            else: st.error("กระสุนไม่พอ!")

st.markdown("---")

# ส่วนที่ 1: ตารางหุ้น (Real-time Focus)
data = get_stock_data(tickers)
if not data.empty:
    st.subheader("🚀 Market Live Pulse")
    st.dataframe(data.sort_values("Change %", ascending=False), use_container_width=True)

# ส่วนที่ 2: Breaking News Only (โชว์เฉพาะเรื่องสำคัญ)
breaking = get_breaking_news(tickers)
if breaking:
    st.markdown("---")
    st.subheader("🚨 Strategic Intel: Breaking Alerts")
    for news in breaking:
        st.warning(f"**[{news['Ticker']}] {news['Title']}** \n\n {news['Summary']} \n\n *Source: {news['Publisher']} | {news['Time']}*")
else:
    # ถ้าไม่มีข่าวสำคัญ ไม่ต้องโชว์ส่วนนี้เลย
    pass

st.markdown("---")

# ส่วนที่ 3: Battle Log
st.subheader("📜 Battle Log")
if st.session_state.battle_log:
    st.table(pd.DataFrame(st.session_state.battle_log).iloc[::-1])

st.caption("© 2026 Chairman Nu Intelligence System • High-Signal Filtering Mode")
