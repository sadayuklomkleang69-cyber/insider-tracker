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
    "Last Price": [215.37, 387.00, 1484.35, 13.97, 387.13, 413.84, 407.93, 264.32, 205.10, 438.09, 736.95, 114.52],
    "Change %": ["-1.85%", "-4.34%", "-5.20%", "-2.13%", "-0.39%", "-3.41%", "-1.15%", "-1.74%", "-3.55%", "-4.51%", "-7.34%", "-2.41%"],
    "Status": ["Hold", "Entry 1", "Wait", "Hold", "Entry 1", "Wait", "Hold", "Wait", "Wait", "Entry 2", "Wait", "Entry 1"]
}
df = pd.DataFrame(data)

# --- ฟังก์ชันแสดง Action Advice ---
def show_action_advice(current_mode):
    st.markdown("---")
    st.subheader("💡 Jarvis Action Advice")
    if current_mode == "🎯 กลยุทธ์ & ความคุ้มค่า":
        st.error("🚨 **สถานะตอนนี้: อยู่เฉยๆ (Stay Flat)**")
        st.write("เหตุผล: ท่านเติมไปแล้วตัวละ 1,000 บาท และกระสุนเหลือเพียง 4,000 บาท การเติมเพิ่มในวันที่ตลาดไหลแรง (Aggressive Down) จะทำให้ท่านเสียเปรียบถ้าพรุ่งนี้ลงต่อ")
    elif current_mode == "📰 News Intelligence":
        st.warning("⚠️ **สถานะตอนนี้: ติดตามใกล้ชิด (Watch Closely)**")
        st.write("เหตุผล: ข่าวน้ำมันพุ่ง $107 และความกังวลงบ NVDA คือแรงกดดันหลัก ห้ามเชื่อพาดหัวข่าว 100% ให้เน้นดูปริมาณการซื้อขายจริง")
    elif current_mode == "🐳 Insider Live Feed":
        st.success("✅ **สถานะตอนนี้: สะสมตามเจ้ามือ (Accumulate with Whales)**")
        st.write("เหตุผล: แม้ราคาจะแดง แต่ Insider ใน RKLB และ ARM ยังไม่ถอย เป็นจังหวะเก็บของราคา Discount")

# --- การแสดงผลตามโหมด ---

if mode == "🎯 กลยุทธ์ & ความคุ้มค่า":
    st.title("🎯 กลยุทธ์การลงทุน: จุดซื้อไม้ 1-2-3")
    st.dataframe(df[["Ticker", "Last Price", "Change %", "Status"]], use_container_width=True)
    show_action_advice(mode)

elif mode == "🐳 Insider Live Feed":
    st.title("🐳 Insider Live Feed: เจาะรอยเท้าเจ้ามือ")
    col1, col2 = st.columns(2)
    with col1:
        st.success("🚀 **RKLB:** ตรวจพบแรงซื้อสะสมจากระดับ Executive (Heavy Buying)")
        st.warning("⚠️ **MU:** แรงขายรุนแรง (-7.34%) จากกลุ่มสถาบันเพื่อปรับพอร์ต")
    show_action_advice(mode)

elif mode == "📰 News Intelligence":
    st.title("📰 News Intelligence: Market Pulse")
    st.error("⛽ **Energy Crisis:** น้ำมันพุ่ง $107 ทุบกลุ่ม Tech")
    st.info("📊 **Focus:** ตลาดรอจับตาผลประกอบการ NVDA สัปดาห์หน้า")
    show_action_advice(mode)

else:
    st.title(f"{mode}")
    st.write("ระบบกำลังเตรียมข้อมูล...")
