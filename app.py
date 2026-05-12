import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# 1. Setup & Configuration
st.set_page_config(page_title="Chairman Nu Command Center V12.0", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")

# 2. ฐานข้อมูลพอร์ตจริง (ชุดที่ประธานเพิ่งเขียนเมื่อกี้)
# ข้อมูลชุดนี้จะเป็น "ฐาน" ที่นิ่งที่สุดจนกว่าจะมีการยิงกระสุนเพิ่ม
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

# 3. Market Data Engine (ดึงราคาตลาดโลกเพื่อส่องจังหวะช้อน)
@st.cache_data(ttl=60)
def get_market_data(ticker_list):
    results = {}
    for s in ticker_list:
        try:
            t = yf.Ticker(s)
            df = t.history(period="5d", interval="15m")
            if df.empty: continue
            # RSI Calculation
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
            # Current Price
            curr = float(df['Close'].iloc[-1])
            prev = t.fast_info['previousClose']
            chg = ((curr - prev) / prev) * 100
            results[s] = {"Price": curr, "Chg": chg, "RSI": rsi}
        except: continue
    return results

# --- HEADER SECTION ---
st.title("🎯 Chairman Nu Command Center V12.0")
m_data = get_market_data(list(st.session_state.my_assets.keys()))

# ยอดรวมพอร์ต (นิ่งตามที่ประธานระบุ)
current_total = sum(v['Val'] for v in st.session_state.my_assets.values())

h1, h2, h3, h4 = st.columns([2, 2, 1, 1])
with h1: st.metric("💰 มูลค่ารวมในพอร์ต", f"{current_total:,.2f} THB")
with h2: st.metric("🔥 กระสุนคงเหลือ", f"{st.session_state.cash_balance:,.2f} THB")

with h3:
    with st.popover("📥 เติมเงิน"):
        amt = st.number_input("เติม THB", min_value=0.0)
        if st.button("Confirm"): st.session_state.cash_balance += amt; st.rerun()

with h4:
    with st.popover("🎯 ยิงกระสุน"):
        target = st.selectbox("เป้าหมาย", list(st.session_state.my_assets.keys()))
        spent = st.number_input("จำนวนเงิน (THB)", min_value=0.0)
        if st.button("Fire Now!"):
            if spent <= st.session_state.cash_balance and spent > 0:
                st.session_state.cash_balance -= spent
                # บวกเพิ่มเข้ามูลค่าสะสมทันที
                st.session_state.my_assets[target]["Val"] += spent
                st.session_state.battle_log.append({"Time": time.strftime("%H:%M:%S"), "Ticker": target, "Amount": spent})
                st.balloons(); st.rerun()

st.markdown("---")

# --- SECTION 1: THE VAULT (ข้อมูลเป๊ะตามที่ประธานเขียนเมื่อกี้) ---
st.subheader("📁 My Strategic Assets (ข้อมูลพอร์ตล่าสุด)")
p_display = []
for t, info in st.session_state.my_assets.items():
    p_display.append({
        "สินทรัพย์": t,
        "มูลค่าสะสม (บาท)": f"{info['Val']:,.2f}",
        "กำไร/ขาดทุน (%)": f"{info['PL']:+.2f}%",
        "ราคาตลาด ($)": f"{m_data.get(t, {}).get('Price', 0):.2f}",
        "RSI (สัญญาณรบ)": round(m_data.get(t, {}).get('RSI', 0), 2),
        "สถานะ": "🔥 น่าช้อน" if m_data.get(t, {}).get('RSI', 0) < 35 else "📉 เริ่มถูก" if m_data.get(t, {}).get('RSI', 0) < 45 else "⚖️ ปกติ"
    })
st.table(pd.DataFrame(p_display))

st.markdown("---")

# --- SECTION 2: BATTLE LOG ---
st.subheader("📜 Recent Orders (ประวัติการช้อนล่าสุด)")
if st.session_state.battle_log:
    st.table(pd.DataFrame(st.session_state.battle_log).iloc[::-1])
else:
    st.info("ยังไม่มีการช้อนเพิ่มในรอบนี้")

st.caption("© 2026 Chairman Nu Intelligence System • Sync with Latest Manual Input")
