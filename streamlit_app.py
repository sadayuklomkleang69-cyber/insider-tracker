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

# 3. ข้อมูลหุ้นจริงจาก Watchlist ของประธานนุ (อัปเดตล่าสุด)
data = {
    "Ticker": ["NVDA", "TSM", "ASML", "PLTR", "GOOGL", "AVGO", "MSFT", "AMZN", "ARM", "AMD", "MU", "RKLB"],
    "Last Price": [217.79, 390.43, 1497.52, 135.12, 387.22, 418.72, 408.59, 264.64, 206.24, 443.00, 750.46, 116.35],
    "Status": ["Hold", "Entry 1", "Wait", "Hold", "Entry 1", "Wait", "Hold", "Wait", "Wait", "Entry 2", "Wait", "Entry 1"],
    "Action": ["ถือต่อ", "เข้าไม้ 1", "รอก่อน", "ถือต่อ", "เข้าไม้ 1", "รอก่อน", "ถือต่อ", "รอก่อน", "รอก่อน", "เข้าไม้ 2", "รอก่อน", "เข้าไม้ 1"]
}
df = pd.DataFrame(data)

# --- การแสดงผลตามโหมด ---

if mode == "🎯 กลยุทธ์ & ความคุ้มค่า":
    st.title("🎯 กลยุทธ์การลงทุน: จุดซื้อไม้ 1-2-3")
    st.write("คำแนะนำจาก Jarvis: พิจารณาเข้าตามแผนเมื่อราคาแตะ Target")
    st.dataframe(df, use_container_width=True)

elif mode == "📰 News Intelligence":
    st.title("📰 News Intelligence: ข้อมูลข่าวสารวันนี้")
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("🔥 ข่าวเด่นที่กระทบพอร์ต")
        st.info("📌 **Oil Crisis:** ราคาน้ำมันดิบพุ่งกระทบต้นทุนขนส่งและเงินเฟ้อ")
        st.warning("📌 **AI Tech:** ตลาดเริ่มระมัดระวังแรงเทขายก่อนงบ NVDA ออก")
        st.success("📌 **Space Sector:** RKLB มีแรงซื้อสะสมจากกองทุน Ark")
    with col2:
        st.subheader("⚡ สรุปด่วน")
        st.metric(label="Market Sentiment", value="Fearful", delta="-5%")
        st.write("คำแนะนำ: 'ถือเงินสดเพิ่มขึ้น 10%'")

elif mode == "🐳 Insider Live Feed":
    st.title("🐳 Insider Live Feed")
    st.write("ตรวจพบการเคลื่อนไหวของเจ้ามือในหุ้น: **RKLB** และ **ARM**")
    st.image("https://img.freepik.com/free-vector/digital-world-map-with-dots_1017-14251.jpg", width=500)

else:
    st.title(f"{mode}")
    st.write("ระบบกำลังดึงข้อมูล... โปรดรอสักครู่")
