import streamlit as st
import pandas as pd

#ตั้งค่าหน้ากระดาษ
st.set_page_config(page_title="Chairman Nu Command Center V7.2", layout="wide")

# 1. Sidebar Menu (รวมทุกโหมดไว้ที่นี่)
mode = st.sidebar.radio(
    "เลือกโหมด:",
    ("🎯 กลยุทธ์ & ความคุ้มค่า", "📊 Whale Sentiment Score", "🐳 Insider Live Feed", "📰 News Intelligence", "🧮 ตารางคำนวณ Dime")
)

# ข้อมูลหุ้นหลัก (ตัวอย่างข้อมูลเดิมที่ควรมี)
stocks = ["NVDA", "TSM", "ASML", "PLTR", "GOOGL", "AVGO", "MSFT", "AMZN", "ARM", "AMD", "MU"]

# --- MODE: กลยุทธ์ & ความคุ้มค่า ---
if mode == "🎯 กลยุทธ์ & ความคุ้มค่า":
    st.title("🎯 กลยุทธ์การลงทุน & จุดซื้อไม้ 1-2-3")
    st.write("วิเคราะห์ความคุ้มค่าตามตรรกะระดับมืออาชีพ")
    # ใส่โค้ดตารางหุ้นเดิมของท่านที่นี่ (ผมทำโครงสร้างไว้ให้)
    df = pd.DataFrame({
        "Ticker": stocks,
        "Status": ["Wait", "Entry 1", "Hold", "Entry 1", "Wait", "Wait", "Hold", "Hold", "Wait", "Wait", "Wait"],
        "Target Price": [200, 380, 1450, 130, 380, 400, 400, 260, 200, 440, 750]
    })
    st.table(df)

# --- MODE: News Intelligence (โหมดใหม่) ---
elif mode == "📰 News Intelligence":
    st.title("📰 News Intelligence: Market Pulse")
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔥 Top Market Headlines")
        news_data = [
            {"Title": "Oil Prices Surge to $107 as Middle East Tensions Escalate", "Impact": "Critical", "Category": "Energy"},
            {"Title": "Fed Minutes: No Rate Cuts Expected Until Inflation Hits 2%", "Impact": "High", "Category": "Macro"},
            {"Title": "Nvidia Earnings Preview: Can Blackwell Deliver?", "Impact": "High", "Category": "AI/Tech"},
        ]
        for news in news_data:
            with st.expander(f"[{news['Category']}] {news['Title']}"):
                st.write(f"**Impact Level:** {news['Impact']}")
                st.write("Analysis: ความผันผวนสูงในสัปดาห์นี้ แนะนำให้ถือเงินสดรอจุดรับสำคัญ")
    
    with col2:
        st.subheader("⚡ Quick Insights")
        st.info("**Sentiment:** Fearful Greed (42/100)")
        st.warning("**Watch out:** CPI Data release this Friday.")
        st.success("**Alpha Note:** Accumulate ASML if it drops below $1430.")

# --- MODE: ตารางคำนวณ Dime ---
elif mode == "🧮 ตารางคำนวณ Dime":
    st.title("🧮 ตารางคำนวณ Dime")
    st.write("ส่วนคำนวณงบประมาณการซื้อหุ้น")
    # ใส่โค้ดคำนวณของท่านที่นี่
