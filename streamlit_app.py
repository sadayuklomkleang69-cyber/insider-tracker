import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Insider Tracker", layout="wide")

st.title('🎯 ระบบจับตา "คนใน" (Yahoo Finance Edition)')
st.write("ดึงข้อมูลโดยตรง ไม่ต้องใช้ API Key")

# ช่องกรอกชื่อหุ้น
symbol = st.sidebar.text_input("กรอกชื่อหุ้น (เช่น NVDA, TSLA, AAPL)", "NVDA").upper()

try:
    ticker = yf.Ticker(symbol)
    
    # ดึงข้อมูลการซื้อขายของคนใน
    df = ticker.insider_transactions
    
    if df is not None and not df.empty:
        # กรองเฉพาะรายการซื้อ (P-Purchase)
        df_buys = df[df['Text'].str.contains('Purchase', case=False, na=False)].copy()
        
        if not df_buys.empty:
            col1, col2 = st.columns([1, 2])
            with col1:
                # กราฟวงกลมสัดส่วนจำนวนหุ้นที่ซื้อ
                fig = px.pie(df_buys, values='Shares', names='Insider', hole=0.7,
                             title=f"สัดส่วนการเก็บหุ้น {symbol}",
                             color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.write(f"### 💎 รายการซื้อโดยผู้บริหาร {symbol}")
                st.dataframe(df_buys[['Date', 'Insider', 'Shares', 'Price']], use_container_width=True)
        else:
            st.warning(f"ช่วงนี้ยังไม่มีผู้บริหาร {symbol} ซื้อหุ้นเพิ่มครับ")
    else:
        st.error("ไม่พบข้อมูล Insider สำหรับหุ้นตัวนี้")

except Exception as e:
    st.info("กรุณากรอกชื่อหุ้นที่ต้องการตรวจสอบด้านซ้ายมือครับ")
