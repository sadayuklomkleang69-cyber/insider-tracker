import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="Insider Tracker - Market Watch", layout="wide")

# 2. ส่วนหัว
st.title('🎯 ระบบจับตา "คนใน" (ฉบับเสถียรที่สุด)')
st.write(f"อัปเดตล่าสุด: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# 3. รายชื่อหุ้นยักษ์ใหญ่ที่ต้องจับตา
watchlist = ['NVDA', 'TSLA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'NFLX', 'AMD', 'INTC']

@st.cache_data(ttl=600)
def get_market_insider():
    all_data = []
    for ticker in watchlist:
        try:
            t = yf.Ticker(ticker)
            df = t.insider_transactions
            if df is not None and not df.empty:
                # กรองเฉพาะรายการซื้อ (Purchase)
                buys = df[df['Text'].str.contains('Purchase', case=False, na=False)].copy()
                if not buys.empty:
                    buys['Symbol'] = ticker
                    all_data.append(buys)
        except:
            continue
    
    if all_data:
        return pd.concat(all_data)
    return pd.DataFrame()

try:
    with st.spinner('กำลังกวาดข้อมูลจากตลาด...'):
        final_df = get_market_insider()

    if not final_df.empty:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write("### 📊 สัดส่วนการเก็บหุ้น")
            # ใช้ชื่อคอลัมน์ที่ระบบมีอยู่จริง
            fig = px.pie(final_df, values='Shares', names='Symbol', hole=0.7,
                         color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_traces(textfont=dict(color='white', size=14))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.write("### 💎 รายการซื้อล่าสุด")
            # แสดงข้อมูลทั้งหมดที่ดึงมาได้โดยไม่ล็อคชื่อคอลัมน์ เพื่อป้องกัน Error
            st.dataframe(final_df.sort_index(ascending=False), use_container_width=True)
    else:
        st.info("💡 ช่วงนี้ผู้บริหารยังไม่มีการซื้อเพิ่ม ระบบจะอัปเดตทันทีที่มีการเคลื่อนไหวครับ")

except Exception as e:
    st.error(f"ระบบกำลังปรับปรุงการเชื่อมต่อ: {e}")

if st.button('🔄 รีเฟรชข้อมูล'):
    st.rerun()
