import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# 1. Setup & Configuration
st.set_page_config(page_title="Chairman Nu Command Center V11.1", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")

# 2. ข้อมูลต้นทุนอ้างอิง (คำนวณจากข้อมูลที่ประธานให้มาเพื่อให้กำไร/ขาดทุนขยับตามจริง)
# สูตร: เราจะหา 'ทุนเริ่มแรก' (Initial Cost) เพื่อให้เวลาหุ้นขยับ มันจะบวก/ลบจากจุดนั้น
BASE_ASSETS = {
    "TSM": {"Current_Val": 55244.24, "PL_Pct": 10.28},
    "NVDA": {"Current_Val": 46038.54, "PL_Pct": 18.95},
    "MU": {"Current_Val": 40188.92, "PL_Pct": 68.75},
    "MSFT": {"Current_Val": 27148.52, "PL_Pct": 4.69},
    "AVGO": {"Current_Val": 25391.97, "PL_Pct": 18.89},
    "GOOGL": {"Current_Val": 24350.15, "PL_Pct": 22.86},
    "PLTR": {"Current_Val": 16743.23, "PL_Pct": -7.75},
    "ARM": {"Current_Val": 16132.26, "PL_Pct": 29.81},
    "AMD": {"Current_Val": 13374.89, "PL_Pct": 61.00},
    "AMZN": {"Current_Val": 12972.02, "PL_Pct": 18.21},
    "ASML": {"Current_Val": 11166.77, "PL_Pct": 8.95},
    "RKLB": {"Current_Val": 6495.83, "PL_Pct": 41.11},
    "NBIS": {"Current_Val": 2955.28, "PL_Pct": 16.69}
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
            # ดึงราคาปัจจุบัน และราคาปิดวันก่อนเพื่อหา % การเปลี่ยนแปลงของวัน
            info = t.fast_info
            curr = info['last_price']
            chg = ((curr - info['previous_close']) / info['previous_close']) * 100
            
            # ดึง RSI
            df = t.history(period="5d", interval="15m")
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
            
            results[s] = {"Price": curr, "Chg": chg, "RSI": rsi}
        except: continue
    return results

# --- HEADER SECTION ---
st.title("🎯 Chairman Nu Command Center V11.1")
m_data = get_market_data(list(BASE_ASSETS.keys()))

# คำนวณมูลค่าพอร์ตปัจจุบัน (อิงจากการเปลี่ยนแปลงรายวันของตลาด)
# เมื่อหุ้นในตลาดขยับกี่ % เงินในพอร์ตส่วนนั้นจะขยับตามทันที
total_portfolio_now = 0
for t, info in BASE_ASSETS.items():
    daily_chg_pct = m_data.get(t, {}).get("Chg", 0)
    # มูลค่าที่ขยับ = มูลค่าฐาน * (1 + % การขยับของวัน)
    asset_now = info['Current_Val'] * (1 + (daily_chg_pct / 100))
    total_portfolio_now += asset_now

h1, h2, h3, h4 = st.columns([2, 2, 1, 1])
with h1: 
    st.metric("💰 มูลค่าพอร์ตปัจจุบัน (เรียลไทม์)", f"{total_portfolio_now:,.2f} THB", 
              delta=f"{(total_portfolio_now - 298225.25):+,.2f} จากจุดเช็คพอร์ตล่าสุด")
with h2: 
    st.metric("🔥 กระสุนคงเหลือ", f"{st.session_state.cash_balance:,.2f} THB")

with h3:
    with st.popover("📥 เติมเงิน"):
        amt = st.number_input("เติมเงิน (THB)", min_value=0.0)
        if st.button("Confirm"): st.session_state.cash_balance += amt; st.rerun()
with h4:
    with st.popover("🎯 ยิงกระสุน"):
        target = st.selectbox("เป้าหมาย", list(BASE_ASSETS.keys()))
        spent = st.number_input("จำนวนเงิน (THB)", min_value=0.0)
        if st.button("Fire!"):
            if spent <= st.session_state.cash_balance:
                st.session_state.cash_balance -= spent
                st.session_state.battle_log.append({"Time": time.strftime("%H:%M"), "Action": f"ช้อน {target}", "Amount": spent})
                st.balloons(); st.rerun()

st.markdown("---")

# --- SECTION 1: ASSETS TRACKER ---
st.subheader("📁 My Strategic Assets (ขยับตามราคาตลาดโลก)")
p_list = []
for t, info in BASE_ASSETS.items():
    daily_chg = m_data.get(t, {}).get("Chg", 0)
    live_val = info['Current_Val'] * (1 + (daily_chg / 100))
    # กำไร/ขาดทุนสะสม + การขยับของวัน
    live_pl = info['PL_Pct'] + daily_chg
    
    p_list.append({
        "สินทรัพย์": t,
        "มูลค่าปัจจุบัน (บาท)": f"{live_val:,.2f}",
        "กำไร/ขาดทุนสะสม (%)": f"{live_pl:+.2f}%",
        "ราคาตลาด ($)": f"{m_data.get(t, {}).get('Price', 0):.2f}",
        "วันนี้": f"{daily_chg:+.2f}%"
    })

st.table(pd.DataFrame(p_list))

st.markdown("---")

# --- SECTION 2: MARKET PULSE ---
col_left, col_right = st.columns([2, 1])
with col_left:
    st.subheader("🚀 Market Live Pulse")
    if m_data:
        pulse_data = []
        for t, d in m_data.items():
            mood = "🔥 น่าช้อน" if d['RSI'] < 35 else "📉 เริ่มถูก" if d['RSI'] < 45 else "⚖️ ปกติ"
            pulse_data.append({"Ticker": t, "Price": d['Price'], "Change %": f"{d['Chg']:+.2f}%", "RSI": round(d['RSI'], 2), "Mood": mood})
        st.dataframe(pd.DataFrame(pulse_data).sort_values("RSI"), use_container_width=True)

with col_right:
    st.subheader("📜 Recent Orders")
    if st.session_state.battle_log:
        st.table(pd.DataFrame(st.session_state.battle_log).iloc[::-1].head(5))

st.caption("© 2026 Chairman Nu Intelligence System • Real-time Portfolio Logic Fixed")
