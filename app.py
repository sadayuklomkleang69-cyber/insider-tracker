import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# 1. Setup & Configuration
st.set_page_config(page_title="Chairman Nu Command Center V8.7", layout="wide")
st_autorefresh(interval=300000, key="datarefresh")

# 2. Initializing Systems
if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 4000.0
if 'battle_log' not in st.session_state:
    st.session_state.battle_log = []

# 3. Strategic Intel (แก้ไขโครงสร้างให้รองรับข้อมูลเก่า)
if 'news_bulletin' not in st.session_state:
    st.session_state.news_bulletin = [
        {
            "Date": "2026-05-13", 
            "Topic": "Cerebras IPO: 3 จุดตายที่ต้องระวัง!", 
            "Impact": "⚠️ High Risk",
            "Detail": """
            • **รายได้กระจุกตัว:** 87% ของรายได้มาจากลูกค้ารายเดียว (G42) ความเสี่ยงสูงมากหากมีการเปลี่ยนแปลงสัญญา
            • **คู่แข่งมหาหิน:** ต้องสู้กับ Ecosystem ของ NVIDIA (CUDA) ที่ครองตลาด AI อยู่ในปัจจุบัน
            • **Burn Rate:** ขาดทุนสะสมยังสูง การระดมทุนครั้งนี้เพื่อต่อลมหายใจในสงคราม Hardware
            """
        }
    ]

# 4. Target Data
target_prices = {
    "NBIS": 170.0, "MU": 730.0, "NVDA": 210.0, "TSM": 380.0, "ASML": 1450.0, 
    "PLTR": 130.0, "GOOGL": 380.0, "AVGO": 400.0, "MSFT": 400.0, 
    "AMZN": 260.0, "ARM": 200.0, "AMD": 430.0, "RKLB": 110.0, "SPY": 530.0
}
tickers = list(target_prices.keys())

# 5. Functions
@st.cache_data(ttl=600)
def get_data(ticker_list):
    stock_data = []
    for symbol in ticker_list:
        try:
            ticker_obj = yf.Ticker(symbol)
            df = ticker_obj.history(period="1mo")
            if df.empty: continue
            
            # Simple RSI Calculation
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            current_rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
            
            current_p = float(df['Close'].iloc[-1])
            prev_p = float(df['Close'].iloc[-2])
            change = ((current_p - prev_p) / prev_p) * 100
            target = target_prices.get(symbol, 0)
            gap = ((current_p - target) / target) * 100

            mood = "🔥 น่าช้อน" if current_rsi < 35 else "📉 เริ่มถูก" if current_rsi < 45 else "⚖️ ปกติ"
            stock_data.append({
                "Ticker": symbol, "Price": round(current_p, 2),
                "Change %": f"{change:+.2f}%", "RSI": round(current_rsi, 2),
                "Market Mood": mood, "Gap to Target %": f"{gap:+.2f}%"
            })
        except: continue
    return pd.DataFrame(stock_data)

# --- SIDEBAR ---
st.sidebar.title("🧨 Ammunition Depot")
st.sidebar.metric("กระสุนคงเหลือ", f"{st.session_state.cash_balance:,.2f} THB")

with st.sidebar.expander("🎯 ยิงกระสุน / 📰 เพิ่มข่าว"):
    mode = st.radio("เลือกโหมด", ["ยิงหุ้น", "เพิ่มข่าว"])
    if mode == "ยิงหุ้น":
        sel_stock = st.selectbox("เป้าหมาย", tickers)
        spent = st.number_input("จำนวนเงิน (THB)", min_value=0.0)
        if st.button("Execute Order"):
            if spent <= st.session_state.cash_balance:
                st.session_state.cash_balance -= spent
                st.session_state.battle_log.append({"Time": time.strftime("%H:%M"), "Ticker": sel_stock, "Spent": spent})
                st.rerun()
    else:
        t = st.text_input("หัวข้อ")
        d = st.text_area("รายละเอียด")
        imp = st.selectbox("Impact", ["🔥 Hot", "⚠️ Warning", "📈 Positive", "📉 Negative"])
        if st.button("บันทึก Intel"):
            st.session_state.news_bulletin.insert(0, {"Date": time.strftime("%Y-%m-%d"), "Topic": t, "Impact": imp, "Detail": d})
            st.rerun()

# --- MAIN ---
st.title("🎯 Chairman Nu Command Center V8.7")

# 1. Table
data = get_data(tickers)
if not data.empty:
    st.subheader("🚀 Market Scan")
    st.dataframe(data.sort_values("RSI"), use_container_width=True)

st.markdown("---")

# 2. Strategic Intel Bulletin (แก้ไขให้กัน Error)
st.subheader("📰 Strategic Intel Bulletin")
for news in st.session_state.news_bulletin:
    with st.expander(f"**[{news.get('Date', 'N/A')}] {news.get('Impact', '')} : {news.get('Topic', 'No Topic')}**"):
        # ใช้ .get() เพื่อกันเหนียว ถ้าไม่มี Detail ให้โชว์คำว่า No details provided
        st.write(news.get('Detail', 'ไม่มีรายละเอียดเพิ่มเติมสำหรับข่าวนี้'))

st.markdown("---")

# 3. Battle Log
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("📜 Battle Log")
    if st.session_state.battle_log: st.table(pd.DataFrame(st.session_state.battle_log).iloc[::-1])
with col2:
    st.subheader("📊 Allocation")
    if st.session_state.battle_log: 
        log_df = pd.DataFrame(st.session_state.battle_log)
        st.bar_chart(log_df.groupby("Ticker")["Spent"].sum())

st.caption("© 2026 Chairman Nu Intelligence System • Bug Fixed & Ready for Cerebras IPO")
