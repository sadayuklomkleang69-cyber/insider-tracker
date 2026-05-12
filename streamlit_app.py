import streamlit as st
import pandas as pd
import yfinance as yf

# 1. ตั้งค่าหน้ากระดาษ
st.set_page_config(page_title="Chairman Nu Command Center V7.2", layout="wide")

# 2. Sidebar & Cash Status
st.sidebar.title("💎 Main Menu")
cash_on_hand = 4000 
st.sidebar.metric("Cash on Hand", f"{cash_on_hand:,} THB")

mode = st.sidebar.radio(
    "เลือกโหมดการทำงาน:",
    ("🎯 กลยุทธ์ & ความคุ้มค่า", "📊 Whale Sentiment Score", "🐳 Insider Live Feed", "📰 News Intelligence")
)

# 3. ข้อมูลหุ้นจาก Watchlist ของท่าน (เชื่อมโยงราคาจริง)
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
            stock_data.append({
                "Ticker": symbol,
                "Price": round(current_p, 2),
                "Change %": f"{change:.2f}%",
                "Raw_Change": change
            })
        except:
            stock_data.append({"Ticker": symbol, "Price": 0, "Change %": "N/A", "Raw_Change": 0})
    return pd.DataFrame(stock_data)

df_live = get_live_data(tickers)

# --- ฟังก์ชันสรุป Action รายวัน (ใช้ทุกหน้า) ---
def jarvis_summary():
    st.markdown("---")
    st.subheader("💡 Jarvis Executive Summary")
    
    # ดึงตัวที่ลงหนักสุดมาเตือน
    worst_stock = df_live.loc[df_live['Raw_Change'].idxmin()]
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"📊 **Market Sentiment:** ตลาดกำลัง Panic จากราคาน้ำมัน $107")
        st.error(f"🚨 **Alert:** {worst_stock['Ticker']} ลงแรงผิดปกติ ({worst_stock['Change %']})")
    with col2:
        st.warning(f"💰 **Cash Strategy:** เหลือ 4,000 THB")
        st.success(f"⚡ **Final Action:** อยู่เฉยๆ (Stay Flat) - รอไม้ 2 ที่จุดกลับตัว")

# --- การแสดงผลแต่ละโหมด ---

if mode == "🎯 กลยุทธ์ & ความคุ้มค่า":
    st.title("🎯 กลยุทธ์การลงทุน: จุดซื้อไม้ 1-2-3")
    st.dataframe(df_live[["Ticker", "Price", "Change %"]], use_container_width=True)
    jarvis_summary()

elif mode == "📊 Whale Sentiment Score":
    st.title("📊 Whale Sentiment Score: แรงซื้อสถาบัน")
    st.write("วิเคราะห์การเคลื่อนย้ายเงินของกองทุนใหญ่ (Smart Money)")
    st.progress(35, text="Whale Accumulation Score: 35% (กำลังรอดูเชิง)")
    st.write("👉 สัญญาณ: กองทุนเริ่มชะลอการซื้อหุ้น Tech และย้ายไปถือเงินสดชั่วคราว")
    jarvis_summary()

elif mode == "🐳 Insider Live Feed":
    st.title("🐳 Insider Live Feed: รอยเท้าเจ้ามือ")
    c1, c2 = st.columns(2)
    with c1:
        st.success("🚀 **RKLB:** ผู้บริหารยังถือครองเหนียวแน่น ไม่พบการเทขายตามตลาด")
    with c2:
        st.error("⚠️ **MU:** พบแรงเทขายจากสถาบันระยะสั้น (Short-term Flush)")
    jarvis_summary()

elif mode == "📰 News Intelligence":
    st.title("📰 News Intelligence: Market Pulse")
    st.error("📌 Oil Prices at $107 continues to pressure Tech stocks.")
    st.info("📌 จับตางบ NVDA อาทิตย์หน้า: ตัวตัดสินชะตาหุ้น AI ทั้งพอร์ต")
    jarvis_summary()
