import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

# --- CONFIGURATION & UI STYLE ---
st.set_page_config(page_title="Insider Tracker", layout="wide")

# ปรับแต่ง CSS ให้เหมือนต้นฉบับ image_09ec5e.png
st.markdown("""
    <style>
    .main { background-color: #121212; color: white; }
    h1, h2, h3 { color: #4FA3FF !important; font-family: 'Kanit', sans-serif; }
    .buy-text { color: #2ECC71; font-weight: bold; font-size: 24px; }
    .sell-text { color: #E74C3C; font-weight: bold; font-size: 24px; }
    .metric-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #4FA3FF;
        margin-bottom: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    .ticker-name { color: #F1C40F; font-size: 22px; font-weight: bold; }
    .price-text { color: #4FA3FF; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title('วงใน "ซื้อ"')
st.subheader("Insiders วงใน")
st.write(f"อัปเดตล่าสุด: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# --- DATA SOURCE ---
API_KEY = "77f3e82845c843c98369269418e2444c"

@st.cache_data(ttl=300)
def fetch_insider_data():
    url = f"https://financialmodelingprep.com/api/v4/insider-trading?limit=100&apikey={API_KEY}"
    r = requests.get(url)
    return pd.DataFrame(r.json())

try:
    df = fetch_insider_data()
    # กรองเฉพาะรายการซื้อ (P-Purchase)
    df_buys = df[df['transactionType'] == 'P-Purchase'].copy()
    df_buys['Value_USD'] = df_buys['securitiesTransacted'] * df_buys['price']
    
    # เน้นหุ้นที่ประธานสนใจเป็นพิเศษ
    target_stocks = ['NVDA', 'TSM', 'MSFT', 'PLTR', 'UPST', 'SOFI', 'GOOGL']
    df_filtered = df_buys[df_buys['symbol'].isin(target_stocks)].sort_values(by='Value_USD', ascending=False).head(10)

    # --- LAYOUT (LEFT: DONUT, RIGHT: CARDS) ---
    col_left, col_right = st.columns([1, 2])

    with col_left:
        # กราฟวงกลม Donut แบบ image_09ec5e.png
        fig = px.pie(df_filtered, values='Value_USD', names='symbol', hole=0.75,
                     color_discrete_sequence=['#4FA3FF', '#2ECC71', '#F1C40F', '#9B59B6', '#E67E22'])
        fig.update_traces(textinfo='none') # คลีนแบบต้นฉบับ
        fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10),
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown('<p class="buy-text">● ซื้อ (Buy)</p>', unsafe_allow_html=True)
        
        if df_filtered.empty:
            st.write("ยังไม่มีรายการซื้อใหญ่ในหุ้นกลุ่มเป้าหมายวันนี้ครับประธาน")
        else:
            for _, row in df_filtered.iterrows():
                # สร้าง Card ข้อมูลรายตัว
                st.markdown(f"""
                <div class="metric-card">
                    <table style="width:100%;">
                        <tr>
                            <td style="width:20%;"><span class="ticker-name">{row['symbol']}</span><br><small>เมื่อ {row['transactionDate']}</small></td>
                            <td style="width:30%; text-align:center;">จำนวน: {int(row['securitiesTransacted']):,} หุ้น</td>
                            <td style="width:20%; text-align:center;"><span class="price-text">${row['price']:.2f}</span></td>
                            <td style="width:30%; text-align:right;">
                                <b>{row['reportingName']}</b><br>
                                <span style="color:#888;">{row['typeOfOwner']}</span>
                            </td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<p class="sell-text">● ขาย (Sell)</p>', unsafe_allow_html=True)
    st.write("พอร์ตนี้ไม่มีการขายซ้ำในหุ้นเป้าหมาย 🛒")

except Exception as e:
    st.error("จาร์วิสกำลังเชื่อมต่อระบบ API... หากรอนานเกินไป โปรดตรวจสอบการยืนยันอีเมลของบัญชี FMP ครับประธาน")
