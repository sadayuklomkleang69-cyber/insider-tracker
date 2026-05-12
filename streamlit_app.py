import streamlit as st
import pandas as pd
import yfinance as yf

# 1. ตั้งค่าหน้ากระดาษ
st.set_page_config(page_title="Chairman Nu Command Center V7.2", layout="wide")

# 2. Sidebar & Cash Management
st.sidebar.title("💎 Main Menu")
cash_on_hand = 4000  # จำนวนเงินคงเหลือที่ท่านแจ้งไว้
st.sidebar.metric("Cash on Hand", f"{cash_on_hand:,} THB")

mode = st.sidebar.radio(
    "เลือกโหมดการทำงาน:",
    ("🎯 กลยุทธ์ & ความคุ้มค่า", "📊 Whale Sentiment Score", "🐳 Insider Live Feed", "📰 News Intelligence")
)

# 3. รายชื่อหุ้นใน Watchlist ของประธาน
tickers = ["NVDA", "TSM", "ASML", "PLTR", "GOOGL", "AVGO", "MSFT", "AMZN", "ARM", "AMD", "MU", "RKLB"]

@st.cache_data(ttl=300) # อัปเดตทุก 5 นาที
def get_live_data(ticker_list):
    stock_data = []
    for symbol in ticker_list:
        try:
            # ดึงข้อมูลจาก Yahoo Finance
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

# ดึงข้อมูล Real-time
df_live = get_live_data(tickers)

# --- 🎯 โหมด กลยุทธ์ & ความคุ้มค่า ---
if mode == "🎯 กลยุทธ์ & ความคุ้มค่า":
    st.title("🎯 กลยุทธ์การลงทุน: Action วันต่อวัน")
    
    # แสดงตารางราคา Real-time
    st.dataframe(df_live[["Ticker", "Price", "Change %"]], use_container_width=True)
    
    st.markdown("---")
    st.subheader("💡 Jarvis Daily Action")
    
    # Logic วิเคราะห์ Action รายวัน
    worst_performer = df_live.loc[df_live['Raw_Change'].idxmin()]
    
    if worst_performer['Raw_Change'] < -5:
        st.error(f"🚨 **Action: เฝ้าระวังพิเศษที่ {worst_performer['Ticker']}**")
        st.write(f"เหตุผล: {worst_performer['Ticker']} ลงแรงกว่า {worst_performer['Change %']} เข้าเขต Panic")
        st.write(f"👉 **คำแนะนำ:** เนื่องจากเงินสดเหลือเพียง {cash_on_hand} บาท 'ห้ามกระจายเติมทุกตัว' ให้เลือกเติมตัวนี้เพียงตัวเดียวถ้าหลุดแนวรับสำคัญ หรือ 'อยู่เฉยๆ' เพื่อรอดูจุดต่ำสุด")
    else:
        st.success("✅ **Action: ถือครอง (Hold) / ทยอยเก็บตามแผน**")
        st.write("สถานะตลาดวันนี้: ยังไม่มีการเทขายที่รุนแรงจนผิดปกติ")

# --- โหมดอื่นๆ ---
elif mode == "📰 News Intelligence":
    st.title("📰 News Intelligence")
    st.write("ดึงข้อมูลจาก AI วิเคราะห์ข่าวต่างประเทศ...")
    st.info("📌 Oil Prices at $107 continues to pressure Tech stocks.")

else:
    st.title(f"{mode}")
    st.write("ระบบกำลังซิงค์ข้อมูล Whale & Insider...")
