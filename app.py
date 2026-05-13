# --- ACTIONS ---
with st.expander("⚙️ จัดการรบ (เติมกระสุน / สั่งยิง / ขาย)"):
    col1, col2, col3 = st.columns(3)
    
    # 1. เติมกระสุน (ของเดิม)
    with col1:
        topup = st.number_input("เติมกระสุน (THB)", min_value=0.0)
        if st.button("ยืนยันการเติม"):
            st.session_state.cash_balance += topup
            st.rerun()

    # 2. สั่งยิง (ของเดิม)
    with col2:
        target = st.selectbox("เป้าหมายการยิง", list(st.session_state.my_assets.keys()))
        spent = st.number_input("จำนวนเงินที่ยิง", min_value=0.0)
        if st.button("FIRE!"):
            if spent <= st.session_state.cash_balance:
                st.session_state.cash_balance -= spent
                st.session_state.my_assets[target]["Val"] += spent
                st.balloons()
                st.rerun()
            else:
                st.error("กระสุนไม่พอ!")

    # 3. ขาย (เพิ่มใหม่ตามสั่ง)
    with col3:
        target_sell = st.selectbox("เป้าหมายการขาย", list(st.session_state.my_assets.keys()), key="sell_select")
        # ดึงมูลค่าล่าสุดจากพอร์ตมาแสดงเพื่อกันประธานคีย์เกิน
        current_val = st.session_state.my_assets[target_sell]["Val"]
        sell_val = st.number_input("จำนวนเงินที่ขาย (THB)", min_value=0.0, max_value=float(current_val))
        if st.button("CONFIRM SELL"):
            if sell_val > 0:
                st.session_state.my_assets[target_sell]["Val"] -= sell_val
                st.session_state.cash_balance += sell_val
                st.success(f"ขาย {target_sell} เรียบร้อย เงินกลับเข้าคลัง!")
                time.sleep(1)
                st.rerun()
