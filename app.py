import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# 1. Setup & Configuration
st.set_page_config(page_title="Chairman Nu Command Center V12.1", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")

# 2. ข้อมูลพอร์ตที่ประธานเขียนให้ล่าสุด (ใช้เป็น Base สำหรับขยับ)
if 'my_assets' not in st.session_state:
    st.session_state.my_assets = {
        "TSM": {"Val": 55244.24, "PL": 10.28, "Note": "🎯 สูงสุด (18.52%)"},
        "NVDA": {"Val": 46038.54, "PL": 18.95, "Note": "สัดส่วน 15.44%"},
        "MU": {"Val": 40188.92, "PL": 68.75, "Note": "🥇 กำไรสูงสุด"},
        "MSFT": {"Val": 27148.52, "PL": 4.69, "Note": ""},
        "AVGO": {"Val": 25391.97, "PL": 18.89, "Note": ""},
        "GOOGL": {"Val": 24350.15, "PL": 22.86, "Note": ""},
        "PLTR": {"Val": 16743.23, "PL": -7.75, "Note": "⚠️ ติดลบตัวเดียว"},
        "ARM": {"Val": 16132.26, "PL": 29.81, "Note": ""},
        "AMD": {"Val": 13374.89, "PL": 61.00, "Note": ""},
        "AMZN": {"Val": 12972.02, "PL": 18.21, "Note": ""},
        "ASML": {"Val": 11166.77, "PL": 8.95, "Note": ""},
        "RKLB": {"Val": 6495.83, "PL": 41.11, "Note": ""},
        "NBIS": {"Val": 2955.28, "PL": 16.69, "Note": ""}
    }

if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 2970.05
if 'battle_log' not in st.session_state:
    st.session_state.battle_log = []

# 3. Market Data Engine
@st.cache_data(ttl=60)
def get_market_data(ticker_list):
    results = {}
    for s in ticker_list:
        try:
            t = yf.Ticker(s)
            df = t.history(period="5d", interval="15m")
            if df.empty: continue
            # RSI & Chg Calculation
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
            curr = float(df['Close'].iloc[-1])
            prev = t.fast_info['previousClose']
            daily_chg = ((curr - prev) / prev) * 100
            results[s] = {"Price": curr, "Chg": daily_chg, "RSI": rsi}
        except: continue
    return results

# --- HEADER SECTION ---
st.title("🎯 Chairman Nu Command Center V12.1")
m_data = get_market_data(list(st.session_state.my_assets.keys()))

# คำนวณมูลค่า Real-time โดยอิงจากราคาที่ขยับวันนี้
current_total_wealth = 0
portfolio_display_list = []

for t, info in st.session_state.my_assets.items():
    chg_pct = m_data.get(t, {}).get("Chg", 0)
    # มูลค่าที่ขยับตามตลาด = มูลค่าฐาน * (1 + %ขยับวันนี้)
    live_val = info['Val'] * (1 + (chg_pct / 100))
    current_total_wealth += live_val
    
    portfolio_display_list.append({
        "สินทรัพย์": t,
        "มูลค่าสะสม (บาท)": f"{live_val:,.2f}",
        "กำไร/ขาดทุน (%)": f"{(info['PL'] + chg_pct):+.2f}%",
        "ราคาตลาด ($)": f"{m_data.get(t, {}).get('Price', 0):.2f}",
        "ความเคลื่อนไหว": f"{chg_pct:+.2f}%",
        "RSI": round(m_data.get(t, {}).get('RSI', 0), 2)
    })

h1, h2, h3, h4 = st.columns([2, 2, 1, 1])
with h1: st.metric("💰 มูลค่ารวม (ขยับเรียลไทม์)", f"{current_total_wealth:,.2f} THB", delta=f"{(current_total_wealth - 298225.25):+,.2f} เทียบยอดตั้งต้น")
with h2: st.metric("🔥 กระสุนคงเหลือ", f"{st.session_state.cash_balance:,.2f} THB")

with h3:
    with st.popover("📥 เติมเงิน"):
        amt = st.number_input("เติม THB", min_value=0.0)
        if st.button("Confirm"): st.session_state.cash_balance += amt; st.rerun()

with h4:
    with st.popover("🎯 ยิงกระสุน"):
        target = st.selectbox("เป้าหมาย", list(st.session_state.my_assets.keys()))
        spent = st.number_input("เงินที่จะยิง (THB)", min_value=0.0)
        if st.button("Fire Now!"):
            if spent <= st.session_state.cash_balance and spent > 0:
                st.session_state.cash_balance -= spent
                st.session_state.my_assets[target]["Val"] += spent
                st.session_state.battle_log.append({"Time": time.strftime("%H:%M:%S"), "Ticker": target, "Amount": spent})
                st.balloons(); st.rerun()

st.markdown("---")

# --- SECTION 1: THE LIVE VAULT ---
st.subheader("📁 My Strategic Assets (ขยับตามตลาดโลกเรียลไทม์)")
df_p = pd.DataFrame(portfolio_display_list)
st.table(df_p)

st.markdown("---")

# --- SECTION 2: BATTLE LOG ---
st.subheader("📜 Recent Orders")
if st.session_state.battle_log:
    st.table(pd.DataFrame(st.session_state.battle_log).iloc[::-1])

st.caption("© 2026 Chairman Nu Intelligence System • Real-time Wealth Tracking Enabled")
