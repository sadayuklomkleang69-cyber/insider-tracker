import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="Insider Tracker - All Market", layout="wide")

# 2. ส่วนหัว
st.title('🎯 ระบบจับตา "คนใน" (อัปเดตทั้งตลาด)')
st.write(f"ข้อมูลล่าสุด ณ วันที่: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# ใช้ API Key เดิมของท่านประธาน (ตัว I ใหญ่ที่แก้แล้ว)
API_KEY = "OIrEUM6wlgFPzMjSC3aWXFkwGkVin2d2"

@st.cache_data(ttl=300)
def get_all_insider_data():
    # ดึงข้อมูลการซื้อขายล่าสุด 100 รายการจากทั้งตลาด
    url = f"https://financialmodelingprep.com/api/v4/insider-trading?limit=100&apikey={API_KEY}"
    r = requests.get(url)
    return pd.DataFrame(r.json())

try:
    df = get_all_insider_data()
    
    # กรองเฉพาะรายการ "ซื้อ" (P-Purchase) จากทุกตัวในตลาด
    df_buys = df[df['transactionType'] == 'P-Purchase'].copy()
    df_buys['มูลค่า_USD'] = df_buys['securitiesTransacted'] * df_buys['price']
    
    # ดึง 15 อันดับแรกที่มีการซื้อมากที่สุดในตลาดตอนนี้
    df_final = df_buys.sort_values(by='มูลค่า_USD', ascending=False).head(15)

    # 3. แสดงผลแบบภาพรวม
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("### 📊 สัดส่วนการซื้อรายหุ้น")
        fig = px.pie(df_final, values='มูลค่า_USD', names='symbol', hole=0.7,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_traces(textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.write("### 💎 15 อันดับรายการซื้อขนาดใหญ่ล่าสุด (ทั้งตลาด)")
        # ปรับแต่งตารางให้ดูง่ายขึ้น
        display_df = df_final[['symbol', 'reportingName', 'securitiesTransacted', 'price', 'มูลค่า_USD', 'transactionDate']]
        display_df.columns = ['ชื่อหุ้น', 'ผู้ซื้อ', 'จำนวนหุ้น', 'ราคาที่ซื้อ', 'มูลค่ารวม (USD)', 'วันที่ซื้อ']
        st.dataframe(display_df.style.format({"มูลค่ารวม (USD)": "{:,.2f}", "ราคาที่ซื้อ": "{:,.2f}"}), use_container_width=True)

    # 4. ส่วนค้นหาเพิ่มเติม
    st.markdown("---")
    st.write("💡 *หมายเหตุ: ข้อมูลนี้เป็นการรวบรวมจากทุกบริษัทในตลาดหลักทรัพย์ที่มีการรายงานการซื้อขายของคนในล่าสุด*")

except Exception as e:
    st.error("กำลังรอการเชื่อมต่อข้อมูล... หากขึ้นแถบนี้เกิน 1 นาที โปรดเช็คการยืนยันอีเมลของ API อีกครั้งครับ")

if st.button('🔄 อัปเดตข้อมูลเดี๋ยวนี้'):
    st.rerun()
