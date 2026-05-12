import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# 1. Setup & Configuration
st.set_page_config(page_title="Chairman Nu Command Center V9.0", layout="wide")
st_autorefresh(interval=300000, key="datarefresh")

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
@st.cache_data(ttl=600)
def get_stock_data(ticker_list):
    stock_data = []
    for symbol in ticker_list:
        try:
            ticker_obj = yf.Ticker(symbol)
            df = ticker_obj.history(period="1mo")
            if df.empty: continue
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            current_rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
            current_p = float(df['Close'].iloc[-1])
            prev_p = float(df['Close'].iloc[-2])
            change = ((current_p - prev_p) / prev_p) * 100
            mood = "🔥 น่าช้อน" if current_rsi < 35 else "📉 เริ่มถูก" if current_rsi < 45 else "⚖️ ปกติ"
            stock_data.append({
                "Ticker": symbol, "Price": round(current_p, 2),
                "Change %": f"{change:+.2f}%", "RSI": round(current_rsi, 2),
                "Market Mood": mood
            })
        except: continue
    return pd.DataFrame(stock_data)

def get_live_news(ticker_list):
    all_news = []
    # ดึงข่าวหุ้น 3 ตัวแรกที่มีการเคลื่อนไหวสูงมาโชว์เพื่อประหยัดเวลาโหลด
    for symbol in ticker_list[:5]:
        try:
            ticker_obj = yf.Ticker(symbol)
            news_items = ticker_obj.news
            for item in news_items[:2]: # เอา 2 ข่าวล่าสุดต่อหุ้นหนึ่งตัว
                all_news.append({
                    "Ticker": symbol,
                    "Title": item.get('title'),
                    "Publisher": item.get('publisher'),
                    "Link": item.get('link'),
                    "Time": time.ctime(item.get('providerPublishTime'))
                })
        except: continue
    return all_news

# --- SIDEBAR ---
st.sidebar.title("🧨 Ammunition Depot")
st.sidebar.metric("กระสุนคงเหลือ", f"{st.session_state.cash_balance:,.2f} THB")

with st.sidebar.expander("🎯 ยิงกระสุน (Buy Order)"):
    sel_stock = st.selectbox("เป้าหมาย", tickers)
    buy_p = st.number_input("ราคาเข้าซื้อ ($)", min_value=0.0)
    spent = st.number_input("จำนวนเงินที่ใช้ (THB)", min_value=0.0)
    if st.button("Execute Order"):
        if spent <= st.session_state.cash_balance:
            st.session_state.cash_balance -= spent
            st.session_state.battle_log.append({"Time": time.strftime("%H:%M"), "Ticker": sel_stock, "Spent": spent, "Price": buy_p})
            st.rerun()

# --- MAIN ---
st.title("🎯 Chairman Nu Command Center V9.0")

# ส่วนที่ 1: ตารางหุ้น
data = get_stock_data(tickers)
if not data.empty:
    st.subheader("🚀 Market Live Scan")
    st.dataframe(data.sort_values("RSI"), use_container_width=True)

st.markdown("---")

# ส่วนที่ 2: ข่าววงในแบบ Real-time (Auto-Fetch)
st.subheader("📰 Real-time Strategic Intel (Auto-Feed)")
news_data = get_live_news(tickers)
if news_data:
    for news in news_data:
        with st.expander(f"**[{news['Ticker']}] {news['Title']}**"):
            st.write(f"📢 **Publisher:** {news['Publisher']}")
            st.write(f"🕒 **Time:** {news['Time']}")
            st.write(f"🔗 [อ่านข่าวฉบับเต็ม]({news['Link']})")
else:
    st.info("กำลังรอข้อมูลข่าวล่าสุดจาก Wall Street...")

st.markdown("---")

# ส่วนที่ 3: Battle Log
st.subheader("📜 Battle Log")
if st.session_state.battle_log:
    st.table(pd.DataFrame(st.session_state.battle_log).iloc[::-1])

st.caption("© 2026 Chairman Nu Intelligence System • Real-time News API Integrated")
