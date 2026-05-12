import streamlit as st
import pandas as pd

# 1. ตั้งค่าหน้ากระดาษ
st.set_page_config(page_title="Chairman Nu Command Center V7.2", layout="wide")

# 2. Sidebar Menu
st.sidebar.title("💎 Main Menu")
mode = st.sidebar.radio(
    "เลือกโหมดการทำงาน:",
    ("🎯 กลยุทธ์ & ความคุ้มค่า", "📊 Whale Sentiment Score", "🐳 Insider Live Feed", "📰 News Intelligence", "🧮 ตารางคำนวณ Dime")
)

# 3. ข้อมูลหุ้นจริง (ดึงจากหน้าจอ TradingView ของท่าน)
data = {
    "Ticker": ["NVDA", "TSM", "ASML", "PLTR", "GOOGL", "AVGO", "MSFT", "AMZN", "ARM", "AMD", "MU", "RKLB"],
    "Last Price": [216.79, 387.80, 1487.72, 134.55, 387.71, 415.93, 408.75, 264.96, 204.49, 438.00, 735.42, 115.20],
    "Status": ["Hold", "Entry 1", "Wait", "Hold", "Entry 1", "Wait", "Hold", "Wait", "Wait", "Entry 2", "Wait", "Entry 1"],
    "Insider": ["Profit Taking", "Neutral", "Wait", "Buying", "Neutral", "Neutral", "Selling", "Neutral", "Buying", "Neutral", "Neutral", "Heavy Buying"]
}
df = pd.DataFrame(data)

# --- 🎯 โหมด กลยุทธ์ ---
if mode == "🎯 กลยุทธ์ & ความคุ้มค่า":
    st.title("🎯 กลยุทธ์การลงทุน: จุดซื้อไม้ 1-2-3")
    st.dataframe(df[["Ticker", "Last Price", "Status"]], use_container_width=True)

# --- 🐳 โหมด Insider ---
elif mode == "🐳 Insider Live Feed":
    st.title("🐳 Insider Live Feed: เจาะรอยเท้าเจ้ามือ")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📢 รายงานสถานะล่าสุด")
        st.success("🚀 **RKLB:** ตรวจพบแรงซื้อสะสมจากระดับ Executive เพิ่มขึ้นต่อเนื่อง (Heavy Buying)")
        st.info("💻 **ARM:** สัญญาณบวกจาก Partner ใหม่ พยุงราคาเหนือ $200")
        st.warning("⚠️ **NVDA:** พบแรงขายทำกำไรระยะสั้นจากกลุ่มสถาบัน")
    with col2:
        st.subheader("📈 ปริมาณการซื้อขายรายตัว")
        st.table(df[["Ticker", "Insider"]])

# --- 📰 โหมดข่าว (จัดเต็มตามคำขอ) ---
elif mode == "📰 News Intelligence":
    st.title("📰 News Intelligence: Market Pulse")
    st.markdown("---")
    
    st.subheader("🔥 Top Headlines")
    st.error("⛽ **Energy Crisis:** น้ำมันพุ่ง $107 ทุบตลาดหุ้น Tech ทั่วโลก")
    st.warning("🦅 **Fed Minute:** อัตราดอกเบี้ยอาจค้างสูงนานกว่าที่คาด (Higher for Longer)")
    
    st.markdown("---")
    st.subheader("🎯 Stock-Specific News")
    with st.expander("🚀 Rocket Lab (RKLB) - เจาะลึก"):
        st.write("ตรวจพบ Volume ผิดปกติที่ระดับ $115 คาดมีการเก็บของก่อนประกาศภารกิจใหม่")
    with st.expander("🟢 NVIDIA (NVDA) - วิเคราะห์งบ"):
        st.write("ตลาดคาดหวังสูงมาก (High Expectation) ระวัง Sell on Fact หลังประกาศงบ")
    with st.expander("📱 ARM Holdings - ข่าวเด่น"):
        st.write("ข่าวลือเรื่องการร่วมมือกับ Apple ในโปรเจกต์ AI Server ล่าสุด")

# --- โหมดอื่นๆ ---
else:
    st.title(f"{mode}")
    st.write("ระบบกำลังเตรียมข้อมูล...")
