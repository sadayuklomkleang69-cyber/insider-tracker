import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# 1. Setup & Configuration
st.set_page_config(page_title="Chairman Nu Command Center V8.6", layout="wide")
st_autorefresh(interval=300000, key="datarefresh")

# 2. Initializing Systems
if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 4000.0
if 'battle_log' not in st.session_state:
    st.session_state.battle_log = []

# 3. Strategic Intel (ยัดรายละเอียดจุดตาย Cerebras ตามที่ประธานต้องการ)
if 'news_bulletin' not in st.session_state:
    st.session_state.news_bulletin = [
        {
            "Date": "2026-05-13", 
            "Topic": "Cerebras IPO: 3 จุดตายที่ต้องระวัง!", 
            "Impact": "⚠️ High Risk",
            "Detail": """
            1. **รายได้กระจุกตัว:** 87% ของรายได้มาจากลูกค้ารายเดียว (G42 จาก UAE) ถ้าเค้าเลิกซื้อคือจบ!
            2. **สงครามชิป:** ต้องแข่งกับ NVIDIA (H100/B200) ตรงๆ แม้ชิปจะใหญ่กว่าแต่ Ecosystem สู้ยาก
            3. **ขาดทุนสะสม:** ตัวเลขขาดทุนยังสูงมาก และการเป็นบริษัท AI Hardware ต้องใช้เงินเผา (Burn Rate) มหาศาล
            """
        },
        {
            "Date": "2026-05-12", 
            "Topic": "ARK (Cathie Wood) เทขาย AMD และ RKLB", 
            "Impact": "📉 Negative",
            "Detail": "ป้าเคที่เริ่มปรับพอร์ต ลดสัดส่วนหุ้นรองเพื่อถือเงินสดเพิ่มในกลุ่ม Semi"
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
def calculate_rsi_manual(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=600)
def get_data(ticker_list):
    stock_data = []
    for symbol in ticker_list:
        try:
            ticker_obj = yf.Ticker(symbol)
            df = ticker_obj.history(period="1mo")
            if df.empty or len(df) < 15: continue
            df['RSI'] = calculate_rsi_manual(df['Close'])
            current_p = float(df['Close'].iloc[-1])
            prev_p = float(df['Close'].iloc[-2])
            current_rsi = float(df['RSI'].iloc[-1])
            change = ((current_p - prev_p) / prev_p) * 100
            target = target_prices.get(symbol, 0)
            gap = ((current_p - target) / target) * 100
            if current_rsi < 35: mood = "🔥 น่าช้อน"
            elif current_rsi < 45: mood = "📉 เริ่มถูก"
            else: mood = "⚖️ ปกติ"
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

with st.sidebar.expander("🎯 ปฏิบัติการยิงกระสุน"):
    sel_stock = st.selectbox("เลือกเป้าหมาย", tickers)
    spent = st.number_input("ใช้กระสุน (THB)", min_value=0.0)
    if st.button("Execute"):
        if spent <= st.session_state.cash_balance:
            st.session_state.cash_balance -= spent
            st.session_state.battle_log.append({"Time": time.strftime("%H:%M"), "Ticker": sel_stock, "Spent": spent})
            st.rerun()

with st.sidebar.expander("📰 เพิ่มข่าว (Intel)"):
    t = st.text_input("หัวข้อ")
    d = st.text_area("รายละเอียดข่าว")
    imp = st.selectbox("Impact", ["🔥 Hot", "⚠️ Warning", "📈 Positive", "📉 Negative"])
    if st.button("บันทึก Intel"):
        st.session_state.news_bulletin.insert(0, {"Date": time.strftime("%Y-%m-%d"), "Topic": t, "Impact": imp, "Detail": d})
        st.rerun()

# --- MAIN ---
st.title("🎯 Chairman Nu Command Center V8.6")

# 1. Table
data = get_data(tickers)
if not data.empty:
    st.subheader("🚀 Market Scan")
    st.dataframe(data.sort_values("RSI"), use_container_width=True)

st.markdown("---")

# 2. Intel Bulletin (โหมดโชว์รายละเอียดที่ประธานต้องการ)
st.subheader("📰 Strategic Intel Bulletin")
for news in st.session_state.news_bulletin:
    with st.expander(f"**[{news['Date']}] {news['Impact']} : {news['Topic']}**"):
        st.write(news['Detail']) # โชว์รายละเอียดตรงนี้ครับประธาน!

st.markdown("---")

# 3. Battle Log
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("📜 Battle Log")
    if st.session_state.battle_log: st.table(pd.DataFrame(st.session_state.battle_log).iloc[::-1])
with col2:
    st.subheader("📊 Allocation")
    if st.session_state.battle_log: st.bar_chart(pd.DataFrame(st.session_state.battle_log).groupby("Ticker")["Spent"].sum())
