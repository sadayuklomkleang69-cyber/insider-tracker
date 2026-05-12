import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="PRO Insider Tracker", layout="wide")

# ส่วนหัวโปรแกรม
st.title("🚀 PRO Insider Tracker")
st.markdown("---")

# Sidebar
st.sidebar.header("การตั้งค่า")
symbol = st.sidebar.text_input("กรอกชื่อหุ้น (เช่น NVDA, TSLA, CPALL.BK)", "NVDA").upper()

# ดึงข้อมูล
ticker = yf.Ticker(symbol)

try:
    # 1. ข้อมูลราคาและกราฟ
    df = ticker.history(period="6mo")
    if df.empty:
        st.error("ไม่พบข้อมูลหุ้นตัวนี้")
    else:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            current_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-2]
            diff = current_price - prev_price
            st.metric("ราคาล่าสุด", f"${current_price:.2f}", f"{diff:.2f}")
            
            st.write("**ข้อมูลบริษัท:**")
            st.write(ticker.info.get('longBusinessSummary', 'ไม่มีข้อมูลสรุป')[:300] + "...")

        with col2:
            fig = go.Figure(data=[go.Candlestick(x=df.index,
                            open=df['Open'], high=df['High'],
                            low=df['Low'], close=df['Close'])])
            fig.update_layout(title=f"กราฟราคา {symbol}", template="plotly_dark", height=400)
            st.plotly_chart(fig, use_container_width=True)

    # 2. ส่วนของ INSIDER (หัวใจหลัก)
    st.markdown("---")
    st.header("🔍 เจาะลึกข้อมูลคนใน (Insider)")
    
    tab1, tab2, tab3 = st.tabs(["การซื้อขายของคนใน", "ผู้ถือหุ้นรายใหญ่", "คำแนะนำจากนักวิเคราะห์"])
    
    with tab1:
        st.subheader("Insider Transactions")
        insider_df = ticker.insider_transactions
        if insider_df is not None and not insider_df.empty:
            st.dataframe(insider_df, use_container_width=True)
        else:
            st.write("❌ ไม่พบข้อมูลการซื้อขายของคนใน (หุ้นไทยอาจต้องดูจากหน้าเว็บ ก.ล.ต.)")

    with tab2:
        st.subheader("Major Holders")
        holders_df = ticker.major_holders
        if holders_df is not None and not holders_df.empty:
            st.table(holders_df)
        else:
            st.write("❌ ไม่พบข้อมูลผู้ถือหุ้นใหญ่")

    with tab3:
        st.subheader("Analyst Recommendations")
        recom_df = ticker.recommendations
        if recom_df is not None and not recom_df.empty:
            st.dataframe(recom_df.tail(10), use_container_width=True)
        else:
            st.write("❌ ไม่พบข้อมูลคำแนะนำ")

except Exception as e:
    st.warning(f"ระบบกำลังรอข้อมูลบางส่วน หรือเกิดข้อผิดพลาด: {e}")

st.sidebar.markdown("---")
if st.sidebar.button('🔄 รีเฟรชข้อมูล'):
    st.rerun()
