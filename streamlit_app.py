import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# 1. ตั้งค่าหน้ากระดาษ
st.set_page_config(page_title="Chairman Nu Command Center V7.2", layout="wide")

# 2. ระบบจัดการเงินสด (บังคับให้เริ่มต้นที่ 4,000 เสมอ)
if 'base_cash' not in st.session_state:
    st.session_state.base_cash = 4000
if 'history_logs' not in st.session_state:
    st.session_state.history_logs = []

# 3. ข้อมูลหุ้นและเป้าหมายไม้ 1
target_prices = {
    "NVDA": 210.00, "TSM": 380.00, "ASML": 1450.00, "PLTR": 130.00, 
    "GOOGL": 380.00, "AVGO": 400.00, "MSFT": 400.00, "AMZN": 260.00, 
    "ARM": 200.00, "AMD": 430.00, "MU": 730.00, "RKLB": 110.00
}
tickers = list(target_prices.keys())

# 4. ฟังก์ชันดึงราคา Real-time
@st.cache_data(ttl=300)
def get_live_data(ticker_list):
    stock_data = []
    for symbol in ticker_list:
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period="2d")
            current_p = hist['Close'].iloc[-1]
            prev_p = hist['Close'].iloc[-2]
            change = ((current_p - prev_p) / prev_p) * 100
            target = target_prices.get(symbol, 0)
            dist_to_target = ((current_p - target) / target) * 100
            stock_data.append({
                "Ticker": symbol, "Price": round(current_p, 2), "Change %": f"{change:.2f}%",
                "Target": target, "Gap": f"{dist_to_target:.2f}%",
                "Raw_Change": change, "Raw_Gap": dist_to_target
            })
        except:
            stock_data.append({"Ticker": symbol, "Price": 0, "Change %": "N/A", "Raw_Gap": 999})
    return pd.DataFrame(stock_data)

df_live = get_live_data(tickers)

# 5. Sidebar Menu
st.sidebar.title("💎 Main Menu")
st.sidebar.metric("Cash Available", f"{st.session_state.base_cash:,} THB")
mode = st.sidebar.radio("เลือกโหมด:", ("🎯 กลยุทธ์ & การช้อนหุ้น", "💰 Cash Tracker", "📊 Whale Score", "🐳 Insider Live", "📰 News"))

# ฟังก์ชันสรุปของจาร์วิส
def jarvis_executive_summary():
    st.markdown("---")
    st.subheader("💡 Jarvis Executive Summary")
    worst = df_live.loc[df_live['Raw_Change'].idxmin()]
    col1, col2 = st.columns(2)
    with col1:
        st.error(f"🚨 **Alert:** {worst['Ticker']} ลงแรงสุด ({worst['Change %']})")
    with col2:
        st.warning(f"💰 **Strategy:** กระสุนเหลือ {st.session_state.base_cash:,} THB")
        st.success("✅ **Action:** อยู่เฉยๆ หรือช้อนตามป้ายเขียว")

# --- การแสดงผลแต่ละโหมด ---
if mode == "🎯 กลยุทธ์ & การช้อนหุ้น":
    st.title("🎯 กลยุทธ์: ตัวไหนน่าช้อน?")
    st.dataframe(df_live[["Ticker", "Price", "Change %", "Target", "Gap"]], use_container_width=True)
    buy_list = df_live[df_live['Raw_Gap'] <= 1.0].sort_values(by='Raw_Gap')
    if not buy_list.empty:
        st.success(f"🔥 โอกาสช้อน! มี {len(buy_list)} ตัวเข้าเป้า")
        for _, row in buy_list.iterrows():
            st.write(f"✅ **{row['Ticker']}** ห่างเป้าแค่ {row['Gap']} (ช้อนได้เลย!)")
    jarvis_executive_summary()

elif mode == "💰 Cash Tracker":
    st.title("💰 บริหารเงินสด & บันทึกการเติมรายตัว")
    with st.expander("➕ เติมเงินเข้าพอร์ต"):
        amt = st.number_input("เงินที่โอนเข้า:", min_value=0, step=500)
        if st.button("ยืนยัน"):
            st.session_state.base_cash += amt
            st.rerun()
    
    st.subheader("🛒 บันทึกการช้อนหุ้นรายตัว")
    c1, c2 = st.columns(2)
    with c1: stock = st.selectbox("เลือกหุ้น:", tickers)
    with c2: buy_amt = st.number_input(f"เงินที่เติม {stock}:", min_value=0, value=1000)
    
    if st.button(f"🚀 บันทึกการช้อน {stock}"):
        if st.session_state.base_cash >= buy_amt:
            st.session_state.base_cash -= buy_amt
            st.session_state.history_logs.append({"เวลา": datetime.now().strftime("%H:%M"), "หุ้น": stock, "เงิน": buy_amt})
            st.rerun()
    
    if st.session_state.history_logs:
        st.table(pd.DataFrame(st.session_state.history_logs))

elif mode == "📊 Whale Score":
    st.title("📊 Whale Sentiment")
    st.metric("Whale Score", "35%", delta="-5%")
    jarvis_executive_summary()

elif mode == "🐳 Insider Live":
    st.title("🐳 Insider Live")
    st.success("🚀 **RKLB:** ผู้บริหารยังถือเหนียวแน่น")
    st.error("⚠️ **MU:** พบแรงเทขายรุนแรงจากสถาบัน")
    jarvis_executive_summary()

elif mode == "📰 News":
    st.title("📰 News Intelligence")
    st.error("📌 **Oil Crisis:** ราคา Brent $107")
    jarvis_executive_summary()
