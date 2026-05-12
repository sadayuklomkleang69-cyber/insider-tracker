import streamlit as st
import pandas as pd

# 1. เพิ่มตัวเลือกใน Sidebar (วิทยุเลือกโหมด)
# แก้ไขบรรทัดเดิมที่มี st.sidebar.radio ให้เพิ่ม "📰 News Intelligence" ลงไป
mode = st.sidebar.radio(
    "เลือกโหมด:",
    ("🎯 กลยุทธ์ & ความคุ้มค่า", "📊 Whale Sentiment Score", "🐳 Insider Live Feed", "📰 News Intelligence", "🧮 ตารางคำนวณ Dime")
)

# 2. สร้างฟังก์ชันการแสดงผล News Feed
if mode == "📰 News Intelligence":
    st.title("📰 News Intelligence: Market Pulse")
    st.markdown("---")
    
    # แบ่งคอลัมน์เพื่อให้ข้อมูลไม่แน่นเกินไป
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔥 Top Market Headlines")
        # ข้อมูลสมมติสำหรับการแสดงผล (ในอนาคตเชื่อม API ของ News ได้)
        news_data = [
            {"Title": "Oil Prices Surge to $107 as Middle East Tensions Escalate", "Impact": "Critical", "Category": "Energy"},
            {"Title": "Fed Minutes: No Rate Cuts Expected Until Inflation Hits 2%", "Impact": "High", "Category": "Macro"},
            {"Title": "Nvidia Earnings Preview: Can Blackwell Deliver?", "Impact": "High", "Category": "AI/Tech"},
            {"Title": "TSMC Q2 Forecast: AI Demand Stays Resilient Amid Global Weakness", "Impact": "Medium", "Category": "Semi"},
        ]
        
        for news in news_data:
            with st.expander(f"[{news['Category']}] {news['Title']}"):
                st.write(f"**Impact Level:** {news['Impact']}")
                st.write("Analysis: ราคาน้ำมันที่พุ่งสูงจะกดดันเงินเฟ้อ ทำให้หุ้นกลุ่ม Growth (NVDA, MSFT) อาจโดนเทขายในระยะสั้น")
    
    with col2:
        st.subheader("⚡ Quick Insights")
        st.info("**Sentiment:** Fearful Greed (42/100)")
        st.warning("**Watch out:** CPI Data release this Friday.")
        st.success("**Alpha Note:** Accumulate ASML if it drops below $1430.")
        
    # เพิ่มตารางสรุปราคา Real-time (Optional)
    st.markdown("---")
    st.write("### 🧮 Asset Price Quick Check")
    price_df = pd.DataFrame({
        "Ticker": ["Brent Oil", "DXY (Dollar Index)", "S&P 500", "Bitcoin"],
        "Price": ["$107.72", "105.45", "5,120.20", "$62,450"],
        "Change": ["+3.2%", "+0.5%", "-0.8%", "-1.2%"]
    })
    st.table(price_df)
