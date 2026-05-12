import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="Insider Tracker - Market Watch", layout="wide")

# 2. ส่วนหัว
st.title('🎯 ระบบจับตา "คนใน" (ฉบับอัปเดตเรียลไทม์)')
st.write(f"ดึงข้อมูลตรงจากตลาดหลักทรัพย์ ณ วันที่: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# 3. รายชื่อหุ้นยักษ์ใหญ่ที่ต้องจับตา (ท่านประธานสามารถเพิ่มชื่อหุ้นได้ที่นี่)
watchlist = ['NVDA', 'TSLA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'NFLX', 'AMD', 'INTC']

@st.cache_data(ttl=600)
def get_market_insider():
    all_data = []
    for ticker in watchlist:
        t = yf.Ticker(ticker)
        df = t.insider_transactions
        if df is not None and not df.empty:
            # กรองเฉพาะรายการซื้อ (Purchase)
            buys = df[df['Text'].str.contains('Purchase', case=False, na=False)].copy()
            if not buys.empty:
                buys['Symbol'] = ticker
                all_data.append(buys)
    
    if all_data:
        return pd.concat(all_data)
    return pd.DataFrame()

try:
    with st.spinner('กำลังกวาดข้อมูลจากตลาด...'):
        final_df = get_market_insider()

    if not final_df.empty:
        # 4. แสดงผล
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write("### 📊 สัดส่วนการเก็บหุ้นของคนใน")
            fig = px.pie(final_df, values='Shares', names='Symbol', hole=0.7,
                         color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.write("### 💎 รายการซื้อล่าสุดจาก Watchlist")
            display_df = final_df[['Date', 'Symbol', 'Insider', 'Shares', 'Price']]
            display_df.columns = ['วันที่', 'หุ้น', 'ผู้ซื้อ', 'จำนวนหุ้น', 'ราคา']
            st.dataframe(display_df.sort_values(by='วันที่', ascending=False), use_container_width=True)
    else:
        st.info("💡 ช่วงนี้ผู้บริหารใน Watchlist ยังไม่มีการซื้อเพิ่ม ระบบจะอัปเดตทันทีที่มีการเคลื่อนไหวครับ")
        st.write("**หุ้นที่กำลังจับตา:** " + ", ".join(watchlist))

except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")

if st.button('🔄 รีเฟรชข้อมูล'):
    st.rerun()
