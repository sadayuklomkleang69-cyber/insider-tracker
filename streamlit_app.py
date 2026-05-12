import streamlit as st
import pandas as pd
import yfinance as yf

# 1. ตั้งค่าหน้ากระดาษ
st.set_page_config(page_title="Chairman Nu Command Center V7.2", layout="wide")

# 2. ระบบจัดการเงินสด (Cash Management)
# เริ่มต้นด้วยเงิน 4,000 ที่ท่านแจ้งไว้
if 'base_cash' not in st.session_state:
    st.session_state.base_cash = 4000

# 3. Sidebar Menu
st.sidebar.title("💎 Main Menu")
mode = st.sidebar.radio(
    "เลือกโหมดการทำงาน:",
    ("🎯 กลยุทธ์ & ความคุ้มค่า", "💰 Cash & Refill Tracker", "📊 Whale Sentiment Score", "🐳 Insider Live Feed", "📰 News Intelligence")
)

# 4. ดึงข้อมูลราคาหุ้น Real-time
tickers = ["NVDA", "TSM", "ASML", "PLTR", "GOOGL", "AVGO", "MSFT", "AMZN", "ARM", "AMD", "MU", "RKLB"]

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
            stock_data.append({"Ticker": symbol, "Price": round(current_p, 2), "Change %": f"{change:.2f}%", "Raw_Change": change})
        except:
            stock_data.append({"Ticker": symbol, "Price": 0, "Change %": "N/A", "Raw_Change": 0})
    return pd.DataFrame(stock_data)

df_live = get_live_data(tickers)

# --- ฟังก์ชันสรุปของจาร์วิส ---
def jarvis_summary(available_cash):
    st.markdown("---")
    st.subheader("💡 Jarvis Executive Summary")
    worst_stock = df_live.loc[df_live['Raw_Change'].idxmin()]
    
    c1, c2 = st.columns(2)
    with c1:
        st.error(f"🚨 **Alert:** {worst_stock['Ticker']} ลงแรงสุด ({worst_stock['Change %']})")
        st.info(f"⛽ **Market:** น้ำมันยังค้างที่ $107 กดดันหุ้น Tech")
    with c2:
        st.warning(f"💰 **สถานะกระสุน:** เหลือพร้อมใช้ {available_cash:,} THB")
        if available_cash < 2000:
            st.error("❌ **Final Action:** กระสุนวิกฤต! ห้ามเติมเพิ่มเด็ดขาด")
        else:
            st.success("✅ **Final Action:** รอจังหวะปลาใหญ่กินเบ็ดไม้ 2")

# --- 💰 โหมดใหม่: Cash & Refill Tracker ---
if mode == "💰 Cash & Refill Tracker":
    st.title("💰 Cash & Refill Tracker: บริหารกระสุนเรียลไทม์")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💵 เติมเงินเข้าพอร์ต (Top-up)")
        add_cash = st.number_input("ใส่จำนวนเงินที่โอนเข้าวันนี้ (THB):", min_value=0, step=500)
        if st.button("ยืนยันการเติมเงิน"):
            st.session_state.base_cash += add_cash
            st.success(f"บันทึกการเติมเงิน {add_cash:,} บาท เรียบร้อย!")

    with col2:
        st.subheader("📉 บันทึกการซื้อวันนี้")
        buy_count = st.number_input("วันนี้เติมหุ้นไปกี่ตัว (ตัวละ 1,000):", min_value=0, step=1)
        used_cash = buy_count * 1000
        
    current_available = st.session_state.base_cash - used_cash
    
    st.markdown("---")
    st.metric(label="กระสุนที่เหลือพร้อมลุย (Available Cash)", value=f"{current_available:,} THB", delta=f"-{used_cash} Used")
    
    if current_available <= 0:
        st.error("⚠️ ท่านใช้กระสุนหมดแล้ว! กรุณาเติมเงินเข้าพอร์ตก่อนทำไม้ถัดไป")

# --- โหมดอื่นๆ ---
elif mode == "🎯 กลยุทธ์ & ความคุ้มค่า":
    st.title("🎯 กลยุทธ์การลงทุน: จุดซื้อไม้ 1-2-3")
    st.dataframe(df_live[["Ticker", "Price", "Change %"]], use_container_width=True)
    # ดึงค่าเงินปัจจุบันไปโชว์ในสรุป
    current_available = st.session_state.base_cash - (0) # สมมติว่ายังไม่ได้หักในหน้านี้
    jarvis_summary(st.session_state.base_cash)

elif mode == "📰 News Intelligence":
    st.title("📰 News Intelligence")
    st.info("📌 จับตา [MU](https://th.tradingview.com/chart/5JVFrU0o/?symbol=NASDAQ%3AMU) ที่ลงแรงถึง -6.72% เป็นโอกาสหรือความเสี่ยง?")
    jarvis_summary(st.session_state.base_cash)

else:
    st.title(f"{mode}")
    st.write("ระบบกำลังซิงค์ข้อมูล...")
    jarvis_summary(st.session_state.base_cash)
