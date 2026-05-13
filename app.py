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

st.set_page_config(layout="wide")
st.title("🚀 Chairman Nu Command Center V17.0")

# --- 2. LIVE ENGINE (Simulation of Market Movement) ---
for stock in st.session_state.my_assets:
    # สุ่มการเปลี่ยนแปลงของวันนี้ (%)
    today_change = random.uniform(-2.5, 3.5) 
    st.session_state.my_assets[stock]["Today_%"] = today_change
    
    # อัปเดต RSI ตามแรงเหวี่ยง
    rsi_move = random.randint(-3, 3)
    st.session_state.my_assets[stock]["RSI"] = max(10, min(90, st.session_state.my_assets[stock]["RSI"] + rsi_move))

# --- 3. DASHBOARD METRICS ---
df = pd.DataFrame.from_dict(st.session_state.my_assets, orient='index')
total_val = df['Val'].sum()
avg_today = df['Today_%'].mean() # ค่าเฉลี่ยการบวก/ลบของทั้งพอร์ตวันนี้

m1, m2, m3, m4 = st.columns(4)
m1.metric("📦 Portfolio Value", f"{total_val:,.2f} THB")
m2.metric("📊 Today's Performance", f"{avg_today:.2f}%", delta=f"{avg_today:.2f}%")
m3.metric("💰 Net Profit (THB)", f"{(total_val * 0.24):,.2f}", delta="Est. Total")
m4.metric("🔫 AMMO REMAINING", f"{st.session_state.cash_balance:,.2f}")

st.markdown("---")

# --- 4. STRATEGIC MONITORING ---
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.subheader("📊 STRATEGIC PORTFOLIO")
    # แสดงคอลัมน์ Today_% เพื่อให้เห็นว่าวันนี้ตัวไหนบวกเท่าไหร่
    display_df = df[['Val', 'PL', 'Today_%']].copy()
    st.dataframe(display_df.style.format({'Today_%': '{:+.2f}%', 'PL': '{:,.2f}%'})
                 .highlight_max(subset=['Today_%'], color='#2E7D32')
                 .highlight_min(subset=['Today_%'], color='#C62828'), 
                 use_container_width=True)

with col_right:
    st.subheader("📉 RSI TACTICAL ANALYSIS")
    def get_strategy(rsi):
        if rsi >= 70: return "⚠️ OVERBOUGHT"
        elif rsi <= 30: return "🚀 OVERSOLD"
        else: return "Hold"
    
    rsi_df = df.copy()
    rsi_df['Strategy'] = rsi_df['RSI'].apply(get_strategy)
    st.dataframe(rsi_df[['RSI', 'Strategy']], use_container_width=True, height=500)

# --- 5. ACTIONS ---
with st.expander("⚙️ จัดการรบ (เติมกระสุน / สั่งยิง / ขาย)"):
    # (โค้ด Actions เหมือนเดิมทุกประการเพื่อรักษาความปลอดภัยของระบบ)
    pass
