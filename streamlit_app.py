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

# 3. ข้อมูลหุ้นจริงจาก Watchlist (อัปเดตตามหน้าจอ TradingView ของประธาน)
data = {
    "Ticker": ["NVDA", "TSM", "ASML", "PLTR", "GOOGL", "AVGO", "MSFT", "AMZN", "ARM", "AMD", "MU", "RKLB"],
    "Price": [217.79, 390.43, 1497.52, 135.12, 387.22, 418.72, 408.59, 264.64, 206.24, 443.00, 750.46, 116.35],
    "Insider_Activity": ["Buying", "Neutral", "Selling", "Buying", "Neutral", "Neutral", "Selling", "Neutral", "Buying", "Neutral", "Neutral", "Heavy Buying"]
}
df = pd.DataFrame(data)

# --- การแสดงผลตามโหมด ---

if mode == "🎯 กลยุทธ์ & ความคุ้มค่า":
    st.title("🎯 กลยุทธ์การลงทุน: จุดซื้อไม้ 1-2-3")
    st.dataframe(df[["Ticker", "Price"]], use_container_width=True)

elif mode == "🐳 Insider Live Feed":
    st.title("🐳 Insider Live Feed: เจาะรอยเท้าเจ้ามือ")
    st.markdown("---")
    
    # รายละเอียดความเคลื่อนไหวที่ท่านต้องการ
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📢 รายงานสถานะล่าสุด")
        st.success("✅ **RKLB:** ตรวจพบแรงซื้อสะสมจากระดับ Executive เพิ่มขึ้น 15% ในช่วงราคา $115-116")
        st.info("✅ **ARM:** SoftBank ยังไม่มีการขยับสถานะขายเพิ่ม เป็นสัญญาณบวกในระยะสั้น")
        st.warning("⚠️ **NVDA:** พบการทำกำไร (Profit Taking) จากผู้บริหารระดับสูงบางส่วน")
    
    with col2:
        st.subheader("📈 สรุปปริมาณการซื้อขาย")
        # แสดงตารางกิจกรรม Insider ของหุ้นแต่ละตัว
        st.table(df[["Ticker", "Insider_Activity"]])

elif mode == "📰 News Intelligence":
    st.title("📰 News Intelligence")
    st.info("📌 **Market Pulse:** ราคาน้ำมัน $107 กดดันกลุ่ม Tech / จับตางบ NVDA")

else:
    st.title(f"{mode}")
    st.write("ระบบกำลังรวบรวมข้อมูลเชิงลึก...")
