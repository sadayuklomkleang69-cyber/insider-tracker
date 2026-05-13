import streamlit as st
import pandas as pd
import time

# --- 1. INITIAL STATE (รักษาหุ้นและค่าเดิมของประธานทั้งหมด) ---
if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 2970.05  # ยอดเงินล่าสุดจากหน้าจอ

if 'my_assets' not in st.session_state:
    # ดึงค่าล่าสุดจาก STRATEGIC PORTFOLIO ของประธานมาทั้งหมด
    st.session_state.my_assets = {
        "TSM": {"Val": 55244.24, "PL": 10.28},
        "NVDA": {"Val": 46038.54, "PL": 18.95},
        "MU": {"Val": 40188.92, "PL": 68.75},
        "MSFT": {"Val": 27148.52, "PL": 4.69},
        "AVGO": {"Val": 25391.97, "PL": 18.89},
        "GOOGL": {"Val": 24350.15, "PL": 22.86},
        "PLTR": {"Val": 16743.23, "PL": -7.75},
        "ARM": {"Val": 16132.26, "PL": 29.81},
        "AMD": {"Val": 13374.89, "PL": 61.00},
        "AMZN": {"Val": 12972.02, "PL": 18.21},
        "ASML": {"Val": 11166.77, "PL": 8.95},
        "RKLB": {"Val": 6495.83, "PL": 41.11},
        "NBIS": {"Val": 2955.28, "PL": 16.69}
    }

st.title("🚀 Chairman Nu Command Center")

# --- 2. MONITORING ---
st.subheader("📊 STRATEGIC PORTFOLIO")
df = pd.DataFrame.from_dict(st.session_state.my_assets, orient='index')
st.table(df)

st.metric("💰 AMMO REMAINING (THB)", f"{st.session_state.cash_balance:,.2f}")

# --- 3. ACTIONS (คงเดิม + เพิ่มช่องขาย) ---
with st.expander("⚙️ จัดการรบ (เติมกระสุน / สั่งยิง / ขาย)"):
    col1, col2, col3 = st.columns(3)
    
    # เติมเสบียง (ของเดิม)
    with col1:
        st.markdown("### 📥 เติมเสบียง")
        topup = st.number_input("เติมกระสุน (THB)", min_value=0.0, key="topup_in")
        if st.button("ยืนยันการเติมเงิน"):
            st.session_state.cash_balance += topup
            st.rerun()

    # สั่งยิง (ของเดิม)
    with col2:
        st.markdown("### 🚀 สั่งยิง (BUY)")
        target_buy = st.selectbox("เป้าหมายการยิง", list(st.session_state.my_assets.keys()), key="buy_tg")
        spent = st.number_input("จำนวนเงินที่ยิง (THB)", min_value=0.0, key="buy_am")
        if st.button("FIRE!"):
            if spent <= st.session_state.cash_balance:
                st.session_state.cash_balance -= spent
                st.session_state.my_assets[target_buy]["Val"] += spent
                st.balloons()
                st.rerun()
            else:
                st.error("กระสุนไม่พอ!")

    # เก็บเกี่ยว/ขาย (ส่วนที่เพิ่มมาใหม่)
    with col3:
        st.markdown("### 💰 เก็บเกี่ยว (SELL)")
        target_sell = st.selectbox("เป้าหมายการขาย", list(st.session_state.my_assets.keys()), key="sell_tg")
        curr_val = st.session_state.my_assets[target_sell]["Val"]
        sell_val = st.number_input("จำนวนเงินที่ขาย (THB)", min_value=0.0, max_value=float(curr_val), key="sell_am")
        if st.button("CONFIRM SELL"):
            if sell_val > 0:
                st.session_state.my_assets[target_sell]["Val"] -= sell_val
                st.session_state.cash_balance += sell_val
                st.warning(f"ขาย {target_sell} เรียบร้อย!")
                time.sleep(1)
                st.rerun()

st.info("ระบบกำลังติดตามสถานะตลาดโลกตามคำสั่งของประธานนุ...")
