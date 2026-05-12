import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# 1. Setup & Configuration
st.set_page_config(page_title="Chairman Nu Command Center V9.9", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")

# 2. ข้อมูลพอร์ตคงที่ของประธานนุ (ข้อมูลจริง 13 รายการ)
PORTFOLIO_BASE = {
    "TSM": {"Value": 55244.24, "PL": 10.28, "Note": "🎯 สูงสุด (18.52%)"},
    "NVDA": {"Value": 46038.54, "PL": 18.95, "Note": "สัดส่วน 15.44%"},
    "MU": {"Value": 40188.92, "PL": 68.75, "Note": "🥇 กำไรสูงสุด"},
    "MSFT": {"Value": 27148.52, "PL": 4.69, "Note": ""},
    "AVGO": {"Value": 25391.97, "PL": 18.89, "Note": ""},
    "GOOGL": {"Value": 24350.15, "PL": 22.86, "Note": ""},
    "PLTR": {"Value": 16743.23, "PL": -7.75, "Note": "⚠️ ติดลบตัวเดียว"},
    "ARM": {"Value": 16132.26, "PL": 29.81, "Note": ""},
    "AMD": {"Value": 13374.89, "PL": 61.00, "Note": ""},
    "AMZN": {"Value": 12972.02, "PL": 18.21, "Note": ""},
    "ASML": {"Value": 11166.77, "PL": 8.95, "Note": ""},
    "RKLB": {"Value": 6495.83, "PL": 41.11, "Note": ""},
    "NBIS": {"Value": 2955.28, "PL": 16.69, "Note": ""}
}

if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 2970.05
if 'battle_log' not in st.session_state:
    st.session_state.battle_log = []

# 3. Market Tickers
tickers = list(PORTFOLIO_BASE.keys())

# 4. Functions
@st.cache_data(ttl=60)
def get_market_data(ticker_list):
    results = {}
    for s in ticker_list:
        try:
            t = yf.Ticker(s)
            df = t.history(period="5d", interval="15m")
            if df.empty: continue
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
            # Price
            curr = float(df['Close'].iloc[-1])
            prev = t.fast_info['previousClose']
            chg = ((curr - prev) / prev) * 100
            results[s] = {"Price": curr, "Chg": chg, "RSI": rsi}
        except: continue
    return results

# --- HEADER ---
st.title("🎯 Chairman Nu Command Center V9.9")
total_val = sum(v['Value'] for v in PORTFOLIO_BASE.values())
h1, h2, h3, h4 = st.columns([2, 2, 1, 1])
h1.metric("💰 รวมมูลค่าพอร์ต", f"{total_val:,.2f} THB")
h2.metric("🔥 กระสุนคงเหลือ", f"{st.session_state.cash_balance:,.2f} THB")

with h3:
    with st.popover("📥 เติมเงิน"):
        if st.button("เติม 5,000"): st.session_state.cash_balance += 5000; st.rerun()
with h4:
    with st.popover("🎯 ยิงกระสุน"):
        target = st.selectbox("เป้าหมาย", tickers)
        if st.button("Execute Fire!"): st.balloons()

st.markdown("---")

# --- SECTION 1: THE PORTFOLIO (ข้อมูลที่ประธานใส่มา) ---
st.subheader("📁 My Strategic Assets (สถานะพอร์ตปัจจุบัน)")
m_data = get_market_data(tickers)

p_list = []
for t, info in PORTFOLIO_BASE.items():
    curr_p = m_data.get(t, {}).get("Price", 0)
    p_list.append({
        "สินทรัพย์": t,
        "มูลค่าสะสม (บาท)": f"{info['Value']:,.2f}",
        "กำไร/ขาดทุน (%)": f"{info['PL']:+.2f}%",
        "ราคาตลาด ($)": f"{curr_p:.2f}",
        "สถานะ/บันทึก": info['Note']
    })

st.table(pd.DataFrame(p_list))

st.markdown("---")

# --- SECTION 2: LIVE PULSE (RSI & MOOD) ---
st.subheader("🚀 Market Live Pulse (จังหวะช้อน)")
if m_data:
    pulse_data = []
    for t, d in m_data.items():
        mood = "🔥 น่าช้อน" if d['RSI'] < 35 else "📉 เริ่มถูก" if d['RSI'] < 45 else "⚖️ ปกติ"
        pulse_data.append({
            "Ticker": t, "Price": d['Price'], "Change %": f"{d['Chg']:+.2f}%",
            "RSI": round(d['RSI'], 2), "Market Mood": mood
        })
    st.dataframe(pd.DataFrame(pulse_data).sort_values("RSI"), use_container_width=True)

st.caption("© 2026 Chairman Nu Intelligence System • Battle-Ready Portfolio")
