elif mode == "📰 News Intelligence":
    st.title("📰 News Intelligence: Market Pulse")
    st.markdown("---")
    
    # ส่วนที่ 1: ข่าวร้อนที่กระทบดัชนีหลัก
    st.subheader("🔥 Top Headlines & Macro Impact")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.error("⛽ **Energy Crisis**")
        st.write("Brent Crude พุ่งแตะ $107.72 ส่งผลให้เงินเฟ้อสหรัฐฯ มีแนวโน้มสูงกว่าคาด")
    with col2:
        st.warning("🦅 **Fed Sentiment**")
        st.write("รายงานประชุม Fed บ่งชี้ว่าอาจยังไม่มีการลดดอกเบี้ยจนกว่าจะไตรมาส 4")
    with col3:
        st.success("🚀 **Space Economy**")
        st.write("NASA เตรียมประกาศงบประมาณใหม่สำหรับ Artemis ซึ่งเป็นบวกต่อหุ้นกลุ่ม Aerospace")

    st.markdown("---")
    
    # ส่วนที่ 2: เจาะลึกข่าวหุ้นใน Watchlist ของท่าน (RKLB, NVDA, ARM)
    st.subheader("🎯 Stock-Specific Intelligence")
    
    with st.expander("🚀 Rocket Lab (RKLB) - Deep Insight"):
        st.write("""
        - **News:** ตรวจพบปริมาณการซื้อขาย (Volume) ผิดปกติในโซน $115
        - **Impact:** เป็นสัญญาณ 'Accumulation' หรือการเก็บของของสถาบันก่อนมีข่าวใหญ่
        - **Strategy:** หากยืนเหนือ $116 ได้ มีโอกาสทดสอบ High เดิม
        """)
        
    with st.expander("🟢 NVIDIA (NVDA) - Earnings Watch"):
        st.write("""
        - **News:** ความต้องการชิป Blackwell ยังคงล้นตลาด แต่ปัญหา Supply Chain เริ่มถูกพูดถึง
        - **Impact:** ตลาดอาจจะผันผวนแรง (Volatility) ในช่วง 1 สัปดาห์ก่อนประกาศงบ
        """)

    with st.expander("📱 ARM Holdings - Partnership News"):
        st.write("""
        - **News:** มีข่าวลือเรื่องความร่วมมือใหม่กับ Apple ในส่วนของชิป AI Server
        - **Impact:** ช่วยพยุงราคาหุ้นไม่ให้หลุดแนวรับสำคัญที่ $200
        """)

    # ส่วนที่ 3: สรุปกลยุทธ์จากจาร์วิส
    st.sidebar.markdown("---")
    st.sidebar.subheader("💡 Jarvis's Daily Advice")
    st.sidebar.write("ประธานครับ วันนี้ตลาด 'กลัว' (Fear) มากกว่า 'โลภ' แนะนำให้ใจเย็นๆ รอปลาใหญ่กินเบ็ดที่ไม้ 1 ตามตารางครับ")
