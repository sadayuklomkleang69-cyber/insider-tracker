import streamlit as st
import pandas as pd
import yfinance as yf

# 1. ตั้งค่าหน้ากระดาษ
st.set_page_config(page_title="Chairman Nu Command Center V7.2", layout="wide")

# 2. ระบบจัดการเงินสด (Session State)
if 'base_cash' not in st.session_state:
    st.session_state.base_cash = 4000

# 3. ข้อมูลหุ้นและราคาเป้าหมายไม้ 1
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
                "Target ไม้ 1": target, "Gap to Buy": f"{dist_to_target:.2f}%",
                "Raw_Change": change, "Raw_Gap": dist_to_target
            })
        except:
            stock_data.append({"Ticker": symbol, "Price": 0, "Change %": "N/A", "Raw_Change": 0, "Raw_Gap": 999})
    return pd.DataFrame(stock_data)

df_live = get_live_data(tickers)

# 5. Sidebar Menu
st.sidebar.title("💎 Main Menu")
st.sidebar.metric("Cash Available", f"{st.session_state.base_cash:,} THB")
mode = st.sidebar.radio(
    "เลือกโหมดการทำงาน:",
    ("🎯 กลยุทธ์ & การช้อนหุ้น", "📊 Whale Sentiment Score", "🐳 Insider Live Feed", "📰 News Intelligence", "💰 Cash Tracker")
)

# ฟังก์ชันสรุปของจาร์วิส
def jarvis_advice():
    st.markdown("---")
    st.subheader("💡 Jarvis Executive Summary")
    worst_stock = df_live.loc[df_live['Raw_Change'].idxmin()]
    col1, col2 = st.columns(2)
    with col1:
        st.error(f"🚨 **Alert:** {worst_stock['Ticker']} ลงแรงสุด ({worst_stock['Change %']})")
        st.info("⛽ **Market:** น้ำมันพุ่ง $107 กดดันหุ้น Tech ทั่วโลก")
    with col2:
        st.warning(f"💰 **Strategy:** กระสุนเหลือ {st.session_state.base_cash:,} THB")
        if st.session_state.base_cash < 2000:
            st.error("❌ **Action:** กระสุนเหลือน้อย 'ห้ามเติมเพิ่ม' เพื่อรอดูจุดกลับตัว")
        else:
            st.success("✅ **Action:** ทยอยช้อนตัวที่เข้าเขตเป้าหมายไม้ 1 เท่านั้น")

# --- โหมดต่างๆ ---
if mode == "🎯 กลยุทธ์ & การช้อนหุ้น":
    st.title("🎯 กลยุทธ์การลงทุน: ตัวไหนน่าช้อน?")
    st.dataframe(df_live[["Ticker", "Price", "Change %", "Target ไม้ 1", "Gap to Buy"]], use_container_width=True)
    
    st.markdown("---")
    st.subheader("🤖 Jarvis Analysis: คืนนี้ช้อนตัวไหนดี?")
    buy_list = df_live[df_live['Raw_Gap'] <= 1.0].sort_values(by='Raw_Gap')
    if not buy_list.empty:
        st.success(f"🔥 **ตรวจพบโอกาสช้อน! มี {len(buy_list)} ตัวเข้าเขตไม้ 1**")
        for _, row in buy_list.iterrows():
            with st.expander(f"✅ ช้อนได้เลย: {row['Ticker']} (ห่างเป้าแค่ {row['Gap to Buy']})"):
                st.write(f"ราคาปัจจุบัน {row['Price']} | เป้าไม้ 1: {row['Target ไม้ 1']}")
                st.write("**คำแนะนำ:** เติม 1,000 บาท เพื่อดึงต้นทุนลงในจังหวะ Panic")
    else:
        st.warning("⏳ **สถานะ:** ยังไม่ต้องรีบช้อน ราคาส่วนใหญ่ยังอยู่สูงกว่าเป้าหมาย")
    jarvis_advice()

elif mode == "📊 Whale Sentiment Score":
    st.title("📊 Whale Sentiment: แรงซื้อสถาบัน")
    st.metric("Whale Accumulation Score", "35%", delta="-5% (ชะลอการซื้อ)")
    st.write("👉 สถาบันกำลังโยกเงินหนีความเสี่ยงจากเงินเฟ้อ")
    jarvis_advice()

elif mode == "🐳 Insider Live Feed":
    st.title("🐳 Insider Live Feed: รอยเท้าเจ้ามือ")
    st.success("🚀 **RKLB:** ผู้บริหารยังถือครองเหนียวแน่น ไม่พบการเทขายผิดปกติ")
    st.error("⚠️ **MU:** พบแรงเทขายรุนแรงจากกลุ่มสถาบันระยะสั้น")
    jarvis_advice()

elif mode == "📰 News Intelligence":
    st.title("📰 News Intelligence: Market Pulse")
    st.error("📌 **Oil Crisis:** ราคา Brent พุ่งแตะ $107 ทุบตลาดหุ้น")
    st.info("📌 **AI Earnings:** ตลาดรอจับตา NVDA สัปดาห์หน้า (ตัวตัดสินทิศทางพอร์ต)")
    jarvis_advice()

elif mode == "💰 Cash Tracker":
    st.title("💰 บริหารเงินสด (Refill System)")
    add_cash = st.number_input("เติมเงินเข้าพอร์ต (THB):", min_value=0, step=500)
    if st.button("ยืนยันการเติมเงิน"):
        st.session_state.base_cash += add_cash
        st.success(f"เติมสำเร็จ! ยอดปัจจุบัน: {st.session_state.base_cash}")
    
    st.markdown("---")
    buy_count = st.number_input("วันนี้เติมหุ้นไปกี่ตัว (ตัวละ 1,000):", min_value=0, step=1)
    if st.button("บันทึกการใช้เงินซื้อหุ้น"):
        st.session_state.base_cash -= (buy_count * 1000)
        st.success("บันทึกเรียบร้อย!")
    st.metric("เงินสดที่เหลือพร้อมใช้", f"{st.session_state.base_cash:,} THB")
