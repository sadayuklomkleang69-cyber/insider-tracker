import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# 1. Setup & Configuration
st.set_page_config(page_title="Chairman Nu Command Center V9.7", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")

# 2. Initializing Systems (Hardcoded Assets - ข้อมูลจะไม่หายอีกต่อไป)
if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 2970.05 # ยอดกระสุนล่าสุดจากหน้าจอประธาน
if 'battle_log' not in st.session_state:
    st.session_state.battle_log = []

# ข้อมูลพอร์ตจริงของประธานนุ (ฝังลงในระบบ)
initial_portfolio = {
    "TSM": {"Value_THB": 55244.24, "PL_Pct": 10.28, "Note": "🎯 สินทรัพย์สัดส่วนสูงสุด (18.52%)"},
    "NVDA": {"Value_THB": 46038.54, "PL_Pct": 18.95, "Note": "สัดส่วน 15.44%"},
    "MU": {"Value_THB": 40188.92, "PL_Pct": 68.75, "Note": "🥇 กำไรสูงสุด"},
    "MSFT": {"Value_THB": 27148.52, "PL_Pct": 4.69, "Note": ""},
    "AVGO": {"Value_THB": 25391.97, "PL_Pct": 18.89, "Note": ""},
    "GOOGL": {"Value_THB": 24350.15, "PL_Pct": 22.86, "Note": ""},
    "PLTR": {"Value_THB": 16743.23, "PL_Pct": -7.75, "Note": "⚠️ สินทรัพย์เดียวที่ติดลบ"},
    "ARM": {"Value_THB": 16132.26, "PL_Pct": 29.81, "Note": ""},
    "AMD": {"Value_THB": 13374.89, "PL_Pct": 61.00, "Note": ""},
    "AMZN": {"Value_THB": 12972.02, "PL_Pct": 18.21, "Note": ""},
    "ASML": {"Value_THB": 11166.77, "PL_Pct": 8.95, "Note": ""},
    "RKLB": {"Value_THB": 6495.83, "PL_Pct": 41.11, "Note": ""},
    "NBIS": {"Value_THB": 2955.28, "PL_Pct": 16.69, "Note": ""}
}

if 'my_portfolio' not in st.session_state:
    st.session_state.my_portfolio = initial_portfolio

# 3. Target Data & Tickers
target_prices = {"NBIS": 170.0, "MU": 730.0, "NVDA": 210.0, "TSM": 380.0, "ASML": 1450.0, "PLTR": 130.0, "GOOGL": 380.0, "AVGO": 400.0, "MSFT": 400.0, "AMZN": 260.0, "ARM": 200.0, "AMD": 430.0, "RKLB": 110.0, "SPY": 530.0}
tickers = list(st.session_state.my_portfolio.keys())

# 4. Functions
@st.cache_data(ttl=60)
def get_stock_data(ticker_list):
    stock_data = {}
    for symbol in ticker_list:
        try:
            ticker_obj = yf.Ticker(symbol)
            df = ticker_obj.history(period="5d", interval="15m")
            if df.empty: continue
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(window=14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            current_rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
            current_p = float(df['Close'].iloc[-1]); prev_close = ticker_obj.fast_info['previousClose']; change = ((current_p - prev_close) / prev_close) * 100
            stock_data[symbol] = {"Price": current_p, "Change %": change, "RSI": current_rsi, "Mood": "🔥 น่าช้อน" if current_rsi < 35 else "📉 เริ่มถูก" if current_rsi < 45 else "⚖️ ปกติ"}
        except: continue
    return stock_data

# --- TOP HUD ---
st.title("🎯 Chairman Nu Command Center V9.7")
total_port_value = sum(item['Value_THB'] for item in st.session_state.my_portfolio.values())
col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
with col1: st.metric("💰 รวมมูลค่าพอร์ต", f"{total_port_value:,.2f} THB")
with col2: st.metric("🔥 กระสุนคงเหลือ", f"{st.session_state.cash_balance:,.2f} THB")
with col3:
    with st.popover("📥 เติมเงิน"):
        amt = st.number_input("จำนวนเงิน", min_value=0.0); 
        if st.button("ยืนยัน"): st.session_state.cash_balance += amt; st.rerun()
with col4:
    with st.popover("🎯 ยิงกระสุน"):
        sel = st.selectbox("เป้าหมาย", tickers); p = st.number_input("ราคา ($)"); s = st.number_input("เงิน (THB)")
        if st.button("Execute"):
            if s <= st.session_state.cash_balance:
                st.session_state.cash_balance -= s; st.session_state.battle_log.append({"Time": time.strftime("%H:%M"), "Ticker": sel, "Spent": s}); st.rerun()

st.markdown("---")

# --- ส่วนที่ 1: รายละเอียดพอร์ตจริงของประธาน (The Vault) ---
st.subheader("📁 My Strategic Assets (เจาะลึกพอร์ตรายตัว)")
p_data = []
for t, info in st.session_state.my_portfolio.items():
    p_data.append({"สินทรัพย์": t, "มูลค่า (บาท)": f"{info['Value_THB']:,.2f}", "กำไร/ขาดทุน (%)": f"{info['PL_Pct']:+.2f}%", "สถานะ": info['Note']})
st.table(pd.DataFrame(p_data))

st.markdown("---")

# ส่วนที่ 2: Market Live Pulse
m_data = get_stock_data(tickers)
if m_data:
    st.subheader("🚀 Market Live Pulse")
    display_df = pd.DataFrame.from_dict(m_data, orient='index').reset_index()
    display_df.columns = ["Ticker", "Price", "Change %", "RSI", "Market Mood"]
    st.dataframe(display_df.sort_values("RSI"), use_container_width=True)

st.caption("© 2026 Chairman Nu Intelligence System • Assets Secured")
