import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# 1. Setup & Configuration
st.set_page_config(page_title="Chairman Nu Command Center V9.2", layout="wide")
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

def get_live_news_brief(ticker_list):
    all_news = []
    for symbol in ticker_list[:5]:
        try:
            ticker_obj = yf.Ticker(symbol)
            news_items = ticker_obj.news
            if news_items:
                item = news_items[0]
                all_news.append({
                    "Ticker": symbol, "Title": item.get('title'),
                    "Summary": item.get('summary', 'ไม่มีบทสรุปเพิ่มเติม'),
                    "Publisher": item.get('publisher'),
                    "Time": time.ctime(item.get('providerPublishTime'))
                })
        except: continue
    return all_news

# --- TOP HUD: AMMO & COMMANDS ---
st.title("🎯 Chairman Nu Command Center V9.2")

# สร้างแถวบนสุดสำหรับดูเงินและปุ่มเติมเงิน
col_ammo, col_fill, col_fire = st.columns([2, 1, 1])

with col_ammo:
    st.metric("🔥 กระสุนคงเหลือ (Ammunition)", f"{st.session_state.cash_balance:,.2f} THB")

with col_fill:
    with st.popover("📥 เติมเงิน"):
        add_amt = st.number_input("จำนวนเงินที่เติม", min_value=0.0, step=500.0)
        if st.button("ยืนยันการเติม"):
            st.session_state.cash_balance += add_amt
            st.rerun()

with col_fire:
    with st.popover("🎯 ยิงกระสุน"):
        sel_stock = st.selectbox("เป้าหมาย", tickers)
        buy_p = st.number_input("ราคาเข้า ($)", min_value=0.0)
        spent = st.number_input("ใช้กระสุน (THB)", min_value=0.0)
        if st.button("Execute Order"):
            if spent <= st.session_state.cash_balance:
                st.session_state.cash_balance -= spent
                st.session_state.battle_log.append({"Time": time.strftime("%H:%M"), "Ticker": sel_stock, "Spent": spent, "Price": buy_p})
                st.balloons()
                st.rerun()
            else:
                st.error("กระสุนไม่พอ!")

st.markdown("---")

# ส่วนที่ 1: ตารางหุ้น
data = get_stock_data(tickers)
if not data.empty:
    st.subheader("🚀 Market Live Scan")
    st.dataframe(data.sort_values("RSI"), use_container_width=True)

st.markdown("---")

# ส่วนที่ 2: Intelligence Briefing
st.subheader("📰 Daily Intelligence Briefing")
news_data = get_live_news_brief(tickers)
if news_data:
    for news in news_data:
        with st.container():
            ca, cb = st.columns([1, 4])
            with ca:
                st.subheader(f"[{news['Ticker']}]")
                st.caption(f"{news['Time']}")
            with cb:
                st.markdown(f"### {news['Title']}")
                st.write(f"{news['Summary']}")
                st.caption(f"Source: {news['Publisher']}")
            st.markdown("---")

# ส่วนที่ 3: Battle Log
st.subheader("📜 Battle Log")
if st.session_state.battle_log:
    st.table(pd.DataFrame(st.session_state.battle_log).iloc[::-1])

st.caption("© 2026 Chairman Nu Intelligence System • Tactical HUD Active")
