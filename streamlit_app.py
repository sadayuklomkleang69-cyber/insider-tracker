import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

# 1. ตั้งค่าหน้าจอและ UI แบบ Dark Theme
st.set_page_config(page_title="Insider Tracker", layout="wide")

# ปรับแต่ง CSS ให้เหมือนรูป image_0a68dc.png
st.markdown("""
    <style>
    .main { background-color: #121212; color: white; }
    .stDataFrame { border: 1px solid #333; border-radius: 10px; }
    h1, h2, h3 { color: #4FA3FF !important; }
    .metric-card {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4FA3FF;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. หัวข้อระบบ
st.title('วงใน "ซื้อ"')
st.subheader("Insiders วงใน")
st.write(f"อัปเดตล่าสุด: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# 3. ข้อมูลและการเชื่อมต่อ
API_KEY = "OirEUM6wlgFPzMjSC3aWXFkwGkVin2d2"

@st.cache_data(ttl=300)
def get_data():
    url = f"https://financialmodelingprep.com/api/v4/insider-trading?limit=50&apikey={API_KEY}"
    r = requests.get(url)
    return pd.DataFrame(r.json())

try:
    df = get_data()
    df_buys = df[df['transactionType'] == 'P-Purchase'].copy()
    df_buys['Value_USD'] = df_buys['securitiesTransacted'] * df_buys['price']
    
    # หุ้นเป้าหมายของประธานนุ (Semi & Tech)
    target_stocks = ['NVDA', 'TSM', 'MSFT', 'PLTR', 'UPST', 'SOFI']
    df_final = df_buys[df_buys['symbol'].isin(target_stocks)].head(10)

    # 4. การจัดวาง Layout แบบในรูป (ซ้ายกราฟ - ขวาตาราง)
    col1, col2 = st.columns([1, 2])

    with col1:
        # กราฟวงกลม Donut แบบ image_0a68dc.png
        fig = px.pie(df_final, values='Value_USD', names='symbol', hole=0.7,
                     color_discrete_sequence=['#4FA3FF', '#2ECC71', '#F1C40F', '#E74C3C'])
        fig.update_traces(textinfo='none') # ซ่อนตัวเลขในกราฟให้คลีนแบบรูปต้นฉบับ
        fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), 
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<span style='color:#2ECC71;'>● ซื้อ (Buy)</span>", unsafe_allow_html=True)
        # ปรับแต่งตารางให้ดูง่าย
        for index, row in df_final.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="metric-card">
                    <table style="width:100%; border:none;">
                        <tr>
                            <td style="width:25%; font-size:20px; font-weight:bold; color:#F1C40F;">{row['symbol']}</td>
                            <td style="width:25%;">จำนวน: {int(row['securitiesTransacted']):,} หุ้น</td>
                            <td style="width:25%; color:#2ECC71;">${row['price']:.2f}</td>
                            <td style="width:25%; text-align:right; font-size:12px;">{row['reportingName']}<br>{row['typeOfOwner']}</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<span style='color:#E74C3C;'>● ขาย (Sell)</span>", unsafe_allow_html=True)
    st.write("พอร์ตนี้ไม่มีการขายซ้ำ 🛒")

except Exception as e:
    st.info("กำลังรอข้อมูลจากตลาด หรือ API กำลังเปิดใช้งานครับท่านประธานนุ")
