import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบติดตามหุ้นคนใน", layout="wide")

# ส่วนหัวของโปรแกรม
st.title("🚀 ระบบติดตามหุ้นระดับโปร (Insider Tracker)")
st.markdown("---")

# แถบเมนูด้านซ้าย
st.sidebar.header("เมนูการตั้งค่า")
symbol = st.sidebar.text_input("กรอกชื่อหุ้น (เช่น NVDA, TSLA, CPALL.BK)", "NVDA").upper()

# ดึงข้อมูลจาก Yahoo Finance
ticker = yf.Ticker(symbol)

try:
    # 1. ส่วนแสดงราคาล่าสุดและกราฟ
    df = ticker.history(period="6mo")
    if df.empty:
        st.error("❌ ไม่พบข้อมูลหุ้นตัวนี้ กรุณาเช็คชื่อย่อหุ้นอีกครั้ง")
    else:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            current_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-2]
            diff = current_price - prev_price
            color = "green" if diff >= 0 else "red"
            
            st.metric("ราคาล่าสุด", f"${current_price:.2f}", f"{diff:.2f}")
            
            st.write("### 🏢 ข้อมูลบริษัท")
            info = ticker.info.get('longBusinessSummary', 'ไม่มีข้อมูลภาษาไทย')
            st.write(info[:500] + "...")

        with col2:
            # สร้างกราฟแท่งเทียน
            fig = go.Figure(data=[go.Candlestick(x=df.index,
                            open=df['Open'], high=df['High'],
                            low=df['Low'], close=df['Close'])])
            fig.update_layout(
                title=f"กราฟราคาหุ้น {symbol} (ย้อนหลัง 6 เดือน)",
                template="plotly_dark",
                height=450,
                xaxis_title="วันที่",
                yaxis_title="ราคา"
            )
            st.plotly_chart(fig, use_container_width=True)

    # 2. ส่วนข้อมูลเชิงลึก
    st.markdown("---")
    st.header("🔍 เจาะลึกข้อมูลวงใน")
    
    แถบ1, แถบ2, แถบ3 = st.tabs(["📊 การซื้อขายของคนใน", "👥 ผู้ถือหุ้นรายใหญ่", "📢 คำแนะนำจากนักวิเคราะห์"])
    
    with แถบ1:
        st.subheader("รายการซื้อขายโดยผู้บริหาร (Insider)")
        insider_data = ticker.insider_transactions
        if insider_data is not None and not insider_data.empty:
            st.dataframe(insider_data, use_container_width=True)
        else:
            st.info("ไม่พบข้อมูลการซื้อขายของคนในสำหรับหุ้นตัวนี้ (ส่วนใหญ่จะแสดงเฉพาะหุ้น US)")

    with แถบ2:
        st.subheader("รายชื่อผู้ถือหุ้นรายใหญ่")
        holders = ticker.major_holders
        if holders is not None and not holders.empty:
            st.table(holders)
        else:
            st.info("ไม่พบข้อมูลผู้ถือหุ้นรายใหญ่")

    with แถบ3:
        st.subheader("บทวิเคราะห์ล่าสุด")
        recommendations = ticker.recommendations
        if recommendations is not None and not recommendations.empty:
            st.dataframe(recommendations.tail(10), use_container_width=True)
        else:
            st.info("ไม่พบข้อมูลคำแนะนำจากนักวิเคราะห์")

except Exception as e:
    st.warning(f"ระบบกำลังเตรียมข้อมูล: {e}")

st.sidebar.markdown("---")
if st.sidebar.button('🔄 รีเฟรชข้อมูล'):
    st.rerun()
