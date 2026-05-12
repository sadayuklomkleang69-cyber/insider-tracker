import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# 1. Setup & Configuration
st.set_page_config(page_title="Chairman Nu Command Center V11.0", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")

# 2. ข้อมูลต้นทุนคงที่ (Cost Basis) จากที่ประธานให้มา
# จาร์วิสจะใช้ข้อมูลนี้เป็น "จุดอ้างอิง" เพื่อคำนวณการขยับของเงิน
BASE_ASSETS = {
    "TSM": {"Cost_THB": 55244.24, "Base_PL": 10.28, "Ref_Price": 173.20}, # Ref_Price คือราคาตลาดตอนบันทึกข้อมูล
    "NVDA": {"Cost_THB": 46038.54, "Base_PL": 18.95, "Ref_Price": 121.50},
    "MU": {"Cost_THB": 40188.92, "Base_PL": 68.75, "Ref_Price": 135.00},
    "MSFT": {"Cost_THB": 27148.52, "Base_PL": 4.69, "Ref_Price": 415.00},
    "AVGO": {"Cost_THB": 25391.97, "Base_PL": 18.89, "Ref_Price": 155.00},
    "GOOGL": {"Cost_THB": 24350.15, "Base_PL": 22.86, "Ref_Price": 175.00},
    "PLTR": {"Cost_THB": 16743.23, "Base_PL": -7.75, "Ref_Price": 35.50},
    "ARM": {"Cost_THB": 16132.26, "Base_PL": 29.81, "Ref_Price": 145.00},
    "AMD": {"Cost_THB": 13374.89, "Base_PL": 61.00, "Ref_Price": 150.00},
    "AMZN": {"Cost_THB": 12972.02, "Base_PL": 18.21, "Ref_Price": 185.00},
    "ASML": {"Cost_THB": 11166.77, "Base_PL": 8.95, "Ref_Price": 850.00},
    "RKLB": {"Cost_THB": 6495.83, "Base_PL": 41.11, "Ref_Price": 8.50},
    "NBIS": {"Cost_THB": 2955.28, "Base_PL": 16.69, "Ref_Price": 165.00}
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
st.title("🎯 Chairman Nu Command Center V11.0")
m_data = get_market_data(list(BASE_ASSETS.keys()))

# คำนวณมูลค่ารวมแบบ Real-time
current_total_wealth = 0
for t, info in BASE_ASSETS.items():
    current_p = m_data.get(t, {}).get("Price", info['Ref_Price'])
    # สูตร: มูลค่าใหม่ = มูลค่าเดิม * (ราคาปัจจุบัน / ราคาอ้างอิง)
    realtime_val = info['Cost_THB'] * (current_p / info['Ref_Price'])
    current_total_wealth += realtime_val

h1, h2, h3, h4 = st.columns([2, 2, 1, 1])
with h1: st.metric("💰 มูลค่าพอร์ตปัจจุบัน (เรียลไทม์)", f"{current_total_wealth:,.2f} THB", delta=f"{(current_total_wealth - 298225.25):+,.2f} เทียบต้นทุน")
with h2: st.metric("🔥 กระสุนคงเหลือ", f"{st.session_state.cash_balance:,.2f} THB")

with h3:
    with st.popover("📥 เติมเงิน"):
        add_amt = st.number_input("เติม THB", min_value=0.0)
        if st.button("Confirm"): st.session_state.cash_balance += add_amt; st.rerun()
with h4:
    with st.popover("🎯 ยิงกระสุน"):
        target = st.selectbox("เป้าหมาย", list(BASE_ASSETS.keys()))
        spent = st.number_input("จำนวนเงิน (THB)", min_value=0.0)
        if st.button("Fire Now!"):
            if spent <= st.session_state.cash_balance:
                st.session_state.cash_balance -= spent
                st.session_state.battle_log.append({"Time": time.strftime("%H:%M"), "Action": f"ช้อน {target}", "Amount": spent})
                st.balloons(); st.rerun()

st.markdown("---")

# --- SECTION 1: THE LIVE VAULT (ขยับตามตลาดโลก) ---
st.subheader("📁 My Strategic Assets (มูลค่าขยับตามราคาตลาดโลก)")
p_list = []
for t, info in BASE_ASSETS.items():
    curr_p = m_data.get(t, {}).get("Price", info['Ref_Price'])
    # คำนวณ Profit/Loss ใหม่ตามราคาที่ขยับ
    price_ratio = curr_p / info['Ref_Price']
    live_val_thb = info['Cost_THB'] * price_ratio
    # คำนวณ %PL ใหม่: ((ราคาปัจจุบัน/ราคาอ้างอิง) * (1 + Base_PL)) - 1
    live_pl_pct = ((price_ratio * (1 + (info['Base_PL']/100))) - 1) * 100
    
    p_list.append({
        "สินทรัพย์": t,
        "มูลค่าปัจจุบัน (บาท)": f"{live_val_thb:,.2f}",
        "กำไร/ขาดทุน (%)": f"{live_pl_pct:+.2f}%",
        "ราคาตลาดโลก ($)": f"{curr_p:.2f}",
        "การเคลื่อนไหว": "📈 ขึ้น" if price_ratio > 1 else "📉 ลง" if price_ratio < 1 else "➖ นิ่ง"
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
            pulse_data.append({"Ticker": t, "Price": d['Price'], "Change %": f"{d['Chg']:+.2f}%", "RSI": round(d['RSI'], 2), "Mood": mood})
        st.dataframe(pd.DataFrame(pulse_data).sort_values("RSI"), use_container_width=True)

with col_right:
    st.subheader("📜 Recent Orders")
    if st.session_state.battle_log:
        st.table(pd.DataFrame(st.session_state.battle_log).iloc[::-1].head(5))

st.caption("© 2026 Chairman Nu Intelligence System • Real-time Mark-to-Market Active")
