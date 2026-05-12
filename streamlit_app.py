import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="Insider Tracker", layout="wide")

# 2. ส่วนหัว
st.title('🎯 ระบบจับตา "คนใน" (Insider Buy)')
st.write(f"อัปเดตล่าสุด: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# 3. เชื่อมต่อข้อมูล (ใช้ API ของท่านที่กรอกไว้)
API_KEY = "OirEUM6wlgFPzMjSC3aWXFkwGkVin2d2"

@st.cache_data(ttl=300)
def get_data():
    # ดึงข้อมูลการซื้อขายล่าสุด 100 รายการจากทั้งตลาด
    url = f"https://financialmodelingprep.com/api/v4/insider-trading?limit=100&apikey={API_KEY}"
    r = requests.get(url)
    return pd.DataFrame(r.json())

try:
    df = get_data()
    # กรองเฉพาะรายการ "ซื้อ" (P-Purchase)
    df_buys = df[df['transactionType'] == 'P-Purchase'].copy()
    df_buys['Value_USD'] = df_buys['securitiesTransacted'] * df_buys['price']
    
    # ดึง 10 อันดับแรกที่มีการซื้อมากที่สุดในตลาดตอนนี้
    df_final = df_buys.sort_values(by='Value_USD', ascending=False).head(10)

    # 4. แสดงผล
    col1, col2 = st.columns([1, 2])
    with col1:
        # กราฟสัดส่วนการซื้อ
        fig = px.pie(df_final, values='Value_USD', names='symbol', hole=0.7,
                     title="สัดส่วนการซื้อรายหุ้น",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.write("### 💎 รายการซื้อขนาดใหญ่ล่าสุด")
        for index, row in df_final.iterrows():
            st.info(f"**{row['symbol']}** | ซื้อโดย: {row['reportingName']} | มูลค่า: ${row['Value_USD']:,.2f}")

except Exception as e:
    st.error("กำลังดึงข้อมูล... หากนานเกินไปกรุณาตรวจสอบ API Key ครับ")
