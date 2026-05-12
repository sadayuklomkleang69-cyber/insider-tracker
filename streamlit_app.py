import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# 1. ตั้งค่าหน้ากระดาษ
st.set_page_config(page_title="Chairman Nu Command Center V7.2", layout="wide")

# 2. ระบบจัดการเงินสด & ประวัติการซื้อ (Session State)
if 'base_cash' not in st.session_state:
    st.session_state.base_cash = 4000
if 'history_logs' not in st.session_state:
    st.session_state.history_logs = [] # เก็บประวัติ: {date, ticker, amount}

# 3. ข้อมูลหุ้น
target_prices = {
    "NVDA": 210.00, "TSM": 380.00, "ASML": 1450.00, "PLTR": 130.00, 
    "GOOGL": 380.00, "AVGO": 400.00, "MSFT": 400.00, "AMZN": 260.00, 
    "ARM": 200.00, "AMD": 430.00, "MU": 730.00, "RKLB": 110.00
}
tickers = list(target_prices.keys())

# 4. Sidebar Menu
st.sidebar.title("💎 Main Menu")
st.sidebar.metric("เงินสดที่เหลือพร้อมใช้", f"{st.session_state.base_cash:,} THB")
mode = st.sidebar.radio("เลือกโหมด:", ("🎯 กลยุทธ์ & การช้อนหุ้น", "💰 Cash Tracker", "📊 Whale Score", "🐳 Insider Live", "📰 News"))

# --- 💰 โหมดที่ประธานสั่งอัปเกรด: Cash Tracker ---
if mode == "💰 Cash Tracker":
    st.title("💰 บริหารเงินสด & ประวัติการเติมรายตัว")
    
    # ส่วนที่ 1: เติมเงินเข้า (Top-up)
    with st.expander("➕ เติมเงินเข้าพอร์ต (Refill)"):
        add_amount = st.number_input("จำนวนเงินที่โอนเข้า (THB):", min_value=0, step=500)
        if st.button("ยืนยันเติมเงิน"):
            st.session_state.base_cash += add_amount
            st.success(f"เติมเงินสำเร็จ! ยอดรวม: {st.session_state.base_cash:,}")

    st.markdown("---")

    # ส่วนที่ 2: บันทึกการซื้อหุ้น (ระบุรายตัวและจำนวนเงิน)
    st.subheader("🛒 บันทึกการเติมหุ้นรายวัน")
    col1, col2 = st.columns(2)
    with col1:
        selected_stock = st.selectbox("เลือกหุ้นที่เติม:", tickers)
    with col2:
        individual_buy_amount = st.number_input(f"ระบุจำนวนเงินที่เติม {selected_stock} (THB):", min_value=0, value=1000, step=100)
    
    if st.button(f"🚀 บันทึกการช้อน {selected_stock}"):
        if st.session_state.base_cash >= individual_buy_amount:
            st.session_state.base_cash -= individual_buy_amount
            # บันทึกลง Log
            new_log = {
                "วันที่-เวลา": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "หุ้น (Ticker)": selected_stock,
                "จำนวนเงิน (THB)": individual_buy_amount
            }
            st.session_state.history_logs.append(new_log)
            st.success(f"บันทึกเรียบร้อย: เติม {selected_stock} ไป {individual_buy_amount:,} บาท")
        else:
            st.error("❌ กระสุนไม่พอ! กรุณาเติมเงินก่อน")

    st.markdown("---")

    # ส่วนที่ 3: ตารางสรุปประวัติ (Log)
    st.subheader("📋 ประวัติการเติมหุ้นวันนี้")
    if st.session_state.history_logs:
        log_df = pd.DataFrame(st.session_state.history_logs)
        st.table(log_df)
        
        # แสดงยอดรวมแยกรายตัว (Total per stock)
        st.subheader("📈 สรุปยอดสะสมรวมรายตัว")
        summary_df = log_df.groupby("หุ้น (Ticker)")["จำนวนเงิน (THB)"].sum().reset_index()
        st.dataframe(summary_df, use_container_width=True)
    else:
        st.info("ยังไม่มีข้อมูลการช้อนในวันนี้")

# --- โหมดอื่นๆ (คงเดิมเพื่อความเสถียร) ---
elif mode == "🎯 กลยุทธ์ & การช้อนหุ้น":
    st.title("🎯 กลยุทธ์: ตัวไหนน่าช้อน?")
    st.info(f"Available Cash: {st.session_state.base_cash:,} THB")
    st.write("ระบบกำลังซิงค์ราคาจาก [TradingView](https://th.tradingview.com/chart/5JVFrU0o/?symbol=NASDAQ%3AMU)...")

else:
    st.title(f"{mode}")
    st.write("Jarvis is monitoring...")
