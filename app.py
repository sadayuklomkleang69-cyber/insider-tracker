import streamlit as st
import pandas as pd
import time
import random

# --- 1. INITIAL STATE ---
if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 2970.05

if 'my_assets' not in st.session_state:
    st.session_state.my_assets = {
        "TSM": {"Val": 55244.24, "PL": 10.28, "RSI": 62},
        "NVDA": {"Val": 46038.54, "PL": 18.95, "RSI": 58},
        "MU": {"Val": 40188.92, "PL": 68.75, "RSI": 75},
        "MSFT": {"Val": 27148.52, "PL": 4.69, "RSI": 45},
        "AVGO": {"Val": 25391.97, "PL": 18.89, "RSI": 52},
        "GOOGL": {"Val": 24350.15, "PL": 22.86, "RSI": 48},
        "PLTR": {"Val": 16743.23, "PL": -7.75, "RSI": 35},
        "ARM": {"Val": 16132.26, "PL": 29.81, "RSI": 68},
        "AMD": {"Val": 13374.89, "PL": 61.00, "RSI": 55},
        "AMZN": {"Val": 12972.02, "PL": 18.21, "RSI": 50},
        "ASML": {"Val": 11166.77, "PL": 8.95, "RSI": 42},
        "RKLB": {"Val": 6495.83, "PL": 41.11, "RSI": 82},
        "NBIS": {"Val": 2955.28, "PL": 16.69, "RSI": 30}
    }

# --- 2. RSI LIVE ENGINE (Simulation) ---
for stock in st.session_state.my_assets:
    if "RSI" not in st.session_state.my_assets[stock]:
        st.session_state.my_assets[stock]["RSI"] = 50
    # สุ่มการขยับ RSI เล็กน้อยเพื่อให้รู้ว่าระบบทำงาน
    st.session_state.my_assets[stock]["RSI"] = max(10, min(90, st.session_state.my_assets[stock]["RSI"] + random.randint(-2, 2)))

st.set_page_config(layout="wide")
st.title("🚀 Chairman Nu Command Center")

# --- 3. DASHBOARD METRICS ---
df = pd.DataFrame.from_dict(st.session_state.my_assets, orient='index')
total_val = df['Val'].sum()
avg_pl = df['PL'].mean()
total_profit = (total_val * avg_pl) / 100

m1, m2, m3, m4 = st.columns(4)
m1.metric("📦 Portfolio Value", f"{total_val:,.2f} THB")
m2.metric("📈 Avg Profit (%)", f"{avg_pl:.2f}%", delta=f"{avg_pl:.2f}%")
m3.metric("💰 Net Profit (THB)", f"{total_profit:,.2f}")
m4.metric("🔫 AMMO REMAINING", f"{st.session_state.cash_balance:,.2f}")

st.markdown("---")

# --- 4. MONITORING (PORTFOLIO & RSI คู่กัน) ---
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.subheader("📊 STRATEGIC PORTFOLIO")
    st.table(df[['Val', 'PL']])

with col_right:
    st.subheader("📉 RSI TACTICAL ANALYSIS")
    def get_strategy(rsi):
        if rsi >= 70: return "⚠️ OVERBOUGHT (เก็บเกี่ยว)"
        elif rsi <= 30: return "🚀 OVERSOLD (สั่งยิง)"
        else: return "Hold (เฝ้าระวัง)"
    
    rsi_df = df.copy()
    rsi_df['Strategy'] = rsi_df['RSI'].apply(get_strategy)
    # ใช้ dataframe ปกติเพื่อเลี่ยง Error ของ matplotlib
    st.dataframe(rsi_df[['RSI', 'Strategy']], use_container_width=True, height=520)

# --- 5. ACTIONS ---
with st.expander("⚙️ จัดการรบ (เติมกระสุน / สั่งยิง / ขาย)"):
    c1, c2, c3 = st.columns(3)
    with c1:
        topup = st.number_input("เติมกระสุน (THB)", min_value=0.0, key="topup")
        if st.button("ยืนยันการเติม"):
            st.session_state.cash_balance += topup
            st.rerun()
    with c2:
        target_buy = st.selectbox("เป้าหมายการยิง", list(st.session_state.my_assets.keys()), key="buy_target")
        spent = st.number_input("เงินที่ยิง", min_value=0.0, key="buy_amt")
        if st.button("FIRE!"):
            if spent <= st.session_state.cash_balance:
                st.session_state.cash_balance -= spent
                st.session_state.my_assets[target_buy]["Val"] += spent
                st.balloons()
                st.rerun()
    with c3:
        target_sell = st.selectbox("เป้าหมายการขาย", list(st.session_state.my_assets.keys()), key="sell_target")
        curr_v = st.session_state.my_assets[target_sell]["Val"]
        sell_v = st.number_input("เงินที่ขาย", min_value=0.0, max_value=float(curr_v), key="sell_amt")
        if st.button("CONFIRM SELL"):
            st.session_state.my_assets[target_sell]["Val"] -= sell_v
            st.session_state.cash_balance += sell_v
            st.success("ขายเรียบร้อย!")
            time.sleep(1)
            st.rerun()
