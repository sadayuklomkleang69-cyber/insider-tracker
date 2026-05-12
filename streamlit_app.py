import streamlit as st
import pandas as pd
import yfinance as ticker_data
import time

# สั่งให้หน้านี้รีเฟรชตัวเองทุกๆ 60 วินาที
st.empty() 
st.write("ระบบจะอัปเดตข้อมูลอัตโนมัติ")
# เพิ่มปุ่มกดรีเฟรชเองแบบแมนนวลด้วย
if st.button('อัปเดตราคาเดี๋ยวนี้'):
    st.rerun()

st.set_page_config(page_title="Insider Tracker", layout="wide")

st.title("📊 ระบบติดตามหุ้น Insider Tracker")
st.write(f"สวัสดีครับท่านประธาน วันนี้วันที่ {pd.Timestamp.now().strftime('%d/%m/%Y')}")

# สร้าง Sidebar สำหรับเลือกหุ้น
st.sidebar.header("การตั้งค่า")
stock_symbol = st.sidebar.text_input("กรอกชื่อหุ้น (เช่น CPALL.BK, TSLA, AAPL)", "CPALL.BK")

# ดึงข้อมูลหุ้น
st.subheader(f"ข้อมูลหุ้น: {stock_symbol}")
try:
    data = ticker_data.Ticker(stock_symbol)
    df = data.history(period="1mo")
    
    # แสดงราคาล่าสุด
    current_price = df['Close'].iloc[-1]
    st.metric(label="ราคาล่าสุด", value=f"{current_price:.2f}")

    # แสดงกราฟ
    st.line_chart(df['Close'])
    
    st.write("ตารางข้อมูลย้อนหลัง 1 เดือน")
    st.dataframe(df.tail())
except:
    st.error("ไม่พบข้อมูลหุ้นตัวนี้ กรุณาตรวจสอบชื่อย่อหุ้นอีกครั้งครับ (หุ้นไทยต้องมี .BK ต่อท้าย)")
