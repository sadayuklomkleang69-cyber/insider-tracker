import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# 1. Setup & Configuration
st.set_page_config(page_title="Chairman Nu Command Center V10.0", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")

# 2. ข้อมูลฐานราก (Base Portfolio) - ข้อมูลจริงที่ประธานให้มา
INITIAL_PORTFOLIO = {
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

# 3. Persistent Data System (Session State)
if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 2970.05
if 'live_portfolio' not in st.session_state:
    # เริ่มต้นโดยใช้ข้อมูลฐานที่ประธานให้มา
    st.session_state.live_portfolio = INITIAL_PORTFOLIO.copy()
if 'battle_log' not in st.session_state:
    st.session_state.battle_log = []

# 4. Market Data Engine
@st.cache_data(ttl=60)
def get_market_data(ticker_list):
    results = {}
    for s in ticker_list:
        try:
            t = yf.Ticker(s)
            df = t.history(period="5d", interval="15m")
            if df.empty: continue
            # RSI & Price
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
            curr = float(df['Close'].iloc[-1])
            prev = t.fast_info['previousClose']
            chg = ((curr - prev) / prev) * 100
            results[s] = {"Price": curr, "Chg": chg, "RSI": rsi}
        except: continue
    return results

# --- HEADER SECTION ---
st.title("🎯 Chairman Nu Command Center V10.0")
total_val = sum(v['Value'] for v in st.session_state.live_portfolio.values())
h1, h2, h3, h4 = st.columns([2, 2, 1, 1])

with h1: st.metric("💰 มูลค่ารวมในพอร์ต", f"{total_val:,.2f} THB")
with h2: st.metric("🔥 กระสุนคงเหลือ", f"{st.session_state.cash_balance:,.2f} THB")

with h3:
    with st.popover("📥 เติมเงิน"):
        add_amt = st.number_input("จำนวน (THB)", min_value=0.0, step=1000.0)
        if st.button("Confirm Top-up"):
            st.session_state.cash_balance += add_amt
            st.rerun()

with h4:
    with st.popover("🎯 ยิงกระสุน"):
        target = st.selectbox("เลือกเป้าหมาย", list(st.session_state.live_portfolio.keys()))
        spent_thb = st.number_input("จำนวนเงินที่จะยิง (THB)", min_value=0.0)
        if st.button("Fire Now!"):
            if spent_thb <= st.session_state.cash_balance and spent_thb > 0:
                # 1. หักเงินกระสุน
                st.session_state.cash_balance -= spent_thb
                # 2. บวกเข้าพอร์ตปัจจุบันทันที
                st.session_state.live_portfolio[target]["Value"] += spent_thb
                # 3. บันทึกประวัติ
                st.session_state.battle_log.append({
                    "Time": time.strftime("%H:%M:%S"),
                    "Action": f"ช้อน {target}",
                    "Amount": f"{spent_thb:,.2f} THB"
                })
                st.balloons()
                st.rerun()
            else:
                st.error("กระสุนไม่พอหรือยอดเงินไม่ถูกต้อง")

st.markdown("---")

# --- SECTION 1: THE LIVE VAULT ---
st.subheader("📁 My Strategic Assets (สถานะอัปเดตเรียลไทม์)")
m_data = get_market_data(list(st.session_state.live_portfolio.keys()))

p_list = []
for t, info in st.session_state.live_portfolio.items():
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

# --- SECTION 2: LIVE PULSE ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🚀 Market Live Pulse")
    if m_data:
        pulse_data = []
        for t, d in m_data.items():
            mood = "🔥 น่าช้อน" if d['RSI'] < 35 else "📉 เริ่มถูก" if d['RSI'] < 45 else "⚖️ ปกติ"
            pulse_data.append({
                "Ticker": t, "Price": d['Price'], "Change %": f"{d['Chg']:+.2f}%",
                "RSI": round(d['RSI'], 2), "Market Mood": mood
            })
        st.dataframe(pd.DataFrame(pulse_data).sort_values("RSI"), use_container_width=True)

with col_right:
    st.subheader("📜 Recent Orders")
    if st.session_state.battle_log:
        st.table(pd.DataFrame(st.session_state.battle_log).iloc[::-1].head(5))
    else:
        st.caption("ยังไม่มีการรบในเซสชันนี้")

st.caption("© 2026 Chairman Nu Intelligence System • Fully Automated Integrated Portfolio")
