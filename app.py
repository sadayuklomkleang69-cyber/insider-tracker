import streamlit as st
import pandas as pd
import time

# --- INITIAL STATE (รักษาของเดิมไว้ทั้งหมด) ---
if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 1000000.0  # งบตั้งต้น

if 'my_assets' not in st.session_state:
    st.session_state.my_assets = {
        "CPALL": {"Val": 50000.0, "PL": 5.2},
        "AOT": {"Val": 120000.0, "PL": -2.1},
        "PTT": {"Val": 85000.0, "PL": 1.5}
    }

st.title("🚀 Chairman Nu Command Center")

# --- MONITORING: STRATEGIC PORTFOLIO ---
st.subheader("📊 STRATEGIC PORTFOLIO")
df = pd.DataFrame.from_dict(st.session_state.my_assets, orient='index')
st.table(df)

st.metric("💰 AMMO REMAINING (THB)", f"{st.session_state.cash_balance:,.2f}")

# --- ACTIONS (ส่วนที่เพิ่มปุ่มขาย โดยรักษาของเดิมไว้) ---
with st.expander("⚙️ จัดการรบ (เติมกระสุน / สั่งยิง / ขาย)"):
    col1, col2, col3 = st.columns(3)
    
    # 1. เติมกระสุน (ของเดิม)
    with col1:
        st.markdown("### 📥 เติมเสบียง")
        topup = st.number_input("เติมกระสุน (THB)", min_value=0.0, key="topup_input")
        if st.button("ยืนยันการเติมเงิน"):
            st.session_state.cash_balance += topup
            st.rerun()

    # 2. สั่งยิง (ของเดิม)
    with col2:
        st.markdown("### 🚀 สั่งยิง (BUY)")
        target_buy = st.selectbox("เป้าหมายการยิง", list(st.session_state.my_assets.keys()), key="buy_target")
        spent = st.number_input("จำนวนเงินที่ยิง (THB)", min_value=0.0, key="buy_amount")
        if st.button("FIRE!"):
            if spent <= st.session_state.cash_balance:
                st.session_state.cash_balance -= spent
                st.session_state.my_assets[target_buy]["Val"] += spent
                st.balloons()
                st.rerun()
            else:
                st.error("กระสุนไม่พอ!")

    # 3. ขาย (เพิ่มใหม่ตามสั่ง - เชื่อมโยงกับ Portfolio)
    with col3:
        st.markdown("### 💰 เก็บเกี่ยว (SELL)")
        target_sell = st.selectbox("เป้าหมายการขาย", list(st.session_state.my_assets.keys()), key="sell_target")
        current_val = st.session_state.my_assets[target_sell]["Val"]
        sell_val = st.number_input("จำนวนเงินที่ขาย (THB)", min_value=0.0, max_value=float(current_val), key="sell_amount")
        if st.button("CONFIRM SELL"):
            if sell_val > 0:
                st.session_state.my_assets[target_sell]["Val"] -= sell_val
                st.session_state.cash_balance += sell_val
                st.warning(f"ขาย {target_sell} เรียบร้อย!")
                time.sleep(1)
                st.rerun()

# --- FOOTER ---
st.info("ระบบกำลังติดตามสถานะตลาดโลกตามคำสั่งของประธานนุ...")
