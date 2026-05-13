import streamlit as st
import pandas as pd
import time
import random

# --- 1. INITIAL STATE ---
if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 2970.05

if 'my_assets' not in st.session_state:
    # เพิ่มค่า RSI เริ่มต้นให้หุ้นทุกตัว
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

# ฟังก์ชันจำลองการขยับของ RSI (เพื่อให้ระบบดู Real-time)
for stock in st.session_state.my_assets:
    change = random.randint(-2, 2)
    new_rsi = st.session_state.my_assets[stock]["RSI"] + change
    st.session_state.my_assets[stock]["RSI"] = max(10, min(90, new_rsi))

st.set_page_config(layout="wide")
st.title("🚀 Chairman Nu Command Center")

# --- 2. PORTFOLIO PERFORMANCE ---
df = pd.DataFrame.from_dict(st.session_state.my_assets, orient='index')
total_val = df['Val'].sum()
avg_pl = df['PL'].mean()
total_profit = (total_val * avg_pl) / 100

m1, m2, m3, m4 = st.columns(4)
m1.metric("📦 Total Portfolio Value", f"{total_val:,.2f} THB")
m2.metric("📈 Overall Profit (%)", f"{avg_pl:.2f}%", delta=f"{avg_pl:.2f}%")
m3.metric("💰 Net Profit (THB)", f"{total_profit:,.2f}", delta="Updated")
m4.metric("🔫 AMMO REMAINING", f"{st.session_state.cash_balance:,.2f}")

st.markdown("---")

# --- 3. COMBINED MONITORING (PORTFOLIO + RSI) ---
view_col1, view_col2 = st.columns([1.2, 1])

with view_col1:
    st.subheader("📊 STRATEGIC PORTFOLIO")
    st.table(df[['Val', 'PL']])

with view_col2:
    st.subheader("📉 RSI TACTICAL ANALYSIS")
    def get_strategy(rsi):
        if rsi >= 70: return "⚠️ OVERBOUGHT (ควรขาย)"
        elif rsi <= 30: return "🚀 OVERSOLD (สั่งยิง)"
        else: return "Hold (เฝ้าระวัง)"
    
    rsi_df = df.copy()
    rsi_df['Strategy'] = rsi_df['RSI'].apply(get_strategy)
    # แสดงตาราง RSI พร้อมสีสัน
    st.dataframe(rsi_df[['RSI', 'Strategy']].style.highlight_max(subset=['RSI'], color='#2E7D32').highlight_min(subset=['RSI'], color='#C62828'), use_container_width=True, height=520)

# --- 4. ACTIONS ---
with st.expander("⚙️ จัดการรบ (เติมกระสุน / สั่งยิง / ขาย)"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📥 เติมเสบียง")
        topup = st.number_input("เติมกระสุน (THB)", min_value=0.0, key="t_in")
        if st.button("ยืนยันการเติมเงิน"):
            st.session_state.cash_balance += topup
            st.rerun()

    with col2:
        st.markdown("### 🚀 สั่งยิง (BUY)")
        target_buy = st.selectbox("เป้าหมายการยิง", list(st.session_state.my_assets.keys()), key="b_tg")
        spent = st.number_input("เงินที่ยิง", min_value=0.0, key="b_am")
        if st.button("FIRE!"):
            if spent <= st.session_state.cash_balance:
                st.session_state.cash_balance -= spent
                st.session_state.my_assets[target_buy]["Val"] += spent
                st.balloons()
                st.rerun()
            else: st.error("กระสุนไม่พอ!")

    with col3:
        st.markdown("### 💰 เก็บเกี่ยว (SELL)")
        target_sell = st.selectbox("เป้าหมายการขาย", list(st.session_state.my_assets.keys()), key="s_tg")
        curr_val = st.session_state.my_assets[target_sell]["Val"]
        sell_val = st.number_input("เงินที่ขาย", min_value=0.0, max_value=float(curr_val), key="s_am")
        if st.button("CONFIRM SELL"):
            if sell_val > 0:
                st.session_state.my_assets[target_sell]["Val"] -= sell_val
                st.session_state.cash_balance += sell_val
                st.success(f"ขาย {target_sell} เรียบร้อย!")
                time.sleep(1)
                st.rerun()
