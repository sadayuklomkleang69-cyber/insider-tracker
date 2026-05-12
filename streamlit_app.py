import streamlit as st
import pandas as pd
import yfinance as yf

# 1. ตั้งค่าหน้ากระดาษ
st.set_page_config(page_title="Chairman Nu Command Center V7.2", layout="wide")

# 2. ระบบเงินสดในมือ
if 'base_cash' not in st.session_state:
    st.session_state.base_cash = 4000

# 3. ข้อมูลหุ้นและราคาเป้าหมายไม้ 1 (อิงจากกลยุทธ์ของประธาน)
target_prices = {
    "NVDA": 210.00, "TSM": 380.00, "ASML": 1450.00, "PLTR": 130.00, 
    "GOOGL": 380.00, "AVGO": 400.00, "MSFT": 400.00, "AMZN": 260.00, 
    "ARM": 200.00, "AMD": 430.00, "MU": 730.00, "RKLB": 110.00
}

tickers = list(target_prices.keys())

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
            # คำนวณความห่างจากจุดช้อน
            dist_to_target = ((current_p - target) / target) * 100
            
            stock_data.append({
                "Ticker": symbol,
                "Price": round(current_p, 2),
                "Change %": f"{change:.2f}%",
                "Target ไม้ 1": target,
                "Gap to Buy": f"{dist_to_target:.2f}%",
                "Raw_Change": change,
                "Raw_Gap": dist_to_target
            })
        except:
            stock_data.append({"Ticker": symbol, "Price": 0, "Change %": "N/A", "Raw_Change": 0, "Raw_Gap": 999})
    return pd.DataFrame(stock_data)

df_live = get_live_data(tickers)

# --- 🎯 โหมดหลัก ---
mode = st.sidebar.radio("เลือกโหมด:", ("🎯 กลยุทธ์ & การช้อนหุ้น", "💰 Cash Tracker", "📰 News"))

if mode == "🎯 กลยุทธ์ & การช้อนหุ้น":
    st.title("🎯 กลยุทธ์การลงทุน: ตัวไหนน่าช้อน?")
    
    # แสดงตารางพร้อมไฮไลท์ตัวที่ Gap น้อยๆ (ใกล้จุดช้อน)
    st.dataframe(df_live[["Ticker", "Price", "Change %", "Target ไม้ 1", "Gap to Buy"]], use_container_width=True)

    st.markdown("---")
    st.subheader("🤖 Jarvis Analysis: คืนนี้ช้อนตัวไหนดี?")
    
    # คัดเลือกตัวที่น่าช้อน (Gap < 2% หรือทะลุ Target ไปแล้ว)
    buy_list = df_live[df_live['Raw_Gap'] <= 2.0].sort_values(by='Raw_Gap')

    if not buy_list.empty:
        st.success(f"🔥 **ตรวจพบโอกาสช้อน! มี {len(buy_list)} ตัวเข้าเขตไม้ 1**")
        for index, row in buy_list.iterrows():
            with st.expander(f"✅ ซื้อได้: {row['Ticker']} (ห่างจากเป้าแค่ {row['Gap to Buy']})"):
                st.write(f"ราคาปัจจุบัน {row['Price']} | เป้าหมาย {row['Target ไม้ 1']}")
                st.write(f"**Jarvis Action:** ด้วยเงิน 4,000 ที่เหลือ เติม {row['Ticker']} ได้อีก 1,000 บาท จะช่วยดึงค่าเฉลี่ยได้ดีมาก")
    else:
        st.warning("⏳ **สถานะ: ยังไม่ต้องรีบช้อน**")
        st.write("เหตุผล: ราคาส่วนใหญ่ยังอยู่สูงกว่าเป้าหมายไม้ 1 เกิน 2% แนะนำให้รอน้ำมันนิ่งกว่านี้ก่อน")

    # สรุปภาพรวม
    st.info(f"💡 **สรุป:** ตัวที่ลงหนักสุดตอนนี้คือ {df_live.loc[df_live['Raw_Change'].idxmin()]['Ticker']} ({df_live.loc[df_live['Raw_Change'].idxmin()]['Change %']})")

elif mode == "💰 Cash Tracker":
    st.title("💰 บริหารเงินสด")
    st.metric("เงินสดพร้อมใช้", f"{st.session_state.base_cash} THB")
