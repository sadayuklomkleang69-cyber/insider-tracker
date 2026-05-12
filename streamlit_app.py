import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="Chairman Nu Command Center V6.9", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0A0A0A; color: #E0E0E0; }
    h1, h2, h3 { color: #00AAFF !important; }
    .whale-card { background: linear-gradient(145deg, #1a1a1a, #252525); padding: 20px; border-radius: 15px; border-left: 8px solid #00FF88; margin-bottom: 15px; }
    .sell-card { border-left: 8px solid #FF4444; }
    .status-live { color: #00FF88; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# --- 2. WATCHLIST ---
watchlist = ['NVDA', 'TSM', 'ASML', 'PLTR', 'GOOGL', 'AVGO', 'MSFT', 'AMZN', 'ARM', 'AMD', 'MU', 'NBIS', 'RKLB', 'JEPQ', 'SPYI', 'SOFI', 'UPST']

@st.cache_data(ttl=300)
def fetch_all_data():
    all_data_list = []
    prices = {}
    for ticker in watchlist:
        try:
            t = yf.Ticker(ticker)
            p = t.info.get('regularMarketPrice') or t.info.get('currentPrice') or 0
            prices[ticker] = p
            df = t.insider_transactions
            if df is not None and not df.empty:
                df = df.copy()
                df['Symbol'] = ticker
                df['Date'] = pd.to_datetime(df['Start Date'] if 'Start Date' in df.columns else df.index)
                all_data_list.append(df)
        except: continue
    return (pd.concat(all_data_list) if all_data_list else pd.DataFrame()), prices

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🎛️ Command Center V6.9")
    menu = st.radio("เลือกโหมด:", ["📊 Whale Sentiment", "🎯 กลยุทธ์การช้อน & ขาย", "🐳 Insider Feed", "🧮 คำนวณ Dime"])
    st.markdown("---")
    st.markdown(f"สถานะ: <span class='status-live'>● LIVE</span>", unsafe_allow_html=True)

try:
    full_df, current_prices = fetch_all_data()

    if menu == "🎯 กลยุทธ์การช้อน & ขาย":
        st.title("🎯 กลยุทธ์เข้าทำและทางหนีไฟ (ไม้ 1-2-3)")
        
        strategy_data = []
        for ticker in watchlist:
            price = current_prices.get(ticker, 0)
            if price == 0: continue
            
            # คำนวณ Sentiment เพื่อดูความเสี่ยง
            risk_level = "🟢 ต่ำ"
            if not full_df.empty:
                ticker_data = full_df[full_df['Symbol'] == ticker]
                sells = ticker_data[ticker_data['Text'].str.contains('Sale', case=False, na=False)]
                if len(sells) > 5: risk_level = "🔴 เสี่ยง (วาฬรินขาย)"
            
            strategy_data.append({
                "หุ้น": ticker,
                "ราคาปัจจุบัน": f"${price:.2f}",
                "ช้อนไม้ 1 (-5%)": f"${price*0.95:.2f}",
                "ช้อนไม้ 2 (-10%)": f"${price*0.90:.2f}",
                "ช้อนไม้ 3 (-15%)": f"${price*0.85:.2f}",
                "ขายไม้ 1 (+10%)": f"${price*1.10:.2f}",
                "ขายไม้ 2 (+20%)": f"${price*1.20:.2f}",
                "ความเสี่ยง": risk_level
            })
        
        st.dataframe(pd.DataFrame(strategy_data), use_container_width=True)
        st.info("💡 คำแนะนำ: ไม้ 1 คือเริ่มสะสม, ไม้ 2 คือจุดแนวรับแข็ง, ไม้ 3 คือจุดถัวเฉลี่ยเมื่อเกิด Panic Sell")

    elif menu == "📊 Whale Sentiment":
        st.title("📊 Whale Confidence Score")
        scores = []
        for ticker in watchlist:
            f_score, status = 0, "💤 นิ่ง"
            if not full_df.empty:
                ticker_data = full_df[full_df['Symbol'] == ticker]
                buys = ticker_data[ticker_data['Text'].str.contains('Purchase|Exercise|Acquisition', case=False, na=False)]
                if not buys.empty:
                    f_score = 10
                    status = "🔥 แรงมาก"
            scores.append({"หุ้น": ticker, "คะแนน": f_score, "สถานะ": status})
        st.dataframe(pd.DataFrame(scores).sort_values("คะแนน", ascending=False), use_container_width=True)

    # ... (ส่วนอื่นคงเดิมเพื่อให้ระบบไม่พัง) ...
    elif menu == "🐳 Insider Feed":
        st.title("🐳 Insider Feed")
        st.write("ตรวจสอบรายการย้อนหลังในหน้าหลัก")

    elif menu == "🧮 คำนวณ Dime":
        st.title("🧮 คำนวณ Dime")
        st.number_input("จำนวนหุ้น", value=0.0)

except Exception as e:
    st.error(f"ระบบขัดข้อง: {e}")
